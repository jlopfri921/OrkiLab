"""B9.2 Flask read-only Benchmark report API tests on isolated SQLite fixtures."""
import sqlite3
from contextlib import closing
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

    def create_active_project_fixture(self):
        projects_db = self.base / "settings" / "orkilab" / "projects.sqlite3"
        projects_db.parent.mkdir(parents=True, exist_ok=True)
        from contextlib import closing
        with closing(sqlite3.connect(projects_db)) as con, con:
            con.execute("CREATE TABLE projects (id TEXT PRIMARY KEY, archived INT)")
            con.execute("INSERT INTO projects VALUES ('project-a',0)")
            con.execute("INSERT INTO projects VALUES ('project-archived',1)")

    def test_draft_options_lists_real_workflows_and_devices_without_writes(self):
        from unittest.mock import patch
        self.create_active_project_fixture()
        wf_db = self.base / "settings" / "orkilab" / "workflows.sqlite3"
        from contextlib import closing
        with closing(sqlite3.connect(wf_db)) as conn, conn:
            conn.execute("CREATE TABLE workflows (id TEXT,name TEXT,category TEXT)")
            conn.execute("INSERT INTO workflows VALUES ('wf-1','Flujo español','image')")
        prior = wf_db.read_bytes()
        with patch("benchmark_gpu_memory_probe.sample_devices", return_value={
            "ok": True, "devices": [{"uuid":"GPU-123","name":"Test card","index":0}]
        }) as mock:
            response = self.client.get(
                "/api/workspace/benchmark/draft-options?project_id=project-a"
            )
        self.assertEqual(response.status_code, 200, response.get_json())
        body = response.get_json()
        self.assertEqual(body["workflows"][0]["name"], "Flujo español")
        self.assertEqual(body["devices"][0]["uuid"], "GPU-123")
        self.assertTrue(body["metadata_only"])
        self.assertFalse(body["auto_verified"])
        self.assertFalse(body["execution_submitted"])
        self.assertEqual(wf_db.read_bytes(), prior)
        self.assertFalse(self.db.exists())
        mock.assert_called_once_with()

    def test_draft_options_missing_workflow_database_and_gpu_returns_empty(self):
        from unittest.mock import patch
        self.create_active_project_fixture()
        with patch("benchmark_gpu_memory_probe.sample_devices",
                   return_value={"ok": False, "reason": "unavailable"}):
            response = self.client.get(
                "/api/workspace/benchmark/draft-options?project_id=project-a"
            )
        self.assertEqual(response.status_code, 200, response.get_json())
        self.assertEqual(response.get_json()["workflows"], [])
        self.assertEqual(response.get_json()["devices"], [])
        self.assertFalse(response.get_json()["gpu_inventory_available"])
        self.assertFalse(self.db.exists())

    def test_draft_options_reject_remote_and_other_projects(self):
        from unittest.mock import patch
        self.create_active_project_fixture()
        remote = self.client.get(
            "/api/workspace/benchmark/draft-options?project_id=project-a",
            environ_overrides={"REMOTE_ADDR":"198.51.100.10"}
        )
        self.assertEqual(remote.status_code, 403)
        unknown = self.client.get(
            "/api/workspace/benchmark/draft-options?project_id=other"
        )
        self.assertEqual(unknown.status_code, 404)
        archived = self.client.get(
            "/api/workspace/benchmark/draft-options?project_id=project-archived"
        )
        self.assertEqual(archived.status_code, 404)
        invalid = self.client.get(
            "/api/workspace/benchmark/draft-options?project_id=../bad"
        )
        self.assertEqual(invalid.status_code, 400)
        self.assertFalse(self.db.exists())

    def test_confirmed_draft_api_creates_only_inactive_plan(self):
        from test_benchmark_draft_creation import payload
        self.create_active_project_fixture()
        response = self.client.post("/api/workspace/benchmark/drafts", json=payload())
        self.assertEqual(response.status_code, 201, response.get_json())
        self.assertEqual(response.get_json()["state"], "draft")
        self.assertFalse(response.get_json()["generation_submitted"])
        self.assertFalse(response.get_json()["execution_verified"])
        index = self.client.get("/api/workspace/benchmark/reports?project_id=project-a")
        self.assertEqual(index.status_code, 200, index.get_json())
        self.assertEqual(index.get_json()["runs"][0]["id"], response.get_json()["id"])
        self.assertEqual(index.get_json()["runs"][0]["variant_count"], 2)
        self.assertEqual(index.get_json()["runs"][0]["observation_count"], 0)

    def test_draft_api_refuses_remote_invalid_and_archived_project(self):
        from test_benchmark_draft_creation import payload
        self.create_active_project_fixture()
        remote = self.client.post("/api/workspace/benchmark/drafts", json=payload(),
                                 environ_overrides={"REMOTE_ADDR":"198.51.100.7"})
        self.assertEqual(remote.status_code, 403)
        bad = payload()
        bad["confirm"] = False
        self.assertEqual(self.client.post("/api/workspace/benchmark/drafts",
                                          json=bad).status_code, 400)
        archived = payload()
        archived["project_id"] = "project-archived"
        self.assertEqual(self.client.post("/api/workspace/benchmark/drafts",
                                          json=archived).status_code, 404)
        self.assertFalse(self.db.exists())

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

    def test_b9_9_local_history_matches_immutable_lineage_without_backend_execution(self):
        import json
        from benchmark_generation_adapter import snapshot_generation
        self.fill()
        gen = {
            "id": "generation-1",
            "prompt_id": "prompt-1",
            "workflow_id": "workflow-1",
            "state": "completed",
            "graph": json.dumps({"4":{"class_type":"KSampler","inputs":{"seed":14}}}),
            "outputs": "[]",
        }
        snap = snapshot_generation(gen)
        with closing(sqlite3.connect(self.db)) as conn, conn:
            conn.execute(
                "INSERT INTO benchmark_generation_lineage VALUES (?,?,?,?)",
                ("obs-a", "run-a", gen["id"], json.dumps(snap)),
            )
        history = self.base / "settings" / "orkilab" / "generations.sqlite3"
        with closing(sqlite3.connect(history)) as conn, conn:
            conn.execute(
                "CREATE TABLE generations (id TEXT,prompt_id TEXT,workflow_id TEXT,"
                "state TEXT,graph TEXT,outputs TEXT)"
            )
            conn.execute(
                "INSERT INTO generations VALUES (?,?,?,?,?,?)",
                (gen["id"], gen["prompt_id"], gen["workflow_id"],
                 gen["state"], gen["graph"], gen["outputs"]),
            )
        history_before = history.read_bytes()
        response = self.client.get(
            "/api/workspace/benchmark/reports/run-a?project_id=project-a"
        )
        self.assertEqual(response.status_code, 200, response.get_json())
        check = response.get_json()["saved_history_consistency"]
        self.assertEqual(check["variants"][0]["counts"]["local_record_match"], 1)
        self.assertFalse(check["remote_execution_verified"])
        self.assertFalse(check["ranking_eligible"])
        self.assertEqual(history.read_bytes(), history_before)
        self.assertNotIn("graph", str(check))
        self.assertNotIn("prompt-1", str(check))

    def test_b10_2_node_choices_are_explicit_read_only_and_project_bound(self):
        import json
        from unittest.mock import patch
        self.fill()
        protocol = {"schema":"orkilab-repro-v1","vary":"lora","workflow_id":"wf1",
                    "prompt_sha256":"a"*64,"negative_prompt_sha256":"b"*64,
                    "input_sha256":"c"*64,"gpu_uuid":"GPU-123",
                    "cache":"cold","seed_policy":"fixed",
                    "repetitions":2,"resolution":[1024,1024]}
        with closing(sqlite3.connect(self.db)) as con, con:
            con.execute("UPDATE benchmark_runs SET protocol_json=? WHERE id='run-a'",
                        (json.dumps(protocol),))
            con.execute("INSERT INTO benchmark_variants VALUES (?,?,?,?)",
                        ("variant-b","run-a","Variant B",json.dumps({"controlled_value":"b.safetensors"})))
            con.execute("UPDATE benchmark_variants SET config_json=? WHERE id='variant-a'",
                        (json.dumps({"controlled_value":"a.safetensors"}),))
        wf = self.base / "settings" / "orkilab" / "workflows.sqlite3"
        with closing(sqlite3.connect(wf)) as con, con:
            con.execute("CREATE TABLE workflows (id TEXT,graph TEXT)")
            con.execute("INSERT INTO workflows VALUES (?,?)",(
                "wf1",json.dumps({"3":{"class_type":"LoraLoader","inputs":{
                    "lora_name":"base.safetensors","strength_model":1.0}},
                    "5":{"class_type":"CLIPTextEncode","inputs":{"text":"hello"}}})
            ))
        cfg = self.base / "settings" / "orkilab" / "comfyui.json"
        cfg.write_text(json.dumps({"mode":"hybrid","url":"http://127.0.0.1:8188",
            "model_folder":"","lora_folder":""}), encoding="utf-8")
        before = self.db.read_bytes()
        with patch("comfyui_connect.get_json",return_value={"LoraLoader":{
            "input":{"required":{"lora_name":[[
              "base.safetensors","a.safetensors","b.safetensors"]]}}}}) as fetch:
            response = self.client.get(
                "/api/workspace/benchmark/model-check?project_id=project-a&run_id=run-a")
        self.assertEqual(response.status_code,200,response.get_json())
        payload=response.get_json()
        self.assertEqual(payload["status"],"static_candidate")
        self.assertTrue(payload["graph_single_field_change_verified"])
        self.assertEqual(len(payload["variants"]),2)
        self.assertFalse(payload["comparison_execution_authorized"])
        self.assertFalse(payload["file_bytes_verified"])
        self.assertFalse(payload["generation_submitted"])
        self.assertEqual(self.db.read_bytes(),before)
        fetch.assert_called_once_with("http://127.0.0.1:8188",
            "/object_info/LoraLoader",max_bytes=500_000,timeout=5)

    def test_b10_2_incomplete_declaration_denied_without_comfyui_query(self):
        import json
        from unittest.mock import patch
        self.fill()
        with closing(sqlite3.connect(self.db)) as con, con:
            con.execute(
                "UPDATE benchmark_runs SET protocol_json=? WHERE id='run-a'",
                (json.dumps({"schema":"orkilab-repro-v1","vary":"lora",
                             "workflow_id":"wf1"}),),
            )
        with patch("comfyui_connect.get_json") as fetch:
            response = self.client.get(
                "/api/workspace/benchmark/model-check?project_id=project-a&run_id=run-a"
            )
            self.assertEqual(response.status_code, 409, response.get_json())
            self.assertFalse(response.get_json()["comparison_execution_authorized"])
            fetch.assert_not_called()

    def test_b10_2_denies_remote_and_cross_project_without_network(self):
        from unittest.mock import patch
        self.fill()
        with patch("comfyui_connect.get_json") as fetch:
            self.assertEqual(self.client.get(
                "/api/workspace/benchmark/model-check?project_id=project-a&run_id=run-a",
                environ_overrides={"REMOTE_ADDR":"198.51.100.90"}).status_code,403)
            self.assertEqual(self.client.get(
                "/api/workspace/benchmark/model-check?project_id=project-b&run_id=run-a"
                ).status_code,404)
            self.assertEqual(self.client.get(
                "/api/workspace/benchmark/model-check?project_id=../bad&run_id=run-a"
                ).status_code,400)
            fetch.assert_not_called()

    def test_b10_1_declared_plan_does_not_authorize_execution(self):
        self.fill()
        before = self.db.read_bytes()
        response = self.client.get(
            "/api/workspace/benchmark/reports/run-a?project_id=project-a"
        )
        self.assertEqual(response.status_code, 200, response.get_json())
        preflight = response.get_json()["b10_comparison_preflight"]
        self.assertEqual(preflight["declaration_status"], "incomplete")
        self.assertFalse(preflight["comparison_execution_authorized"])
        self.assertFalse(preflight["generation_submitted"])
        self.assertFalse(preflight["ranking_eligible"])
        self.assertEqual(self.db.read_bytes(), before)

    def test_b9_10_closeout_read_only_and_not_a_ranking(self):
        self.fill()
        before = self.db.read_bytes()
        response = self.client.get(
            "/api/workspace/benchmark/reports/run-a?project_id=project-a"
        )
        self.assertEqual(response.status_code, 200, response.get_json())
        closure = response.get_json()["b9_closure"]
        self.assertEqual(closure["status"], "not_fully_verified")
        self.assertFalse(closure["ranking_eligible"])
        self.assertFalse(closure["execution_verified"])
        self.assertFalse(closure["generation_submitted"])
        self.assertFalse(closure["database_modified"])
        self.assertIsNone(closure["best_variant"])
        self.assertEqual(self.db.read_bytes(), before)

    def test_b9_9_missing_history_cannot_claim_local_record_match(self):
        self.fill()
        response = self.client.get(
            "/api/workspace/benchmark/reports/run-a?project_id=project-a"
        )
        self.assertEqual(response.status_code, 200, response.get_json())
        check = response.get_json()["saved_history_consistency"]
        self.assertEqual(check["variants"][0]["status"], "incomplete")
        self.assertFalse(check["remote_execution_verified"])

    def test_b9_8_read_only_report_does_not_claim_submitted_content_proof(self):
        self.fill()
        response = self.client.get(
            "/api/workspace/benchmark/reports/run-a?project_id=project-a"
        )
        self.assertEqual(response.status_code, 200, response.get_json())
        verification = response.get_json()["recorded_execution_evidence"]
        self.assertEqual(verification["status"], "no_execution_evidence")
        self.assertFalse(verification["ranking_eligible"])
        self.assertFalse(verification["variants"][0]["prompt_content_verified"])
        self.assertIn("no_recorded_generation_lineage",
                      verification["variants"][0]["reason_codes"])
        self.assertNotIn("generation_lineage", response.get_json()["variants"][0])

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
