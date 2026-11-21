"""Checkpoint ratings and curated trained LoRA library (local-only metadata)."""
import sqlite3
import base64
import binascii
import hashlib
import os
import tempfile
from contextlib import closing
from pathlib import Path
from flask import jsonify, request, send_file
from project_checkpoints import inventory

FIELDS = ("duration_minutes", "gpu_vram_gb", "peak_vram_gb", "peak_ram_gb")

def db_path(base):
    return Path(base) / "settings" / "orkilab" / "checkpoint_reviews.sqlite3"

def connect(base):
    path = db_path(base)
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path, timeout=10)
    conn.row_factory = sqlite3.Row
    conn.execute("""CREATE TABLE IF NOT EXISTS reviews (
        project_id TEXT NOT NULL, filename TEXT NOT NULL,
        rating INTEGER CHECK (rating BETWEEN 1 AND 5),
        notes TEXT NOT NULL DEFAULT '',
        is_final INTEGER NOT NULL DEFAULT 0 CHECK (is_final IN (0,1)),
        updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
        PRIMARY KEY(project_id,filename))""")
    columns = {row["name"] for row in conn.execute("PRAGMA table_info(reviews)")}
    extras = {
        "is_best": "INTEGER NOT NULL DEFAULT 0",
        "base_model": "TEXT NOT NULL DEFAULT ''",
        "workflow_id": "TEXT NOT NULL DEFAULT ''",
        "workflow_name": "TEXT NOT NULL DEFAULT ''",
        "duration_minutes": "REAL",
        "gpu_name": "TEXT NOT NULL DEFAULT ''",
        "gpu_vram_gb": "REAL",
        "peak_vram_gb": "REAL",
        "peak_ram_gb": "REAL",
        "metrics_source": "TEXT NOT NULL DEFAULT 'not_recorded'",
        "reference_ext": "TEXT NOT NULL DEFAULT ''"
    }
    for key, definition in extras.items():
        if key not in columns:
            conn.execute(f"ALTER TABLE reviews ADD COLUMN {key} {definition}")
    conn.execute("CREATE UNIQUE INDEX IF NOT EXISTS one_final_per_project ON reviews(project_id) WHERE is_final=1")
    conn.commit()
    return conn

def get_reviews(base, project_id):
    names = {c["name"] for c in inventory(base,project_id)["checkpoints"]}
    with closing(connect(base)) as conn:
        rows = conn.execute("SELECT * FROM reviews WHERE project_id=?", (project_id,)).fetchall()
    return {r["filename"]: dict(r) | {"is_best":bool(r["is_best"]),"is_final":bool(r["is_final"])}
            for r in rows if r["filename"] in names}

def catalog(base):
    with closing(connect(base)) as conn:
        rows = conn.execute("SELECT * FROM reviews WHERE is_best=1 OR is_final=1 ORDER BY is_final DESC,updated_at DESC").fetchall()
    models = []
    for r in rows:
        try:
            project = inventory(base,r["project_id"])
        except (LookupError,ValueError):
            continue
        checkpoint = next((c for c in project["checkpoints"] if c["name"]==r["filename"]), None)
        if checkpoint is None:
            continue
        result = dict(r)
        result["reference_url"] = ("/api/workspace/trained-loras/reference/" + r["project_id"] + "/" + r["filename"]) if r["reference_ext"] else None
        result.update(project_name=project["project_name"],engine=project["engine"],
            step=checkpoint["step"],comfy_name=checkpoint["comfy_name"],
            size_bytes=checkpoint["size_bytes"],
            source_path=str(Path(project["output_folder"])/r["filename"]),
            is_best=bool(r["is_best"]),is_final=bool(r["is_final"]))
        models.append(result)
    return models

def reference_file(base, project_id, filename, extension):
    if extension not in (".png", ".jpg", ".webp"):
        raise ValueError("Invalid image format")
    key = hashlib.sha256((project_id + ":" + filename).encode("utf-8")).hexdigest()
    return Path(base) / "settings" / "orkilab" / "lora_references" / (key + extension)

def image_extension(data):
    if data.startswith(b"\x89PNG\r\n\x1a\n") and len(data) >= 24:
        return ".png"
    if data.startswith(b"\xff\xd8\xff") and data.endswith(b"\xff\xd9"):
        return ".jpg"
    if len(data) >= 16 and data[:4] == b"RIFF" and data[8:12] == b"WEBP":
        return ".webp"
    raise ValueError("Use a valid PNG, JPEG or WebP reference image")

