"""Workspace routes, alongside the existing launcher."""
from flask import jsonify, request, send_from_directory
import shutil
import sqlite3
from contextlib import closing
from pathlib import Path

from workspace_store import ProjectStore
import comfyui_connect
import workflow_library
import generation_studio
import dataset_studio
import multiview_studio
import multiview_assist
import multiview_export
import multiview_recovery
import multiview_viewpoint_ai
import multiview_generate_views
import multiview_official_workflows
import gpu_monitor
import gpu_stats
import project_layout
import promotions_feed
import project_checkpoints
import managed_checkpoints
import checkpoint_reviews
import benchmark_reporting_routes


def register(app, base, load_config):
    base = Path(base)
    promotions_feed.register(app)
    comfyui_connect.register(app, base)
    workflow_library.register(app, base)
    generation_studio.register(app, base)
    benchmark_reporting_routes.report_routes(app, base)
    dataset_studio.register(app, base)
    multiview_studio.register(app, base)
    multiview_assist.register(app, base)
    multiview_export.register(app, base)
    multiview_recovery.register(app, base)
    multiview_viewpoint_ai.register(app, base)
    multiview_generate_views.register(app, base)
    multiview_official_workflows.register(app, base)
    project_checkpoints.register(app, base)
    managed_checkpoints.register(app, base)
    checkpoint_reviews.register(app, base)
    store = ProjectStore(base / "settings" / "orkilab" / "projects.sqlite3")

    @app.get("/workspace/guide")
    def orkilab_guide_page():
        return send_from_directory(str(base / "GUI"), "orkilab_guide.html")

    @app.get("/workspace/datasets")
    def dataset_studio_page():
        return send_from_directory(str(base / "GUI"), "dataset_studio.html")

    @app.get("/workspace/multiview")
    def multiview_studio_page():
        return send_from_directory(str(base / "GUI"), "multiview_studio.html")

    @app.get("/workspace/comfyui")
    @app.get("/workspace")
    def workspace_page():
        return send_from_directory(str(base / "GUI"), "workspace.html")

    @app.get("/api/workspace/gpu/monitor")
    def workspace_gpu_monitor():
        if request.remote_addr not in ("127.0.0.1", "::1"):
            return jsonify(error="GPU monitoring is available on the launcher PC only"), 403
        data = gpu_monitor.get_gpu_metrics().copy()
        data["training_active"] = bool(project_layout.training_in_progress(base))
        data["selected_gpu"] = gpu_stats.saved_gpu() or None
        try:
            import psutil
            ram = psutil.virtual_memory()
            data["system_ram"] = {"total_bytes": ram.total, "available_bytes": ram.available,
                                  "used_bytes": ram.total - ram.available,
                                  "percent": round((ram.total - ram.available) * 100 / ram.total, 1)
                                  if ram.total else None}
        except (ImportError, OSError, ValueError):
            data["system_ram"] = None
        return jsonify(data)

    @app.get("/api/workspace/overview")
    def workspace_overview():
        try:
            import psutil
            ram = psutil.virtual_memory()
            memory = {"total": ram.total, "available": ram.available}
        except (ImportError, OSError):
            memory = None
        disk = shutil.disk_usage(base)
        return jsonify({"engines": load_config()["trainers"],
                        "memory": memory, "disk": {"total": disk.total, "free": disk.free},
                        "version": load_config().get("orkilab_version", "development")})

    @app.route("/api/workspace/projects", methods=["GET", "POST"])
    def workspace_projects():
        if request.method == "GET":
            projects = store.list(request.args.get("archived") == "1")
            # Image references live in Dataset Studio's separate SQLite database.
            dataset_db = base / "settings" / "orkilab" / "datasets.sqlite3"
            counts, captioned, sources, prepared = {}, {}, {}, {}
            if dataset_db.is_file():
                try:
                    with closing(sqlite3.connect(dataset_db, timeout=5)) as conn:
                        counts = {pid: count for pid, count in conn.execute(
                            "SELECT project_id, COUNT(*) FROM dataset_images GROUP BY project_id")}
                        tables = {row[0] for row in conn.execute(
                            "SELECT name FROM sqlite_master WHERE type='table'")}
                        if "dataset_captions" in tables:
                            captioned = {pid: count for pid, count in conn.execute(
                                "SELECT i.project_id, COUNT(*) FROM dataset_images i "
                                "JOIN dataset_captions c ON c.image_id=i.id AND c.project_id=i.project_id "
                                "WHERE i.review != 'rejected' AND LENGTH(TRIM(c.caption)) > 0 "
                                "GROUP BY i.project_id")}
                        for project_id, path in conn.execute(
                                "SELECT project_id,path FROM dataset_images ORDER BY project_id,path"):
                            sources.setdefault(project_id, set()).add(str(Path(path).parent))
                        if "dataset_preparations" in tables:
                            for project_id, path in conn.execute(
                                    "SELECT project_id,path FROM dataset_preparations ORDER BY rowid DESC"):
                                prepared.setdefault(project_id, path)
                except sqlite3.Error:
                    counts, captioned, sources, prepared = {}, {}, {}, {}
            for project in projects:
                project_id = project["id"]
                project["dataset_image_count"] = counts.get(project_id, 0)
                project["dataset_caption_count"] = captioned.get(project_id, 0)
                project["dataset_source_folders"] = sorted(sources.get(project_id, ()))
                prepared_path = prepared.get(project_id)
                project["dataset_prepared_path"] = (
                    prepared_path if prepared_path and Path(prepared_path).is_dir() else None)
                project["dataset_train_ready"] = False  # Engine-specific validation pending.
            return jsonify({"projects": projects})
        if request.mimetype != "application/json":
            return jsonify({"error": "JSON required"}), 415
        if request.content_length is None or request.content_length > 16384:
            return jsonify({"error": "Invalid request size"}), 413
        try:
            engines = {x["id"] for x in load_config()["trainers"]}
            return jsonify(store.create(request.get_json(silent=True), engines)), 201
        except ValueError as exc:
            return jsonify({"error": str(exc)}), 400

    @app.post("/api/workspace/projects/<project_id>/archive")
    def workspace_archive(project_id):
        if request.mimetype != "application/json":
            return jsonify({"error": "JSON required"}), 415
        if request.content_length is None or request.content_length > 1024:
            return jsonify({"error": "Invalid request size"}), 413
        body = request.get_json(silent=True)
        if not isinstance(body, dict) or not isinstance(body.get("archived"), bool):
            return jsonify({"error": "Expected archived boolean"}), 400
        if not store.archive(project_id, body["archived"]):
            return jsonify({"error": "Project not found"}), 404
        return jsonify({"ok": True})
