"""Safely stage real Multiview reference photos in the configured private ComfyUI.

This is an explicit, local-only upload, NOT a generation action. The actual
ComfyUI job is prepared/validated/submitted through OrkiLab's existing
generation endpoints. Original photo bytes and Multiview records are untouched.
"""
import hashlib
import json
import sqlite3
import uuid
from contextlib import closing
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, build_opener, ProxyHandler

from flask import jsonify, request

from comfyui_connect import validate_settings, DEFAULT_SETTINGS, NoRedirect
from dataset_studio import valid_origin
from multiview_studio import identifier, source_path, MAX_IMAGE_BYTES

MAX_REFERENCES = 4
MAX_RESPONSE = 16384
SUPPORTED = {".png": "image/png", ".jpg": "image/jpeg",
             ".jpeg": "image/jpeg", ".webp": "image/webp"}


def multipart_image(filename, data, mime):
    boundary = "orkilab" + uuid.uuid4().hex
    def header(value):
        return value.encode("ascii")
    prefix = (
        "--" + boundary + "\r\n"
        + 'Content-Disposition: form-data; name="image"; filename="' + filename + '"\r\n'
        + "Content-Type: " + mime + "\r\n\r\n"
    ).encode("ascii")
    suffix = ("\r\n--" + boundary
              + '\r\nContent-Disposition: form-data; name="type"\r\n\r\ninput'
              + "\r\n--" + boundary
              + '\r\nContent-Disposition: form-data; name="overwrite"\r\n\r\nfalse'
              + "\r\n--" + boundary + "--\r\n").encode("ascii")
    return prefix + data + suffix, "multipart/form-data; boundary=" + boundary


def upload_reference(url, filename, data, mime):
    body, content_type = multipart_image(filename, data, mime)
    req = Request(url + "/upload/image", data=body, method="POST",
                  headers={"Content-Type": content_type})
    with build_opener(ProxyHandler({}), NoRedirect()).open(req, timeout=40) as response:
        if response.status != 200:
            raise ValueError("ComfyUI rejected image upload")
        payload = response.read(MAX_RESPONSE + 1)
    if len(payload) > MAX_RESPONSE:
        raise ValueError("ComfyUI upload response too large")
    result = json.loads(payload)
    if not isinstance(result, dict) or result.get("type") != "input":
        raise ValueError("ComfyUI did not confirm an input image")
    returned = result.get("name")
    subfolder = result.get("subfolder", "")
    if not isinstance(returned, str) or not returned or len(returned) > 200:
        raise ValueError("Invalid ComfyUI image name")
    if ("/" in returned or "\\" in returned or ":" in returned
            or returned in (".", "..")):
        raise ValueError("Unsafe ComfyUI upload filename")
    if not isinstance(subfolder, str) or len(subfolder) > 200:
        raise ValueError("Invalid ComfyUI subfolder")
    segments = subfolder.replace("\\", "/").split("/") if subfolder else []
    if any(x in (".", "..", "") for x in segments) or ":" in subfolder:
        raise ValueError("Unsafe ComfyUI subfolder")
    return "/".join([*segments, returned])


def register(app, base):
    root = Path(base) / "settings" / "orkilab"
    projects_db = root / "projects.sqlite3"
    captures_db = root / "multiview.sqlite3"
    comfy_config = root / "comfyui.json"

    @app.post("/api/workspace/multiview/projects/<project_id>/subjects/<subject_id>/reference-upload")
    def multiview_upload_references(project_id, subject_id):
        if request.remote_addr not in ("127.0.0.1", "::1") or not valid_origin():
            return jsonify(error="Local same-origin access required"), 403
        if not identifier(project_id) or not identifier(subject_id):
            return jsonify(error="Subject not found"), 404
        if request.mimetype != "application/json" or not 0 < (request.content_length or 0) <= 2048:
            return jsonify(error="Invalid reference upload request"), 400
        body = request.get_json(silent=True)
        ids = body.get("capture_ids") if isinstance(body, dict) else None
        if (not isinstance(body, dict) or body.get("confirm") is not True
                or not isinstance(ids, list) or not 1 <= len(ids) <= MAX_REFERENCES
                or len(set(ids)) != len(ids) or any(not identifier(x) for x in ids)):
            return jsonify(error="Explicitly select 1-4 distinct reference photographs"), 400
        if not projects_db.is_file() or not captures_db.is_file():
            return jsonify(error="Project or subject not found"), 404
        with closing(sqlite3.connect(projects_db, timeout=5)) as conn:
            active = conn.execute(
                "SELECT 1 FROM projects WHERE id=? AND archived=0 AND category='image'",
                (project_id,)).fetchone()
        if not active:
            return jsonify(error="Active image project not found"), 404
        with closing(sqlite3.connect(captures_db, timeout=5)) as conn:
            marks = ",".join("?" for _ in ids)
            subject = conn.execute(
                "SELECT 1 FROM mv_subjects WHERE id=? AND project_id=?",
                (subject_id, project_id)).fetchone()
            rows = conn.execute(
                "SELECT id,path,sha256,bytes,source_type,review FROM mv_captures "
                "WHERE project_id=? AND subject_id=? AND id IN ("+marks+")",
                (project_id, subject_id, *ids)).fetchall()
        if not subject or len(rows) != len(ids):
            return jsonify(error="Reference does not belong to the selected subject"), 404
        by_id = {r[0]: r for r in rows}
        if any(by_id[x][4] not in ("real_photo", "unknown", "video_frame")
               or by_id[x][5] == "rejected" for x in ids):
            return jsonify(error="Only real, non-rejected reference images are allowed"), 400
        try:
            cfg = validate_settings(json.loads(comfy_config.read_text(encoding="utf-8")),
                                    DEFAULT_SETTINGS)
            if cfg["mode"] == "native":
                return jsonify(error="Connect ComfyUI before staging references"), 409
            # Validate ALL files before the first upload to avoid sending a partial
            # selection due to a missing/changed original.
            safe = []
            for capture_id in ids:
                row = by_id[capture_id]
                path = source_path(row[1])
                mime = SUPPORTED.get(path.suffix.lower())
                if not mime or path.stat().st_size != row[3] or row[3] > MAX_IMAGE_BYTES:
                    raise ValueError("Unsupported or changed source image")
                data = path.read_bytes()
                if hashlib.sha256(data).hexdigest() != row[2]:
                    raise ValueError("Original image has changed")
                # ComfyUI's input folder receives copies, never source file moves.
                ext = ".jpg" if path.suffix.lower() == ".jpeg" else path.suffix.lower()
                name = "orkilab_" + capture_id + "_" + row[2][:16] + ext
                safe.append((capture_id, name, data, mime))
            uploaded = []
            for capture_id, name, data, mime in safe:
                server_name = upload_reference(cfg["url"], name, data, mime)
                uploaded.append({"capture_id": capture_id, "comfy_name": server_name})
            return jsonify(references=uploaded, endpoint=cfg["url"],
                           note="Reference copies staged. No generation has been submitted."), 200
        except (OSError, ValueError, TypeError, json.JSONDecodeError,
                HTTPError, URLError) as exc:
            app.logger.warning("Multiview ComfyUI reference upload failed: %s", str(exc)[:160])
            return jsonify(error="Could not stage all reference photos; generation not started",
                           detail=str(exc)[:160]), 502
