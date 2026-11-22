"""B9.2 read-only project-scoped Benchmark Studio reporting HTTP views.

All queries use a SQLite read-only connection. These routes never initialize
BenchmarkStore (which could create/alter tables), submit jobs or change runs.
Local launcher access only and explicit project/run binding for detail.
"""
from __future__ import annotations

import re
import sqlite3
from contextlib import closing
from pathlib import Path

from flask import jsonify, request
from benchmark_report_summary import summarize_benchmark_report

ID = re.compile(r"^[A-Za-z0-9_-]{1,200}$")


def report_routes(app, base):
    db = Path(base) / "settings" / "orkilab" / "benchmarks.sqlite3"

    def local():
        return request.remote_addr in ("127.0.0.1", "::1")

    def open_ro():
        if not db.is_file():
            return None
        conn = sqlite3.connect(db.resolve().as_uri() + "?mode=ro", uri=True, timeout=5)
        conn.row_factory = sqlite3.Row
        return conn

    @app.get("/api/workspace/benchmark/reports")
    def benchmark_reports_index():
        if not local():
            return jsonify(error="Reports available on the launcher PC only"), 403
        project_id = request.args.get("project_id", "")
        if not ID.fullmatch(project_id):
            return jsonify(error="Explicit project ID required"), 400
        try:
            con = open_ro()
            if con is None:
                return jsonify(project_id=project_id, runs=[], database_available=False)
            with closing(con):
                rows = con.execute(
                    "SELECT r.id,r.project_id,r.name,r.state,r.created_at,r.updated_at,"
                    "(SELECT COUNT(*) FROM benchmark_variants v WHERE v.run_id=r.id) AS variant_count,"
                    "(SELECT COUNT(*) FROM benchmark_observations o WHERE o.run_id=r.id) AS observation_count "
                    "FROM benchmark_runs r WHERE r.project_id=? "
                    "ORDER BY r.created_at DESC,r.id DESC LIMIT 100",
                    (project_id,),
                ).fetchall()
            return jsonify(project_id=project_id, runs=[dict(x) for x in rows],
                           database_available=True, read_only=True)
        except sqlite3.Error:
            return jsonify(error="Benchmark reports unavailable"), 503

    @app.get("/api/workspace/benchmark/reports/<run_id>")
    def benchmark_report_detail(run_id):
        if not local():
            return jsonify(error="Reports available on the launcher PC only"), 403
        project_id = request.args.get("project_id", "")
        if not ID.fullmatch(project_id) or not ID.fullmatch(run_id):
            return jsonify(error="Explicit project and run IDs required"), 400
        try:
            con = open_ro()
            if con is None:
                return jsonify(error="Benchmark database unavailable"), 404
            with closing(con):
                row = con.execute(
                    "SELECT * FROM benchmark_runs WHERE id=? AND project_id=?",
                    (run_id, project_id),
                ).fetchone()
                if row is None:
                    return jsonify(error="Benchmark run not found in project"), 404
                variants = con.execute(
                    "SELECT id,run_id,label,config_json FROM benchmark_variants "
                    "WHERE run_id=? ORDER BY label,id", (run_id,),
                ).fetchall()
                obs = con.execute(
                    "SELECT id,run_id,variant_id,repetition,status,duration_ms,peak_vram_bytes "
                    "FROM benchmark_observations WHERE run_id=? "
                    "ORDER BY variant_id,repetition", (run_id,),
                ).fetchall()
            report = {
                "schema_version": 1, "run": dict(row),
                "variants": [dict(v) for v in variants],
                "observations": [dict(o) for o in obs],
            }
            result = summarize_benchmark_report(report)
            result["project_id"] = project_id
            result["name"] = row["name"]
            result["run_created_at"] = row["created_at"]
            result["read_only"] = True
            return jsonify(result)
        except (sqlite3.Error, ValueError, TypeError):
            return jsonify(error="Benchmark report could not be verified"), 503
