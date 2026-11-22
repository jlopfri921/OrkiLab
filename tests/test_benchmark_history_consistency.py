"""B9.9 exact-record verification; no ComfyUI, mutable DB or GPU."""
import copy
import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from benchmark_generation_adapter import snapshot_generation
from benchmark_history_consistency import (
    compare_saved_generation, summarize_saved_history_matches,
    match_declared_literal_text_hashes,
)


def record():
    return {"id": "gen1", "prompt_id": "prompt1", "workflow_id": "wf1",
            "state": "completed", "graph": json.dumps({
                "1": {"class_type": "CLIPTextEncode", "inputs": {"text": "hola"}},
                "2": {"class_type": "KSampler", "inputs": {"seed": 12}},
            }), "outputs": "[]"}


def report():
    snap = snapshot_generation(record())
    return {"run": {"id": "r1"},
            "variants": [{"id": "v1", "run_id": "r1"}],
            "observations": [{"id": "o1", "run_id": "r1",
                              "variant_id": "v1",
                              "generation_lineage": snap}]}


class LocalHistoryConsistencyTests(unittest.TestCase):
    def test_exact_declared_prompt_hash_matches_literal_graph_text_only(self):
        import hashlib
        positive = hashlib.sha256(b"hola").hexdigest()
        negative = hashlib.sha256(b"").hexdigest()
        proto = {"schema":"orkilab-repro-v1",
                 "prompt_sha256":positive,
                 "negative_prompt_sha256":negative}
        outcome = match_declared_literal_text_hashes(record(), proto)
        self.assertTrue(outcome["positive_digest_found"])
        self.assertFalse(outcome["negative_digest_found"])
        self.assertFalse(outcome["polarity_verified"])
        self.assertFalse(outcome["input_file_verified"])

    def test_dynamic_input_or_custom_node_does_not_assert_a_match(self):
        import hashlib
        proto = {"schema":"orkilab-repro-v1",
                 "prompt_sha256":hashlib.sha256(b"hola").hexdigest(),
                 "negative_prompt_sha256":hashlib.sha256(b"").hexdigest()}
        case = record()
        case["graph"] = json.dumps({
            "1":{"class_type":"MyCustomTextNode",
                 "inputs":{"text":"hola"}},
            "2":{"class_type":"CLIPTextEncode",
                 "inputs":{"text":["1",0]}}
        })
        result = match_declared_literal_text_hashes(case,proto)
        self.assertFalse(result["positive_digest_found"])
        self.assertEqual(result["supported_literal_nodes"],0)

    def test_exact_saved_history_records_match_without_verifying_inputs(self):
        snap = snapshot_generation(record())
        orig = copy.deepcopy(snap)
        result = compare_saved_generation(snap, record())
        self.assertEqual(result["status"], "local_record_match")
        self.assertEqual(result["checked_fields"], 5)
        self.assertFalse(result["prompt_content_verified"])
        self.assertFalse(result["input_content_verified"])
        self.assertFalse(result["remote_execution_verified"])
        self.assertEqual(snap, orig)

    def test_mismatched_local_graph_cannot_supply_prompt_hash_evidence(self):
        import hashlib
        case = report()
        case["run"]["protocol"] = {
            "schema": "orkilab-repro-v1",
            "prompt_sha256": hashlib.sha256(b"hola").hexdigest(),
            "negative_prompt_sha256": hashlib.sha256(b"").hexdigest(),
        }
        changed = record()
        changed["graph"] = json.dumps({
            "1": {"class_type": "CLIPTextEncode", "inputs": {"text": "hola"}}
        })
        result = summarize_saved_history_matches(case, {"gen1": changed})
        item = result["variants"][0]
        self.assertFalse(item["literal_prompt_evidence"]["positive_digest_found_in_any_record"])
        self.assertEqual(item["status"], "mismatch")

    def test_changed_graph_bytes_are_flagged(self):
        altered = record()
        altered["graph"] = '{"3":{"class_type":"KSampler","inputs":{"seed":13}}}'
        result = compare_saved_generation(snapshot_generation(record()), altered)
        self.assertEqual(result["status"], "local_record_mismatch")
        self.assertIn("history_record_submitted_graph_sha256_mismatch", result["reason_codes"])

    def test_changed_prompt_and_workflow_identifiers_are_flagged(self):
        changed = record()
        changed["prompt_id"] = "other"
        changed["workflow_id"] = "other"
        result = compare_saved_generation(snapshot_generation(record()), changed)
        self.assertIn("history_record_comfyui_prompt_id_mismatch", result["reason_codes"])
        self.assertIn("history_record_workflow_id_mismatch", result["reason_codes"])

    def test_missing_history_remains_unknown(self):
        result = compare_saved_generation(snapshot_generation(record()), None)
        self.assertEqual(result["status"], "history_missing")
        self.assertFalse(result["record_consistent"])

    def test_unusable_history_does_not_claim_match(self):
        bad = record()
        bad["graph"] = "not-json"
        result = compare_saved_generation(snapshot_generation(record()), bad)
        self.assertEqual(result["status"], "history_invalid")

    def test_report_groups_only_scoped_observations_and_does_not_rank(self):
        sample = report()
        result = summarize_saved_history_matches(sample, {"gen1": record()})
        self.assertEqual(result["variants"][0]["status"], "local_records_consistent")
        self.assertEqual(result["variants"][0]["counts"]["local_record_match"], 1)
        self.assertFalse(result["ranking_eligible"])
        self.assertFalse(result["remote_execution_verified"])

    def test_missing_snapshot_and_missing_history_do_not_pass(self):
        sample = report()
        sample["observations"].append({
            "id": "o2", "run_id": "r1", "variant_id": "v1",
            "generation_lineage": None,
        })
        result = summarize_saved_history_matches(sample, {"gen1": record()})
        self.assertEqual(result["variants"][0]["status"], "incomplete")
        self.assertEqual(result["variants"][0]["counts"]["lineage_missing"], 1)
        self.assertEqual(result["variants"][0]["counts"]["local_record_match"], 1)

    def test_different_run_scope_rejected(self):
        sample = report()
        sample["observations"][0]["run_id"] = "r2"
        with self.assertRaises(ValueError):
            summarize_saved_history_matches(sample, {"gen1": record()})

    def test_truncated_history_is_not_marked_verified(self):
        result = summarize_saved_history_matches(report(), {}, truncated=True)
        self.assertEqual(result["variants"][0]["status"], "not_checked")
        self.assertTrue(result["history_check_truncated"])


if __name__ == "__main__":
    unittest.main()
