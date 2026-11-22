"""Bundled OrkiLab Multiview templates: offline catalog, ZIP and explicit import.

Only project-authored core-node graphs are served/imported locally. External
ComfyUI upstream examples are linked for reference, not silently rebranded,
downloaded, executed or redistributed.
"""
import copy
import hashlib
import io
import json
import re
import sqlite3
import zipfile
from contextlib import closing
from pathlib import Path

from flask import jsonify, request, send_file

from comfyui_connect import DEFAULT_SETTINGS, get_json, validate_settings
from dataset_studio import valid_origin
from workflow_library import inspect_graph, multiview_reference_profile

LOCAL = (
    {
        "id": "core-img2img",
        "name": "OrkiLab · Multiview · Core Img2Img",
        "file": "orkilab-multiview-core-img2img-api.json",
        "references": 1,
        "core_only": True,
        "status": "starter",
        "description": "Basic img2img conditioning; no accurate viewpoint control.",
    },
    {
        "id": "core-preserve",
        "name": "OrkiLab · Multiview · Core Preserve",
        "file": "orkilab-multiview-core-preserve-api.json",
        "references": 1,
        "core_only": True,
        "status": "starter",
        "description": "Low denoise (0.30), preserves appearance but limited camera change.",
    },
    {
        "id": "core-variation",
        "name": "OrkiLab · Multiview · Core Variation",
        "file": "orkilab-multiview-core-variation-api.json",
        "references": 1,
        "core_only": True,
        "status": "starter",
        "description": "Higher denoise (0.72), more changes but invented details likely.",
    },
)
EXTERNAL = (
    {
        "id": "qwen-image-2.1-edit",
        "name": "ComfyUI · Qwen Image 2.1 Edit (upstream)",
        "references": None,
        "status": "upstream-unverified",
        "core_only": False,
        "url": "https://github.com/Comfy-Org/workflow_templates/blob/main/templates/image_qwen_image_2_1_image_edit.json",
        "description": "Official ComfyUI image editing template; review embedded subgraphs and installed dependencies.",
    },
    {
        "id": "flux3-klein-edit",
        "name": "ComfyUI · FLUX.3 Klein Image Edit (upstream)",
        "references": None,
        "status": "upstream-unverified",
        "core_only": False,
        "url": "https://github.com/Comfy-Org/workflow_templates/blob/main/templates/image_flux3_klein_image_edit.json",
        "description": "Official ComfyUI edit template; may require extra native and custom nodes.",
    },
    {
        "id": "flux3-klein-distilled",
        "name": "ComfyUI · FLUX.3 Klein Distilled Image Edit (upstream)",
        "references": None,
        "status": "upstream-unverified",
        "core_only": False,
        "url": "https://github.com/Comfy-Org/workflow_templates/blob/main/templates/image_flux3_klein_distilled_image_edit.json",
        "description": "Official distilled editing graph; use only after confirming node availability.",
    },
)
IMAGE_NAME = re.compile(r"orkilab_[0-9a-f]{32}_[0-9a-f]{16}\.(?:jpg|png|webp)\Z")


def validate_official_graph(graph):
    details = inspect_graph(graph)
    if details["format"] != "api":
        raise ValueError("Official workflow must be in API format")
    allowed = {
        "LoadImage", "CheckpointLoaderSimple", "VAEEncode", "CLIPTextEncode",
        "KSampler", "VAEDecode", "SaveImage",
    }
    if any(kind not in allowed for kind in details["node_types"]):
        raise ValueError("Official core template contains an unsupported node")
    profile = multiview_reference_profile(graph, "image")
    if not profile["likely_compatible"] or profile["image_inputs"] != 1:
        raise ValueError("Official template lacks connected reference or prompt")
    return details


def catalog(root):
    result = []
    for entry in LOCAL:
        path = root / entry["file"]
        raw = path.read_bytes()
        graph = json.loads(raw)
        validate_official_graph(graph)
        result.append({
            **entry, "sha256": hashlib.sha256(raw).hexdigest(),
            "requires_checkpoint": True, "downloadable": True,
        })
    return result


def build_bundle(root):
    entries = catalog(root)
    target = io.BytesIO()
    with zipfile.ZipFile(target, "w", compression=zipfile.ZIP_DEFLATED) as bundle:
        for entry in entries:
            data = (root / entry["file"]).read_bytes()
            bundle.writestr("orkilab-multiview/" + entry["file"], data)
        bundle.writestr("orkilab-multiview/README.md",
                        (root / "README.md").read_bytes())
        bundle.writestr("orkilab-multiview/manifest.json",
                        json.dumps({"schema": 1, "bundled": entries,
                                    "external_references": EXTERNAL},
                                   indent=2, ensure_ascii=False).encode("utf-8"))
    target.seek(0)
    return target


def checkpoint_choices(settings):
    info = get_json(settings["url"], "/object_info/CheckpointLoaderSimple",
                    max_bytes=2_000_000, timeout=6)
    loader = info.get("CheckpointLoaderSimple", {})
    definitions = loader.get("input", {}).get("required", {}).get("ckpt_name", [])
    names = definitions[0] if definitions and isinstance(definitions[0], list) else []
    return [x for x in names if isinstance(x, str) and len(x) <= 250][:1000]


