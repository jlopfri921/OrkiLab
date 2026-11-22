"""B8.2g tests — fake ComfyUI and fake NVIDIA; no actual GPU/HTTP work."""
import json
import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from benchmark_gpu_live_capture import observe


class LiveCaptureTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.base = Path(self.temp.name)
        folder = self.base / "settings" / "orkilab"
        folder.mkdir(parents=True)
        (folder / "comfyui.json").write_text(
            json.dumps({"mode": "hybrid", "url": "http://127.0.0.1:8188"}),
            encoding="utf-8",
        )
        self.db = folder / "generations.sqlite3"
        with sqlite3.connect(self.db) as con:
            con.execute("CREATE TABLE generations (id TEXT, prompt_id TEXT, state TEXT, url TEXT)")
            con.execute("INSERT INTO generations VALUES (?,?,?,?)",
                        ("gen", "prompt-1", "running", "http://127.0.0.1:8188"))
        self.calls = []
        self.tick = iter((1_800_000_000.25, 1_800_000_000.35,
                          1_800_000_001.25, 1_800_000_001.35))
        self.status_count = 0

    def tearDown(self):
        self.temp.cleanup()

    def fetch(self, url, path, **kwargs):
        self.calls.append(path)
        if path == "/queue":
            return {"queue_running": [["x"]], "queue_pending": []}
        if path == "/history/prompt-1":
            self.status_count += 1
            if self.status_count < 3:
                return {}
            return {"prompt-1": {"status": {"completed": True, "messages": [
                ["execution_start", {"prompt_id": "prompt-1", "timestamp": 1_800_000_000_000}],
                ["execution_success", {"prompt_id": "prompt-1", "timestamp": 1_800_000_002_000}],
            ]}}}
        raise AssertionError("Unexpected read-only request " + path)

    def memory(self):
        return {"ok": True, "devices": [
            {"uuid": "GPU-test", "used_bytes": 7000, "total_bytes": 24000},
        ]}

    def test_existing_running_job_window_captures_without_writing(self):
        before = self.db.read_bytes()
        result = observe(
            self.base, "gen", gpu_uuid="GPU-test",
            samples_limit=3, interval_seconds=0.2,
            fetch=self.fetch, memory_sample=self.memory,
            epoch_clock=lambda: next(self.tick), sleep=lambda _: None,
        )
        self.assertTrue(result["ok"])
        self.assertEqual(result["termination"], "completed_history")
        self.assertEqual(result["sample_count_total"], 2)
        self.assertEqual(result["sample_count_in_window"], 2)
        self.assertEqual(result["max_observed_global_used_bytes"], 7000)
        self.assertIsNone(result["peak_vram_bytes"])
        self.assertFalse(result["attributable_to_generation"])
        self.assertEqual(self.db.read_bytes(), before)
        self.assertEqual(self.calls, [
            "/history/prompt-1", "/queue", "/history/prompt-1",
            "/queue", "/history/prompt-1"
        ])

    def test_completed_history_before_first_sample_is_safe(self):
        self.status_count = 2
        result = observe(
            self.base, "gen", gpu_uuid="GPU-test",
            samples_limit=2, interval_seconds=0.2,
            fetch=self.fetch, memory_sample=lambda: self.fail("No GPU poll expected"),
        )
        self.assertEqual(result["sample_count"], 0)
        self.assertFalse(result["window_supported_by_server_events"])

    def test_terminal_job_refused_before_polling(self):
        with sqlite3.connect(self.db) as con:
            con.execute("UPDATE generations SET state='completed'")
        with self.assertRaises(ValueError):
            observe(self.base, "gen", gpu_uuid="GPU-test",
                    fetch=lambda *a, **k: self.fail("No HTTP expected"))

    def test_unavailable_memory_discards_series(self):
        with self.assertRaises(ValueError):
            observe(
                self.base, "gen", gpu_uuid="GPU-test",
                samples_limit=2, interval_seconds=0.2, fetch=self.fetch,
                memory_sample=lambda: {"ok": False},
                epoch_clock=lambda: 1_800_000_000.1, sleep=lambda _: None
            )

    def test_bound_restrictions_prevent_any_network(self):
        for count, interval in ((1, 0.3), (121, 0.3), (2, 0.01), (2, 5.1)):
            with self.assertRaises(ValueError):
                observe(
                    self.base, "gen", gpu_uuid="GPU-test",
                    samples_limit=count, interval_seconds=interval,
                    fetch=lambda *a, **k: self.fail("No HTTP expected"),
                )


if __name__ == "__main__":
    unittest.main()