def set_reference_image(base, project_id, filename, encoded):
    # Explicitly chosen reference, not an assumed training image or generated preview.
    valid = {c["name"] for c in inventory(base, project_id)["checkpoints"]}
    if not isinstance(filename, str) or filename not in valid:
        raise ValueError("Unknown project checkpoint")
    if not isinstance(encoded, str) or len(encoded) > 3_000_000:
        raise ValueError("Reference image exceeds size limit")
    try:
        content = base64.b64decode(encoded, validate=True)
    except (binascii.Error,ValueError):
        raise ValueError("Invalid reference image data")
    if not 0 < len(content) <= 2_000_000:
        raise ValueError("Maximum image size is 2 MB")
    extension = image_extension(content)
    with closing(connect(base)) as conn:
        row = conn.execute("SELECT is_best,is_final,reference_ext FROM reviews WHERE project_id=? AND filename=?",
                           (project_id, filename)).fetchone()
        if row is None or not (row["is_best"] or row["is_final"]):
            raise ValueError("First mark this checkpoint Best or Final")
        dest = reference_file(base, project_id, filename, extension)
        dest.parent.mkdir(parents=True, exist_ok=True)
        if dest.parent.is_symlink():
            raise ValueError("Reference directory cannot be a symbolic link")
        tmp = None
        try:
            with tempfile.NamedTemporaryFile(dir=dest.parent, delete=False) as handle:
                tmp = Path(handle.name)
                handle.write(content)
            os.replace(tmp, dest)
            with conn:
                conn.execute("UPDATE reviews SET reference_ext=?,updated_at=CURRENT_TIMESTAMP WHERE project_id=? AND filename=?",
                             (extension, project_id, filename))
        finally:
            if tmp is not None:
                tmp.unlink(missing_ok=True)
        old = row["reference_ext"]
        if old and old != extension:
            reference_file(base, project_id, filename, old).unlink(missing_ok=True)
    return extension

def workflow_name(base, workflow_id):
    if not workflow_id:
        return ""
    path = Path(base)/"settings"/"orkilab"/"workflows.sqlite3"
    if not path.is_file():
        raise ValueError("Selected workflow is unavailable")
    with closing(sqlite3.connect(path)) as conn:
        row = conn.execute("SELECT name FROM workflows WHERE id=?", (workflow_id,)).fetchone()
    if not row:
        raise ValueError("Selected workflow is unavailable")
    return str(row[0])[:200]

def save_review(base,project_id,filename,rating=None,notes="",is_best=False,is_final=False,
                base_model="",workflow_id="",duration_minutes=None,gpu_name="",
                gpu_vram_gb=None,peak_vram_gb=None,peak_ram_gb=None):
    data=inventory(base,project_id)
    if not isinstance(filename,str) or filename not in {c["name"] for c in data["checkpoints"]}:
        raise ValueError("Checkpoint is not in this project")
    if rating is not None and (type(rating) is not int or not 1 <= rating <= 5):
        raise ValueError("Rating must be 1-5 or empty")
    if type(is_best) is not bool or type(is_final) is not bool:
        raise ValueError("Best/final must be booleans")
    for value,limit in ((notes,1000),(base_model,200),(workflow_id,100),(gpu_name,200)):
        if not isinstance(value,str) or len(value)>limit or any(ord(c)<32 and c not in "\n\t" for c in value):
            raise ValueError("Invalid text metadata")
    for value in (duration_minutes,gpu_vram_gb,peak_vram_gb,peak_ram_gb):
        if value is not None and (type(value) not in (int,float) or not 0 <= value <= 100000):
            raise ValueError("Invalid hardware or duration measurement")
    wf_name=workflow_name(base,workflow_id)
    with closing(connect(base)) as conn:
        with conn:
            if is_final:
                conn.execute("UPDATE reviews SET is_final=0 WHERE project_id=? AND is_final=1",(project_id,))
            conn.execute("""INSERT INTO reviews(project_id,filename,rating,notes,is_best,is_final,base_model,
                workflow_id,workflow_name,duration_minutes,gpu_name,gpu_vram_gb,peak_vram_gb,peak_ram_gb,metrics_source)
                VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
                ON CONFLICT(project_id,filename) DO UPDATE SET
                rating=excluded.rating,notes=excluded.notes,is_best=excluded.is_best,
                is_final=excluded.is_final,base_model=excluded.base_model,workflow_id=excluded.workflow_id,
                workflow_name=excluded.workflow_name,duration_minutes=excluded.duration_minutes,
                gpu_name=excluded.gpu_name,gpu_vram_gb=excluded.gpu_vram_gb,
                peak_vram_gb=excluded.peak_vram_gb,peak_ram_gb=excluded.peak_ram_gb,
                metrics_source=excluded.metrics_source,updated_at=CURRENT_TIMESTAMP""",
                (project_id,filename,rating,notes,int(is_best),int(is_final),base_model,
                 workflow_id,wf_name,duration_minutes,gpu_name,gpu_vram_gb,peak_vram_gb,peak_ram_gb,
                 "user_supplied" if any(x is not None for x in (duration_minutes,gpu_vram_gb,peak_vram_gb,peak_ram_gb)) or gpu_name else "not_recorded"))
    return get_reviews(base,project_id)

