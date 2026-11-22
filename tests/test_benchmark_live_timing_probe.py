"""Read-only B8.1 probe tests with isolated SQLite + fake ComfyUI GET."""
import json
import sqlite3
import sys
import tempfile
import unittest
from contextlib import closing
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from benchmark_live_timing_probe import inspect
from generation_history import GenerationHistory


class LiveTimingProbeTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        folder = self.root / "settings" / "orkilab"
        folder.mkdir(parents=True)
        (folder / "comfyui.json").write_text(
            json.dumps({"mode": "hybrid", "url": "http://127.0.0.1:8188"}),
            encoding="utf-8",
        )
        self.hist = GenerationHistory(self.root)
        self.hist.add("gen", "http://127.0.0.1:8188", "prompt",
                      "wf", "fixture", {"1": {"class_type": "SaveImage", "inputs": {}}})
        self.hist.update("gen", "completed", [])
        self.calls = []
        self.messages = [
            ["execution_start", {"prompt_id": "prompt", "timestamp": 1_800_000_000_000}],
            ["execution_success", {"prompt_id": "prompt", "timestamp": 1_800_000_001_500}],
        ]

    def tearDown(self):
        self.tmp.cleanup()

    def fetch(self, url, path, **kwargs):
        self.calls.append((url, path))
        return {"prompt": {"status": {"completed": True, "messages": self.messages}}}

    def test_reports_real_events_without_writing_database(self):
        folder = self.root / "settings" / "orkilab"
        db = folder / "generations.sqlite3"
        before = db.read_bytes()
        result = inspect(self.root, "gen", fetch=self.fetch)
        self.assertTrue(result["ok"])
        self.assertTrue(result["measured"])
        self.assertEqual(result["duration_ms"], 1500)
        self.assertEqual(result["cache_status"], "undetermined")
        self.assertFalse(result["full_inference_verified"])
        self.assertEqual(self.calls, [("http://127.0.0.1:8188", "/history/prompt")])
        self.assertEqual(db.read_bytes(), before)
        self.assertFalse((folder / "benchmarks.sqlite3").exists())

    def test_missing_event_reports_unknown(self):
        self.messages = []
        result = inspect(self.root, "gen", fetch=self.fetch)
        self.assertTrue(result["ok"])
        self.assertFalse(result["measured"])
        self.assertIsNone(result["duration_ms"])

    def test_cache_event_is_reported_without_claiming_full_inference(self):
        self.messages.insert(
            1, ["execution_cached", {"prompt_id": "prompt", "nodes": ["1"]}]
        )
        result = inspect(self.root, "gen", fetch=self.fetch)
        self.assertTrue(result["measured"])
        self.assertEqual(result["cache_status"], "cache_event_observed")
        self.assertTrue(result["execution_cached_event_observed"])
        self.assertFalse(result["full_inference_verified"])

    def test_bad_generation_makes_zero_http_calls(self):
        self.assertFalse(inspect(self.root, "other", fetch=self.fetch)["ok"])
        self.assertFalse(inspect(self.root, "../bad", fetch=self.fetch)["ok"])
        self.assertEqual(self.calls, [])


if __name__ == "__main__":
    unittest.main()
