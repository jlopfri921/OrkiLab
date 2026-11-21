"""Deterministic, non-destructive Multiview Studio 0.5.0-beta.2 exports.

Every photograph remains in its original location. A separate portable ZIP
contains approved images, an explicit manifest and SHA256 checksums; subject
groups are never split across train/validation. This is a generic archive, NOT
a claim that a specific trainer supports multi-view conditioning.
"""
import hashlib
import io
import json
import sqlite3
import tempfile
import zipfile
from contextlib import closing
from pathlib import Path

from flask import jsonify, request, send_file

from dataset_studio import valid_origin
from multiview_studio import identifier, source_path

MAX_CAPTURES = 500
MAX_TOTAL_BYTES = 350 * 1024 * 1024
MAX_ZIP_BYTES = 400 * 1024 * 1024
ZIP_TIMESTAMP = (2020, 1, 1, 0, 0, 0)
FORMATS = {"PNG": ".png", "JPEG": ".jpg", "WEBP": ".webp", "BMP": ".bmp"}
SPLITS = {"train", "validation"}


class ExportError(ValueError):
    pass


def split_for_subject(subject_id, seed, validation_percent):
    """Stable across imports/deletes and row insertion order; never split a subject."""
    if validation_percent == 0:
        return "train"
    digest = hashlib.sha256(
        ("orkilab-mv-split-v1:" + str(seed) + ":" + subject_id).encode("ascii")
    ).digest()
    bucket = int.from_bytes(digest[:8], "big") % 100
    return "validation" if bucket < validation_percent else "train"


def request_options(body):
    if not isinstance(body, dict):
        raise ExportError("Expected JSON object")
    mode = body.get("mode", "preview")
    validation_percent = body.get("validation_percent", 20)
    seed = body.get("seed", 42)
    include_synthetic = body.get("include_synthetic", False)
    if mode not in ("preview", "download"):
        raise ExportError("Invalid export mode")
    if type(validation_percent) is not int or not 0 <= validation_percent <= 50:
        raise ExportError("Validation percent must be an integer from 0 to 50")
    if type(seed) is not int or not 0 <= seed <= 2_147_483_647:
        raise ExportError("Seed must be an integer from 0 to 2147483647")
    if type(include_synthetic) is not bool:
        raise ExportError("include_synthetic must be a boolean")
    if mode == "download" and body.get("confirm") is not True:
        raise ExportError("Explicit download confirmation is required")
    return dict(mode=mode, validation_percent=validation_percent,
                seed=seed, include_synthetic=include_synthetic)


