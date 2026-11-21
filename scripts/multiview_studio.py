"""Multiview Studio 0.5.0-alpha.1: immutable image references and manual views.

This module never moves, edits, deletes or generates source photographs.
It deliberately does not infer camera geometry from EXIF or file names.
"""
import hashlib
import mimetypes
import sqlite3
import uuid
from contextlib import closing
from pathlib import Path

from flask import jsonify, request, send_file
from PIL import Image, UnidentifiedImageError
from dataset_studio import valid_origin

MAX_IMAGE_BYTES = 20 * 1024 * 1024
MAX_PIXELS = 60_000_000
ALLOWED_FORMATS = {"PNG", "JPEG", "WEBP", "BMP"}
SOURCE_TYPES = {"real_photo", "video_frame", "synthetic", "unknown"}
PROVENANCES = {"manual", "unknown", "workflow", "embedded_exif", "estimated"}
REVIEWS = {"unreviewed", "approved", "rejected"}
HEX = set("0123456789abcdef")


def identifier(value):
    return isinstance(value, str) and len(value) == 32 and set(value) <= HEX


def text_field(value, max_length, required=False):
    if not isinstance(value, str):
        raise ValueError("Expected text")
    value = value.strip()
    if len(value) > max_length or (required and not value):
        raise ValueError("Text length is invalid")
    return value


def coordinate(value, low, high, label):
    if value is None or value == "":
        return None
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(label + " must be a number")
    import math
    if not math.isfinite(value) or not low <= value <= high:
        raise ValueError(label + " outside valid range")
    return round(float(value), 4)


def source_path(value):
    if not isinstance(value, str) or not 0 < len(value) <= 2048:
        raise ValueError("Invalid image path")
    source = Path(value).expanduser()
    if not source.is_absolute() or source.suffix.lower() not in {
            ".png", ".jpg", ".jpeg", ".webp", ".bmp"}:
        raise ValueError("Select an absolute image path (PNG/JPEG/WebP/BMP)")
    # Reject all symlinks in the path, not only the final component.
    for component in (source, *source.parents):
        if component.is_symlink():
            raise ValueError("Symbolic links cannot be imported")
    if not source.is_file():
        raise ValueError("Image not found")
    size = source.stat().st_size
    if not 0 < size <= MAX_IMAGE_BYTES:
        raise ValueError("Image exceeds 20 MiB or is empty")
    return source


def inspect_image(source):
    try:
        with Image.open(source) as image:
            width, height = image.size
            fmt = image.format
            if fmt not in ALLOWED_FORMATS or width <= 0 or height <= 0 or width * height > MAX_PIXELS:
                raise ValueError("Unsupported image or excessive dimensions")
            image.verify()
    except (UnidentifiedImageError, OSError, Image.DecompressionBombError, Image.DecompressionBombWarning) as exc:
        raise ValueError("Unreadable or invalid image") from exc
    digest = hashlib.sha256()
    with source.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return {"width": width, "height": height, "sha256": digest.hexdigest(),
            "bytes": source.stat().st_size, "format": fmt}


