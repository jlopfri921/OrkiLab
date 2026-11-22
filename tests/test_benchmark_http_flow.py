"""B6f: Flask route integration using a fake ComfyUI; never contacts a GPU.

Exercises the real Generation Studio HTTP endpoints, generation history,
benchmark binding and finalization in isolated temporary SQLite databases.
"""
import json
import sqlite3
import sys
import tempfile
import unittest
from contextlib import closing
from pathlib import Path
from unittest.mock import patch

from flask import Flask

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import generation_studio
from benchmark_store import BenchmarkStore
from workspace_store import ProjectStore


class BenchmarkHttpFlowTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        settings = self.root / "settings" / "orkilab"
        settings.mkdir(parents=True)
        (settings / "comfyui.json").write_text(
            json.dumps({"mode": "hybrid", "url": "http://127.0.0.1:8188"}),
            encoding="utf-8",
        )
        self.graph = {"1": {"class_type": "SaveImage", "inputs": {}}}
        with closing(sqlite3.connect(settings / "workflows.sqlite3")) as con, con:
            con.execute("CREATE TABLE workflows (id TEXT PRIMARY KEY, name TEXT, graph TEXT)")
            con.execute(
                "INSERT INTO workflows VALUES (?,?,?)",
                ("workflow-1", "Fixture workflow", json.dumps(self.graph)),
            )
        project_store = ProjectStore(settings / "projects.sqlite3")
        project = project_store.create({
            "name": "Fixture project", "engine": "fixture", "category": "image"
        }, {"fixture"})
        self.project_id = project["id"]
        self.benchmark_path = settings / "benchmarks.sqlite3"
        with BenchmarkStore(self.benchmark_path) as bench:
            self.run_id = bench.create_run(self.project_id, "Integration", {"seed": 42})
            self.variant_id = bench.add_variant(self.run_id, "checkpoint-1", {"weight": 0.5})
            bench.transition(self.run_id, "running")
        self.app = Flask(__name__)
        generation_studio.register(self.app, self.root)
        self.client = self.app.test_client()
        self.mock_queue = {"queue_running": [], "queue_pending": []}
        self.history_entry = None
        self.submitted_requests = []
        self.patches = [
            patch.object(generation_studio, "inspect_graph", return_value={"format": "api"}),
            patch.object(generation_studio, "node_schema", return_value={}),
            patch.object(generation_studio, "validate_prompt", return_value=None),
            patch.object(generation_studio, "editable_fields", return_value=[]),
            patch.object(generation_studio, "build_opener", side_effect=self.fake_opener),
            patch.object(generation_studio.project_layout, "training_in_progress", return_value=False),
            patch.object(generation_studio, "get_json", side_effect=self.fake_comfyui),
        ]
        for mocked in self.patches:
            mocked.start()

    def tearDown(self):
        for mocked in reversed(self.patches):
            mocked.stop()
        self.temp.cleanup()

    def fake_opener(self, *handlers):
        """Intercept only the real nested submit() HTTP call; never use network."""
        testcase = self

        class Response:
            status = 200

            def __enter__(self):
                return self

            def __exit__(self, *args):
                return None

            def read(self, *args):
                return json.dumps({"prompt_id": "prompt-comfy"}).encode("utf-8")

        class Opener:
            def open(self, request, timeout=None):
                if request.full_url != "http://127.0.0.1:8188/prompt" or request.get_method() != "POST":
                    raise AssertionError("Unexpected HTTP request: " + request.full_url)
                testcase.submitted_requests.append(request)
                return Response()

        return Opener()

    def fake_comfyui(self, url, path, **kwargs):
        if path == "/queue":
            return self.mock_queue
        if path == "/history/prompt-comfy":
            return {"prompt-comfy": self.history_entry} if self.history_entry else {}
        raise AssertionError("Unexpected external request: " + path)

    def prepare(self):
        response = self.client.post(
            "/api/workspace/generation/prepare", json={"workflow_id": "workflow-1"}
        )
        self.assertEqual(response.status_code, 200, response.get_json())
        return response.get_json()["token"]

    def submit(self, with_benchmark=True, project_id=None):
        payload = {
            "workflow_id": "workflow-1", "confirm": True,
            "token": self.prepare(),
        }
        if with_benchmark:
            payload["benchmark"] = {
                "project_id": project_id or self.project_id,
                "run_id": self.run_id,
                "variant_id": self.variant_id,
                "repetition": 0,
                "confirm": True,
            }
        return self.client.post("/api/workspace/generation", json=payload)

    def observations(self):
        with BenchmarkStore(self.benchmark_path) as bench:
            return bench.report(self.run_id)["observations"]

    def test_capabilities_reports_live_benchmark_route_without_submitting(self):
        response = self.client.get("/api/workspace/generation/capabilities")
        self.assertEqual(response.status_code, 200)
        body = response.get_json()
        self.assertEqual(body["generation_studio"], "benchmark-submission-v1")
        self.assertIs(body["benchmark_submit"], True)
        self.assertIs(body["benchmark_terminal_finalization"], True)
        self.assertEqual(self.submitted_requests, [])
        self.assertEqual(self.observations(), [])

    def test_capabilities_rejects_nonlocal_client(self):
        response = self.client.get(
            "/api/workspace/generation/capabilities",
            environ_overrides={"REMOTE_ADDR": "192.0.2.10"},
        )
        self.assertEqual(response.status_code, 403)
        self.assertEqual(self.submitted_requests, [])

    def test_benchmark_submission_and_terminal_status_records_once(self):
        created = self.submit()
        self.assertEqual(created.status_code, 201, created.get_json())
        job = created.get_json()
        self.assertEqual(job["benchmark_binding"], "bound")
        self.assertEqual(len(self.submitted_requests), 1)
        token = job["id"]
        self.history_entry = {"status": {"completed": True, "status_str": "success"},
                              "outputs": {}}
        status = self.client.get("/api/workspace/generation/" + token)
        self.assertEqual(status.status_code, 200)
        self.assertEqual(status.get_json()["state"], "completed")
        self.assertEqual(self.client.get("/api/workspace/generation/" + token).status_code, 200)
        rows = self.observations()
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["generation_lineage"]["generation_id"], token)
        self.assertIsNone(rows[0]["peak_vram_bytes"])

    def test_real_comfyui_history_event_duration_is_stored_with_provenance(self):
        created = self.submit()
        self.assertEqual(created.status_code, 201, created.get_json())
        token = created.get_json()["id"]
        self.history_entry = {
            "status": {
                "completed": True,
                "status_str": "success",
                "messages": [
                    ["execution_start", {"prompt_id": "prompt-comfy", "timestamp": 1_800_000_000_000}],
                    ["execution_success", {"prompt_id": "prompt-comfy", "timestamp": 1_800_000_003_600}],
                ],
            },
            "outputs": {},
        }
        result = self.client.get("/api/workspace/generation/" + token)
        self.assertEqual(result.status_code, 200)
        self.assertEqual(result.get_json()["state"], "completed")
        first = self.observations()
        self.assertEqual(len(first), 1)
        self.assertEqual(first[0]["duration_ms"], 3600)
        self.assertEqual(
            first[0]["generation_lineage"]["execution_timing"]["source"],
            "comfyui_history_status_messages",
        )
        self.assertIsNone(first[0]["peak_vram_bytes"])
        # Terminal polling and a launcher restart must never duplicate or
        # rewrite the original measurement.
        self.assertEqual(self.client.get("/api/workspace/generation/" + token).status_code, 200)
        self.assertEqual(self.observations(), first)

    def test_cached_generation_retains_interval_only_as_audit_not_comparison(self):
        created = self.submit()
        self.assertEqual(created.status_code, 201, created.get_json())
        token = created.get_json()["id"]
        self.history_entry = {
            "status": {
                "completed": True, "status_str": "success",
                "messages": [
                    ["execution_start", {"prompt_id": "prompt-comfy", "timestamp": 1_800_000_000_000}],
                    ["execution_cached", {"prompt_id": "prompt-comfy", "nodes": ["1"]}],
                    ["execution_success", {"prompt_id": "prompt-comfy", "timestamp": 1_800_000_000_014}],
                ],
            },
            "outputs": {},
        }
        status = self.client.get("/api/workspace/generation/" + token)
        self.assertEqual(status.status_code, 200)
        self.assertEqual(status.get_json()["state"], "completed")
        rows = self.observations()
        self.assertEqual(len(rows), 1)
        self.assertIsNone(rows[0]["duration_ms"])
        timing = rows[0]["generation_lineage"]["execution_timing"]
        self.assertEqual(timing["duration_ms"], 14)
        self.assertTrue(timing["execution_cached_event_observed"])
        self.assertEqual(timing["comparability"], "cache_observed_not_comparable")
        self.assertFalse(timing["full_inference_verified"])
        self.assertEqual(self.client.get("/api/workspace/generation/" + token).status_code, 200)
        self.assertEqual(self.observations(), rows)

    def test_warm_sampler_duration_kept_when_loader_cached(self):
        self.graph["7"] = {"class_type": "KSampler", "inputs": {"seed": 43}}
        with closing(sqlite3.connect(
            self.root / "settings" / "orkilab" / "workflows.sqlite3"
        )) as con, con:
            con.execute("UPDATE workflows SET graph=? WHERE id=?",
                        (json.dumps(self.graph), "workflow-1"))
        created = self.submit()
        self.assertEqual(created.status_code, 201, created.get_json())
        token = created.get_json()["id"]
        self.history_entry = {
            "status": {"completed": True, "status_str": "success", "messages": [
                ["execution_start", {"prompt_id": "prompt-comfy", "timestamp": 1_800_000_000_000}],
                ["execution_cached", {"prompt_id": "prompt-comfy", "nodes": ["1"]}],
                ["execution_success", {"prompt_id": "prompt-comfy", "timestamp": 1_800_000_013_622}],
            ]}, "outputs": {},
        }
        self.assertEqual(
            self.client.get("/api/workspace/generation/" + token).get_json()["state"],
            "completed",
        )
        observation = self.observations()[0]
        self.assertEqual(observation["duration_ms"], 13622)
        timing = observation["generation_lineage"]["execution_timing"]
        self.assertEqual(timing["sampler_node_ids"], ["7"])
        self.assertEqual(timing["sampler_cached_node_ids"], [])
        self.assertEqual(timing["comparability"], "sampler_cache_miss_partial_cache")
        self.assertFalse(timing["full_inference_verified"])

    def test_cached_sampler_never_populates_comparison_duration(self):
        self.graph["7"] = {"class_type": "KSampler", "inputs": {"seed": 42}}
        with closing(sqlite3.connect(
            self.root / "settings" / "orkilab" / "workflows.sqlite3"
        )) as con, con:
            con.execute("UPDATE workflows SET graph=? WHERE id=?",
                        (json.dumps(self.graph), "workflow-1"))
        created = self.submit()
        self.assertEqual(created.status_code, 201, created.get_json())
        token = created.get_json()["id"]
        self.history_entry = {
            "status": {"completed": True, "status_str": "success", "messages": [
                ["execution_start", {"prompt_id": "prompt-comfy", "timestamp": 1_800_000_000_000}],
                ["execution_cached", {"prompt_id": "prompt-comfy", "nodes": ["1", "7"]}],
                ["execution_success", {"prompt_id": "prompt-comfy", "timestamp": 1_800_000_000_014}],
            ]}, "outputs": {},
        }
        self.assertEqual(
            self.client.get("/api/workspace/generation/" + token).get_json()["state"],
            "completed",
        )
        observation = self.observations()[0]
        self.assertIsNone(observation["duration_ms"])
        timing = observation["generation_lineage"]["execution_timing"]
        self.assertEqual(timing["sampler_cached_node_ids"], ["7"])
        self.assertEqual(timing["comparability"], "sampler_cached_not_comparable")

    def test_missing_comfyui_events_never_infers_duration(self):
        created = self.submit()
        self.assertEqual(created.status_code, 201, created.get_json())
        token = created.get_json()["id"]
        self.history_entry = {"status": {"completed": True}, "outputs": {}}
        self.assertEqual(
            self.client.get("/api/workspace/generation/" + token).get_json()["state"],
            "completed",
        )
        self.assertIsNone(self.observations()[0]["duration_ms"])

    def test_cross_project_request_denied_before_submission(self):
        result = self.submit(project_id="not-active")
        self.assertEqual(result.status_code, 404)
        self.assertEqual(len(self.submitted_requests), 0)
        self.assertEqual(self.observations(), [])
        history_path = self.root / "settings" / "orkilab" / "generations.sqlite3"
        if history_path.is_file():
            with closing(sqlite3.connect(history_path)) as con:
                generation_rows = con.execute(
                    "SELECT count(*) FROM generations"
                ).fetchone()[0]
        else:
            generation_rows = 0
        self.assertEqual(generation_rows, 0)

    def test_normal_generation_does_not_create_binding(self):
        created = self.submit(with_benchmark=False)
        self.assertEqual(created.status_code, 201)
        self.assertNotIn("benchmark_binding", created.get_json())
        self.assertEqual(len(self.submitted_requests), 1)
        token = created.get_json()["id"]
        self.history_entry = {"status": {"completed": True}, "outputs": {}}
        self.assertEqual(
            self.client.get("/api/workspace/generation/" + token).get_json()["state"],
            "completed",
        )
        self.assertEqual(self.observations(), [])
        with BenchmarkStore(self.benchmark_path) as bench:
            count = bench.db.execute(
                "SELECT COUNT(*) FROM benchmark_generation_bindings"
            ).fetchone()[0]
            self.assertEqual(count, 0)

    def test_comfyui_error_records_failed_observation(self):
        created = self.submit()
        self.assertEqual(created.status_code, 201, created.get_json())
        token = created.get_json()["id"]
        self.history_entry = {"status": {"completed": False, "status_str": "error"},
                              "outputs": {}}
        response = self.client.get("/api/workspace/generation/" + token)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["state"], "error")
        rows = self.observations()
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["status"], "failed")
        self.assertEqual(rows[0]["generation_lineage"]["generation_id"], token)

    def test_running_job_does_not_finalize_benchmark(self):
        created = self.submit()
        self.assertEqual(created.status_code, 201, created.get_json())
        token = created.get_json()["id"]
        self.mock_queue = {
            "queue_running": [[1, "prompt-comfy"]],
            "queue_pending": [],
        }
        response = self.client.get("/api/workspace/generation/" + token)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["state"], "running")
        self.assertEqual(self.observations(), [])

    def test_cancelled_generation_history_records_cancelled_once(self):
        created = self.submit()
        self.assertEqual(created.status_code, 201, created.get_json())
        token = created.get_json()["id"]
        # The existing status handler finalizes a previously acknowledged
        # cancellation when ComfyUI no longer lists its prompt in the queue.
        from generation_history import GenerationHistory
        GenerationHistory(self.root).update(token, "cancelling", [])
        response = self.client.get("/api/workspace/generation/" + token)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["state"], "cancelled")
        self.assertEqual(self.client.get("/api/workspace/generation/" + token).status_code, 200)
        rows = self.observations()
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["status"], "cancelled")



if __name__ == "__main__":
    unittest.main()
