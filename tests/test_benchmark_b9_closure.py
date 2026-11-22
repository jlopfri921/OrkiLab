"""B9.10 closure: incomplete facts must never generate proof or rankings."""
import copy
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from benchmark_b9_closure import summarize_b9_closure


def fixture():
    return {
        "reproducibility_protocol": {"status": "declared_unverified", "variants": [{"variant_id":"v1"}]},
        "comparability": {"status":"not_established","variants":[{"status":"not_established"}]},
        "recorded_execution_evidence": {
            "status": "partially_verified",
            "variants": [{"status":"partially_verified","observations":1,"lineage_records":1}],
        },
        "saved_history_consistency": {
            "history_check_truncated": False,
            "variants": [{"status":"local_records_consistent","observations":1}],
        },
    }


class BenchmarkB9ClosureTests(unittest.TestCase):
    def test_complete_local_records_still_not_experimentally_verified(self):
        data = fixture()
        before = copy.deepcopy(data)
        result = summarize_b9_closure(data)
        self.assertEqual(result["status"], "not_fully_verified")
        states = {x["code"]: x["status"] for x in result["checks"]}
        self.assertEqual(states["protocol_declaration"], "recorded_only")
        self.assertEqual(states["recorded_lineage"], "recorded_only")
        self.assertEqual(states["local_history"], "recorded_only")
        self.assertEqual(states["duration_comparability"], "pending")
        self.assertEqual(states["prompt_and_input_attestation"], "pending")
        self.assertFalse(result["ranking_eligible"])
        self.assertFalse(result["execution_verified"])
        self.assertFalse(result["comparability_verified"])
        self.assertIsNone(result["best_variant"])
        self.assertEqual(data, before)

    def test_explicit_cache_blocker_is_contradiction(self):
        data = fixture()
        data["comparability"]["status"] = "blocked"
        result = summarize_b9_closure(data)
        self.assertEqual(result["status"], "contradiction_detected")
        self.assertFalse(result["ranking_eligible"])

    def test_workflow_mismatch_is_contradiction(self):
        data = fixture()
        data["recorded_execution_evidence"]["status"] = "mismatch"
        self.assertEqual(summarize_b9_closure(data)["status"],
                         "contradiction_detected")

    def test_local_record_mismatch_is_contradiction(self):
        data = fixture()
        data["saved_history_consistency"]["variants"][0]["status"] = "mismatch"
        self.assertEqual(summarize_b9_closure(data)["status"],
                         "contradiction_detected")

    def test_missing_history_does_not_pass(self):
        data = fixture()
        data["saved_history_consistency"]["history_check_truncated"] = True
        result = summarize_b9_closure(data)
        states = {x["code"]: x["status"] for x in result["checks"]}
        self.assertEqual(states["local_history"], "pending")

    def test_missing_or_zero_observations_do_not_pass(self):
        data = fixture()
        data["recorded_execution_evidence"]["variants"][0]["observations"] = 0
        data["recorded_execution_evidence"]["variants"][0]["lineage_records"] = 0
        data["saved_history_consistency"]["variants"][0]["observations"] = 0
        states = {x["code"]: x["status"] for x in
                  summarize_b9_closure(data)["checks"]}
        self.assertEqual(states["recorded_lineage"], "pending")
        self.assertEqual(states["local_history"], "pending")

    def test_missing_section_is_rejected(self):
        data = fixture()
        del data["comparability"]
        with self.assertRaises(ValueError):
            summarize_b9_closure(data)

    def test_invalid_payload_rejected(self):
        for data in (None, {}, []):
            with self.subTest(data=data), self.assertRaises(ValueError):
                summarize_b9_closure(data)


if __name__ == "__main__":
    unittest.main()