def register(app, base):
    base = Path(base)
    database = base / "settings" / "orkilab" / "multiview.sqlite3"
    projects = base / "settings" / "orkilab" / "projects.sqlite3"

    def connect():
        database.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(database, timeout=10)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys=ON")
        conn.execute("""CREATE TABLE IF NOT EXISTS mv_subjects(
            id TEXT PRIMARY KEY, project_id TEXT NOT NULL, name TEXT NOT NULL,
            notes TEXT NOT NULL DEFAULT '',
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(project_id, name))""")
        conn.execute("""CREATE TABLE IF NOT EXISTS mv_captures(
            id TEXT PRIMARY KEY, project_id TEXT NOT NULL, subject_id TEXT NOT NULL,
            path TEXT NOT NULL, name TEXT NOT NULL,
            sha256 TEXT NOT NULL, bytes INTEGER NOT NULL,
            width INTEGER NOT NULL, height INTEGER NOT NULL, format TEXT NOT NULL,
            view_name TEXT NOT NULL DEFAULT '',
            azimuth_deg REAL, elevation_deg REAL, distance_m REAL,
            source_type TEXT NOT NULL DEFAULT 'unknown',
            provenance TEXT NOT NULL DEFAULT 'unknown',
            review TEXT NOT NULL DEFAULT 'unreviewed',
            notes TEXT NOT NULL DEFAULT '',
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(subject_id) REFERENCES mv_subjects(id) ON DELETE CASCADE,
            UNIQUE(subject_id, path))""")
        conn.execute("CREATE INDEX IF NOT EXISTS mv_subject_project ON mv_subjects(project_id)")
        conn.execute("CREATE INDEX IF NOT EXISTS mv_capture_subject ON mv_captures(project_id, subject_id)")
        return conn

    def active_project(project_id):
        if not identifier(project_id) or not projects.is_file():
            return False
        with closing(sqlite3.connect(projects, timeout=5)) as conn:
            return conn.execute(
                "SELECT 1 FROM projects WHERE id=? AND archived=0",
                (project_id,)).fetchone() is not None

    def allowed(mutation=False):
        if request.remote_addr not in ("127.0.0.1", "::1"):
            return False
        return not mutation or valid_origin()

    def payload():
        if request.mimetype != "application/json" or not (
                request.content_length is not None and 0 < request.content_length <= 6000):
            raise ValueError("JSON body is missing or too large")
        body = request.get_json(silent=True)
        if not isinstance(body, dict):
            raise ValueError("Expected JSON object")
        return body

    def not_found():
        return jsonify(error="Multiview record not found"), 404

    def validate_fields(body, creation=False):
        result = {}
        for label, low, high in (
                ("azimuth_deg", 0, 359.9999),
                ("elevation_deg", -90, 90),
                ("distance_m", 0.0001, 1_000_000)):
            if label in body:
                result[label] = coordinate(body[label], low, high, label)
        for label in ("source_type", "provenance", "review"):
            if label in body:
                options = {"source_type": SOURCE_TYPES, "provenance": PROVENANCES,
                           "review": REVIEWS}[label]
                if body[label] not in options:
                    raise ValueError("Invalid " + label)
                result[label] = body[label]
        for label, limit in (("view_name", 100), ("notes", 1000)):
            if label in body:
                result[label] = text_field(body[label], limit)
        return result

    @app.route("/api/workspace/multiview/projects/<project_id>/subjects", methods=["GET", "POST"])
    def multiview_subjects(project_id):
        if not allowed(request.method == "POST"):
            return jsonify(error="Local same-origin access required"), 403
        if not active_project(project_id):
            return not_found()
        if request.method == "GET":
            with closing(connect()) as conn:
                rows = conn.execute(
                    "SELECT s.*, COUNT(c.id) AS capture_count FROM mv_subjects s "
                    "LEFT JOIN mv_captures c ON c.subject_id=s.id "
                    "WHERE s.project_id=? GROUP BY s.id ORDER BY s.updated_at DESC,s.name COLLATE NOCASE",
                    (project_id,)).fetchall()
            return jsonify(subjects=[dict(row) for row in rows])
        try:
            body = payload()
            name = text_field(body.get("name"), 120, required=True)
            notes = text_field(body.get("notes", ""), 1000)
            subject_id = uuid.uuid4().hex
            with closing(connect()) as conn, conn:
                conn.execute("INSERT INTO mv_subjects(id,project_id,name,notes) VALUES (?,?,?,?)",
                             (subject_id, project_id, name, notes))
            return jsonify(id=subject_id, name=name), 201
        except sqlite3.IntegrityError:
            return jsonify(error="Subject name is already used in this project"), 409
        except ValueError as exc:
            return jsonify(error=str(exc)), 400

    @app.route("/api/workspace/multiview/projects/<project_id>/subjects/<subject_id>",
               methods=["PATCH", "DELETE"])
    def multiview_subject(project_id, subject_id):
        if not allowed(True):
            return jsonify(error="Local same-origin access required"), 403
        if not active_project(project_id) or not identifier(subject_id):
            return not_found()
        try:
            with closing(connect()) as conn, conn:
                if request.method == "DELETE":
                    row = conn.execute(
                        "DELETE FROM mv_subjects WHERE id=? AND project_id=? RETURNING id",
                        (subject_id, project_id)).fetchone()
                else:
                    body = payload()
                    if not any(k in body for k in ("name", "notes")):
                        raise ValueError("No editable fields supplied")
                    changes = {}
                    if "name" in body:
                        changes["name"] = text_field(body["name"], 120, required=True)
                    if "notes" in body:
                        changes["notes"] = text_field(body["notes"], 1000)
                    assignments = ",".join(k+"=?" for k in changes)
                    row = conn.execute("UPDATE mv_subjects SET "+assignments+
                        ",updated_at=CURRENT_TIMESTAMP WHERE id=? AND project_id=? RETURNING id",
                        (*changes.values(), subject_id, project_id)).fetchone()
            return jsonify(ok=True) if row else not_found()
        except sqlite3.IntegrityError:
            return jsonify(error="Subject name already exists"), 409
        except ValueError as exc:
            return jsonify(error=str(exc)), 400

    @app.route("/api/workspace/multiview/projects/<project_id>/subjects/<subject_id>/captures",
               methods=["GET", "POST"])
    def multiview_captures(project_id, subject_id):
        if not allowed(request.method == "POST"):
            return jsonify(error="Local same-origin access required"), 403
        if not active_project(project_id) or not identifier(subject_id):
            return not_found()
        with closing(connect()) as conn:
            exists = conn.execute("SELECT 1 FROM mv_subjects WHERE id=? AND project_id=?",
                                  (subject_id, project_id)).fetchone()
        if not exists:
            return not_found()
        if request.method == "GET":
            q = request.args.get("q", "").strip()
            source_type = request.args.get("source", "")
            sort = request.args.get("sort", "newest")
            if len(q) > 120 or source_type not in SOURCE_TYPES | {""} or sort not in (
                    "newest", "oldest", "name", "azimuth", "distance"):
                return jsonify(error="Invalid search/filter"), 400
            try:
                offset = int(request.args.get("offset", 0))
            except ValueError:
                return jsonify(error="Invalid offset"), 400
            if not 0 <= offset <= 100000:
                return jsonify(error="Invalid offset"), 400
            where = ["project_id=?", "subject_id=?"]
            args = [project_id, subject_id]
            if source_type:
                where.append("source_type=?")
                args.append(source_type)
            if q:
                where.append("(view_name LIKE ? ESCAPE '\\' OR name LIKE ? ESCAPE '\\' OR notes LIKE ? ESCAPE '\\')")
                escaped = q.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
                args.extend(("%"+escaped+"%",)*3)
            clause = " AND ".join(where)
            ordering = {
                "newest": "created_at DESC,id DESC", "oldest": "created_at ASC,id ASC",
                "name": "view_name COLLATE NOCASE ASC,id ASC",
                "azimuth": "azimuth_deg IS NULL,azimuth_deg ASC,id ASC",
                "distance": "distance_m IS NULL,distance_m ASC,id ASC"
            }[sort]
            with closing(connect()) as conn:
                count = conn.execute("SELECT COUNT(*) FROM mv_captures WHERE "+clause, args).fetchone()[0]
                rows = conn.execute("SELECT * FROM mv_captures WHERE "+clause+
                    " ORDER BY "+ordering+" LIMIT 60 OFFSET ?", (*args,offset)).fetchall()
            return jsonify(total=count, captures=[dict(row) for row in rows])
        try:
            body = payload()
            source = source_path(body.get("path"))
            meta = validate_fields(body, creation=True)
            props = inspect_image(source)
            capture_id = uuid.uuid4().hex
            fields = dict(id=capture_id, project_id=project_id, subject_id=subject_id,
                          path=str(source), name=source.name, **props, **meta)
            with closing(connect()) as conn, conn:
                keys = ",".join(fields)
                conn.execute("INSERT INTO mv_captures("+keys+") VALUES ("+
                             ",".join("?" for _ in fields)+")", tuple(fields.values()))
                conn.execute("UPDATE mv_subjects SET updated_at=CURRENT_TIMESTAMP WHERE id=?",
                             (subject_id,))
            return jsonify(id=capture_id, **props), 201
        except sqlite3.IntegrityError:
            return jsonify(error="This photograph is already linked to this subject"), 409
        except (OSError, ValueError) as exc:
            return jsonify(error=str(exc) if isinstance(exc, ValueError)
                           else "Cannot read source image"), 400

    @app.route("/api/workspace/multiview/projects/<project_id>/captures/<capture_id>",
               methods=["PATCH", "DELETE"])
    def multiview_capture(project_id, capture_id):
        if not allowed(True):
            return jsonify(error="Local same-origin access required"), 403
        if not active_project(project_id) or not identifier(capture_id):
            return not_found()
        try:
            with closing(connect()) as conn, conn:
                if request.method == "DELETE":
                    row = conn.execute("DELETE FROM mv_captures WHERE id=? AND project_id=? RETURNING id",
                                       (capture_id, project_id)).fetchone()
                else:
                    body = payload()
                    fields = validate_fields(body)
                    if not fields:
                        raise ValueError("No editable metadata supplied")
                    assignments = ",".join(k+"=?" for k in fields)
                    row = conn.execute("UPDATE mv_captures SET "+assignments+
                        ",updated_at=CURRENT_TIMESTAMP WHERE id=? AND project_id=? RETURNING id",
                        (*fields.values(),capture_id,project_id)).fetchone()
            return jsonify(ok=True) if row else not_found()
        except ValueError as exc:
            return jsonify(error=str(exc)), 400

    @app.get("/api/workspace/multiview/projects/<project_id>/captures/<capture_id>/preview")
    def multiview_preview(project_id, capture_id):
        if not allowed() or not active_project(project_id) or not identifier(capture_id):
            return not_found() if allowed() else (jsonify(error="Local-only image preview"),403)
        with closing(connect()) as conn:
            row = conn.execute("SELECT path,sha256,bytes,format FROM mv_captures "
                               "WHERE project_id=? AND id=?", (project_id,capture_id)).fetchone()
        if not row:
            return not_found()
        try:
            path = source_path(row["path"])
            if path.stat().st_size != row["bytes"]:
                return jsonify(error="Original image changed; reimport the reference"), 409
            digest = hashlib.sha256()
            with path.open("rb") as stream:
                for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                    digest.update(chunk)
            if digest.hexdigest() != row["sha256"]:
                return jsonify(error="Original image changed; reimport the reference"), 409
            mime = {"PNG":"image/png","JPEG":"image/jpeg","WEBP":"image/webp","BMP":"image/bmp"}[row["format"]]
            return send_file(path,mimetype=mime,conditional=True,max_age=0)
        except (ValueError, OSError, KeyError):
            return jsonify(error="Image is missing, inaccessible or unsafe"), 404
