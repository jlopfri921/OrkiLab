"""Explicit, local-only installation of project checkpoints into ComfyUI.
Copies are independently named and tracked; original trainer outputs are untouched.
"""
import hashlib
import json
import os
import shutil
import tempfile
import threading
from pathlib import Path
from flask import jsonify, request
from project_checkpoints import inventory

_LOCK = threading.RLock()
_PREFIX = "OrkiLab_"

def model_name(project_id, name):
    # Prefix plus project identity prevents two trainings from colliding.
    if Path(name).name != name or not name.lower().endswith(".safetensors"):
        raise ValueError("Invalid checkpoint filename")
    return f"{_PREFIX}{project_id[:12]}_{name}"

def destination(raw):
    if not isinstance(raw, str) or len(raw) > 1024:
        raise ValueError("Select the local ComfyUI/models/loras directory")
    p = Path(raw.strip()).expanduser()
    if not p.is_absolute() or not p.is_dir() or p.is_symlink():
        raise ValueError("Select an existing local ComfyUI/models/loras directory")
    if p.name.lower() != "loras" or p.parent.name.lower() != "models" or p.parent.is_symlink():
        raise ValueError("Folder must be ComfyUI/models/loras")
    return p.resolve(strict=True)

def manifest_path(base):
    return Path(base) / "settings" / "orkilab" / "managed_checkpoints.json"

def load_manifest(base):
    path = manifest_path(base)
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except (OSError, ValueError):
        return {}

def save_manifest(base, data):
    path = manifest_path(base)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = None
    try:
        with tempfile.NamedTemporaryFile("w", dir=path.parent, encoding="utf-8", delete=False) as fh:
            tmp = Path(fh.name)
            json.dump(data, fh, indent=2)
        os.replace(tmp, path)
    finally:
        if tmp is not None:
            tmp.unlink(missing_ok=True)

def file_hash(path):
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for buf in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(buf)
    return h.hexdigest()

def manage(base, project_id, directory, names, action):
    if action not in ("status", "install", "uninstall"):
        raise ValueError("Unknown action")
    data = inventory(base, project_id)
    found = {item["name"]: item for item in data["checkpoints"]}
    if not isinstance(names, list) or len(names) > 6 or any(not isinstance(n, str) or n not in found for n in names) or len(set(names)) != len(names):
        raise ValueError("Select up to six project checkpoints")
    root = destination(directory)
    output = Path(data["output_folder"]).resolve()
    report = []
    with _LOCK:
        manifest = load_manifest(base)
        for name in names:
            alias = model_name(project_id, name)
            target = root / alias
            source = output / name
            if source.is_symlink() or not source.is_file() or not source.resolve().is_relative_to(output):
                raise ValueError("Source checkpoint is unavailable")
            key = str(target)
            record = manifest.get(key)
            tracked = isinstance(record, dict) and record.get("project_id") == project_id and record.get("source") == name
            exists = target.exists() or target.is_symlink()
            if action == "install":
                if exists:
                    if not tracked or target.is_symlink() or file_hash(target) != record.get("sha256"):
                        raise FileExistsError(f"Destination exists and is not an unchanged OrkiLab-managed copy: {alias}")
                else:
                    # Exclusive creation avoids overwriting external files.
                    try:
                        with source.open("rb") as src, target.open("xb") as dst:
                            shutil.copyfileobj(src, dst, 1024 * 1024)
                        digest = file_hash(target)
                        manifest[key] = {"project_id": project_id, "source": name, "sha256": digest}
                        save_manifest(base, manifest)
                        tracked = True
                    except BaseException:
                        if key not in manifest:
                            target.unlink(missing_ok=True)
                        raise
            elif action == "uninstall":
                if not tracked:
                    raise ValueError(f"Checkpoint is not registered as managed by OrkiLab: {alias}")
                if exists:
                    if target.is_symlink() or not target.is_file() or file_hash(target) != record.get("sha256"):
                        raise ValueError(f"Checkpoint changed since installation; it will not be deleted: {alias}")
                    target.unlink()
                manifest.pop(key, None)
                save_manifest(base, manifest)
                tracked, exists = False, False
            report.append({"name": name, "comfy_name": alias, "installed": target.is_file() and not target.is_symlink(), "managed": tracked})
    return {"checkpoints": report, "directory": str(root), "model_refresh_required": action != "status"}

def register(app, base):
    @app.post("/api/workspace/projects/<project_id>/checkpoints/manage")
    def managed_project_checkpoints(project_id):
        if request.remote_addr not in ("127.0.0.1", "::1"):
            return jsonify(error="Checkpoint management is local-only"), 403
        if request.mimetype != "application/json" or not 0 < (request.content_length or 0) <= 8192:
            return jsonify(error="Invalid request"), 400
        body = request.get_json(silent=True)
        if not isinstance(body, dict):
            return jsonify(error="Invalid request"), 400
        try:
            return jsonify(manage(base, project_id, body.get("directory"), body.get("checkpoints"), body.get("action")))
        except LookupError as exc:
            return jsonify(error=str(exc)), 404
        except (ValueError, FileExistsError) as exc:
            return jsonify(error=str(exc)), 409
        except OSError as exc:
            return jsonify(error="File operation failed", detail=str(exc)[:250]), 500
