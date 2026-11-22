"""Contract tests for the read-only proposed observation bridge."""
import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from benchmark_generation_import import prepare_terminal_observation


class ObservationPreparationTests(unittest.TestCase):
    def setUp(self):
        self.entry = {
            "id": "generation-1", "workflow_id": "workflow-1",
            "prompt_id": "comfy-job-1", "state": "completed",
            "graph": json.dumps({"2": {"class_type": "SaveImage", "inputs": {}}}),
            "outputs": "[]",
        }

    def test_preserves_lineage_but_does_not_infer_metrics(self):
        proposal = prepare_terminal_observation(self.entry)
        self.assertFalse(proposal["persisted"])
        self.assertEqual(proposal["source_snapshot"]["generation_id"], "generation-1")
        self.assertEqual(len(proposal["source_snapshot"]["submitted_graph_sha256"]), 64)
        for key in ("seed", "duration_ms", "peak_vram_bytes", "output_sha256"):
            self.assertIsNone(proposal[key])

    def test_rejects_running_generation(self):
        self.entry["state"] = "running"
        with self.assertRaises(ValueError):
            prepare_terminal_observation(self.entry)

    def test_terminal_failure_is_not_silent_success(self):
        self.entry["state"] = "error"
        proposal = prepare_terminal_observation(self.entry)
        self.assertEqual(proposal["status"], "failed")
        self.assertIn("failed", proposal["error_message"])


if __name__ == "__main__":
    unittest.main()
