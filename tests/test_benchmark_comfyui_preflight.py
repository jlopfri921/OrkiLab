"""B7 read-only ComfyUI preflight contract tests; no live external calls."""
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from benchmark_comfyui_preflight import assess_preflight, check_live


class BenchmarkPreflightTests(unittest.TestCase):
    def setUp(self):
        self.cfg = {"mode": "hybrid", "url": "http://127.0.0.1:8188"}
        self.stats = {"system": {"comfyui_version": "fixture"}, "devices": [{"name": "Mock GPU"}]}
        self.queue = {"queue_running": [], "queue_pending": []}
        self.temp = tempfile.TemporaryDirectory()
        path = Path(self.temp.name) / "settings" / "orkilab"
        path.mkdir(parents=True)
        (path / "comfyui.json").write_text(json.dumps(self.cfg), encoding="utf-8")

    def tearDown(self):
        self.temp.cleanup()

    def test_idle_valid_queue_allows_readiness_without_generation(self):
        result = assess_preflight(self.cfg, training_active=False,
                                  system_stats=self.stats, queue=self.queue)
        self.assertTrue(result["ready"])
        self.assertEqual(result["devices"], ["Mock GPU"])

    def test_training_or_pending_queue_blocks(self):
        self.assertFalse(assess_preflight(self.cfg, training_active=True,
                                         system_stats=self.stats, queue=self.queue)["ready"])
        occupied = {"queue_running": [], "queue_pending": [[1, "other-job"]]}
        self.assertFalse(assess_preflight(self.cfg, training_active=False,
                                         system_stats=self.stats, queue=occupied)["ready"])

    def test_missing_queue_fields_fails_closed(self):
        result = assess_preflight(self.cfg, training_active=False,
                                  system_stats=self.stats, queue={})
        self.assertFalse(result["ready"])

    def test_live_check_only_queries_two_read_only_endpoints(self):
        calls = []
        def fake_fetch(url, path, **kwargs):
            calls.append((url, path))
            return self.stats if path == "/system_stats" else self.queue
        result = check_live(Path(self.temp.name), fetch=fake_fetch,
                            is_training=lambda base: False)
        self.assertTrue(result["ready"])
        self.assertEqual([path for _, path in calls], ["/system_stats", "/queue"])

    def test_active_training_makes_zero_http_calls(self):
        calls = []
        result = check_live(Path(self.temp.name), fetch=lambda *a, **k: calls.append(a),
                            is_training=lambda base: True)
        self.assertFalse(result["ready"])
        self.assertEqual(calls, [])


if __name__ == "__main__":
    unittest.main()
