"""Local workflow library. Import and inspect only; never execute a graph."""
import json
import os
import time
import hashlib
from contextlib import closing
import sqlite3
import uuid
from pathlib import Path
from flask import request, jsonify
from workflow_compatibility import assess_workflow

MAX_BYTES = 4_000_000
CATEGORIES = ("image", "video", "audio", "music", "3d", "other")
MODEL_EXT = (".safetensors", ".ckpt", ".gguf", ".pt", ".pth", ".bin", ".onnx")

def inspect_graph(graph):
    if not isinstance(graph, dict):
        raise ValueError("Invalid workflow JSON")
    if isinstance(graph.get("nodes"), list):
        fmt = "ui"
        nodes = graph["nodes"]
        key = "type"
    else:
        fmt = "api"
        nodes = list(graph.values())
        key = "class_type"
    if not nodes or len(nodes) > 2000 or any(not isinstance(n, dict) or not isinstance(n.get(key), str) or not n[key] for n in nodes):
        raise ValueError("Unsupported workflow format")
    if fmt == "api" and any(not isinstance(n.get("inputs"), dict) for n in nodes):
        raise ValueError("Unsupported workflow format")
    types, models = set(), set()
    for n in nodes:
        types.add(n[key][:300])
        inputs = n.get("inputs", {}) if fmt == "api" else n.get("widgets_values", [])
        values = inputs.values() if isinstance(inputs, dict) else inputs if isinstance(inputs, list) else []
        for value in values:
            if isinstance(value, str) and len(value) <= 1024 and value.lower().endswith(MODEL_EXT):
                models.add(value)
    return {"format": fmt, "node_count": len(nodes), "node_types": sorted(types),
            "model_references": sorted(models)}

def multiview_reference_profile(graph, category):
    """Conservative static Multiview eligibility. Final schema validation
    still happens in generation/prepare against the running ComfyUI."""
    if category != "image" or not isinstance(graph, dict):
        return {"likely_compatible": False, "image_inputs": 0,
                "has_prompt": False, "reason": "not_image"}
    image_inputs = 0
    has_prompt = False
    if isinstance(graph.get("nodes"), list):
        # UI workflow: links map origin IDs to downstream consumers.
        nodes = graph["nodes"]
        sources = {str(link[1]) for link in graph.get("links", [])
                   if isinstance(link, list) and len(link) >= 3}
        for node in nodes:
            if not isinstance(node, dict):
                continue
            kind = str(node.get("type", ""))
            if "LoadImage" in kind and str(node.get("id")) in sources:
                image_inputs += 1
            if any(x in kind.lower() for x in ("cliptextencode", "prompt", "textencode")):
                has_prompt = True
    else:
        connected = set()
        for node in graph.values():
            if not isinstance(node, dict):
                continue
            inputs = node.get("inputs", {})
            if isinstance(inputs, dict):
                for value in inputs.values():
                    if (isinstance(value, list) and len(value) == 2
                            and isinstance(value[0], (str, int))
                            and isinstance(value[1], int)):
                        connected.add(str(value[0]))
        for ident, node in graph.items():
            if not isinstance(node, dict):
                continue
            kind = str(node.get("class_type", ""))
            inputs = node.get("inputs", {})
            if "LoadImage" in kind and str(ident) in connected and isinstance(inputs, dict) and "image" in inputs:
                image_inputs += 1
            if isinstance(inputs, dict) and any(isinstance(value, str) and
                    any(term in key.lower() for term in ("text", "prompt"))
                    for key, value in inputs.items()):
                has_prompt = True
    return {"likely_compatible": bool(image_inputs and has_prompt),
            "image_inputs": image_inputs, "has_prompt": has_prompt,
            "reason": "candidate" if image_inputs and has_prompt else
                      ("no_connected_loadimage" if not image_inputs else "no_prompt")}


