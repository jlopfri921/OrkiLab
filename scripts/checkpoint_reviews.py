"""Human checkpoint reviews, scoped to a project; does not alter training outputs."""
import sqlite3
from contextlib import closing
from pathlib import Path
from flask import jsonify, request
from project_checkpoints import inventory

def db_path(base):
    return Path(base) / "settings" / "orkilab" / "checkpoint_reviews.sqlite3"

def connect(base):
    path = db_path(base)
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path, timeout=10)
    conn.execute("""CREATE TABLE IF NOT EXISTS reviews (
        project_id TEXT NOT NULL,
        filename TEXT NOT NULL,
        rating INTEGER CHECK (rating BETWEEN 1 AND 5),
        notes TEXT NOT NULL DEFAULT '',
        is_final INTEGER NOT NULL DEFAULT 0 CHECK (is_final IN (0,1)),
        updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
        PRIMARY KEY (project_id, filename)
    )""")
    conn.execute("CREATE UNIQUE INDEX IF NOT EXISTS one_final_per_project ON reviews(project_id) WHERE is_final=1")
    return conn

def get_reviews(base, project_id):
    checkpoints = inventory(base, project_id)["checkpoints"]
    names = {c["name"] for c in checkpoints}
    with closing(connect(base)) as conn:
        rows = conn.execute("SELECT filename,rating,notes,is_final FROM reviews WHERE project_id=?",
                            (project_id,)).fetchall()
    return {n: {"rating": r, "notes": note, "is_final": bool(final)}
            for n, r, note, final in rows if n in names}

def save_review(base, project_id, filename, rating, notes, is_final):
    valid = {c["name"] for c in inventory(base, project_id)["checkpoints"]}
    if filename not in valid:
        raise ValueError("Checkpoint is not in the selected project")
    if rating is not None and (type(rating) is not int or not 1 <= rating <= 5):
        raise ValueError("Rating must be 1 to 5 or empty")
    if not isinstance(notes, str) or len(notes) > 1000 or any(ord(c) < 32 and c not in "\n\t" for c in notes):
        raise ValueError("Notes must be text of up to 1000 characters")
    if type(is_final) is not bool:
        raise ValueError("Final selection must be true or false")
    with closing(connect(base)) as conn:
        with conn:
            if is_final:
                conn.execute("UPDATE reviews SET is_final=0,updated_at=CURRENT_TIMESTAMP WHERE project_id=? AND is_final=1", (project_id,))
            conn.execute("""INSERT INTO reviews(project_id,filename,rating,notes,is_final)
                VALUES(?,?,?,?,?) ON CONFLICT(project_id,filename) DO UPDATE SET
                rating=excluded.rating,notes=excluded.notes,is_final=excluded.is_final,updated_at=CURRENT_TIMESTAMP""",
                (project_id,filename,rating,notes,is_final))
    return get_reviews(base, project_id)

def register(app, base):
    @app.get("/api/workspace/projects/<project_id>/checkpoints/reviews")
    def checkpoint_reviews(project_id):
        if request.remote_addr not in ("127.0.0.1", "::1"):
            return jsonify(error="Checkpoint reviews are local-only"), 403
        try:
            return jsonify(reviews=get_reviews(base,project_id))
        except LookupError as e:
            return jsonify(error=str(e)),404
        except ValueError as e:
            return jsonify(error=str(e)),400

    @app.post("/api/workspace/projects/<project_id>/checkpoints/reviews")
    def checkpoint_review_update(project_id):
        if request.remote_addr not in ("127.0.0.1", "::1"):
            return jsonify(error="Checkpoint reviews are local-only"),403
        if request.mimetype != "application/json" or not 0 < (request.content_length or 0) <= 4096:
            return jsonify(error="Invalid request"),400
        body = request.get_json(silent=True)
        if not isinstance(body,dict):
            return jsonify(error="Invalid request"),400
        try:
            return jsonify(reviews=save_review(base,project_id,body.get("filename"),
                body.get("rating"),body.get("notes",""),body.get("is_final",False)))
        except LookupError as e:
            return jsonify(error=str(e)),404
        except ValueError as e:
            return jsonify(error=str(e)),400
