"""Opt-in multiview capture registration from completed local ComfyUI jobs.

Uses existing OrkiLab generation queue, validation, cancel and persistent history.
Never trusts a browser-provided filename or upstream URL. Generated output is copied
to a project-owned snapshot, inspected, hashed and only then indexed as synthetic.
"""
import hashlib
import json
import os
import sqlite3
import tempfile
import uuid
from contextlib import closing
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, build_opener, ProxyHandler
from urllib.error import HTTPError, URLError

from flask import jsonify, request

from comfyui_connect import validate_settings, DEFAULT_SETTINGS, NoRedirect
from dataset_studio import valid_origin
from generation_history import GenerationHistory
from multiview_studio import (
    identifier, coordinate, text_field, inspect_image, sharpness_score,
    MAX_IMAGE_BYTES,
)

MIMES = {"image/png":".png", "image/jpeg":".jpg", "image/webp":".webp"}
MAX_READ = MAX_IMAGE_BYTES + 1


def seed_from_graph(graph):
    """Best-effort provenance, never infer a seed from a prompt or filename."""
    seeds = []
    if isinstance(graph, dict):
        for item in graph.values():
            if isinstance(item, dict) and isinstance(item.get("inputs"), dict):
                for key, value in item["inputs"].items():
                    if key in ("seed", "noise_seed") and type(value) is int:
                        seeds.append(value)
    return seeds[:16]


def read_image_output(url, item):
    """A bounded, redirect-free read from an already validated *local* ComfyUI."""
    if (not isinstance(item,dict) or item.get("mime") not in MIMES
            or item.get("type") != "output"):
        raise ValueError("Only saved PNG/JPEG/WebP output images may be imported")
    name, subfolder = item.get("filename"), item.get("subfolder")
    if (not isinstance(name,str) or not 0 < len(name) <= 500
            or any(c in name for c in "/\\:") or name in (".","..")
            or not isinstance(subfolder,str) or len(subfolder)>1000
            or subfolder.startswith(("/","\\"))
            or ":" in subfolder
            or any(s in (".","..") for s in subfolder.replace("\\","/").split("/"))):
        raise ValueError("Unsafe generation output descriptor")
    query = urlencode({k:item[k] for k in ("filename","subfolder","type")})
    with build_opener(ProxyHandler({}),NoRedirect()).open(
            Request(url + "/view?" + query), timeout=30) as stream:
        if stream.status != 200:
            raise ValueError("ComfyUI image unavailable")
        result=stream.read(MAX_READ)
        if len(result)>MAX_IMAGE_BYTES or not result:
            raise ValueError("Generated image too large or empty")
    return result


