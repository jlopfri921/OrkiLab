"""Persistent local generation records and safe output descriptors."""
import json
import sqlite3
import time
from contextlib import closing
from pathlib import Path

class GenerationHistory:
    def __init__(self, base):
        self.path = Path(base) / "settings" / "orkilab" / "generations.sqlite3"

    def connect(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        con = sqlite3.connect(self.path, timeout=10)
        con.row_factory = sqlite3.Row
        con.execute("""CREATE TABLE IF NOT EXISTS generations (
            id TEXT PRIMARY KEY, url TEXT NOT NULL, prompt_id TEXT NOT NULL,
            workflow_id TEXT NOT NULL, name TEXT NOT NULL, graph TEXT NOT NULL,
            created REAL NOT NULL, updated REAL NOT NULL, state TEXT NOT NULL,
            outputs TEXT NOT NULL)""")
        con.commit()
        return con

    def add(self, token, url, prompt_id, workflow_id, name, graph):
        now = time.time()
        with closing(self.connect()) as con, con:
            con.execute("INSERT INTO generations VALUES (?,?,?,?,?,?,?,?,?,?)",
                        (token,url,prompt_id,workflow_id,name,json.dumps(graph,ensure_ascii=False,allow_nan=False),now,now,"queued","[]"))

    def get(self, token):
        with closing(self.connect()) as con:
            row = con.execute("SELECT * FROM generations WHERE id=?", (token,)).fetchone()
            return dict(row) if row else None

    def search(self, limit=100, offset=0, query="", state="", sort="newest"):
        """Filter before pagination, using only whitelisted SQL ordering."""
        orders = {
            "newest": "created DESC, id DESC",
            "oldest": "created ASC, id ASC",
            "name_asc": "name COLLATE NOCASE ASC, created DESC, id DESC",
            "name_desc": "name COLLATE NOCASE DESC, created DESC, id DESC",
        }
        if sort not in orders or state not in ("", "queued", "running", "completed", "error", "cancelled"):
            raise ValueError("Invalid history filter")
        if not isinstance(query,str) or len(query)>120:
            raise ValueError("Invalid history search")
        # Search by name/ID/workflow. Escape wildcard characters for literal matching.
        safe = query.strip().replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
        where = ["1=1"]
        params = []
        if safe:
            where.append("(name LIKE ? ESCAPE '\\' OR id LIKE ? ESCAPE '\\' OR workflow_id LIKE ? ESCAPE '\\')")
            params.extend(["%"+safe+"%"]*3)
        if state:
            where.append("state=?")
            params.append(state)
        clause = " AND ".join(where)
        with closing(self.connect()) as con:
            total = con.execute("SELECT COUNT(*) FROM generations WHERE "+clause, params).fetchone()[0]
            rows = con.execute(
                "SELECT id,prompt_id,workflow_id,name,created,updated,state,outputs FROM generations WHERE "+
                clause+" ORDER BY "+orders[sort]+" LIMIT ? OFFSET ?",
                [*params, limit, offset]).fetchall()
        return {"jobs":[{**dict(row),"outputs":json.loads(row["outputs"])} for row in rows],"total":total}

    def list(self, limit=100, offset=0):
        return self.search(limit,offset)["jobs"]

    def update(self, token, state, outputs):
        with closing(self.connect()) as con, con:
            con.execute("UPDATE generations SET state=?,outputs=?,updated=? WHERE id=? AND state NOT IN ('completed','error','cancelled')",
                        (state,json.dumps(outputs,ensure_ascii=False),time.time(),token))

MEDIA = {".png":"image/png",".jpg":"image/jpeg",".jpeg":"image/jpeg",".webp":"image/webp",".gif":"image/gif",".mp4":"video/mp4",".webm":"video/webm",".mp3":"audio/mpeg",".wav":"audio/wav",".ogg":"audio/ogg",".flac":"audio/flac",".m4a":"audio/mp4",".glb":"application/octet-stream",".gltf":"application/octet-stream",".obj":"application/octet-stream",".stl":"application/octet-stream",".ply":"application/octet-stream"}

def describe_outputs(entry):
    result = []
    for node in (entry.get("outputs") or {}).values():
        if not isinstance(node,dict):
            continue
        for kind, items in node.items():
            if not isinstance(items,list):
                continue
            for item in items:
                if not isinstance(item,dict):
                    continue
                filename, folder, location = item.get("filename"),item.get("subfolder",""),item.get("type","output")
                if not isinstance(filename,str) or not filename or len(filename)>500 or any(c in filename for c in '/\\:' ) or filename in (".","..") or any(ord(c)<32 for c in filename):
                    continue
                if not isinstance(folder,str) or len(folder)>1000 or any(ord(c)<32 for c in folder) or ":" in folder or folder.startswith(("/","\\")) or any(p in (".","..") for p in folder.replace("\\","/").split("/")):
                    continue
                if location not in ("output","temp"):
                    continue
                mime = MEDIA.get(Path(filename).suffix.lower())
                if not mime:
                    continue
                result.append(dict(filename=filename,subfolder=folder,type=location,kind=kind,mime=mime))
                if len(result)>=100:
                    return result
    return result