def register(app, base):
    base = Path(base)
    root = base / "workflows" / "multiview"
    db_path = base / "settings" / "orkilab" / "workflows.sqlite3"
    cfg_path = base / "settings" / "orkilab" / "comfyui.json"

    def authorized():
        return request.remote_addr in ("127.0.0.1", "::1") and valid_origin()

    def config():
        try:
            value = json.loads(cfg_path.read_text(encoding="utf-8"))
            return validate_settings(value, DEFAULT_SETTINGS)
        except (OSError, ValueError, TypeError, KeyError):
            return dict(DEFAULT_SETTINGS)

    @app.get("/api/workspace/multiview/official-workflows")
    def multiview_official_catalog():
        if not authorized():
            return jsonify(error="Local same-origin access required"), 403
        if config()["mode"] == "native":
            return jsonify(error="ComfyUI disabled in standalone mode"), 409
        try:
            return jsonify(official=catalog(root), upstream=EXTERNAL)
        except (OSError, ValueError, TypeError):
            app.logger.exception("Official Multiview catalog missing or invalid")
            return jsonify(error="Official workflow library is unavailable"), 503

    @app.get("/api/workspace/multiview/official-workflows/download")
    def multiview_official_download():
        if not authorized():
            return jsonify(error="Local same-origin access required"), 403
        if config()["mode"] == "native":
            return jsonify(error="ComfyUI disabled in standalone mode"), 409
        try:
            return send_file(build_bundle(root), mimetype="application/zip",
                             download_name="OrkiLab-Multiview-Workflows-0.5.0-rc1.zip",
                             as_attachment=True)
        except (OSError, ValueError, TypeError):
            return jsonify(error="Could not package official workflows"), 503

    @app.get("/api/workspace/multiview/official-workflows/checkpoints")
    def multiview_official_checkpoints():
        if not authorized():
            return jsonify(error="Local same-origin access required"), 403
        settings = config()
        if settings["mode"] == "native":
            return jsonify(error="ComfyUI disabled in standalone mode"), 409
        try:
            return jsonify(checkpoints=checkpoint_choices(settings))
        except (OSError, ValueError, TypeError, KeyError, TimeoutError):
            return jsonify(error="Could not read checkpoints from the running ComfyUI"), 502

    @app.post("/api/workspace/multiview/official-workflows/install")
    def multiview_official_install():
        if not authorized():
            return jsonify(error="Local same-origin access required"), 403
        settings = config()
        if settings["mode"] == "native":
            return jsonify(error="ComfyUI disabled in standalone mode"), 409
        if request.mimetype != "application/json" or not 0 < (request.content_length or 0) <= 1024:
            return jsonify(error="Invalid workflow installation request"), 400
        body = request.get_json(silent=True)
        if not isinstance(body, dict) or body.get("confirm") is not True:
            return jsonify(error="Explicit consent is required"), 400
        entry = next((e for e in LOCAL if e["id"] == body.get("template_id")), None)
        image = body.get("image_name")
        checkpoint = body.get("checkpoint")
        if (entry is None or not isinstance(image, str) or not IMAGE_NAME.fullmatch(image)
                or not isinstance(checkpoint, str) or len(checkpoint) > 250):
            return jsonify(error="Select an official workflow, a staged photo and checkpoint"), 400
        try:
            names = checkpoint_choices(settings)
            if checkpoint not in names:
                return jsonify(error="Selected checkpoint is not installed in ComfyUI"), 409
            graph = copy.deepcopy(json.loads((root / entry["file"]).read_text(encoding="utf-8")))
            validate_official_graph(graph)
            for node in graph.values():
                if node["class_type"] == "LoadImage":
                    node["inputs"]["image"] = image
                if node["class_type"] == "CheckpointLoaderSimple":
                    node["inputs"]["ckpt_name"] = checkpoint
            summary = inspect_graph(graph)
            raw = json.dumps(graph, ensure_ascii=False, sort_keys=True)
            db_path.parent.mkdir(parents=True, exist_ok=True)
            with closing(sqlite3.connect(db_path, timeout=10)) as con, con:
                con.execute("CREATE TABLE IF NOT EXISTS workflows "
                            "(id TEXT PRIMARY KEY, name TEXT NOT NULL, category TEXT NOT NULL, "
                            "favorite INTEGER NOT NULL DEFAULT 0, graph TEXT NOT NULL, summary TEXT NOT NULL)")
                existing = con.execute("SELECT id,graph FROM workflows WHERE name=? "
                                       "AND category='image'", (entry["name"],)).fetchall()
                for ident, previous in existing:
                    if json.loads(previous) == graph:
                        return jsonify(id=ident, name=entry["name"], installed=False), 200
                if con.execute("SELECT COUNT(*) FROM workflows").fetchone()[0] >= 500:
                    return jsonify(error="Workflow library limit reached"), 409
                import uuid
                ident = uuid.uuid4().hex
                con.execute("INSERT INTO workflows (id,name,category,favorite,graph,summary)"
                            " VALUES (?,?, 'image',0,?,?)",
                            (ident, entry["name"], raw, json.dumps(summary)))
            return jsonify(id=ident, name=entry["name"], installed=True), 201
        except (OSError, ValueError, TypeError, sqlite3.Error) as exc:
            app.logger.warning("Official Multiview template installation failed: %s", str(exc)[:140])
            return jsonify(error="Cannot install this workflow; check ComfyUI and the model selection"), 502
