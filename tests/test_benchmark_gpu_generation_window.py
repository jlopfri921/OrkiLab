"""B8.2f time-window attribution safety, isolated fixtures only."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from benchmark_gpu_generation_window import analyze_generation_window


START = 1_800_000_000_000
END = START + 3000


def history():
    return {"status": {"completed": True, "messages": [
        ["execution_start", {"prompt_id": "prompt", "timestamp": START}],
        ["execution_success", {"prompt_id": "prompt", "timestamp": END}],
    ]}}


def measure(offset, used, uuid="GPU-test"):
    return {"epoch_ms": START + offset, "gpu_uuid": uuid,
            "used_bytes": used, "total_bytes": 24_000}


class GenerationWindowTests(unittest.TestCase):
    def test_global_memory_inside_window_not_attributed_to_job(self):
        samples = [measure(-100, 6000), measure(0, 6100),
                   measure(1000, 7100), measure(2000, 6700),
                   measure(3000, 6300), measure(3100, 9000)]
        result = analyze_generation_window(history(), "prompt", samples,
                                           gpu_uuid="GPU-test")
        self.assertTrue(result["window_supported_by_server_events"])
        self.assertEqual(result["sample_count_in_window"], 4)
        self.assertEqual(result["max_observed_global_used_bytes"], 7100)
        self.assertEqual(result["observed_global_increase_bytes"], 1000)
        self.assertEqual(result["window_coverage"], "sampled_within_configured_gap")
        self.assertFalse(result["attributable_to_generation"])
        self.assertIsNone(result["peak_vram_bytes"])

    def test_missing_execution_history_returns_unknown_metric(self):
        result = analyze_generation_window({}, "prompt",
                                           [measure(1000, 5000)],
                                           gpu_uuid="GPU-test")
        self.assertFalse(result["window_supported_by_server_events"])
        self.assertIsNone(result["max_observed_global_used_bytes"])
        self.assertFalse(result["benchmark_database_modified"])

    def test_sparse_sampling_does_not_claim_complete_window(self):
        result = analyze_generation_window(history(), "prompt",
                                           [measure(1500, 8000)],
                                           gpu_uuid="GPU-test")
        self.assertEqual(result["window_coverage"], "incomplete_sampling")
        self.assertIsNone(result["peak_vram_bytes"])

    def test_no_samples_inside_window(self):
        result = analyze_generation_window(history(), "prompt",
                                           [measure(-10, 5000),
                                            measure(3010, 6000)],
                                           gpu_uuid="GPU-test")
        self.assertEqual(result["window_coverage"], "no_samples_in_window")
        self.assertIsNone(result["max_observed_global_used_bytes"])

    def test_bad_gpu_timestamp_and_memory_rejected(self):
        bad = (
            [measure(0, 6000), measure(1000, 7000, uuid="GPU-other")],
            [measure(1000, 6000), measure(0, 5000)],
            [measure(0, 30000)],
            [dict(measure(0, 4000), epoch_ms=100.0)],
        )
        for samples in bad:
            with self.subTest(samples=samples):
                with self.assertRaises(ValueError):
                    analyze_generation_window(history(), "prompt", samples,
                                              gpu_uuid="GPU-test")

    def test_concurrency_is_annotation_not_claim_of_isolation(self):
        result = analyze_generation_window(
            history(), "prompt", [measure(0, 5000), measure(1000, 7000),
                                  measure(2000, 6500), measure(3000, 6000)],
            gpu_uuid="GPU-test", concurrent_gpu_activity_observed=True
        )
        self.assertTrue(result["concurrent_gpu_activity_observed"])
        self.assertFalse(result["attributable_to_generation"])


if __name__ == "__main__":
    unittest.main()
