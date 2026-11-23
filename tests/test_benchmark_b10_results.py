"""B10.4 recorded median differences: display-only, never rankings."""
import copy
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from benchmark_b10_results import describe_cross_variant_measurements


def fixture():
    summary={"run_id":"r1","variants":[
        {"variant_id":"v1","label":"A","measured_duration_count":2,
         "duration_ms_median":1000},
        {"variant_id":"v2","label":"B","measured_duration_count":2,
         "duration_ms_median":1200},
    ]}
    comparability={"run_id":"r1","variants":[
        {"variant_id":"v1","status":"not_established"},
        {"variant_id":"v2","status":"not_established"},
    ]}
    return summary, comparability


class B10ResultDescriptionTests(unittest.TestCase):
    def test_two_complete_variants_are_descriptive_not_winners(self):
        inputs=fixture()
        before=copy.deepcopy(inputs)
        value=describe_cross_variant_measurements(*inputs)
        self.assertEqual(value["pair_count"],1)
        pair=value["pairs"][0]
        self.assertEqual(pair["median_b_minus_a_ms"],200)
        self.assertEqual(pair["status"],"observed_difference_unverified")
        self.assertFalse(pair["measured_comparability_verified"])
        self.assertFalse(value["ranking_eligible"])
        self.assertFalse(value["speedup_claim_allowed"])
        self.assertIsNone(value["best_variant"])
        self.assertFalse(value["generation_submitted"])
        self.assertEqual(inputs,before)

    def test_negative_difference_is_not_speed_proof(self):
        summary,compare=fixture()
        summary["variants"][1]["duration_ms_median"]=800
        item=describe_cross_variant_measurements(summary,compare)
        self.assertEqual(item["pairs"][0]["median_b_minus_a_ms"],-200)
        self.assertFalse(item["pairs"][0]["full_inference_verified"])

    def test_cached_sampler_blocks_descriptive_comparison(self):
        summary,compare=fixture()
        compare["variants"][1]["status"]="blocked"
        pair=describe_cross_variant_measurements(summary,compare)["pairs"][0]
        self.assertEqual(pair["status"],"observed_difference_blocked")
        self.assertFalse(pair["measured_comparability_verified"])

    def test_missing_duration_is_unknown_not_zero(self):
        summary,compare=fixture()
        summary["variants"][1]["duration_ms_median"]=None
        summary["variants"][1]["measured_duration_count"]=0
        pair=describe_cross_variant_measurements(summary,compare)["pairs"][0]
        self.assertEqual(pair["status"],"insufficient_measurements")
        self.assertIsNone(pair["median_b_minus_a_ms"])
        self.assertIsNone(pair["median_a_ms"])
        self.assertIsNone(pair["median_b_ms"])

    def test_nonfinite_median_is_unknown_and_never_serialized(self):
        for value in (float("nan"),float("inf"),float("-inf")):
            summary,compare=fixture()
            summary["variants"][1]["duration_ms_median"]=value
            pair=describe_cross_variant_measurements(summary,compare)["pairs"][0]
            self.assertIsNone(pair["median_b_minus_a_ms"])
            self.assertEqual(pair["status"],"insufficient_measurements")

    def test_multiple_variants_create_unique_pairs_not_ranking(self):
        summary,compare=fixture()
        summary["variants"].append({"variant_id":"v3","label":"C",
            "measured_duration_count":1,"duration_ms_median":1500})
        compare["variants"].append({"variant_id":"v3","status":"not_established"})
        value=describe_cross_variant_measurements(summary,compare)
        self.assertEqual(value["pair_count"],3)
        self.assertFalse(value["ranking_eligible"])

    def test_cross_run_and_unmatched_variant_rejected(self):
        summary,compare=fixture()
        compare["run_id"]="other"
        with self.assertRaises(ValueError):
            describe_cross_variant_measurements(summary,compare)
        compare["run_id"]="r1"
        compare["variants"].pop()
        with self.assertRaises(ValueError):
            describe_cross_variant_measurements(summary,compare)

    def test_duplicate_ids_or_too_many_variants_rejected(self):
        summary,compare=fixture()
        summary["variants"][1]["variant_id"]="v1"
        with self.assertRaises(ValueError):
            describe_cross_variant_measurements(summary,compare)
        summary,compare=fixture()
        for index in range(19):
            ident=f"new-{index}"
            summary["variants"].append({"variant_id":ident,
                "measured_duration_count":1,"duration_ms_median":100})
            compare["variants"].append({"variant_id":ident,"status":"not_established"})
        with self.assertRaises(ValueError):
            describe_cross_variant_measurements(summary,compare)

    def test_empty_variants_acceptable_and_unranked(self):
        value=describe_cross_variant_measurements(
            {"run_id":"r1","variants":[]},{"run_id":"r1","variants":[]})
        self.assertEqual(value["pair_count"],0)
        self.assertIsNone(value["best_variant"])

    def test_invalid_payload_rejected(self):
        for a,b in ((None,{}),({},{}),({"run_id":"r1","variants":[]},None)):
            with self.assertRaises(ValueError):
                describe_cross_variant_measurements(a,b)


if __name__=="__main__":
    unittest.main()