def collect(project_db, mv_db, project_id, options):
    if not identifier(project_id) or not project_db.is_file() or not mv_db.is_file():
        raise ExportError("Project not found")
    with closing(sqlite3.connect(project_db)) as conn:
        project = conn.execute(
            "SELECT name, category FROM projects WHERE id=? AND archived=0",
            (project_id,)).fetchone()
    if project is None or project[1] != "image":
        raise ExportError("Active image project not found")
    with closing(sqlite3.connect(mv_db)) as conn:
        conn.row_factory = sqlite3.Row
        captures = [dict(row) for row in conn.execute(
            "SELECT c.*,s.name AS subject_name FROM mv_captures c "
            "JOIN mv_subjects s ON s.id=c.subject_id AND s.project_id=c.project_id "
            "WHERE c.project_id=? AND c.review='approved' "
            + ("" if options["include_synthetic"] else "AND c.source_type!='synthetic' ")
            + "ORDER BY s.id ASC,c.id ASC",
            (project_id,))]
        if len(captures)>MAX_CAPTURES:
            raise ExportError("Export exceeds 500 approved captures; select fewer")
        lineage = {}
        table = conn.execute(
            "SELECT 1 FROM sqlite_master WHERE type='table' AND name='mv_generated_lineage'"
        ).fetchone()
        if table and captures:
            ids = [r["id"] for r in captures]
            for chunk_start in range(0,len(ids),400):
                chunk = ids[chunk_start:chunk_start+400]
                marks = ",".join("?" for _ in chunk)
                for row in conn.execute(
                    "SELECT * FROM mv_generated_lineage WHERE capture_id IN ("+marks+")",chunk
                ):
                    lineage[row["capture_id"]]=dict(row)
    total_bytes = sum(r["bytes"] for r in captures)
    if total_bytes>MAX_TOTAL_BYTES:
        raise ExportError("Export exceeds 350 MiB; select fewer captures")
    entries = []
    for row in captures:
        # Filenames are constructed exclusively from validated UUID identifiers.
        sid,cid = row["subject_id"],row["id"]
        if not identifier(sid) or not identifier(cid) or row["format"] not in FORMATS:
            raise ExportError("Invalid stored capture metadata")
        split = split_for_subject(sid,options["seed"],options["validation_percent"])
        filename = "images/"+split+"/"+sid+"/"+cid+FORMATS[row["format"]]
        linked = lineage.get(cid)
        record = dict(
            capture_id=cid,subject_id=sid,subject_name=row["subject_name"],
            filename=filename,split=split,
            view_name=row["view_name"],source_filename=row["name"],
            sha256=row["sha256"],bytes=row["bytes"],
            width=row["width"],height=row["height"],format=row["format"],
            azimuth_deg=row["azimuth_deg"],elevation_deg=row["elevation_deg"],
            distance_m=row["distance_m"],source_type=row["source_type"],
            provenance=row["provenance"],review=row["review"],
            notes=row["notes"],sharpness_score=row["sharpness_score"],
            generation=None if not linked else dict(
                generation_id=linked["generation_id"],
                workflow_id=linked["workflow_id"],
                workflow_sha256=linked["workflow_sha256"],
                prompt_id=linked["prompt_id"],
                output_index=linked["output_index"],
                seeds=json.loads(linked["seeds_json"]),
                source_filename=linked["source_filename"],
            ),
        )
        entries.append((record,row["path"]))
    subjects = sorted({e["subject_id"] for e,_ in entries})
    breakdown = {s:dict(subjects=len({e["subject_id"] for e,_ in entries if e["split"]==s}),
                        captures=sum(e["split"]==s for e,_ in entries))
                 for s in ("train","validation")}
    counts = dict(real=sum(e["source_type"]=="real_photo" for e,_ in entries),
                  synthetic=sum(e["source_type"]=="synthetic" for e,_ in entries),
                  frames=sum(e["source_type"]=="video_frame" for e,_ in entries),
                  unknown=sum(e["source_type"]=="unknown" for e,_ in entries))
    return dict(
        format="orkilab-multiview-v1",project_id=project_id,
        project_name=project[0],options=dict(
            seed=options["seed"],validation_percent=options["validation_percent"],
            include_synthetic=options["include_synthetic"],approved_only=True,
            split_unit="subject",split_method="sha256-subject-v1"),
        summary=dict(subjects=len(subjects),captures=len(entries),
                     total_bytes=total_bytes,splits=breakdown,source_types=counts),
        entries=entries,
    )


def verified_capture(path, entry):
    """Verify originals against indexed sha/length at point of export."""
    try:
        original = source_path(path)
        if original.stat().st_size != entry["bytes"]:
            raise ExportError("Original photograph changed: "+entry["capture_id"])
        sha = hashlib.sha256()
        with original.open("rb") as stream:
            while chunk := stream.read(1024 * 1024):
                sha.update(chunk)
        if sha.hexdigest()!=entry["sha256"]:
            raise ExportError("Original photograph changed: "+entry["capture_id"])
        return original
    except (OSError,ValueError) as exc:
        if isinstance(exc,ExportError):
            raise
        raise ExportError("Missing/unsafe photograph: "+entry["capture_id"]) from exc


