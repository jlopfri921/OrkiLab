"""Multiview 0.5 RC1: read-only project health and explicit Dataset Studio linking.

Dataset Studio and Multiview use separate image-reference indexes. This adapter
never creates a project or moves/deletes originals; it links already indexed
project photos to a selected Multiview subject only after local confirmation.
"""
import sqlite3
import uuid
from contextlib import closing
from pathlib import Path

from flask import jsonify, request

from dataset_studio import valid_origin
from multiview_studio import identifier, source_path, inspect_image, sharpness_score

MAX_CANDIDATES = 300
MAX_LINK_REQUEST = 30


def register(app, base):
    base = Path(base)
    root = base / "settings" / "orkilab"
    projects = root / "projects.sqlite3"
    captures = root / "multiview.sqlite3"
    dataset = root / "datasets.sqlite3"

    def allowed(mutation=False):
        return (request.remote_addr in ("127.0.0.1", "::1")
                and (not mutation or valid_origin()))

    def project_exists(project_id):
        if not identifier(project_id) or not projects.is_file():
            return False
        with closing(sqlite3.connect(projects, timeout=5)) as conn:
            return conn.execute(
                "SELECT 1 FROM projects WHERE id=? AND archived=0 AND category='image'",
                (project_id,)).fetchone() is not None

    def dataset_rows(project_id):
        if not dataset.is_file():
            return [], 0
        with closing(sqlite3.connect(dataset, timeout=5)) as conn:
            conn.row_factory = sqlite3.Row
            table = conn.execute(
                "SELECT 1 FROM sqlite_master WHERE type='table' AND name='dataset_images'"
            ).fetchone()
            if not table:
                return [], 0
            total = conn.execute(
                "SELECT COUNT(*) FROM dataset_images WHERE project_id=?",
                (project_id,)).fetchone()[0]
            rows = conn.execute(
                "SELECT id,name,path,review FROM dataset_images WHERE project_id=? "
                "ORDER BY name COLLATE NOCASE,id LIMIT ?",
                (project_id, MAX_CANDIDATES)).fetchall()
            return [dict(row) for row in rows], total

    def capture_counts(project_id):
        if not captures.is_file():
            return dict(subjects=0, captures=0, missing=0)
        with closing(sqlite3.connect(captures, timeout=5)) as conn:
            subjects = conn.execute(
                "SELECT COUNT(*) FROM mv_subjects WHERE project_id=?",
                (project_id,)).fetchone()[0]
            rows = conn.execute(
                "SELECT path FROM mv_captures WHERE project_id=?",
                (project_id,)).fetchall()
        # Read-only bounded filesystem stat; no image files opened or decoded.
        missing = sum(1 for (path,) in rows if not Path(path).is_file())
        return dict(subjects=subjects, captures=len(rows), missing=missing)

    @app.get("/api/workspace/multiview/projects/<project_id>/recovery")
    def multiview_recovery_status(project_id):
        if not allowed():
            return jsonify(error="Use Multiview on the launcher computer"), 403
        if not project_exists(project_id):
            return jsonify(error="Active image project not found"), 404
        found, total = dataset_rows(project_id)
        counts = capture_counts(project_id)
        paths = {str(Path(row["path"])) for row in found}
        already = set()
        if captures.is_file() and paths:
            with closing(sqlite3.connect(captures, timeout=5)) as conn:
                already = {row[0] for row in conn.execute(
                    "SELECT DISTINCT path FROM mv_captures WHERE project_id=?",
                    (project_id,))}
        return jsonify(
            project_id=project_id, dataset_images=total,
            multiview_subjects=counts["subjects"],
            multiview_captures=counts["captures"],
            missing_originals=counts["missing"],
            candidates=[dict(id=row["id"], name=row["name"],
                             review=row["review"],
                             linked=str(Path(row["path"])) in already,
                             available=Path(row["path"]).is_file())
                        for row in found],
            limited=total > MAX_CANDIDATES,
        )

    @app.post("/api/workspace/multiview/projects/<project_id>/subjects/<subject_id>/link-dataset")
    def multiview_link_dataset(project_id, subject_id):
        if not allowed(True):
            return jsonify(error="Local same-origin access required"), 403
        if not project_exists(project_id) or not identifier(subject_id):
            return jsonify(error="Project or subject not found"), 404
        if request.mimetype != "application/json" or not 0 < (request.content_length or 0) <= 4000:
            return jsonify(error="Invalid link request"), 400
        body = request.get_json(silent=True)
        ids = body.get("image_ids") if isinstance(body, dict) else None
        if (not isinstance(body, dict) or body.get("confirm") is not True
                or not isinstance(ids, list) or not 1 <= len(ids) <= MAX_LINK_REQUEST
                or any(not identifier(item) for item in ids) or len(set(ids)) != len(ids)):
            return jsonify(error="Confirm 1-30 distinct Dataset Studio image references"), 400
        if not dataset.is_file() or not captures.is_file():
            return jsonify(error="Dataset Studio or Multiview index is missing"), 404
        try:
            with closing(sqlite3.connect(captures, timeout=10)) as conn:
                if not conn.execute(
                    "SELECT 1 FROM mv_subjects WHERE id=? AND project_id=?",
                    (subject_id, project_id)).fetchone():
                    return jsonify(error="Subject does not belong to project"), 404
            with closing(sqlite3.connect(dataset, timeout=10)) as conn:
                marks = ",".join("?" for _ in ids)
                rows = conn.execute(
                    "SELECT id,path FROM dataset_images "
                    "WHERE project_id=? AND id IN (" + marks + ")",
                    (project_id, *ids)).fetchall()
            if len(rows) != len(ids):
                return jsonify(error="Some Dataset Studio references do not belong to project"), 404
            # All original images are inspected BEFORE starting a DB transaction.
            records = []
            for image_id, path in sorted(rows):
                source = source_path(path)
                details = inspect_image(source)
                score = sharpness_score(source)
                records.append((uuid.uuid4().hex, project_id, subject_id,
                                str(source), source.name, details["sha256"],
                                details["bytes"], details["width"], details["height"],
                                details["format"], score))
            inserted = 0
            with closing(sqlite3.connect(captures, timeout=10)) as conn:
                conn.execute("BEGIN IMMEDIATE")
                if not conn.execute(
                    "SELECT 1 FROM mv_subjects WHERE id=? AND project_id=?",
                    (subject_id, project_id)).fetchone():
                    return jsonify(error="Subject no longer exists"), 409
                for record in records:
                    before = conn.total_changes
                    conn.execute("""INSERT OR IGNORE INTO mv_captures
                        (id,project_id,subject_id,path,name,sha256,bytes,width,height,
                         format,sharpness_score,source_type,provenance,review)
                        VALUES (?,?,?,?,?,?,?,?,?,?,?,'unknown','unknown','unreviewed')""", record)
                    inserted += conn.total_changes - before
                if inserted:
                    conn.execute(
                        "UPDATE mv_subjects SET updated_at=CURRENT_TIMESTAMP WHERE id=?",
                        (subject_id,))
                conn.commit()
            return jsonify(linked=inserted, already_linked=len(records)-inserted,
                           review="unreviewed", source_type="unknown"), 200
        except (OSError, ValueError, sqlite3.Error) as exc:
            app.logger.warning("Multiview Dataset Studio linking failed: %s", str(exc)[:160])
            return jsonify(error="Could not safely link images",
                           detail=str(exc)[:150] if isinstance(exc, ValueError) else ""), 400
