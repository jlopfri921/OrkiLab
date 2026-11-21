"""Read-only, project-scoped checkpoint inventory. No trainer files are changed."""
import re
import sqlite3
from contextlib import closing
from pathlib import Path
from flask import jsonify, request

HEX = frozenset("0123456789abcdef")
STEP = re.compile(r"_step_(\d{1,9})\.safetensors$", re.IGNORECASE)
MAX_FILES = 300

def inventory(base, project_id):
    if not isinstance(project_id, str) or len(project_id) != 32 or not set(project_id) <= HEX:
        raise ValueError("Invalid project")
    base = Path(base)
    database = base / "settings" / "orkilab" / "projects.sqlite3"
    if not database.is_file():
        raise LookupError("Project not found")
    with closing(sqlite3.connect(database)) as conn:
        row = conn.execute("SELECT engine,category,name FROM projects WHERE id=? AND archived=0",
                           (project_id,)).fetchone()
    if not row:
        raise LookupError("Project not found")
    engine, category, display_name = row
    if category != "image":
        raise ValueError("Checkpoint comparison currently supports image projects")
    # Exact output layout used by the project-scoped trainer drafts.
    project_name = "orkilab_" + project_id[:12]
    folder = base / "Outputs" / (engine + "_lora_output_" + project_name)
    resolved_root = (base / "Outputs").resolve()
    if folder.is_symlink() or not folder.is_dir():
        return {"engine": engine, "project_name": display_name, "checkpoints": [], "output_folder": str(folder), "truncated": False}
    if not folder.resolve().is_relative_to(resolved_root):
        raise ValueError("Output directory is not inside OrkiLab")
    items = []
    for file in folder.iterdir():
        if file.is_symlink() or not file.is_file():
            continue
        match = STEP.search(file.name)
        if not match:
            continue
        try:
            size = file.stat().st_size
        except OSError:
            continue
        if not 0 < size < 100 * 1024**3:
            continue
        items.append({"step": int(match.group(1)), "name": file.name,
                      "size_bytes": size})
    items.sort(key=lambda item: (item["step"], item["name"].lower()))
    return {"engine": engine, "project_name": display_name, "checkpoints": items[:MAX_FILES],
            "output_folder": str(folder), "truncated": len(items) > MAX_FILES}

def register(app, base):
    @app.get("/api/workspace/projects/<project_id>/checkpoints")
    def project_checkpoints(project_id):
        if request.remote_addr not in ("127.0.0.1", "::1"):
            return jsonify(error="Checkpoint inventory is local-only"), 403
        try:
            return jsonify(inventory(base, project_id))
        except LookupError as exc:
            return jsonify(error=str(exc)), 404
        except ValueError as exc:
            return jsonify(error=str(exc)), 400
