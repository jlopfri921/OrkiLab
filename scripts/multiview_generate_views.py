"""Safely stage real Multiview reference photos in the configured private ComfyUI.

This is an explicit, local-only upload, NOT a generation action. The actual
ComfyUI job is prepared/validated/submitted through OrkiLab's existing
generation endpoints. Original photo bytes and Multiview records are untouched.
"""
import hashlib
import os
import tempfile
import threading
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


def validate_input_folder(raw):
    """Restrict manual local copies to an existing ComfyUI input directory."""
    if (not isinstance(raw, str) or not 1 <= len(raw) <= 1024
            or any(ord(char) < 32 for char in raw)):
        raise ValueError("Specify an existing ComfyUI input directory")
    # Never treat a UNC/network share as a local folder, including on Windows.
    value = raw.strip()
    if value.startswith(("\\\\", "//")):
        raise ValueError("Network shares are not supported for local input copies")
    folder = Path(value).expanduser()
    if not folder.is_absolute() or folder.name.lower() != "input":
        raise ValueError("Choose the input folder itself, not the ComfyUI root")
    if folder.is_symlink() or not folder.is_dir():
        raise ValueError("The ComfyUI input folder must already exist and cannot be a symlink")
    resolved = folder.resolve(strict=True)
    if resolved.name.lower() != "input":
        raise ValueError("Input folder does not match its resolved location")
    # ComfyUI may use a custom --input-directory elsewhere; do not assume
    # it must have models/output siblings. The explicit user selection controls this.
    return resolved


def copy_to_input(folder, filename, data):
    """Copy photo bytes only; never overwrite a file or move an original."""
    target = folder / filename
    # O_EXCL prevents preexisting file overwrites and blocks target symlinks.
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    if hasattr(os, "O_BINARY"):
        flags |= os.O_BINARY
    try:
        fd = os.open(target, flags, 0o600)
    except FileExistsError:
        # Existing identical copies are safe to reuse without modifying them.
        with target.open("rb") as saved:
            if saved.read(len(data) + 1) == data:
                return filename
        raise ValueError("A different file already uses this reference name")
    try:
        with os.fdopen(fd, "wb") as out:
            out.write(data)
    except BaseException:
        try:
            target.unlink(missing_ok=True)
        except OSError:
            pass
        raise
    return filename


def browse_local_input_folder():
    """Use the *launcher computer's* native OS folder dialog, not the browser picker."""
    import tkinter
    from tkinter import filedialog
    # No network/server-picker; the dialog is visible on the local desktop.
    root = tkinter.Tk()
    try:
        root.withdraw()
        root.attributes("-topmost", True)
        selection = filedialog.askdirectory(
            parent=root, title="Choose ComfyUI input folder", mustexist=True)
    finally:
        root.destroy()
    return selection


def register(app, base):
    root = Path(base) / "settings" / "orkilab"
    projects_db = root / "projects.sqlite3"
    captures_db = root / "multiview.sqlite3"
    comfy_config = root / "comfyui.json"
    input_pref = root / "multiview_input.json"
    picker_lock = threading.Lock()

    def local_only():
        return request.remote_addr in ("127.0.0.1", "::1") and valid_origin()

    @app.get("/api/workspace/multiview/comfyui-input")
    def multiview_input_info():
        if not local_only():
            return jsonify(error="Local same-origin access required"), 403
        folder = ""
        try:
            record = json.loads(input_pref.read_text(encoding="utf-8"))
            folder = record.get("path", "") if isinstance(record, dict) else ""
            if folder:
                validate_input_folder(folder)
        except (OSError, ValueError, TypeError):
            folder = ""
        return jsonify(path=folder)

    @app.post("/api/workspace/multiview/comfyui-input/browse")
    def multiview_input_browse():
        if not local_only():
            return jsonify(error="Local same-origin access required"), 403
        if request.mimetype != "application/json" or (request.content_length or 0) > 128:
            return jsonify(error="Invalid folder-picker request"), 400
        body = request.get_json(silent=True)
        if not isinstance(body, dict) or body.get("confirm") is not True:
            return jsonify(error="Folder selection requires confirmation"), 400
        try:
            cfg = validate_settings(json.loads(comfy_config.read_text(encoding="utf-8")),
                                    DEFAULT_SETTINGS)
            if cfg["mode"] == "native":
                return jsonify(error="ComfyUI is disabled in native mode"), 409
        except (OSError, ValueError, KeyError, TypeError):
            return jsonify(error="Configure ComfyUI first"), 409
        if not picker_lock.acquire(blocking=False):
            return jsonify(error="A folder dialog is already open"), 409
        try:
            selected = browse_local_input_folder()
            if not selected:
                return jsonify(cancelled=True, path="")
            folder = validate_input_folder(selected)
            return jsonify(cancelled=False, path=str(folder))
        except (OSError, ValueError, ImportError, RuntimeError) as exc:
            return jsonify(error="Could not open a folder dialog on the launcher PC",
                           detail=str(exc)[:160]), 422
        finally:
            picker_lock.release()


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
            method = body.get("transfer_mode", "api")
            if method not in ("api", "folder"):
                return jsonify(error="Unsupported reference transfer mode"), 400
            folder = None
            if method == "folder":
                folder = validate_input_folder(body.get("input_folder"))
            uploaded = []
            for capture_id, name, data, mime in safe:
                server_name = (copy_to_input(folder, name, data) if folder is not None
                               else upload_reference(cfg["url"], name, data, mime))
                uploaded.append({"capture_id": capture_id, "comfy_name": server_name})
            if folder is not None:
                # Successful local selection is remembered for the next visit.
                root.mkdir(parents=True, exist_ok=True)
                with tempfile.NamedTemporaryFile("w", encoding="utf-8",
                         dir=root, delete=False) as temp:
                    json.dump({"path": str(folder)}, temp)
                    temp_name = temp.name
                try:
                    os.replace(temp_name, input_pref)
                finally:
                    if os.path.exists(temp_name):
                        os.unlink(temp_name)
            return jsonify(references=uploaded, endpoint=cfg["url"],
                           transfer_mode=method,
                           input_folder=str(folder) if folder is not None else None,
                           note="Reference copies staged. No generation has been submitted."), 200
        except (OSError, ValueError, TypeError, json.JSONDecodeError,
                HTTPError, URLError) as exc:
            app.logger.warning("Multiview ComfyUI reference upload failed: %s", str(exc)[:160])
            return jsonify(error="Could not stage all reference photos; generation not started",
                           detail=str(exc)[:160]), 502
