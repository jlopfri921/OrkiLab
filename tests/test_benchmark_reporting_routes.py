"""B9.2 Flask read-only Benchmark report API tests on isolated SQLite fixtures."""
import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path

from flask import Flask

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from benchmark_reporting_routes import report_routes


class BenchmarkReportsApiTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.app = Flask(__name__)
        report_routes(self.app, self.base)
        self.client = self.app.test_client()
        self.db = self.base / "settings" / "orkilab" / "benchmarks.sqlite3"

    def fill(self):
        self.db.parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(self.db) as conn:
            conn.executescript("""
                CREATE TABLE benchmark_runs(
                    id TEXT,project_id TEXT,name TEXT,state TEXT,
                    protocol_json TEXT,created_at TEXT,updated_at TEXT);
                CREATE TABLE benchmark_variants(
                    id TEXT,run_id TEXT,label TEXT,config_json TEXT);
                CREATE TABLE benchmark_observations(
                    id TEXT,run_id TEXT,variant_id TEXT,repetition INT,status TEXT,
                    duration_ms INT,peak_vram_bytes INT);
                CREATE TABLE benchmark_generation_lineage(
                    observation_id TEXT,run_id TEXT,generation_id TEXT,snapshot_json TEXT);
                INSERT INTO benchmark_runs VALUES
                  ('run-a','project-a','Comparison A','completed','{}','2026-11-22','2026-11-22'),
                  ('run-b','project-b','Other run','draft','{}','2026-11-22','2026-11-22');
                INSERT INTO benchmark_variants VALUES
                  ('variant-a','run-a','Flux checkpoint','{}');
                INSERT INTO benchmark_observations VALUES
                  ('obs-a','run-a','variant-a',0,'completed',1250,NULL);
            """)
        # Python's sqlite3 context commits but doesn't close connections.
        conn.close()

    def test_absent_database_returns_empty_without_creating_one(self):
        result = self.client.get("/api/workspace/benchmark/reports?project_id=project-a")
        self.assertEqual(result.status_code, 200)
        self.assertFalse(result.get_json()["database_available"])
        self.assertEqual(result.get_json()["runs"], [])
        self.assertFalse(self.db.exists())

    def test_project_scoped_index_and_counts(self):
        self.fill()
        before = self.db.read_bytes()
        result = self.client.get("/api/workspace/benchmark/reports?project_id=project-a")
        self.assertEqual(result.status_code, 200, result.get_json())
        self.assertEqual(len(result.get_json()["runs"]), 1)
        self.assertEqual(result.get_json()["runs"][0]["id"], "run-a")
        self.assertEqual(result.get_json()["runs"][0]["observation_count"], 1)
        self.assertEqual(self.db.read_bytes(), before)

    def test_detail_counts_measured_time_without_inferred_vram(self):
        self.fill()
        result = self.client.get(
            "/api/workspace/benchmark/reports/run-a?project_id=project-a"
        )
        self.assertEqual(result.status_code, 200, result.get_json())
        payload = result.get_json()
        self.assertEqual(payload["variants"][0]["duration_ms_median"], 1250)
        self.assertEqual(payload["variants"][0]["missing_per_job_peak_vram_count"], 1)
        self.assertIsNone(payload["variants"][0]["measured_vram_peak_bytes_max"])
        self.assertIsNone(payload["best_variant"])
        self.assertTrue(payload["read_only"])

    def test_comparability_exposes_evidence_gaps_without_sensitive_details(self):
        self.fill()
        response = self.client.get(
            "/api/workspace/benchmark/reports/run-a?project_id=project-a"
        )
        self.assertEqual(response.status_code, 200, response.get_json())
        result = response.get_json()["comparability"]
        self.assertEqual(result["status"], "not_established")
        self.assertIn("missing_generation_lineage", result["variants"][0]["reason_codes"])
        self.assertFalse(result["ranking_eligible"])
        self.assertIsNone(result["best_variant"])
        self.assertNotIn("generation_lineage", response.get_json()["variants"][0])

    def test_legacy_run_protocol_remains_unverified(self):
        self.fill()
        response = self.client.get(
            "/api/workspace/benchmark/reports/run-a?project_id=project-a"
        )
        self.assertEqual(response.status_code, 200, response.get_json())
        readiness = response.get_json()["reproducibility_protocol"]
        self.assertEqual(readiness["status"], "legacy_unverified")
        self.assertFalse(readiness["execution_verified"])
        self.assertFalse(readiness["ranking_eligible"])
        self.assertNotIn("prompt_sha256", readiness)

    def test_cross_project_detail_not_disclosed(self):
        self.fill()
        result = self.client.get(
            "/api/workspace/benchmark/reports/run-b?project_id=project-a"
        )
        self.assertEqual(result.status_code, 404)

    def test_remote_index_and_detail_denied(self):
        self.fill()
        for url in (
            "/api/workspace/benchmark/reports?project_id=project-a",
            "/api/workspace/benchmark/reports/run-a?project_id=project-a",
        ):
            response = self.client.get(
                url, environ_overrides={"REMOTE_ADDR": "203.0.113.18"}
            )
            self.assertEqual(response.status_code, 403)

    def test_invalid_ids_rejected_without_sql(self):
        for url in (
            "/api/workspace/benchmark/reports",
            "/api/workspace/benchmark/reports?project_id=../bad",
            "/api/workspace/benchmark/reports/run-a",
            "/api/workspace/benchmark/reports/run-a?project_id=%20",
        ):
            response = self.client.get(url)
            self.assertEqual(response.status_code, 400)
        self.assertFalse(self.db.exists())

    def test_missing_detail_and_malformed_database_fail_closed(self):
        response = self.client.get(
            "/api/workspace/benchmark/reports/run-x?project_id=project-x"
        )
        self.assertEqual(response.status_code, 404)
        self.db.parent.mkdir(parents=True, exist_ok=True)
        self.db.write_bytes(b"not a sqlite database")
        response = self.client.get(
            "/api/workspace/benchmark/reports?project_id=project-a"
        )
        self.assertEqual(response.status_code, 503)


if __name__ == "__main__":
    unittest.main()