def manifest_and_sources(report):
    entries=[]
    originals=[]
    for record,path in report["entries"]:
        image=verified_capture(path,record)
        entries.append(record)
        originals.append((record,image))
    manifest={k:v for k,v in report.items() if k!="entries"}
    manifest["captures"]=entries
    manifest["safety"]={"originals_modified":False,
        "angle_inference":False,"training_adapter":"generic multiview archive",
        "warning":"Subject-level split prevents view leakage; trainer support not implied."}
    return manifest, originals


def stable_json(value):
    return (json.dumps(value,ensure_ascii=False,indent=2,sort_keys=True,
                       separators=(",",": "),allow_nan=False)+"\n").encode("utf-8")


def zip_info(name):
    info=zipfile.ZipInfo(name,ZIP_TIMESTAMP)
    info.compress_type=zipfile.ZIP_STORED
    info.external_attr=0o600<<16
    info.create_system=3
    return info


def write_export(target, manifest, originals):
    content=stable_json(manifest)
    checksums=[hashlib.sha256(content).hexdigest()+"  manifest.json"]
    with zipfile.ZipFile(target,"w",allowZip64=False) as archive:
        archive.writestr(zip_info("manifest.json"),content)
        for entry,image in originals:
            with archive.open(zip_info(entry["filename"]),"w",force_zip64=False) as dest:
                with image.open("rb") as source:
                    sha=hashlib.sha256()
                    while part:=source.read(1024*1024):
                        sha.update(part)
                        dest.write(part)
                    if sha.hexdigest()!=entry["sha256"]:
                        raise ExportError("Original changed during export: "+entry["capture_id"])
            checksums.append(entry["sha256"]+"  "+entry["filename"])
        archive.writestr(zip_info("checksums.sha256"),("\n".join(checksums)+"\n").encode())
    if target.tell()>MAX_ZIP_BYTES:
        raise ExportError("Archive exceeds 400 MiB")


def register(app, base):
    base=Path(base)
    project_db=base/"settings"/"orkilab"/"projects.sqlite3"
    mv_db=base/"settings"/"orkilab"/"multiview.sqlite3"

    @app.post("/api/workspace/multiview/projects/<project_id>/export")
    def multiview_export(project_id):
        if request.remote_addr not in ("127.0.0.1","::1") or not valid_origin():
            return jsonify(error="Local same-origin access required"),403
        if request.mimetype!="application/json" or not 0<(request.content_length or 0)<=2500:
            return jsonify(error="Invalid export request"),400
        try:
            body=request.get_json(silent=True)
            options=request_options(body)
            report=collect(project_db,mv_db,project_id,options)
            # Preflight deliberately checks every original's integrity, not
            # merely the paths that happen to be visible on a UI page.
            manifest,originals=manifest_and_sources(report)
            if options["mode"]=="preview":
                return jsonify(summary=manifest["summary"],options=manifest["options"],
                               format=manifest["format"],project_id=project_id,
                               ready=bool(originals),warnings=[] if originals else [
                                   "No approved captures match these options"])
            if not originals:
                return jsonify(error="No eligible approved captures to export"),409
            out=tempfile.TemporaryFile(mode="w+b")
            try:
                write_export(out,manifest,originals)
                out.seek(0)
                response=send_file(out,mimetype="application/zip",
                    as_attachment=True,download_name="orkilab-multiview-"+project_id+".zip",
                    max_age=0)
                response.call_on_close(out.close)
                response.headers["Cache-Control"]="no-store"
                response.headers["X-Content-Type-Options"]="nosniff"
                return response
            except BaseException:
                out.close()
                raise
        except ExportError as exc:
            return jsonify(error=str(exc)),409
        except (OSError,sqlite3.Error,KeyError,TypeError,ValueError,
                zipfile.BadZipFile) as exc:
            app.logger.warning("Multiview export failed: %s",str(exc)[:200])
            return jsonify(error="Could not prepare a safe multiview archive"),400
