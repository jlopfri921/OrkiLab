"""B9.2 read-only project-scoped Benchmark Studio reporting HTTP views.

All queries use a SQLite read-only connection. These routes never initialize
BenchmarkStore (which could create/alter tables), submit jobs or change runs.
Local launcher access only and explicit project/run binding for detail.
"""
from __future__ import annotations

import json
import re
import sqlite3
from contextlib import closing
from pathlib import Path

from flask import jsonify, request
from benchmark_report_summary import summarize_benchmark_report
from benchmark_comparability import assess_duration_comparability
from benchmark_repro_protocol import declared_protocol_readiness
from benchmark_execution_evidence import verify_recorded_execution_evidence
from benchmark_history_consistency import summarize_saved_history_matches
from benchmark_b9_closure import summarize_b9_closure
from benchmark_b10_preflight import inspect_comparison_plan
from benchmark_b10_model_check import inspect_model_variants
from benchmark_b10_results import describe_cross_variant_measurements
from benchmark_b10_release_gate import summarize_b10_release_readiness
from benchmark_draft_creation import create_confirmed_draft, validate_draft_payload

ID = re.compile(r"^[A-Za-z0-9_-]{1,200}$")


def report_routes(app, base):
    db = Path(base) / "settings" / "orkilab" / "benchmarks.sqlite3"

    def local():
        return request.remote_addr in ("127.0.0.1", "::1")

    def open_ro():
        if not db.is_file():
            return None
        conn = sqlite3.connect(db.resolve().as_uri() + "?mode=ro", uri=True, timeout=5)
        conn.row_factory = sqlite3.Row
        return conn

    @app.get("/api/workspace/benchmark/draft-options")
    def benchmark_draft_options():
        """Read-only list of real imported workflow IDs and NVIDIA UUIDs.

        Neither workflows nor GPUs are inferred. Absence of a DB or NVIDIA
        driver returns empty choices with explicit availability flags.
        """
        if not local():
            return jsonify(error="Benchmark options available on launcher PC only"), 403
        project_id = request.args.get("project_id", "")
        if not ID.fullmatch(project_id):
            return jsonify(error="Explicit project ID required"), 400
        project_db = Path(base) / "settings" / "orkilab" / "projects.sqlite3"
        if not project_db.is_file():
            return jsonify(error="Project not found"), 404
        try:
            with closing(sqlite3.connect(project_db.resolve().as_uri() + "?mode=ro", uri=True)) as conn:
                project = conn.execute(
                    "SELECT id FROM projects WHERE id=? AND archived=0",
                    (project_id,),
                ).fetchone()
            if project is None:
                return jsonify(error="Active project not found"), 404
            rows = []
            wf_db = Path(base) / "settings" / "orkilab" / "workflows.sqlite3"
            if wf_db.is_file():
                with closing(sqlite3.connect(wf_db.resolve().as_uri() + "?mode=ro", uri=True)) as conn:
                    rows = conn.execute(
                        "SELECT id,name,category FROM workflows "
                        "ORDER BY name COLLATE NOCASE,id LIMIT 200"
                    ).fetchall()
            from benchmark_gpu_memory_probe import sample_devices
            sampled = sample_devices()
            devices = ([{"uuid": dev["uuid"], "name": dev["name"],
                         "index": dev["index"]}
                        for dev in sampled.get("devices", [])]
                       if sampled.get("ok") is True else [])
            return jsonify(
                project_id=project_id,
                workflows=[{"id": row[0], "name": row[1], "category": row[2]}
                           for row in rows],
                devices=devices,
                gpu_inventory_available=sampled.get("ok") is True,
                read_only=True,
                metadata_only=True,
                auto_verified=False,
                execution_submitted=False,
            )
        except (sqlite3.Error, OSError, TypeError, ValueError):
            return jsonify(error="Benchmark options unavailable"), 503

    @app.get("/api/workspace/benchmark/model-check")
    def benchmark_model_check():
        """User-invoked, bounded read-only ComfyUI node-option inspection.

        Only named fixed loader types and exact run/project IDs are considered.
        No graph contents, complete inventory or private connection URL returned.
        """
        if not local():
            return jsonify(error="Model check available on launcher PC only"), 403
        project_id = request.args.get("project_id", "")
        run_id = request.args.get("run_id", "")
        if not ID.fullmatch(project_id) or not ID.fullmatch(run_id):
            return jsonify(error="Explicit project/run IDs required"), 400
        try:
            con = open_ro()
            if con is None:
                return jsonify(error="Benchmark run unavailable"), 404
            with closing(con):
                row = con.execute(
                    "SELECT project_id,protocol_json FROM benchmark_runs "
                    "WHERE id=? AND project_id=?", (run_id, project_id)
                ).fetchone()
                if row is None:
                    return jsonify(error="Benchmark run not found in project"), 404
                variants = con.execute(
                    "SELECT id,config_json FROM benchmark_variants WHERE run_id=? "
                    "ORDER BY label,id LIMIT 21", (run_id,)
                ).fetchall()
            protocol = json.loads(row["protocol_json"])
            if not isinstance(protocol, dict) or protocol.get("schema") != "orkilab-repro-v1":
                return jsonify(error="Versioned comparison protocol required"), 409
            # The model selector is only inspected for a complete versioned
            # declaration. A partial protocol must not look like a valid
            # candidate even if ComfyUI advertises a similarly named model.
            declaration = declared_protocol_readiness({
                "run": {"id": run_id, "protocol": protocol},
                "variants": [
                    {"id": v["id"], "run_id": run_id,
                     "config_json": v["config_json"]}
                    for v in variants
                ],
            })
            if declaration["status"] != "declared_unverified":
                return jsonify(error="Complete comparison declaration required",
                               reason_codes=declaration["reason_codes"],
                               comparison_execution_authorized=False,
                               generation_submitted=False), 409
            workflow_id = protocol.get("workflow_id")
            if not isinstance(workflow_id, str) or not ID.fullmatch(workflow_id):
                return jsonify(error="Saved workflow reference required"), 409
            wf_db = Path(base) / "settings" / "orkilab" / "workflows.sqlite3"
            if not wf_db.is_file():
                return jsonify(error="Saved workflow unavailable"), 404
            with closing(sqlite3.connect(wf_db.resolve().as_uri() + "?mode=ro", uri=True, timeout=5)) as con:
                stored = con.execute("SELECT graph FROM workflows WHERE id=?", (workflow_id,)).fetchone()
            if stored is None or not isinstance(stored[0], str) or len(stored[0]) > 2_000_000:
                return jsonify(error="Saved workflow unavailable"), 404
            graph = json.loads(stored[0])
            variable = protocol.get("vary")
            kinds = ("CheckpointLoaderSimple",) if variable == "checkpoint" else (
                "LoraLoader", "LoraLoaderModelOnly") if variable == "lora" else ()
            # Fail closed for UI/custom or multi-loader graphs BEFORE network access.
            preliminary = inspect_model_variants(graph, protocol, [dict(v) for v in variants], {})
            if preliminary["reason_codes"] != ["node_options_unavailable"] or not kinds:
                return jsonify(preliminary)
            targets = [n for n in graph.values() if n.get("class_type") in kinds]
            kind = targets[0]["class_type"]
            config_path = Path(base) / "settings" / "orkilab" / "comfyui.json"
            from comfyui_connect import DEFAULT_SETTINGS, validate_settings, get_json
            if not config_path.is_file():
                return jsonify(error="ComfyUI connection not configured"), 409
            cfg = validate_settings(json.loads(config_path.read_text(encoding="utf-8")), DEFAULT_SETTINGS)
            if cfg["mode"] == "native":
                return jsonify(error="ComfyUI disabled in native mode"), 409
            from urllib.parse import quote
            info = get_json(cfg["url"], "/object_info/" + quote(kind, safe=""),
                            max_bytes=500_000, timeout=5)
            schema = info.get(kind) if isinstance(info, dict) else None
            return jsonify(inspect_model_variants(
                graph, protocol, [dict(v) for v in variants], schema))
        except (sqlite3.Error, OSError, ValueError, TypeError, KeyError, OverflowError):
            return jsonify(error="Could not verify saved workflow model choices"), 503

    @app.post("/api/workspace/benchmark/start")
    def benchmark_start_declared_run():
        """Explicitly activate a complete draft; never submit ComfyUI work."""
        if not local():
            return jsonify(error="Benchmark activation is launcher-local only"),403
        if request.mimetype!="application/json" or not 0<(request.content_length or 0)<=1024:
            return jsonify(error="Invalid activation request"),400
        payload=request.get_json(silent=True)
        if (not isinstance(payload,dict) or set(payload)!={"project_id","run_id","confirm"}
                or payload.get("confirm") is not True
                or any(not isinstance(payload.get(k),str) or not ID.fullmatch(payload[k])
                       for k in ("project_id","run_id"))):
            return jsonify(error="Explicit project/run activation confirmation required"),400
        try:
            projects_db=Path(base)/"settings"/"orkilab"/"projects.sqlite3"
            if not db.is_file() or not projects_db.is_file():
                return jsonify(error="Benchmark or project unavailable"),404
            with closing(sqlite3.connect(projects_db.resolve().as_uri()+"?mode=ro",uri=True)) as con:
                active=con.execute("SELECT 1 FROM projects WHERE id=? AND archived=0",
                                   (payload["project_id"],)).fetchone()
            if active is None:
                return jsonify(error="Active project not found"),404
            from benchmark_store import BenchmarkStore
            with BenchmarkStore(db) as store:
                row=store.db.execute(
                    "SELECT id,project_id,state,protocol_json FROM benchmark_runs "
                    "WHERE id=? AND project_id=?",
                    (payload["run_id"],payload["project_id"])).fetchone()
                if row is None:
                    return jsonify(error="Run not found in project"),404
                if row["state"]!="draft":
                    return jsonify(error="Only a draft can be activated"),409
                variants=store.db.execute(
                    "SELECT id,run_id,config_json FROM benchmark_variants WHERE run_id=?",
                    (payload["run_id"],)).fetchall()
                report={"run":{"id":row["id"],"protocol_json":row["protocol_json"]},
                        "variants":[dict(v) for v in variants]}
                if declared_protocol_readiness(report)["status"]!="declared_unverified":
                    return jsonify(error="Complete declared protocol required"),409
                store.transition(payload["run_id"],"running")
            return jsonify(id=payload["run_id"],state="running",
                           generation_submitted=False,execution_verified=False),200
        except (sqlite3.Error,OSError,ValueError,TypeError):
            return jsonify(error="Could not activate benchmark draft"),409

    @app.post("/api/workspace/benchmark/drafts")
    def create_benchmark_draft():
        """Explicitly create an inactive benchmark plan; never run ComfyUI."""
        if not local():
            return jsonify(error="Create drafts on the launcher PC only"), 403
        if request.mimetype != "application/json" or not 0 < (request.content_length or 0) <= 8192:
            return jsonify(error="Invalid draft request"), 400
        payload = request.get_json(silent=True)
        try:
            validated = validate_draft_payload(payload)
            # Reject absent or archived projects; no ProjectStore side-effect
            # when the local projects database is missing.
            project_db = Path(base) / "settings" / "orkilab" / "projects.sqlite3"
            if not project_db.is_file():
                return jsonify(error="Project not found"), 404
            with closing(sqlite3.connect(project_db.resolve().as_uri() + "?mode=ro", uri=True)) as projects:
                project = projects.execute(
                    "SELECT id FROM projects WHERE id=? AND archived=0",
                    (validated["project_id"],)
                ).fetchone()
            if project is None:
                return jsonify(error="Active project not found"), 404
            run_id = create_confirmed_draft(
                base, payload, authorized_project_id=validated["project_id"]
            )
            return jsonify(id=run_id, project_id=validated["project_id"],
                           state="draft", generation_submitted=False,
                           execution_verified=False), 201
        except PermissionError:
            return jsonify(error="Project authorization failed"), 403
        except (ValueError, TypeError, sqlite3.Error, OSError):
            return jsonify(error="Invalid benchmark draft declaration"), 400

    @app.get("/api/workspace/benchmark/reports")
    def benchmark_reports_index():
        if not local():
            return jsonify(error="Reports available on the launcher PC only"), 403
        project_id = request.args.get("project_id", "")
        if not ID.fullmatch(project_id):
            return jsonify(error="Explicit project ID required"), 400
        try:
            con = open_ro()
            if con is None:
                return jsonify(project_id=project_id, runs=[], database_available=False)
            with closing(con):
                rows = con.execute(
                    "SELECT r.id,r.project_id,r.name,r.state,r.created_at,r.updated_at,"
                    "(SELECT COUNT(*) FROM benchmark_variants v WHERE v.run_id=r.id) AS variant_count,"
                    "(SELECT COUNT(*) FROM benchmark_observations o WHERE o.run_id=r.id) AS observation_count "
                    "FROM benchmark_runs r WHERE r.project_id=? "
                    "ORDER BY r.created_at DESC,r.id DESC LIMIT 100",
                    (project_id,),
                ).fetchall()
            return jsonify(project_id=project_id, runs=[dict(x) for x in rows],
                           database_available=True, read_only=True)
        except sqlite3.Error:
            return jsonify(error="Benchmark reports unavailable"), 503

    @app.get("/api/workspace/benchmark/reports/<run_id>")
    def benchmark_report_detail(run_id):
        if not local():
            return jsonify(error="Reports available on the launcher PC only"), 403
        project_id = request.args.get("project_id", "")
        if not ID.fullmatch(project_id) or not ID.fullmatch(run_id):
            return jsonify(error="Explicit project and run IDs required"), 400
        try:
            con = open_ro()
            if con is None:
                return jsonify(error="Benchmark database unavailable"), 404
            with closing(con):
                row = con.execute(
                    "SELECT * FROM benchmark_runs WHERE id=? AND project_id=?",
                    (run_id, project_id),
                ).fetchone()
                if row is None:
                    return jsonify(error="Benchmark run not found in project"), 404
                variants = con.execute(
                    "SELECT id,run_id,label,config_json FROM benchmark_variants "
                    "WHERE run_id=? ORDER BY label,id", (run_id,),
                ).fetchall()
                obs = con.execute(
                    "SELECT id,run_id,variant_id,repetition,status,duration_ms,peak_vram_bytes "
                    "FROM benchmark_observations WHERE run_id=? "
                    "ORDER BY variant_id,repetition", (run_id,),
                ).fetchall()
                lineage = con.execute(
                    "SELECT l.observation_id,l.snapshot_json "
                    "FROM benchmark_generation_lineage l "
                    "WHERE l.run_id=?", (run_id,),
                ).fetchall()
            snap = {x["observation_id"]: json.loads(x["snapshot_json"]) for x in lineage}
            if any(not isinstance(v, dict) for v in snap.values()):
                raise ValueError("Invalid lineage payload")
            report = {
                "schema_version": 1, "run": dict(row),
                "variants": [dict(v) for v in variants],
                "observations": [
                    {**dict(o), "generation_lineage": {
                        key: value for key, value in snap.get(o["id"], {}).items()
                        if key in ("generation_id", "workflow_id", "status", "submitted_graph_sha256", "execution_timing", "comfyui_prompt_id")
                    } if o["id"] in snap else None}
                    for o in obs
                ],
            }
            # B9.9: inspect only existing *local* persisted generation records.
            # Never contact ComfyUI or read arbitrary filesystem paths.
            history_ids = sorted({
                o["generation_lineage"]["generation_id"]
                for o in report["observations"]
                if isinstance(o.get("generation_lineage"), dict)
                and isinstance(o["generation_lineage"].get("generation_id"), str)
                and 0 < len(o["generation_lineage"]["generation_id"]) <= 200
            })
            history_truncated = len(history_ids) > 50
            local_history = {}
            history_db = Path(base) / "settings" / "orkilab" / "generations.sqlite3"
            if history_ids and not history_truncated and history_db.is_file():
                with closing(sqlite3.connect(
                    history_db.resolve().as_uri() + "?mode=ro", uri=True, timeout=5
                )) as hist:
                    for generation_id in history_ids:
                        row_history = hist.execute(
                            "SELECT id,prompt_id,workflow_id,state,graph,outputs "
                            "FROM generations WHERE id=? AND length(graph)<=2000000 "
                            "AND length(outputs)<=500000",
                            (generation_id,),
                        ).fetchone()
                        if row_history is not None:
                            local_history[generation_id] = {
                                "id": row_history[0], "prompt_id": row_history[1],
                                "workflow_id": row_history[2], "state": row_history[3],
                                "graph": row_history[4], "outputs": row_history[5],
                            }
            result = summarize_benchmark_report(report)
            result["comparability"] = assess_duration_comparability(report)
            result["b10_results"] = describe_cross_variant_measurements(
                result, result["comparability"]
            )
            result["reproducibility_protocol"] = declared_protocol_readiness(report)
            result["recorded_execution_evidence"] = verify_recorded_execution_evidence(report)
            result["saved_history_consistency"] = summarize_saved_history_matches(
                report, local_history, truncated=history_truncated
            )
            result["b9_closure"] = summarize_b9_closure(result)
            result["b10_comparison_preflight"] = inspect_comparison_plan(report)
            result["b10_release_readiness"] = summarize_b10_release_readiness(result)
            result["project_id"] = project_id
            result["name"] = row["name"]
            result["run_created_at"] = row["created_at"]
            result["read_only"] = True
            return jsonify(result)
        except (sqlite3.Error, ValueError, TypeError, json.JSONDecodeError):
            return jsonify(error="Benchmark report could not be verified"), 503
