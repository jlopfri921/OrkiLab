"""Explicit submission of saved ComfyUI API graphs; no automatic execution."""
import json
import hashlib
import time
import re
import sqlite3
import threading
import uuid
from contextlib import closing
from urllib.request import Request, build_opener, ProxyHandler
from urllib.error import HTTPError
from pathlib import Path
import shutil
from flask import jsonify, request, Response, stream_with_context, abort
from urllib.parse import urlencode
from generation_history import GenerationHistory, describe_outputs
import project_layout
from comfyui_connect import validate_settings, DEFAULT_SETTINGS, get_json, NoRedirect
from workflow_library import inspect_graph
from workflow_compatibility import assess_workflow
from generation_parameters import editable_fields, apply_edits
from workflow_conversion import convert_visual, node_schema, validate_prompt

def register(app, base):
    base = Path(base)
    jobs = {}
    records = GenerationHistory(base)
    prepared = {}
    guided_targets = {}  # Single-use benchmark preparation token -> exact target tuple.
    # Ephemeral, opt-in GPU diagnostics: not persisted as benchmark observations.
    gpu_monitors = {}
    lock = threading.Lock()

    def run_gpu_monitor(generation_id, option):
        from benchmark_gpu_live_capture import observe
        from benchmark_gpu_monitor_contract import monitoring_receipt
        with lock:
            gpu_monitors[generation_id] = monitoring_receipt("running")
        try:
            report = observe(base, generation_id, gpu_uuid=option["gpu_uuid"],
                             samples_limit=option["samples_limit"],
                             interval_seconds=option["interval_seconds"])
            state = ("completed" if report.get("ok") is True and report.get("termination") == "completed_history"
                     else "partial" if report.get("ok") is True else "failed")
            payload = {**report, **monitoring_receipt(state)}
        except Exception as exc:
            app.logger.warning("Experimental VRAM monitor failed: %s", exc)
            payload = {**monitoring_receipt("failed"),
                       "reason": "GPU diagnostic unavailable; generation unaffected"}
        with lock:
            gpu_monitors[generation_id] = payload


    def config():
        try:
            return validate_settings(json.loads((base / "settings" / "orkilab" / "comfyui.json").read_text(encoding="utf-8")), DEFAULT_SETTINGS)
        except (OSError, ValueError, TypeError):
            return dict(DEFAULT_SETTINGS)

    def local():
        return request.remote_addr in ("127.0.0.1", "::1")

    def submit(url, graph):
        client_id = str(uuid.uuid4())
        payload = json.dumps({"prompt": graph, "client_id": client_id}, allow_nan=False).encode()
        req = Request(url + "/prompt", data=payload, headers={"Content-Type": "application/json"}, method="POST")
        with build_opener(ProxyHandler({}), NoRedirect()).open(req, timeout=30) as response:
            result = json.loads(response.read(1_000_001))
        ident = result.get("prompt_id") if isinstance(result, dict) else None
        if not isinstance(ident, str) or not re.fullmatch(r"[a-zA-Z0-9_-]{1,100}", ident):
            raise ValueError("ComfyUI did not return a valid job ID")
        return ident, client_id

    def read_graph(ident):
        path = base / "settings" / "orkilab" / "workflows.sqlite3"
        if not path.is_file():
            return None
        with closing(sqlite3.connect(path)) as con:
            row = con.execute("SELECT graph FROM workflows WHERE id=?", (ident,)).fetchone()
        return row[0] if row else None

    @app.post("/api/workspace/generation/bridge/install")
    def bridge_install():
        if not local():
            return jsonify(error="Manage workflows on the launcher PC"), 403
        if request.mimetype != "application/json" or not 0 < (request.content_length or 0) <= 4096:
            return jsonify(error="Invalid request"), 400
        body = request.get_json(silent=True)
        raw = body.get("folder") if isinstance(body, dict) else None
        if not isinstance(raw, str) or not raw.strip():
            return jsonify(error="Select the ComfyUI custom_nodes folder"), 400
        try:
            root = Path(raw.strip()).expanduser()
            if not root.is_absolute() or root.name.lower() != "custom_nodes" or not root.is_dir():
                raise ValueError("Select the ComfyUI custom_nodes folder")
            root = root.resolve()
            source = base / "integrations" / "orkilab_bridge"
            target = root / "orkilab_bridge"
            for rel in ("__init__.py", "js/bridge.js"):
                dst = target / rel
                if not dst.resolve().is_relative_to(root) or not (source / rel).is_file():
                    raise ValueError("Invalid bridge installation path")
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(source / rel, dst)
            return jsonify(installed=True, folder=str(target))
        except (OSError, ValueError) as exc:
            return jsonify(error="Bridge installation failed", detail=str(exc)[:300]), 400

    @app.post("/api/workspace/generation/prepare")
    def generation_prepare():
        if not local():
            return jsonify(error="Manage workflows on the launcher PC"), 403
        if request.mimetype != "application/json" or not 0 < (request.content_length or 0) <= 16_000_000:
            return jsonify(error="Invalid request"), 400
        body = request.get_json(silent=True)
        if not isinstance(body, dict) or not isinstance(body.get("workflow_id"), str):
            return jsonify(error="Invalid request"), 400
        cfg = config()
        if cfg["mode"] == "native":
            return jsonify(error="ComfyUI is disabled in native mode"), 409
        ident = body["workflow_id"]
        raw = read_graph(ident)
        if raw is None:
            return jsonify(error="Workflow not found"), 404
        try:
            graph = json.loads(raw)
            fmt = inspect_graph(graph)["format"]
            bridge = body.get("bridge_prompt")
            if bridge is not None:
                if fmt != "ui" or inspect_graph(bridge)["format"] != "api":
                    raise ValueError("Invalid bridge prompt")
                graph = bridge
            elif fmt == "ui":
                graph = convert_visual(graph, cfg["url"], get_json)
            schemas = {kind: node_schema(cfg["url"], kind, get_json)
                       for kind in {n["class_type"] for n in graph.values()}}
            validate_prompt(graph, schemas)
            fields = editable_fields(graph, schemas)
            token = uuid.uuid4().hex
            with lock:
                for key in list(prepared):
                    if time.monotonic() - prepared[key][0] > 1800:
                        prepared.pop(key)
                while len(prepared) >= 20:
                    prepared.pop(next(iter(prepared)))
                prepared[token] = (time.monotonic(), ident, cfg["url"], hashlib.sha256(raw.encode()).hexdigest(), graph, fields, schemas)
            return jsonify(token=token, node_count=len(graph), converted=fmt=="ui", graph=graph, fields=fields)
        except (OSError, ValueError, TypeError, KeyError, RecursionError) as exc:
            return jsonify(error="Workflow preparation failed", detail=str(exc)[:500]), 400

    @app.post("/api/workspace/generation/parameters")
    def generation_parameters():
        if not local():
            return jsonify(error="Manage workflows on the launcher PC"), 403
        if request.mimetype != "application/json" or not 0 < (request.content_length or 0) <= 2_000_000:
            return jsonify(error="Invalid request"), 400
        body = request.get_json(silent=True)
        if not isinstance(body, dict) or not isinstance(body.get("token"), str):
            return jsonify(error="Invalid request"), 400
        cfg = config()
        if cfg["mode"] == "native":
            return jsonify(error="ComfyUI is disabled in native mode"), 409
        try:
            with lock:
                item = prepared.get(body["token"])
                if not item or time.monotonic() - item[0] > 1800 or item[2] != cfg["url"]:
                    return jsonify(error="Prepare workflow before generating"), 409
                graph = apply_edits(item[4], item[5], body.get("edits"))
                validate_prompt(graph, item[6])
                fields = editable_fields(graph, item[6])
                token = uuid.uuid4().hex
                prepared.pop(body["token"])
                prepared[token] = (*item[:4], graph, fields, item[6])
            return jsonify(token=token, graph=graph, fields=fields)
        except (ValueError, TypeError, KeyError, RecursionError, OverflowError) as exc:
            return jsonify(error="Invalid parameter changes", detail=str(exc)[:300]), 400

    @app.post("/api/workspace/generation/compare")
    def generation_compare():
        """Create separately validated, single-use variants from a prepared graph."""
        if not local():
            return jsonify(error="Manage workflows on the launcher PC"),403
        if request.mimetype != "application/json" or not 0 < (request.content_length or 0) <= 8192:
            return jsonify(error="Invalid request"),400
        body = request.get_json(silent=True)
        if not isinstance(body,dict) or not isinstance(body.get("token"),str) or not isinstance(body.get("node"),str):
            return jsonify(error="Invalid request"),400
        weights = body.get("weights")
        if not isinstance(weights,list) or not 2 <= len(weights) <= 6 or any(type(w) not in (int,float) or not -2 <= w <= 2 for w in weights) or len(set(weights)) != len(weights):
            return jsonify(error="Choose two to six distinct LoRA weights between -2 and 2"),400
        cfg = config()
        if cfg["mode"] == "native":
            return jsonify(error="ComfyUI is disabled in native mode"),409
        try:
            with lock:
                item = prepared.get(body["token"])
                if not item or time.monotonic()-item[0]>1800 or item[2]!=cfg["url"]:
                    return jsonify(error="Prepare workflow before generating"),409
                node = item[4].get(body["node"],{})
                if node.get("class_type") not in ("LoraLoader","LoraLoaderModelOnly"):
                    raise ValueError("Choose a supported LoRA loader")
                names = ["strength_model"] + (["strength_clip"] if node["class_type"]=="LoraLoader" else [])
                variants = []
                for weight in weights:
                    graph = apply_edits(item[4],item[5],[{"node":body["node"],"name":name,"value":weight} for name in names])
                    validate_prompt(graph,item[6])
                    variants.append((weight,graph))
                result = []
                while len(prepared)+len(variants)>20:
                    victim = next((key for key in prepared if key!=body["token"]),None)
                    if victim is None:
                        break
                    prepared.pop(victim)
                for weight,graph in variants:
                    token=uuid.uuid4().hex
                    prepared[token]=(time.monotonic(),*item[1:4],graph,editable_fields(graph,item[6]),item[6])
                    result.append({"weight":weight,"token":token})
            return jsonify(workflow_id=item[1],variants=result)
        except (ValueError,TypeError,KeyError,RecursionError) as exc:
            return jsonify(error="Comparison preparation failed",detail=str(exc)[:300]),400

    @app.post("/api/workspace/generation/compare/checkpoints")
    def compare_project_checkpoints():
        """Prepare checkpoint variants; never copy model files or change the saved workflow.

        Each candidate must be an existing project checkpoint and a recognized
        lora_name choice in this ComfyUI install. The graph's prompt/seed and
        all other parameters are unchanged across the variants.
        """
        if not local():
            return jsonify(error="Manage checkpoints on the launcher PC"), 403
        if request.mimetype != "application/json" or not 0 < (request.content_length or 0) <= 8192:
            return jsonify(error="Invalid request"), 400
        body = request.get_json(silent=True)
        if not isinstance(body, dict):
            return jsonify(error="Invalid request"), 400
        token, node_id, project_id = body.get("token"), body.get("node"), body.get("project_id")
        names = body.get("checkpoints")
        if not all(isinstance(v, str) for v in (token, node_id, project_id)):
            return jsonify(error="Select a prepared workflow, LoRA node and project"), 400
        if not isinstance(names, list) or not 2 <= len(names) <= 6 or not all(isinstance(x,str) for x in names) or len(names) != len(set(names)):
            return jsonify(error="Choose 2 to 6 different checkpoints"), 400
        cfg = config()
        if cfg["mode"] == "native":
            return jsonify(error="ComfyUI is disabled in native mode"), 409
        import project_checkpoints
        try:
            discovered = project_checkpoints.inventory(base, project_id)
            if not all(name in {x["name"] for x in discovered["checkpoints"]} for name in names):
                return jsonify(error="One or more checkpoints are missing from the project outputs"), 409
            with lock:
                item = prepared.get(token)
                if not item or time.monotonic()-item[0]>1800 or item[2]!=cfg["url"]:
                    return jsonify(error="Prepare workflow before generating"),409
                saved = read_graph(item[1])
                if not saved:
                    return jsonify(error="Saved workflow unavailable"),404
                with closing(sqlite3.connect(base / "settings" / "orkilab" / "workflows.sqlite3")) as workflows_db:
                    row = workflows_db.execute("SELECT category,name FROM workflows WHERE id=?", (item[1],)).fetchone()
                if not row:
                    return jsonify(error="Saved workflow unavailable"),404
                compatibility = assess_workflow(item[4], row[0], discovered["engine"], row[1])
                if compatibility["status"] != "candidate":
                    return jsonify(error="Workflow model family is not verified compatible with this project",
                                   detail=compatibility["reason"]),409
                node = item[4].get(node_id, {})
                if node.get("class_type") not in ("LoraLoader", "LoraLoaderModelOnly"):
                    return jsonify(error="Choose a standard LoRA loader"),400
                lora_field = next((f for f in item[5] if f["node"]==node_id and f["name"]=="lora_name"), None)
                if not lora_field or lora_field.get("kind")!="choice":
                    return jsonify(error="The workflow LoRA filename is not editable"),409
                choices = set(x for x in lora_field["choices"] if isinstance(x, str))
                from managed_checkpoints import model_name
                # Compare against the installed, human-readable project alias, not the internal UUID.
                # Read current ComfyUI choices rather than the stale list captured before installation.
                fresh_schema = node_schema(cfg["url"], node["class_type"], get_json)
                from workflow_conversion import combo_choices
                inputs = fresh_schema.get("input", {})
                descriptor = inputs.get("required", {}).get("lora_name", inputs.get("optional", {}).get("lora_name"))
                available = combo_choices(descriptor)
                if available is None:
                    return jsonify(error="Unable to read current LoRA options from ComfyUI"), 409
                choices = {choice for choice in available if isinstance(choice, str)}
                selected_models = {}
                for name in names:
                    alias = model_name(discovered["project_name"], name)
                    selected_models[name] = alias if alias in choices else name
                # Refresh only this node schema so edit/validation accepts freshly installed LoRAs.
                schemas = dict(item[6])
                schemas[node["class_type"]] = fresh_schema
                fields = [dict(f, choices=available) if f["node"]==node_id and f["name"]=="lora_name" else f for f in item[5]]
                missing = [name for name in names if selected_models[name] not in choices]
                if missing:
                    return jsonify(error="Checkpoints not installed in ComfyUI/models/loras",
                                   detail="ComfyUI does not recognize: "+", ".join(model_name(discovered["project_name"], name) for name in missing)[:300]+". Refresh its models or restart ComfyUI."),409
                if len(prepared)+len(names)>20:
                    for key in list(prepared):
                        if key != token and len(prepared)+len(names)>20:
                            prepared.pop(key)
                if len(prepared)+len(names)>20:
                    return jsonify(error="Too many pending comparison variants"),409
                variants=[]
                for name in names:
                    graph=apply_edits(item[4],fields,[{"node":node_id,"name":"lora_name","value":selected_models[name]}])
                    validate_prompt(graph,schemas)
                    key=uuid.uuid4().hex
                    prepared[key]=(time.monotonic(),*item[1:4],graph,editable_fields(graph,schemas),schemas)
                    step=next(x["step"] for x in discovered["checkpoints"] if x["name"]==name)
                    variants.append({"step":step,"name":name,"comfy_name":selected_models[name],"token":key})
            return jsonify(workflow_id=item[1], variants=variants)
        except LookupError as exc:
            return jsonify(error=str(exc)),404
        except (OSError,ValueError,TypeError,KeyError,RecursionError) as exc:
            return jsonify(error="Checkpoint comparison preparation failed",detail=str(exc)[:300]),400

    @app.get("/api/workspace/generation/capabilities")
    def generation_capabilities():
        """Report capabilities of the *running* launcher, not checkout files.

        An old launcher process will not expose this route, even after git
        pull. A read-only probe: no ComfyUI calls, history writes or GPU work.
        """
        if not local():
            return jsonify(error="Inspect generation capabilities on the launcher PC"), 403
        return jsonify(
            generation_studio="benchmark-submission-v1",
            benchmark_submit=True,
            benchmark_terminal_finalization=True,
            benchmark_field="benchmark",
            experimental_gpu_monitor=True,
            gpu_monitor_field="gpu_monitor",
            requires_confirmation=True,
        )

    @app.post("/api/workspace/generation/benchmark/prepare-one")
    def benchmark_prepare_one():
        """Prepare exactly one declared variant; never POST to ComfyUI.

        The subsequent /api/workspace/generation submit requires its own
        explicit confirmation and exact benchmark binding.
        """
        if not local():
            return jsonify(error="Benchmark preparation is launcher-local only"), 403
        if request.mimetype != "application/json" or not 0 < (request.content_length or 0) <= 2048:
            return jsonify(error="Invalid benchmark preparation request"), 400
        body = request.get_json(silent=True)
        if not isinstance(body, dict) or set(body) != {
            "project_id", "run_id", "variant_id", "repetition"
        }:
            return jsonify(error="Explicit variant and repetition required"), 400
        project_id, run_id, variant_id = (body.get(k) for k in ("project_id", "run_id", "variant_id"))
        repetition = body.get("repetition")
        if (any(not isinstance(k, str) or not re.fullmatch(r"[A-Za-z0-9_-]{1,200}", k)
                for k in (project_id, run_id, variant_id))
                or type(repetition) is not int or not 0 <= repetition <= 99):
            return jsonify(error="Invalid benchmark identifiers or repetition"), 400
        cfg = config()
        if cfg["mode"] == "native":
            return jsonify(error="ComfyUI is disabled"), 409
        if project_layout.training_in_progress(base):
            return jsonify(error="Training is active"), 409
        try:
            from benchmark_repro_protocol import declared_protocol_readiness
            from benchmark_b10_model_check import inspect_model_variants
            from benchmark_job_binding import preflight_submission_binding
            from benchmark_store import BenchmarkStore
            from workspace_store import ProjectStore
            projects_db = base / "settings" / "orkilab" / "projects.sqlite3"
            bench_db = base / "settings" / "orkilab" / "benchmarks.sqlite3"
            wf_db = base / "settings" / "orkilab" / "workflows.sqlite3"
            if any(not p.is_file() for p in (projects_db, bench_db, wf_db)):
                return jsonify(error="Required project, run or workflow unavailable"), 404
            with closing(sqlite3.connect(projects_db.resolve().as_uri() + "?mode=ro",uri=True)) as con:
                row = con.execute("SELECT id FROM projects WHERE id=? AND archived=0", (project_id,)).fetchone()
            if row is None:
                return jsonify(error="Active project unavailable"), 404
            with BenchmarkStore(bench_db) as bench:
                preflight_submission_binding(bench, project_id=project_id, run_id=run_id,
                                             variant_id=variant_id, repetition=repetition)
                run = bench.db.execute("SELECT protocol_json FROM benchmark_runs WHERE id=?",
                                       (run_id,)).fetchone()
                variants = bench.db.execute("SELECT id,run_id,config_json FROM benchmark_variants "
                                            "WHERE run_id=? ORDER BY id LIMIT 21", (run_id,)).fetchall()
            protocol = json.loads(run["protocol_json"])
            report = {"run":{"id":run_id,"protocol":protocol},
                      "variants":[dict(v) for v in variants]}
            if declared_protocol_readiness(report)["status"] != "declared_unverified":
                return jsonify(error="Complete reproducibility protocol required"), 409
            if repetition >= protocol["repetitions"]:
                return jsonify(error="Repetition is outside declared bounds"), 409
            workflow_id = protocol["workflow_id"]
            with closing(sqlite3.connect(wf_db.resolve().as_uri()+"?mode=ro",uri=True)) as con:
                wf = con.execute("SELECT graph FROM workflows WHERE id=?", (workflow_id,)).fetchone()
            if wf is None or len(wf[0]) > 2_000_000:
                return jsonify(error="Saved workflow unavailable"), 404
            graph = json.loads(wf[0])
            variable = protocol["vary"]
            kinds = ("CheckpointLoaderSimple",) if variable == "checkpoint" else ("LoraLoader","LoraLoaderModelOnly")
            field = "ckpt_name" if variable == "checkpoint" else "lora_name"
            # First check without any ComfyUI request, and fail closed.
            preliminary=inspect_model_variants(graph,protocol,[dict(v) for v in variants],{})
            if preliminary["reason_codes"] != ["node_options_unavailable"]:
                return jsonify(error="Workflow not supported for guided comparison",
                               reason_codes=preliminary["reason_codes"]), 409
            nodes=[(nid,n) for nid,n in graph.items() if n["class_type"] in kinds]
            target_id,node=nodes[0]
            schemas={kind:node_schema(cfg["url"],kind,get_json)
                     for kind in {n["class_type"] for n in graph.values()}}
            model_check=inspect_model_variants(graph,protocol,[dict(v) for v in variants],
                                               schemas[node["class_type"]])
            if model_check["status"] != "static_candidate":
                return jsonify(error="Candidate models are not advertised by ComfyUI",
                               reason_codes=model_check["reason_codes"]), 409
            selected=next((v for v in variants if v["id"]==variant_id),None)
            if selected is None:
                return jsonify(error="Variant not found"), 404
            choice=json.loads(selected["config_json"])["controlled_value"]
            proposal=json.loads(json.dumps(graph,ensure_ascii=False))
            proposal[target_id]["inputs"][field]=choice
            validate_prompt(proposal,schemas)
            # Single variant, single-use prepared token, no disk writes.
            token=uuid.uuid4().hex
            source_hash=hashlib.sha256(wf[0].encode("utf-8")).hexdigest()
            target=(project_id,run_id,variant_id,repetition)
            with lock:
                for key in list(guided_targets):
                    if key not in prepared:
                        guided_targets.pop(key,None)
                while len(prepared)>=20:
                    victim=next(iter(prepared))
                    prepared.pop(victim,None)
                    guided_targets.pop(victim,None)
                prepared[token]=(time.monotonic(),workflow_id,cfg["url"],source_hash,
                                 proposal,editable_fields(proposal,schemas),schemas)
                guided_targets[token]=target
            return jsonify(token=token,workflow_id=workflow_id,
                           project_id=project_id,run_id=run_id,variant_id=variant_id,
                           repetition=repetition,model_choice_advertised=True,
                           graph_validated_against_live_node_schemas=True,
                           execution_submitted=False,submission_requires_confirmation=True)
        except (sqlite3.Error,OSError,ValueError,TypeError,KeyError,RecursionError) as exc:
            return jsonify(error="Guided variant preparation failed",detail=str(exc)[:240]),409

    @app.post("/api/workspace/generation")
    def generation_submit():
        if not local():
            return jsonify(error="Manage workflows on the launcher PC"), 403
        if request.mimetype != "application/json" or not 0 < (request.content_length or 0) <= 2048:
            return jsonify(error="Invalid request"), 400
        body = request.get_json(silent=True)
        if not isinstance(body, dict) or body.get("confirm") is not True or not isinstance(body.get("workflow_id"), str):
            return jsonify(error="Explicit generation confirmation required"), 400
        from benchmark_gpu_monitor_contract import validate_gpu_monitor_option
        try:
            monitor_option = validate_gpu_monitor_option(body.get("gpu_monitor"))
        except ValueError as exc:
            return jsonify(error=str(exc)), 400
        cfg = config()
        if cfg["mode"] == "native":
            return jsonify(error="ComfyUI is disabled in native mode"), 409
        if monitor_option and cfg["url"] != "http://127.0.0.1:8188":
            return jsonify(error="Experimental GPU monitoring needs local ComfyUI on 127.0.0.1:8188"), 409
        raw = read_graph(body["workflow_id"])
        if raw is None:
            return jsonify(error="Workflow not found"), 404
        token = body.get("token")
        if not isinstance(token, str):
            return jsonify(error="Prepare workflow before generating"), 409
        # Optional benchmark linkage is validated *before* ComfyUI submission.
        # Normal generation requests (without benchmark) retain their old path.
        benchmark_target = body.get("benchmark")
        if benchmark_target is not None:
            if (not isinstance(benchmark_target, dict)
                    or set(benchmark_target) != {"project_id", "run_id", "variant_id", "repetition", "confirm"}
                    or benchmark_target.get("confirm") is not True):
                return jsonify(error="Explicit, complete benchmark linkage required"), 400
            try:
                from workspace_store import ProjectStore
                from benchmark_store import BenchmarkStore
                from benchmark_job_binding import preflight_submission_binding
                project_id = benchmark_target.get("project_id")
                if not isinstance(project_id, str) or not any(
                    p["id"] == project_id for p in ProjectStore(
                        base / "settings" / "orkilab" / "projects.sqlite3"
                    ).list()
                ):
                    return jsonify(error="Active project not found"), 404
                with BenchmarkStore(base / "settings" / "orkilab" / "benchmarks.sqlite3") as bench:
                    preflight_submission_binding(
                        bench, project_id=project_id, run_id=benchmark_target["run_id"],
                        variant_id=benchmark_target["variant_id"],
                        repetition=benchmark_target["repetition"],
                    )
            except PermissionError:
                return jsonify(error="Benchmark project authorization mismatch"), 403
            except (ValueError, TypeError, sqlite3.Error, OSError) as exc:
                return jsonify(error="Invalid benchmark target", detail=str(exc)[:200]), 409
        guided=guided_targets.get(token)
        if guided is not None:
            if benchmark_target is None or (
                benchmark_target.get("project_id"),benchmark_target.get("run_id"),
                benchmark_target.get("variant_id"),benchmark_target.get("repetition")
            ) != guided:
                return jsonify(error="Guided variant token is bound to another benchmark target"),409
        try:
            with lock:
                item = prepared.get(token)
                if not item or time.monotonic() - item[0] > 1800 or item[1:4] != (body["workflow_id"], cfg["url"], hashlib.sha256(raw.encode()).hexdigest()):
                    return jsonify(error="Prepare workflow before generating"), 409
                graph = item[4]
                if project_layout.training_in_progress(base):
                    return jsonify(error="Training is active. Finish training before generating."), 409
                queue = get_json(cfg["url"], "/queue")
                if not isinstance(queue, dict) or not all(isinstance(queue.get(k), list) for k in ("queue_running", "queue_pending")):
                    return jsonify(error="Could not verify ComfyUI queue"), 502
                if queue["queue_running"] or queue["queue_pending"]:
                    return jsonify(error="ComfyUI queue is busy"), 409
                prepared.pop(token, None)
                guided_targets.pop(token, None)
                ident, client_id = submit(cfg["url"], graph)
                token = uuid.uuid4().hex
                jobs[token] = (cfg["url"], ident)
                history_saved = False
                try:
                    with closing(sqlite3.connect(base / "settings" / "orkilab" / "workflows.sqlite3")) as con:
                        row = con.execute("SELECT name FROM workflows WHERE id=?", (body["workflow_id"],)).fetchone()
                    records.add(token, cfg["url"], ident, body["workflow_id"], row[0] if row else body["workflow_id"], graph)
                    history_saved = True
                except (OSError, sqlite3.Error, ValueError) as exc:
                    app.logger.warning("Generation submitted but history unavailable: %s", exc)
                benchmark_link = None
                if benchmark_target is not None:
                    benchmark_link = "history_unavailable"
                    if history_saved:
                        try:
                            from benchmark_store import BenchmarkStore
                            from benchmark_job_binding import bind_submitted_generation
                            with BenchmarkStore(base / "settings" / "orkilab" / "benchmarks.sqlite3") as bench:
                                bind_submitted_generation(
                                    bench, project_id=benchmark_target["project_id"],
                                    run_id=benchmark_target["run_id"],
                                    variant_id=benchmark_target["variant_id"],
                                    repetition=benchmark_target["repetition"],
                                    generation_id=token, workflow_id=body["workflow_id"],
                                )
                            benchmark_link = "bound"
                        except (OSError, ValueError, PermissionError, sqlite3.Error) as exc:
                            benchmark_link = "binding_failed"
                            app.logger.warning("Generation submitted but benchmark not bound: %s", exc)
                while len(jobs) > 100:
                    jobs.pop(next(iter(jobs)))
            result = dict(id=token, prompt_id=ident, client_id=client_id)
            if monitor_option is not None:
                # An explicit request cannot change success of an already
                # submitted generation if optional monitoring cannot start.
                if history_saved:
                    from benchmark_gpu_monitor_contract import monitoring_receipt
                    with lock:
                        gpu_monitors[token] = monitoring_receipt("scheduled")
                        while len(gpu_monitors) > 100:
                            gpu_monitors.pop(next(iter(gpu_monitors)))
                    try:
                        threading.Thread(
                            target=run_gpu_monitor, args=(token, monitor_option),
                            daemon=True, name="orkilab-gpu-monitor"
                        ).start()
                        result["gpu_monitor"] = "scheduled"
                    except RuntimeError:
                        with lock:
                            gpu_monitors[token] = monitoring_receipt("failed")
                        result["gpu_monitor"] = "failed_to_start"
                else:
                    result["gpu_monitor"] = "history_unavailable"
            if benchmark_target is not None:
                result["benchmark_binding"] = benchmark_link
                if benchmark_link != "bound":
                    result["warning"] = "Generation was submitted but benchmark binding was not saved; do not assume it will appear in Benchmark."
            return jsonify(result), 201
        except HTTPError as exc:
            return jsonify(error="ComfyUI rejected the request", detail=f"HTTP {exc.code}"), 502
        except (OSError, ValueError, TypeError) as exc:
            return jsonify(error="Generation submission could not be confirmed. Check ComfyUI before retrying.", detail=str(exc)[:300]), 502

    @app.get("/api/workspace/generation/gpu-monitor/devices")
    def generation_gpu_monitor_devices():
        """Read-only NVIDIA UUID inventory for explicitly optional UI control."""
        if not local():
            return jsonify(error="View GPU devices on the launcher PC"), 403
        from benchmark_gpu_memory_probe import sample_devices
        report = sample_devices()
        if report.get("ok") is not True:
            return jsonify(error="NVIDIA memory inventory unavailable"), 503
        return jsonify(devices=[{
            "uuid": d["uuid"], "name": d["name"], "index": d["index"],
        } for d in report["devices"]], scope="device_global_only")

    @app.get("/api/workspace/generation/<generation_id>/gpu-monitor")
    def generation_gpu_monitor_status(generation_id):
        """Read ephemeral opt-in device-global diagnostics. No DB writes."""
        if not local():
            return jsonify(error="View GPU monitoring on the launcher PC"), 403
        if not isinstance(generation_id, str) or len(generation_id) > 200:
            return jsonify(error="Invalid generation ID"), 400
        with lock:
            report = gpu_monitors.get(generation_id)
        if report is None:
            return jsonify(error="No opted-in GPU monitoring for this generation"), 404
        return jsonify(report)

    @app.post("/api/workspace/comfyui/memory/release")
    def release_comfyui_memory():
        """Explicit cache/model unload; refuse when shared ComfyUI is busy."""
        if not local():
            return jsonify(error="Manage ComfyUI on the launcher PC"), 403
        if request.mimetype != "application/json" or not 0 < (request.content_length or 0) <= 128:
            return jsonify(error="Invalid request"), 400
        body = request.get_json(silent=True)
        if not isinstance(body, dict) or body.get("confirm") is not True:
            return jsonify(error="Explicit memory release confirmation required"), 400
        cfg = config()
        if cfg["mode"] == "native":
            return jsonify(error="ComfyUI is disabled in native mode"), 409
        try:
            with lock:
                if project_layout.training_in_progress(base):
                    return jsonify(error="Training is active. Finish training before releasing memory."), 409
                queue = get_json(cfg["url"], "/queue")
                if not isinstance(queue, dict) or not all(
                        isinstance(queue.get(key), list) for key in ("queue_running", "queue_pending")):
                    return jsonify(error="Could not verify ComfyUI queue"), 502
                if queue["queue_running"] or queue["queue_pending"]:
                    return jsonify(error="ComfyUI has queued or running jobs. Memory release refused."), 409
                # Fixed URL/path and payload; never kill Python processes or clear the shared queue.
                req = Request(cfg["url"] + "/free",
                              data=b'{"unload_models":true,"free_memory":true}',
                              headers={"Content-Type": "application/json"}, method="POST")
                with build_opener(ProxyHandler({}), NoRedirect()).open(req, timeout=10) as response:
                    if response.status != 200:
                        raise ValueError("ComfyUI did not accept memory release")
                    response.read(1024)
            return jsonify(accepted=True, detail="ComfyUI accepted model unload and cache release; actual RAM/VRAM reclamation may be delayed or partial")
        except HTTPError as exc:
            return jsonify(error="ComfyUI rejected memory release", detail=f"HTTP {exc.code}"), 502
        except (OSError, ValueError, TypeError) as exc:
            return jsonify(error="Could not request memory release", detail=str(exc)[:300]), 502

    def finalize_benchmark(token, *, execution_entry=None):
        """Best-effort, local-only persistence; never changes generation outcome."""
        try:
            db_path = base / "settings" / "orkilab" / "benchmarks.sqlite3"
            if not db_path.is_file():
                return "unbound"
            from benchmark_store import BenchmarkStore
            from benchmark_job_binding import finalize_bound_history_generation
            with BenchmarkStore(db_path) as bench:
                return finalize_bound_history_generation(bench, records, token, execution_entry=execution_entry)
        except (OSError, ValueError, TypeError, PermissionError, sqlite3.Error, KeyError) as exc:
            app.logger.warning("Benchmark finalization deferred for %s: %s", token, exc)
            return "deferred"

    @app.post("/api/workspace/generation/<token>/cancel")
    def generation_cancel(token):
        """Cancel this job only, never clear the entire shared ComfyUI queue."""
        if not local():
            return jsonify(error="Manage workflows on the launcher PC"), 403
        if request.mimetype != "application/json" or (request.content_length or 0) > 128:
            return jsonify(error="Invalid request"), 400
        with lock:
            job = jobs.get(token)
        saved = records.get(token)
        if saved and saved["state"] in ("completed", "error", "cancelled"):
            return jsonify(error="Generation already finished"), 409
        if not job and saved:
            job = (saved["url"], saved["prompt_id"])
        if not job:
            return jsonify(error="Generation job not found"), 404
        url, ident = job
        try:
            url = validate_settings({"url": url}, DEFAULT_SETTINGS)["url"]
            queue = get_json(url, "/queue")
            if not isinstance(queue, dict):
                raise ValueError("Invalid ComfyUI queue")
            running = [x for x in queue.get("queue_running", [])
                       if isinstance(x, list) and len(x) > 1]
            pending = [x for x in queue.get("queue_pending", [])
                       if isinstance(x, list) and len(x) > 1]
            if any(x[1] == ident for x in pending):
                path, data, state = "/queue", {"delete": [ident]}, "cancelled"
            elif any(x[1] == ident for x in running):
                # Older servers ignore prompt_id and may interrupt globally.
                # Refuse if another job could be affected.
                if len(running) != 1 or pending:
                    return jsonify(error="Cannot safely interrupt while other ComfyUI jobs are present"), 409
                path, data, state = "/interrupt", {"prompt_id": ident}, "cancelling"
            else:
                return jsonify(error="Job no longer in ComfyUI queue; refresh status"), 409
            req = Request(url + path, data=json.dumps(data).encode("utf-8"),
                          headers={"Content-Type": "application/json"}, method="POST")
            with build_opener(ProxyHandler({}), NoRedirect()).open(req, timeout=10) as response:
                if response.status != 200:
                    raise ValueError("Cancellation not accepted by ComfyUI")
                response.read(1024)
            records.update(token, state, [])
            if state == "cancelled":
                finalize_benchmark(token)
            return jsonify(state=state, cancelled=state == "cancelled")
        except (OSError, ValueError, TypeError) as exc:
            return jsonify(error="Could not cancel generation safely", detail=str(exc)[:300]), 502

    @app.get("/api/workspace/generation/<token>")
    def generation_status(token):
        if not local():
            return jsonify(error="Manage workflows on the launcher PC"), 403
        with lock:
            job = jobs.get(token)
        saved = records.get(token)
        if saved and saved["state"] in ("completed","error","cancelled"):
            finalize_benchmark(token)
            return jsonify(state=saved["state"], outputs=json.loads(saved["outputs"]))
        if not job and saved:
            job = (saved["url"], saved["prompt_id"])
        if not job:
            return jsonify(error="Generation job not found"), 404
        url, ident = job
        url = validate_settings({"url":url}, DEFAULT_SETTINGS)["url"]
        try:
            history = get_json(url, "/history/" + ident, max_bytes=16_000_000)
            entry = history.get(ident) if isinstance(history, dict) else None
            if not isinstance(entry, dict):
                queue = get_json(url, "/queue")
                if not isinstance(queue, dict):
                    raise ValueError("Invalid queue")
                for key, state in (("queue_running", "running"), ("queue_pending", "queued")):
                    if any(isinstance(item, list) and len(item) > 1 and item[1] == ident for item in queue.get(key, [])):
                        if saved and saved["state"] == "cancelling":
                            return jsonify(state="cancelling", outputs=[])
                        records.update(token,state,[])
                        return jsonify(state=state, outputs=[])
                if saved and saved["state"] == "cancelling":
                    records.update(token,"cancelled",[])
                    finalize_benchmark(token)
                    return jsonify(state="cancelled", outputs=[])
                return jsonify(state="unknown", outputs=[])
            status = entry.get("status") or {}
            state = "error" if status.get("status_str") == "error" else "completed" if status.get("completed") else "unknown"
            if saved and saved["state"] == "cancelling" and state == "error":
                state = "cancelled"
            outputs = describe_outputs(entry)
            records.update(token,state,outputs)
            if state in ("completed", "error", "cancelled"):
                # Use ComfyUI's historical per-prompt events when present.
                # Never use local request/poll timing as execution duration.
                finalize_benchmark(token, execution_entry=entry)
            return jsonify(state=state, outputs=outputs)
        except (OSError, ValueError, TypeError) as exc:
            return jsonify(error="Could not read generation status", detail=str(exc)[:300]), 502

    @app.get("/api/workspace/generation/history")
    def generation_history():
        if not local():
            return jsonify(error="Manage workflows on the launcher PC"), 403
        try:
            offset = max(0,min(100000,int(request.args.get("offset",0))))
            query = request.args.get("q","")
            state = request.args.get("state","")
            sort = request.args.get("sort","newest")
            return jsonify(records.search(100,offset,query,state,sort))
        except (ValueError,TypeError):
            return jsonify(error="Invalid history filter"),400

    @app.get("/api/workspace/generation/history/<token>")
    def generation_history_detail(token):
        if not local():
            return jsonify(error="Manage workflows on the launcher PC"),403
        row = records.get(token)
        if not row:
            return jsonify(error="Generation job not found"),404
        return jsonify(id=token, name=row["name"], graph=json.loads(row["graph"]), workflow_id=row["workflow_id"])

    @app.get("/api/workspace/generation/media/<token>/<int:index>")
    def generation_media(token,index):
        if not local():
            abort(403)
        row = records.get(token)
        if not row:
            abort(404)
        outputs = json.loads(row["outputs"])
        if not 0 <= index < len(outputs):
            abort(404)
        item = outputs[index]
        try:
            url = validate_settings({"url":row["url"]},DEFAULT_SETTINGS)["url"]
            query = urlencode({key:item[key] for key in ("filename","subfolder","type")})
            headers = {}
            byte_range = request.headers.get("Range","")
            if re.fullmatch(r"bytes=\d*-\d*",byte_range):
                headers["Range"] = byte_range
            upstream = build_opener(ProxyHandler({}),NoRedirect()).open(Request(url+"/view?"+query,headers=headers),timeout=15)
        except (OSError,ValueError):
            abort(404)
        def chunks():
            with upstream:
                while True:
                    chunk = upstream.read(65536)
                    if not chunk:
                        break
                    yield chunk
        response = Response(stream_with_context(chunks()),status=upstream.status,mimetype=item["mime"])
        response.call_on_close(upstream.close)
        for key in ("Content-Length","Content-Range","Accept-Ranges"):
            if upstream.headers.get(key):
                response.headers[key] = upstream.headers[key]
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Cache-Control"] = "no-store"
        response.headers["Content-Security-Policy"] = "default-src 'none'; sandbox"
        if request.args.get("download") == "1" or item["mime"] == "application/octet-stream":
            from werkzeug.http import dump_options_header
            response.headers["Content-Disposition"] = dump_options_header("attachment",{"filename":item["filename"]})
        return response
