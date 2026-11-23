"""B9.8: narrow, read-only execution-evidence verification."""
import copy
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from benchmark_execution_evidence import verify_recorded_execution_evidence


def fixture():
    return {
        "run": {"id": "run1", "protocol": {"schema": "orkilab-repro-v1",
                                           "workflow_id": "saved-1"}},
        "variants": [{"id": "v1", "run_id": "run1"}],
        "observations": [
            {"id": "o1", "run_id": "run1", "variant_id": "v1", "status": "completed",
             "generation_lineage": {
                 "workflow_id": "saved-1",
                 "comfyui_prompt_id": "prompt-abc",
                 "submitted_graph_sha256": "a" * 64,
                 "execution_timing": {
                     "source": "comfyui_history_status_messages",
                     "prompt_id": "prompt-abc",
                 },
             }},
        ],
    }


class RecordedExecutionEvidenceTests(unittest.TestCase):
    def test_matching_record_only_partially_verified(self):
        sample = fixture()
        before = copy.deepcopy(sample)
        result = verify_recorded_execution_evidence(sample)
        v = result["variants"][0]
        self.assertEqual(result["status"], "partially_verified")
        self.assertEqual(v["workflow_id_matches"], 1)
        self.assertEqual(v["timing_prompt_id_matches"], 1)
        self.assertTrue(v["consistent_graph_fingerprint"])
        self.assertFalse(v["prompt_content_verified"])
        self.assertFalse(v["input_content_verified"])
        self.assertFalse(v["gpu_equivalence_verified"])
        self.assertFalse(v["full_inference_verified"])
        self.assertFalse(result["ranking_eligible"])
        self.assertIsNone(result["best_variant"])
        self.assertEqual(sample, before)

    def test_workflow_mismatch_is_detected(self):
        sample = fixture()
        sample["observations"][0]["generation_lineage"]["workflow_id"] = "different"
        result = verify_recorded_execution_evidence(sample)
        self.assertEqual(result["status"], "mismatch")
        self.assertIn("workflow_mismatch", result["variants"][0]["reason_codes"])

    def test_prompt_timing_cross_identity_is_never_verified(self):
        sample = fixture()
        sample["observations"][0]["generation_lineage"]["execution_timing"]["prompt_id"] = "another"
        item = verify_recorded_execution_evidence(sample)["variants"][0]
        self.assertEqual(item["timing_prompt_id_matches"], 0)
        self.assertIn("prompt_timing_identity_not_established", item["reason_codes"])

    def test_missing_lineage_is_not_claimed_verified(self):
        sample = fixture()
        sample["observations"][0]["generation_lineage"] = None
        result = verify_recorded_execution_evidence(sample)
        self.assertEqual(result["status"], "no_execution_evidence")
        self.assertIn("no_recorded_generation_lineage", result["variants"][0]["reason_codes"])

    def test_no_observations_is_not_evidence(self):
        sample = fixture()
        sample["observations"] = []
        v = verify_recorded_execution_evidence(sample)["variants"][0]
        self.assertEqual(v["status"], "no_execution_evidence")
        self.assertIn("no_observations", v["reason_codes"])

    def test_changed_graph_fingerprints_flag_review_not_ranking(self):
        sample = fixture()
        other = copy.deepcopy(sample["observations"][0])
        other["id"] = "o2"
        other["generation_lineage"]["submitted_graph_sha256"] = "b" * 64
        sample["observations"].append(other)
        item = verify_recorded_execution_evidence(sample)["variants"][0]
        self.assertFalse(item["consistent_graph_fingerprint"])
        self.assertIn("different_submitted_graph_fingerprints", item["reason_codes"])

    def test_old_protocol_does_not_infer_workflow(self):
        sample = fixture()
        sample["run"]["protocol"] = {}
        item = verify_recorded_execution_evidence(sample)["variants"][0]
        self.assertEqual(item["workflow_id_matches"], 0)
        self.assertIn("no_declared_workflow_for_match", item["reason_codes"])

    def test_wrong_run_observation_rejected(self):
        sample = fixture()
        sample["observations"][0]["run_id"] = "other"
        with self.assertRaises(ValueError):
            verify_recorded_execution_evidence(sample)

    def test_bad_structure_rejected(self):
        for sample in (None, {}, {"run": {"id": "r"}, "variants": [], "observations": {}}):
            with self.assertRaises(ValueError):
                verify_recorded_execution_evidence(sample)


if __name__ == "__main__":
    unittest.main()
