"""B6: verify bridge reads existing GenerationHistory, without queue mutation."""
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from generation_history import GenerationHistory
from benchmark_history_bridge import prepare_history_observation


class BenchmarkHistoryBridgeTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.history = GenerationHistory(self.directory.name)
        self.history.add(
            "gen-1", "http://127.0.0.1:8188", "prompt-1", "workflow-1",
            "Test fixture", {"1": {"class_type": "SaveImage", "inputs": {}}},
        )

    def tearDown(self):
        self.directory.cleanup()

    def test_does_not_import_queued_job(self):
        with self.assertRaises(ValueError):
            prepare_history_observation(self.history, "gen-1")

    def test_reads_terminal_record_without_mutation(self):
        self.history.update("gen-1", "completed", [])
        before = self.history.get("gen-1")
        proposed = prepare_history_observation(self.history, "gen-1")
        after = self.history.get("gen-1")
        self.assertEqual(before, after)
        self.assertEqual(proposed["source_snapshot"]["comfyui_prompt_id"], "prompt-1")
        self.assertFalse(proposed["persisted"])
        self.assertIsNone(proposed["duration_ms"])

    def test_rejects_unknown_generation(self):
        with self.assertRaises(KeyError):
            prepare_history_observation(self.history, "missing")

    def test_does_not_turn_history_error_into_success(self):
        self.history.update("gen-1", "error", [])
        proposed = prepare_history_observation(self.history, "gen-1")
        self.assertEqual(proposed["status"], "failed")


if __name__ == "__main__":
    unittest.main()
