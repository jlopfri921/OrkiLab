"""Read-only ComfyUI generation-to-benchmark contract tests."""
import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from benchmark_generation_adapter import snapshot_generation

class GenerationBenchmarkAdapterTests(unittest.TestCase):
    def setUp(self):
        self.record = {
            "id": "generation-1",
            "workflow_id": "wf-1",
            "prompt_id": "comfy-job-1",
            "state": "completed",
            "graph": json.dumps({"1": {"class_type": "KSampler", "inputs": {"seed": 123}}}),
            "outputs": json.dumps([{"filename": "image.png", "type": "output"}]),
            "created": 1.0,
            "updated": 2.0,
        }

    def test_snapshot_has_graph_hash_and_no_fabricated_performance(self):
        snap = snapshot_generation(self.record)
        self.assertEqual(snap["status"], "completed")
        self.assertEqual(snap["output_count"], 1)
        self.assertEqual(len(snap["submitted_graph_sha256"]), 64)
        for key in ("seed", "duration_ms", "peak_vram_bytes", "output_sha256"):
            self.assertIsNone(snap[key])

    def test_graph_hash_deterministic_for_key_order(self):
        first = snapshot_generation(self.record)
        self.record["graph"] = {"1": {"inputs": {"seed": 123}, "class_type": "KSampler"}}
        second = snapshot_generation(self.record)
        self.assertEqual(first["submitted_graph_sha256"], second["submitted_graph_sha256"])

    def test_reject_running_or_untrusted_shapes(self):
        self.record["state"] = "running"
        with self.assertRaises(ValueError):
            snapshot_generation(self.record)
        self.record["state"] = "completed"
        self.record["outputs"] = "{}"
        with self.assertRaises(ValueError):
            snapshot_generation(self.record)

    def test_terminal_failure_maps_to_failed_without_fake_metric(self):
        self.record["state"] = "error"
        self.record["outputs"] = "[]"
        snap = snapshot_generation(self.record)
        self.assertEqual(snap["status"], "failed")
        self.assertIsNone(snap["duration_ms"])

if __name__ == "__main__":
    unittest.main()
