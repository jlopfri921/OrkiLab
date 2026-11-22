"""B9.3 evidence classifier — synthetic pure test cases, no GPU/DB."""
import copy
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from benchmark_comparability import assess_duration_comparability


def fixture():
    return {
        "run": {"id": "r1"},
        "variants": [
            {"id": "v1", "run_id": "r1"},
            {"id": "v2", "run_id": "r1"},
        ],
        "observations": [
            {"id": "o1", "run_id": "r1", "variant_id": "v1",
             "repetition": 0, "status": "completed",
             "duration_ms": 2000,
             "generation_lineage": {
                 "workflow_id": "workflow-1",
                 "submitted_graph_sha256": "a" * 64,
                 "execution_timing": {
                     "source": "comfyui_history_status_messages",
                     "sampler_cache_status": "not_listed_as_cached",
                     "comparability": "sampler_cache_miss_partial_cache",
                     "full_inference_verified": False,
                 },
             }},
        ],
    }


class BenchmarkComparabilityTests(unittest.TestCase):
    def test_identical_workflow_and_duration_never_claim_ranking(self):
        sample = fixture()
        before = copy.deepcopy(sample)
        result = assess_duration_comparability(sample)
        self.assertEqual(result["variants"][0]["status"], "not_established")
        self.assertEqual(result["variants"][1]["status"], "not_established")
        self.assertFalse(result["ranking_eligible"])
        self.assertIsNone(result["best_variant"])
        self.assertIn("hardware_equivalence_not_verified",
                      result["variants"][0]["reason_codes"])
        self.assertEqual(sample, before)

    def test_explicit_cached_sampler_blocks_comparison(self):
        sample = fixture()
        sample["observations"][0]["generation_lineage"]["execution_timing"]["sampler_cache_status"] = "cached"
        result = assess_duration_comparability(sample)
        self.assertEqual(result["status"], "blocked")
        self.assertIn("cached_sampler_observed", result["variants"][0]["reason_codes"])

    def test_cached_sampler_blocks_even_when_duration_is_null(self):
        sample = fixture()
        sample["observations"][0]["duration_ms"] = None
        timing = sample["observations"][0]["generation_lineage"]["execution_timing"]
        timing["sampler_cache_status"] = "cached"
        timing["comparability"] = "sampler_cached_not_comparable"
        result = assess_duration_comparability(sample)
        item = result["variants"][0]
        self.assertEqual(item["status"], "blocked")
        self.assertEqual(item["measured_observations"], 0)
        self.assertIn("cached_sampler_observed", item["reason_codes"])
        self.assertIn("no_completed_measured_duration", item["reason_codes"])

    def test_cached_sampler_on_untimed_repeat_blocks_timed_repeats(self):
        sample = fixture()
        other = copy.deepcopy(sample["observations"][0])
        other["id"], other["repetition"] = "uncounted", 1
        other["duration_ms"] = None
        other["generation_lineage"]["execution_timing"]["sampler_cache_status"] = "cached"
        sample["observations"].append(other)
        result = assess_duration_comparability(sample)
        self.assertEqual(result["variants"][0]["status"], "blocked")
        self.assertEqual(result["variants"][0]["measured_observations"], 1)
        self.assertIn("incomplete_duration_coverage",
                      result["variants"][0]["reason_codes"])

    def test_unverified_missing_lineage_not_auto_blocked(self):
        sample = fixture()
        sample["observations"][0]["generation_lineage"] = None
        result = assess_duration_comparability(sample)
        self.assertEqual(result["variants"][0]["status"], "not_established")
        self.assertIn("missing_generation_lineage", result["variants"][0]["reason_codes"])

    def test_two_distinct_workflows_within_variant_are_blocked(self):
        sample = fixture()
        other = copy.deepcopy(sample["observations"][0])
        other["id"], other["repetition"] = "o2", 1
        other["generation_lineage"]["workflow_id"] = "workflow-2"
        sample["observations"].append(other)
        result = assess_duration_comparability(sample)
        self.assertEqual(result["variants"][0]["status"], "blocked")
        self.assertIn("different_workflows_within_variant", result["variants"][0]["reason_codes"])

    def test_changed_graph_fingerprint_is_not_inferred_failure(self):
        sample = fixture()
        other = copy.deepcopy(sample["observations"][0])
        other["id"], other["repetition"] = "o2", 1
        other["generation_lineage"]["submitted_graph_sha256"] = "b" * 64
        sample["observations"].append(other)
        item = assess_duration_comparability(sample)["variants"][0]
        self.assertEqual(item["status"], "not_established")
        self.assertIn("graph_changed_between_repetitions", item["reason_codes"])

    def test_missing_duration_observed_as_missing_not_zero(self):
        sample = fixture()
        sample["observations"][0]["duration_ms"] = None
        item = assess_duration_comparability(sample)["variants"][0]
        self.assertEqual(item["measured_observations"], 0)
        self.assertIn("no_completed_measured_duration", item["reason_codes"])

    def test_malformed_project_lineage_fails_closed(self):
        sample = fixture()
        sample["observations"][0]["run_id"] = "r2"
        with self.assertRaises(ValueError):
            assess_duration_comparability(sample)

    def test_invalid_shape_rejected(self):
        for sample in (None, {}, {"run": {}, "variants": [], "observations": []}):
            with self.assertRaises(ValueError):
                assess_duration_comparability(sample)


if __name__ == "__main__":
    unittest.main()
