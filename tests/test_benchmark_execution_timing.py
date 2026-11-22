"""B8.1: exactly matching ComfyUI server timestamps, never poll estimates."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from benchmark_execution_timing import measured_execution_timing, sampler_cache_assessment


class ExecutionTimingTests(unittest.TestCase):
    def entry(self, messages, completed=True):
        return {"status": {"completed": completed, "messages": messages}}

    def event(self, name, timestamp, prompt="prompt-a"):
        return [name, {"prompt_id": prompt, "timestamp": timestamp}]

    def test_exact_prompt_success_excludes_queue_time(self):
        entry = self.entry([
            self.event("execution_start", 1_800_000_000_000),
            self.event("execution_success", 1_800_000_002_345),
        ])
        result = measured_execution_timing(entry, "prompt-a")
        self.assertEqual(result["duration_ms"], 2345)
        self.assertFalse(result["includes_queue_wait"])
        self.assertEqual(result["source"], "comfyui_history_status_messages")

    def test_sampler_cache_assessment_distinguishes_warm_sampler(self):
        graph = {
            "1": {"class_type": "UNETLoader", "inputs": {}},
            "7": {"class_type": "KSampler", "inputs": {"seed": 43}},
            "9": {"class_type": "SaveImage", "inputs": {}},
        }
        cached_loaders = self.entry([
            self.event("execution_start", 1_800_000_000_000),
            ["execution_cached", {"prompt_id": "prompt-a", "nodes": ["1"]}],
            self.event("execution_success", 1_800_000_013_622),
        ])
        evidence = sampler_cache_assessment(graph, cached_loaders, "prompt-a")
        self.assertEqual(evidence["sampler_node_ids"], ["7"])
        self.assertEqual(evidence["sampler_cached_node_ids"], [])
        self.assertEqual(evidence["comparability"], "sampler_cache_miss_partial_cache")
        self.assertFalse(evidence["full_inference_verified"])
        cached_sampler = self.entry([
            ["execution_cached", {"prompt_id": "prompt-a", "nodes": ["1", "7"]}],
        ])
        self.assertEqual(
            sampler_cache_assessment(graph, cached_sampler, "prompt-a")["comparability"],
            "sampler_cached_not_comparable",
        )

    def test_unknown_sampler_and_other_prompt_are_not_misclassified(self):
        graph = {"7": {"class_type": "CustomSampler", "inputs": {}}}
        entry = self.entry([
            ["execution_cached", {"prompt_id": "prompt-a", "nodes": ["7"]}],
        ])
        self.assertEqual(sampler_cache_assessment(graph, entry, "prompt-a")["comparability"], "unverified")
        graph["7"]["class_type"] = "KSampler"
        self.assertEqual(
            sampler_cache_assessment(graph, entry, "other-prompt")["comparability"],
            "sampler_cache_unverified",
        )
        self.assertEqual(sampler_cache_assessment([], entry, "prompt-a")["comparability"], "unverified")

    def test_absent_events_return_none(self):
        self.assertIsNone(measured_execution_timing(self.entry([]), "prompt-a"))
        self.assertIsNone(measured_execution_timing(self.entry([
            self.event("execution_start", 1_800_000_000_000),
        ]), "prompt-a"))
        self.assertIsNone(measured_execution_timing(self.entry([
            self.event("execution_start", 1_800_000_000_000),
            self.event("execution_success", 1_800_000_002_000),
        ], completed=False), "prompt-a"))

    def test_other_prompt_and_bad_event_shapes_not_counted(self):
        self.assertIsNone(measured_execution_timing(self.entry([
            self.event("execution_start", 1_800_000_000_000, "other"),
            self.event("execution_success", 1_800_000_002_000),
        ]), "prompt-a"))
        self.assertIsNone(measured_execution_timing(self.entry([
            self.event("execution_start", 1_800_000_000_000),
            self.event("execution_start", 1_800_000_000_500),
            self.event("execution_success", 1_800_000_002_000),
        ]), "prompt-a"))

    def test_invalid_timestamps_and_clock_reversal_rejected(self):
        for invalid in (True, "1800000000000", float("nan"), -42):
            with self.subTest(invalid=invalid):
                self.assertIsNone(measured_execution_timing(self.entry([
                    self.event("execution_start", invalid),
                    self.event("execution_success", 1_800_000_002_000),
                ]), "prompt-a"))
        self.assertIsNone(measured_execution_timing(self.entry([
            self.event("execution_start", 1_800_000_002_000),
            self.event("execution_success", 1_800_000_000_000),
        ]), "prompt-a"))


if __name__ == "__main__":
    unittest.main()
