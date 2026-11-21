"""Opt-in local Ollama vision suggestions for relative Multiview camera viewpoints.

Classifications are guesses, NOT measured geometry. No inference result is
persisted here; the user must explicitly review/edit and save metadata via
the existing Multiview capture PATCH endpoint. No original images are changed.
"""
import base64
import hashlib
import io
import json
import sqlite3
import threading
import urllib.error
from contextlib import closing
from pathlib import Path

from flask import jsonify, request
from PIL import Image, ImageOps, UnidentifiedImageError
from dataset_caption_vision import (
    MODEL_PATTERN, cloud_model_name, ollama_json, MAX_OLLAMA_JSON,
)
from dataset_studio import valid_origin
from multiview_studio import identifier, source_path

DIRECTIONS = {"front", "front_right", "right", "back_right", "back",
              "back_left", "left", "front_left", "top", "bottom", "unknown"}
ELEVATIONS = {"above", "level", "below", "unknown"}
DISTANCES = {"close", "medium", "far", "unknown"}
PROMPT = (
    "You are examining one photo of a single subject. Classify the CAMERA viewpoint "
    "relative to the visible subject, not absolute geographical direction. "
    "Without an established reference/front orientation, do not pretend to know "
    "exact azimuth or distance; choose 'unknown' when uncertain. "
    "Return ONLY a JSON object with string keys direction, elevation, distance, "
    "confidence. direction must be one of: front, front_right, right, "
    "back_right, back, back_left, left, front_left, top, bottom, unknown. "
    "elevation must be one of above, level, below, unknown. "
    "distance must be one of close, medium, far, unknown. "
    "confidence must be low, medium or high. No extra text. "
    "For ambiguous symmetrical objects, prefer unknown. "
    "These are qualitative guesses, not numeric measurements."
)
_lock = threading.Lock()


def parse_suggestion(raw):
    if not isinstance(raw, str) or len(raw) > 4096:
        raise ValueError("Invalid vision response")
    raw = raw.strip()
    if raw.startswith("```"):
        raw = raw.split("\n", 1)[-1].rsplit("```", 1)[0].strip()
    value = json.loads(raw)
    if not isinstance(value, dict):
        raise ValueError("Vision response is not an object")
    for key, options in (("direction", DIRECTIONS), ("elevation", ELEVATIONS),
                         ("distance", DISTANCES),
                         ("confidence", {"low", "medium", "high"})):
        if not isinstance(value.get(key), str) or value[key] not in options:
            raise ValueError("Vision response contains an unsupported viewpoint label")
    return {k: value[k] for k in ("direction", "elevation", "distance", "confidence")}


def thumbnail_for_local_vision(path):
    """Decode a bounded locally indexed image, never expose original bytes remotely."""
    with Image.open(path) as img:
        if img.width * img.height > 60_000_000:
            raise ValueError("Image dimensions exceed safety limit")
        if img.format not in {"JPEG", "PNG", "WEBP", "BMP"}:
            raise ValueError("Unsupported image format")
        thumb = ImageOps.exif_transpose(img)
        thumb.thumbnail((768, 768))
        if thumb.mode != "RGB":
            thumb = thumb.convert("RGB")
        output = io.BytesIO()
        thumb.save(output, "JPEG", quality=80)
        return base64.b64encode(output.getvalue()).decode("ascii")


def register(app, base):
    root = Path(base) / "settings" / "orkilab"
    projects_db = root / "projects.sqlite3"
    captures_db = root / "multiview.sqlite3"

    @app.post("/api/workspace/multiview/projects/<project_id>/captures/<capture_id>/viewpoint/suggest")
    def suggest_multiview_viewpoint(project_id, capture_id):
        if request.remote_addr not in ("127.0.0.1", "::1") or not valid_origin():
            return jsonify(error="Local same-origin access required"), 403
        if not identifier(project_id) or not identifier(capture_id):
            return jsonify(error="Capture not found"), 404
        if request.mimetype != "application/json" or not 0 < (request.content_length or 0) <= 2048:
            return jsonify(error="Invalid suggestion request"), 400
        body = request.get_json(silent=True)
        if not isinstance(body, dict) or body.get("confirm") is not True:
            return jsonify(error="Explicit local vision consent required"), 400
        model = body.get("model")
        if not isinstance(model, str) or not MODEL_PATTERN.fullmatch(model) or cloud_model_name(model):
            return jsonify(error="Choose an installed local vision model"), 400
        if not projects_db.is_file() or not captures_db.is_file():
            return jsonify(error="Project or capture not found"), 404
        with closing(sqlite3.connect(projects_db, timeout=5)) as db:
            active = db.execute(
                "SELECT 1 FROM projects WHERE id=? AND archived=0 AND category='image'",
                (project_id,)).fetchone()
        if not active:
            return jsonify(error="Active Image project not found"), 404
        with closing(sqlite3.connect(captures_db, timeout=5)) as db:
            capture = db.execute(
                "SELECT c.path,c.bytes,c.sha256 FROM mv_captures c "
                "JOIN mv_subjects s ON s.id=c.subject_id AND s.project_id=c.project_id "
                "WHERE c.project_id=? AND c.id=?",
                (project_id, capture_id)).fetchone()
        if not capture:
            return jsonify(error="Capture not found in project"), 404
        if not _lock.acquire(blocking=False):
            return jsonify(error="Another viewpoint analysis is running"), 409
        try:
            path = source_path(capture[0])
            # Original must match registered bytes before it can be sent to Ollama.
            if path.stat().st_size != capture[1]:
                return jsonify(error="Original image changed; re-link the capture"), 409
            checksum = hashlib.sha256()
            with path.open("rb") as image_file:
                for chunk in iter(lambda: image_file.read(1024 * 1024), b""):
                    checksum.update(chunk)
            if checksum.hexdigest() != capture[2]:
                return jsonify(error="Original image changed; re-link the capture"), 409
            model_info = ollama_json("/api/show", {"model": model}, timeout=5)
            caps = model_info.get("capabilities", []) if isinstance(model_info, dict) else []
            if "vision" not in caps:
                return jsonify(error="The selected local Ollama model has no vision capability"), 400
            encoded = thumbnail_for_local_vision(path)
            response = ollama_json("/api/generate", {
                "model": model, "prompt": PROMPT, "images": [encoded],
                "stream": False, "think": False, "keep_alive": "0",
                "format": "json", "options": {"num_predict": 180},
            }, timeout=120)
            suggestion = parse_suggestion(response.get("response") if isinstance(response, dict) else None)
            return jsonify(**suggestion, model=model, saved=False,
                           azimuth_deg=None, elevation_deg=None, distance_m=None,
                           provenance="estimated",
                           note="Unverified qualitative AI guess; no measured camera pose. Review before saving.")
        except (OSError, ValueError, TypeError, json.JSONDecodeError,
                urllib.error.URLError, urllib.error.HTTPError,
                TimeoutError, UnidentifiedImageError) as exc:
            app.logger.warning("Multiview viewpoint suggestion failed: %s", str(exc)[:160])
            return jsonify(error="Local viewpoint analysis failed; verify image, model and Ollama"), 502
        finally:
            _lock.release()