def register(app, base):
    base=Path(base)
    projects_db=base/"settings"/"orkilab"/"projects.sqlite3"
    multiview_db=base/"settings"/"orkilab"/"multiview.sqlite3"
    output_root=base/"settings"/"orkilab"/"multiview_generated"
    history=GenerationHistory(base)

    def local():
        return request.remote_addr in ("127.0.0.1","::1")

    def active_subject(project_id,subject_id):
        if not identifier(project_id) or not identifier(subject_id):
            return False
        if not projects_db.is_file() or not multiview_db.is_file():
            return False
        with closing(sqlite3.connect(projects_db)) as conn:
            valid=conn.execute(
                "SELECT 1 FROM projects WHERE id=? AND archived=0 AND category='image'",
                (project_id,)).fetchone()
        if not valid:
            return False
        with closing(sqlite3.connect(multiview_db)) as conn:
            return conn.execute(
                "SELECT 1 FROM mv_subjects WHERE id=? AND project_id=?",
                (subject_id,project_id)).fetchone() is not None

    def lineage_db():
        conn=sqlite3.connect(multiview_db,timeout=10)
        conn.row_factory=sqlite3.Row
        conn.execute("PRAGMA foreign_keys=ON")
        conn.execute("""CREATE TABLE IF NOT EXISTS mv_generated_lineage(
            capture_id TEXT PRIMARY KEY REFERENCES mv_captures(id) ON DELETE CASCADE,
            generation_id TEXT NOT NULL, workflow_id TEXT NOT NULL,
            workflow_sha256 TEXT NOT NULL,
            prompt_id TEXT NOT NULL, output_index INTEGER NOT NULL,
            seeds_json TEXT NOT NULL, source_filename TEXT NOT NULL,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(generation_id, output_index, capture_id)
        )""")
        conn.commit()
        return conn

    @app.get("/api/workspace/multiview/projects/<project_id>/subjects/<subject_id>/generated")
    def generated_lineage(project_id,subject_id):
        if not local():
            return jsonify(error="Run generation tools on launcher computer"),403
        if not active_subject(project_id,subject_id):
            return jsonify(error="Project or subject not found"),404
        with closing(lineage_db()) as conn:
            rows=conn.execute(
                "SELECT l.*,c.view_name,c.review,c.azimuth_deg,c.elevation_deg,"
                "c.distance_m FROM mv_generated_lineage l "
                "JOIN mv_captures c ON c.id=l.capture_id "
                "WHERE c.project_id=? AND c.subject_id=? ORDER BY l.created_at DESC",
                (project_id,subject_id)).fetchall()
        return jsonify(generated=[dict(row) for row in rows])

    @app.post("/api/workspace/multiview/projects/<project_id>/subjects/<subject_id>/generated")
    def import_generated(project_id,subject_id):
        if not local() or not valid_origin():
            return jsonify(error="Local same-origin access required"),403
        if not active_subject(project_id,subject_id):
            return jsonify(error="Active image project and subject required"),404
        if request.mimetype!="application/json" or not 0<(request.content_length or 0)<=4000:
            return jsonify(error="Invalid request"),400
        body=request.get_json(silent=True)
        if not isinstance(body,dict) or body.get("confirm") is not True:
            return jsonify(error="Confirm generated image import"),400
        generation_id=body.get("generation_id")
        index=body.get("output_index")
        if not identifier(generation_id) or type(index) is not int or not 0<=index<100:
            return jsonify(error="Invalid generation or output index"),400
        row=history.get(generation_id)
        if not row or row["state"]!="completed":
            return jsonify(error="Generation must be completed successfully"),409
        try:
            outputs=json.loads(row["outputs"])
            graph=json.loads(row["graph"])
            if not isinstance(outputs,list) or index>=len(outputs):
                return jsonify(error="Image output not found"),404
            item=outputs[index]
            # Only the exact ComfyUI endpoint currently configured for this
            # installation may supply output bytes. No arbitrary URL access.
            configpath=base/"settings"/"orkilab"/"comfyui.json"
            cfg=validate_settings(json.loads(configpath.read_text(encoding="utf-8")),DEFAULT_SETTINGS)
            saved_url=validate_settings({"url":row["url"]},DEFAULT_SETTINGS)["url"]
            if cfg["mode"]=="native" or saved_url!=cfg["url"]:
                return jsonify(error="Generation endpoint differs from current ComfyUI connection"),409
            azimuth=coordinate(body.get("azimuth_deg"),0,359.9999,"azimuth_deg")
            elevation=coordinate(body.get("elevation_deg"),-90,90,"elevation_deg")
            distance=coordinate(body.get("distance_m"),0.0001,1_000_000,"distance_m")
            view=text_field(body.get("view_name",""),100)
            notes=text_field(body.get("notes",""),1000)
            requested = []
            for key, choices in (
                ("requested_direction", {"front","front_right","right","back_right",
                                         "back","back_left","left","front_left","top","bottom"}),
                ("requested_elevation", {"above","level","below"}),
                ("requested_distance", {"close","medium","far"})):
                value=body.get(key)
                if value is not None and (not isinstance(value,str) or value not in choices):
                    raise ValueError("Invalid requested viewpoint")
                requested.append(value)
            ref_ids=body.get("reference_capture_ids")
            if ref_ids is not None and (
                    not isinstance(ref_ids,list) or not 1<=len(ref_ids)<=4
                    or len(set(ref_ids))!=len(ref_ids)
                    or any(not identifier(x) for x in ref_ids)):
                raise ValueError("Invalid source references")
            if ref_ids:
                with closing(sqlite3.connect(multiview_db,timeout=5)) as refdb:
                    marks=",".join("?" for _ in ref_ids)
                    n=refdb.execute(
                        "SELECT COUNT(*) FROM mv_captures WHERE project_id=? AND subject_id=? "
                        "AND id IN ("+marks+") AND source_type IN ('real_photo','unknown','video_frame')",
                        (project_id,subject_id,*ref_ids)).fetchone()[0]
                if n!=len(ref_ids):
                    raise ValueError("Reference image does not belong to this subject")
            # Preserve prompt/seed provenance in the recorded generation graph;
            # also keep selected seed values for quick inspection.
            graph_hash=hashlib.sha256(
                json.dumps(graph,ensure_ascii=False,sort_keys=True).encode("utf-8")).hexdigest()
            if not isinstance(item,dict):
                raise ValueError("Invalid generation output")
            image=read_image_output(saved_url,item)
            directory=output_root/project_id/subject_id
            directory.mkdir(parents=True,exist_ok=True)
            # Directory is app-generated but refuse unexpected symlink anchors.
            if any(parent.is_symlink() for parent in (directory,*directory.parents)):
                raise ValueError("Unsafe output directory")
            capture_id=uuid.uuid4().hex
            ext=MIMES[item["mime"]]
            final=directory/(capture_id+ext)
            # Write to a unique temporary file and atomically publish; never
            # copy/move/modify original reference files or ComfyUI output.
            fd,tmp=tempfile.mkstemp(prefix=".pending-",suffix=ext,dir=directory)
            try:
                with os.fdopen(fd,"wb") as stream:
                    stream.write(image)
                properties=inspect_image(Path(tmp))
                sharpness=sharpness_score(Path(tmp))
                with closing(lineage_db()) as conn, conn:
                    # Serialize check-and-link so simultaneous imports cannot
                    # register the same generation output twice for a subject.
                    conn.execute("BEGIN IMMEDIATE")
                    exists=conn.execute(
                        "SELECT l.capture_id FROM mv_generated_lineage l "
                        "JOIN mv_captures c ON c.id=l.capture_id "
                        "WHERE l.generation_id=? AND l.output_index=? "
                        "AND c.project_id=? AND c.subject_id=?",
                        (generation_id,index,project_id,subject_id)).fetchone()
                    if exists:
                        return jsonify(error="Output already registered for this subject",
                                       capture_id=exists[0]),409
                    os.replace(tmp,final)
                    conn.execute("""INSERT INTO mv_captures
                        (id,project_id,subject_id,path,name,sha256,bytes,width,height,
                         format,sharpness_score,view_name,azimuth_deg,elevation_deg,
                         distance_m,source_type,provenance,review,notes,
                         requested_direction,requested_elevation,requested_distance,
                         reference_capture_ids_json)
                        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                        (capture_id,project_id,subject_id,str(final),final.name,
                         properties["sha256"],properties["bytes"],properties["width"],
                         properties["height"],properties["format"],sharpness,view,
                         azimuth,elevation,distance,"synthetic","workflow","unreviewed",notes,
                         *requested,json.dumps(ref_ids) if ref_ids else None))
                    conn.execute("""INSERT INTO mv_generated_lineage
                        (capture_id,generation_id,workflow_id,workflow_sha256,
                         prompt_id,output_index,seeds_json,source_filename)
                        VALUES (?,?,?,?,?,?,?,?)""",
                        (capture_id,generation_id,row["workflow_id"],graph_hash,
                         row["prompt_id"],index,json.dumps(seed_from_graph(graph)),
                         item["filename"]))
                    conn.execute("UPDATE mv_subjects SET updated_at=CURRENT_TIMESTAMP WHERE id=?",
                                 (subject_id,))
                return jsonify(id=capture_id,source_type="synthetic",review="unreviewed",
                               provenance="workflow",**properties),201
            finally:
                if os.path.exists(tmp):
                    os.unlink(tmp)
                # Rollback can only remove the just-created private snapshot,
                # not source photo nor ComfyUI output.
                if final.exists():
                    with closing(sqlite3.connect(multiview_db)) as conn:
                        committed=conn.execute("SELECT 1 FROM mv_captures WHERE id=?",
                                               (capture_id,)).fetchone()
                    if not committed:
                        final.unlink()
        except (OSError,ValueError,KeyError,IndexError,TypeError,sqlite3.Error,HTTPError,URLError) as exc:
            app.logger.warning("Multiview import rejected: %s",str(exc)[:150])
            return jsonify(error="Could not securely import generated image",detail=str(exc)[:180]),400