def register(app,base):
    base=Path(base)
    @app.get("/api/workspace/trained-loras")
    def trained_lora_catalog():
        if request.remote_addr not in ("127.0.0.1","::1"):
            return jsonify(error="LoRA catalog is local-only"),403
        return jsonify(models=catalog(base))

    @app.post("/api/workspace/trained-loras/reference/<project_id>")
    def save_trained_lora_reference(project_id):
        if request.remote_addr not in ("127.0.0.1","::1"):
            return jsonify(error="LoRA references are local-only"),403
        if request.mimetype != "application/json" or not 0 < (request.content_length or 0) <= 3_100_000:
            return jsonify(error="Reference image too large or invalid"),400
        data=request.get_json(silent=True)
        if not isinstance(data,dict):
            return jsonify(error="Invalid request"),400
        try:
            ext=set_reference_image(base,project_id,data.get("filename"),data.get("image_base64"))
            return jsonify(ok=True,format=ext)
        except (ValueError,LookupError) as exc:
            return jsonify(error=str(exc)),400
        except OSError:
            return jsonify(error="Could not save reference image"),500

    @app.get("/api/workspace/trained-loras/reference/<project_id>/<path:filename>")
    def read_trained_lora_reference(project_id,filename):
        if request.remote_addr not in ("127.0.0.1","::1"):
            return jsonify(error="LoRA references are local-only"),403
        try:
            valid={c["name"] for c in inventory(base,project_id)["checkpoints"]}
            if filename not in valid:
                return jsonify(error="Reference not found"),404
            with closing(connect(base)) as conn:
                row=conn.execute("SELECT reference_ext,is_best,is_final FROM reviews WHERE project_id=? AND filename=?",
                                 (project_id,filename)).fetchone()
            if not row or not (row["is_best"] or row["is_final"]) or not row["reference_ext"]:
                return jsonify(error="Reference not found"),404
            path=reference_file(base,project_id,filename,row["reference_ext"])
            if path.is_symlink() or not path.is_file():
                return jsonify(error="Reference not found"),404
            mimetype={".png":"image/png",".jpg":"image/jpeg",".webp":"image/webp"}[row["reference_ext"]]
            return send_file(path,mimetype=mimetype,conditional=True,max_age=0)
        except (ValueError,LookupError,KeyError):
            return jsonify(error="Reference not found"),404

    @app.get("/api/workspace/projects/<project_id>/checkpoints/reviews")
    def reviews_get(project_id):
        if request.remote_addr not in ("127.0.0.1","::1"):
            return jsonify(error="Checkpoint reviews are local-only"),403
        try:
            return jsonify(reviews=get_reviews(base,project_id))
        except LookupError as exc:
            return jsonify(error=str(exc)),404
        except ValueError as exc:
            return jsonify(error=str(exc)),400

    @app.post("/api/workspace/projects/<project_id>/checkpoints/reviews")
    def reviews_post(project_id):
        if request.remote_addr not in ("127.0.0.1","::1"):
            return jsonify(error="Checkpoint reviews are local-only"),403
        if request.mimetype!="application/json" or not 0<(request.content_length or 0)<=4096:
            return jsonify(error="Invalid request"),400
        data=request.get_json(silent=True)
        if not isinstance(data,dict):
            return jsonify(error="Invalid request"),400
        try:
            allowed=("filename","rating","notes","is_best","is_final","base_model","workflow_id",
                     "duration_minutes","gpu_name","gpu_vram_gb","peak_vram_gb","peak_ram_gb")
            args={k:data[k] for k in allowed if k in data}
            return jsonify(reviews=save_review(base,project_id,**args))
        except (LookupError,ValueError,TypeError) as exc:
            return jsonify(error=str(exc)),400