def register(app, base):
    path = Path(base) / "settings" / "orkilab" / "workflows.sqlite3"

    def db():
        path.parent.mkdir(parents=True, exist_ok=True)
        con = sqlite3.connect(path)
        con.row_factory = sqlite3.Row
        con.execute("CREATE TABLE IF NOT EXISTS workflows (id TEXT PRIMARY KEY, name TEXT NOT NULL, category TEXT NOT NULL, favorite INTEGER NOT NULL DEFAULT 0, graph TEXT NOT NULL, summary TEXT NOT NULL)")
        con.execute("CREATE TABLE IF NOT EXISTS workflow_sources (workflow_id TEXT PRIMARY KEY, root TEXT NOT NULL, relative TEXT NOT NULL, digest TEXT NOT NULL, UNIQUE(root,relative))")
        con.execute("CREATE TABLE IF NOT EXISTS workflow_settings (key TEXT PRIMARY KEY, value TEXT NOT NULL)")
        con.commit()
        return con

    def allowed():
        return request.remote_addr in ("127.0.0.1", "::1")

    def public(row):
        return {"id": row["id"], "name": row["name"], "category": row["category"],
                "favorite": bool(row["favorite"]), **json.loads(row["summary"]), "source": row["relative"] if "relative" in row.keys() else None}

    @app.route("/api/workspace/workflows", methods=["GET", "POST"])
    def workflows():
        if not allowed():
            return jsonify(error="Manage workflows on the launcher PC"), 403
        if request.method == "GET":
            project_id = request.args.get("project_id")
            project_engine = None
            if project_id is not None:
                if len(project_id)!=32 or any(ch not in "0123456789abcdef" for ch in project_id):
                    return jsonify(error="Invalid project reference"), 400
                project_path = Path(base) / "settings" / "orkilab" / "projects.sqlite3"
                if not project_path.is_file():
                    return jsonify(error="Project not found"), 404
                with closing(sqlite3.connect(project_path)) as projects_db:
                    project = projects_db.execute(
                        "SELECT engine,category FROM projects WHERE id=? AND archived=0", (project_id,)).fetchone()
                if not project or project[1]!="image":
                    return jsonify(error="Active image project not found"), 404
                project_engine = project[0]
            with closing(db()) as con, con:
                rows = con.execute("SELECT w.id,w.name,w.category,w.favorite,w.summary,w.graph,s.relative FROM workflows w LEFT JOIN workflow_sources s ON w.id=s.workflow_id ORDER BY w.favorite DESC,w.name COLLATE NOCASE").fetchall()
                result = []
                for row in rows:
                    entry = public(row)
                    try:
                        entry["multiview_reference"] = multiview_reference_profile(
                            json.loads(row["graph"]), row["category"])
                    except (ValueError, TypeError, RecursionError):
                        entry["multiview_reference"] = {
                            "likely_compatible": False, "image_inputs": 0,
                            "has_prompt": False, "reason": "invalid_graph"}
                    if project_engine is not None:
                        try:
                            entry["compatibility"] = assess_workflow(
                                json.loads(row["graph"]), row["category"], project_engine, row["name"])
                        except (ValueError,TypeError,RecursionError):
                            entry["compatibility"] = {
                                "status":"unverified","reason":"invalid_graph","detected":[],
                                "expected":None,"standard_loader":False}
                    result.append(entry)
                return jsonify(workflows=result)
        if request.mimetype != "application/json" or not 0 < (request.content_length or 0) <= MAX_BYTES:
            return jsonify(error="Invalid workflow request or file too large"), 400
        try:
            body = request.get_json()
            if not isinstance(body, dict):
                raise ValueError("Invalid workflow JSON")
            name, cat, graph = body.get("name"), body.get("category"), body.get("graph")
            if not isinstance(name, str) or not name.strip() or len(name) > 120 or cat not in CATEGORIES:
                raise ValueError("Invalid workflow name or category")
            summary = inspect_graph(graph)
            ident = uuid.uuid4().hex
            with db() as con:
                if con.execute("SELECT COUNT(*) FROM workflows").fetchone()[0] >= 500:
                    return jsonify(error="Workflow library limit reached"), 409
                con.execute("INSERT INTO workflows VALUES (?,?,?,?,?,?)",
                            (ident, name.strip(), cat, 0, json.dumps(graph, ensure_ascii=False), json.dumps(summary)))
            return jsonify(id=ident), 201
        except (ValueError, RecursionError, TypeError):
            return jsonify(error="Invalid or unsupported workflow JSON"), 400

    @app.route("/api/workspace/workflows/<ident>", methods=["GET", "PATCH"])
    def workflow(ident):
        if not allowed():
            return jsonify(error="Manage workflows on the launcher PC"), 403
        with db() as con:
            row = con.execute("SELECT * FROM workflows WHERE id=?", (ident,)).fetchone()
            if row is None:
                return jsonify(error="Workflow not found"), 404
            if request.method == "GET":
                return jsonify(**public(row), graph=json.loads(row["graph"]))
            if request.mimetype != "application/json" or not 0 < (request.content_length or 0) <= 1024:
                return jsonify(error="Invalid request"), 400
            body = request.get_json(silent=True)
            if not isinstance(body, dict) or not isinstance(body.get("favorite"), bool):
                return jsonify(error="Invalid request"), 400
            con.execute("UPDATE workflows SET favorite=? WHERE id=?", (int(body["favorite"]), ident))
            return jsonify(ok=True)

    @app.route("/api/workspace/workflows/folder", methods=["GET", "POST"])
    def workflow_folder():
        if not allowed():
            return jsonify(error="Manage workflows on the launcher PC"), 403
        with closing(db()) as con, con:
            if request.method == "GET":
                row = con.execute("SELECT value FROM workflow_settings WHERE key='folder'").fetchone()
                return jsonify(folder=row[0] if row else "")
            if request.mimetype != "application/json" or not 0 < (request.content_length or 0) <= 4096:
                return jsonify(error="Invalid request"), 400
            body = request.get_json(silent=True)
            raw = body.get("folder") if isinstance(body, dict) else None
            if not isinstance(raw, str) or not raw.strip() or len(raw) > 1024:
                return jsonify(error="Invalid workflow folder"), 400
            try:
                root = Path(raw.strip()).expanduser()
                if not root.is_absolute() or not root.is_dir():
                    raise ValueError()
                root = root.resolve()
            except (OSError, ValueError):
                return jsonify(error="Invalid workflow folder"), 400
            con.execute("INSERT OR REPLACE INTO workflow_settings VALUES ('folder',?)", (str(root),))
            stats = dict(imported=0, updated=0, unchanged=0, skipped=0, limited=False)
            deadline = time.monotonic() + 15
            total = con.execute("SELECT COUNT(*) FROM workflows").fetchone()[0]
            visited = 0
            read_bytes = 0
            def linked(p):
                return p.is_symlink() or getattr(p, "is_junction", lambda: False)()
            for current, dirs, files in os.walk(root, followlinks=False):
                if time.monotonic() > deadline:
                    stats["limited"] = True
                    break
                dirs[:] = sorted(d for d in dirs if not d.startswith(".") and not linked(Path(current,d)))
                for name in sorted(files):
                    visited += 1
                    if visited > 10000 or time.monotonic() > deadline or read_bytes >= 64_000_000:
                        stats["limited"] = True
                        break
                    p = Path(current, name)
                    if p.suffix.lower() != ".json" or linked(p):
                        continue
                    try:
                        with p.open("rb") as handle:
                            raw_data = handle.read(MAX_BYTES + 1)
                        read_bytes += len(raw_data)
                        if len(raw_data) > MAX_BYTES:
                            raise ValueError()
                        graph = json.loads(raw_data)
                        summary = inspect_graph(graph)
                        rel = p.relative_to(root).as_posix()
                        digest = hashlib.sha256(json.dumps(graph,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode("utf-8")).hexdigest()
                    except (OSError, ValueError, RecursionError, TypeError):
                        stats["skipped"] += 1
                        continue
                    previous = con.execute("SELECT workflow_id,digest FROM workflow_sources WHERE root=? AND relative=?", (str(root),rel)).fetchone()
                    if previous:
                        if previous["digest"] == digest:
                            stats["unchanged"] += 1
                            continue
                        con.execute("UPDATE workflows SET graph=?,summary=? WHERE id=?", (json.dumps(graph,ensure_ascii=False),json.dumps(summary),previous["workflow_id"]))
                        con.execute("UPDATE workflow_sources SET digest=? WHERE workflow_id=?", (digest,previous["workflow_id"]))
                        stats["updated"] += 1
                        continue
                    if con.execute("SELECT 1 FROM workflow_sources WHERE digest=?", (digest,)).fetchone():
                        stats["unchanged"] += 1
                        continue
                    if total >= 500:
                        stats["limited"] = True
                        continue
                    category = body.get("category", "other")
                    if category not in CATEGORIES:
                        category = "other"
                    segments = rel.lower().replace("-", " ").split("/")
                    for segment in segments[:-1]:
                        for candidate, words in (("image",("image","imagen","imagem")),("video",("video","vídeo")),("music",("music","música")),("audio",("audio","sonido")),("3d",("3d",))):
                            if any(word in segment for word in words):
                                category = candidate
                                break
                        else:
                            continue
                        break
                    ident = uuid.uuid4().hex
                    con.execute("INSERT INTO workflows VALUES (?,?,?,?,?,?)",(ident,p.stem[:120],category,0,json.dumps(graph,ensure_ascii=False),json.dumps(summary)))
                    con.execute("INSERT INTO workflow_sources VALUES (?,?,?,?)",(ident,str(root),rel,digest))
                    total += 1
                    stats["imported"] += 1
                if visited > 10000 or time.monotonic() > deadline or read_bytes >= 64_000_000:
                    break
            return jsonify(folder=str(root), **stats)
