"""B9.4 declared-only reproducibility guardrails; synthetic tests."""
import copy
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from benchmark_repro_protocol import declared_protocol_readiness


def fixture():
    return {"run": {"id": "r1", "protocol": {
        "schema": "orkilab-repro-v1", "vary": "checkpoint",
        "workflow_id": "wf-1", "prompt_sha256": "a" * 64,
        "negative_prompt_sha256": "b" * 64, "input_sha256": "c" * 64,
        "gpu_uuid": "GPU-real-device", "cache": "warm_sampler",
        "seed_policy": "fixed", "repetitions": 3, "resolution": [1024, 1024],
    }}, "variants": [
        {"id": "v1", "config": {"controlled_value": "model-a"}},
        {"id": "v2", "config": {"controlled_value": "model-b"}},
    ]}


class ReproProtocolTests(unittest.TestCase):
    def test_complete_declaration_never_verifies_execution_or_ranks(self):
        case = fixture()
        original = copy.deepcopy(case)
        result = declared_protocol_readiness(case)
        self.assertEqual(result["status"], "declared_unverified")
        self.assertEqual(result["controlled_variable"], "checkpoint")
        self.assertFalse(result["execution_verified"])
        self.assertFalse(result["ranking_eligible"])
        self.assertFalse(result["benchmark_database_modified"])
        self.assertEqual(case, original)

    def test_old_protocol_remains_unverified_not_invalid(self):
        report = fixture()
        report["run"]["protocol"] = {"seed": 42}
        outcome = declared_protocol_readiness(report)
        self.assertEqual(outcome["status"], "legacy_unverified")
        self.assertIsNone(outcome["schema"])

    def test_missing_fixed_input_hash_is_incomplete(self):
        report = fixture()
        del report["run"]["protocol"]["input_sha256"]
        output = declared_protocol_readiness(report)
        self.assertEqual(output["status"], "incomplete")
        self.assertIn("missing_or_invalid_input_sha256", output["reason_codes"])

    def test_invalid_gpu_or_cache_mode_is_incomplete(self):
        report = fixture()
        report["run"]["protocol"]["gpu_uuid"] = "not-a-uuid"
        report["run"]["protocol"]["cache"] = "auto"
        reasons = declared_protocol_readiness(report)["reason_codes"]
        self.assertIn("missing_gpu_identity", reasons)
        self.assertIn("missing_cache_policy", reasons)

    def test_duplicate_variant_only_incomplete_never_auto_fixed(self):
        report = fixture()
        report["variants"][1]["config"]["controlled_value"] = "model-a"
        result = declared_protocol_readiness(report)
        self.assertEqual(result["status"], "incomplete")
        self.assertIn("duplicate_controlled_value", result["variants"][1]["reason_codes"])

    def test_variant_override_requires_independent_review(self):
        report = fixture()
        report["variants"][0]["config"]["graph_override"] = {"1": "anything"}
        result = declared_protocol_readiness(report)
        self.assertEqual(result["status"], "incomplete")
        self.assertIn("graph_override_requires_independent_review", result["variants"][0]["reason_codes"])

    def test_incompatible_variant_variable_is_rejected(self):
        report = fixture()
        report["variants"][0]["config"]["vary"] = "lora"
        result = declared_protocol_readiness(report)
        self.assertIn("variant_variable_mismatch", result["variants"][0]["reason_codes"])

    def test_unhashable_enums_do_not_raise_type_error(self):
        report = fixture()
        for key in ("vary", "cache", "seed_policy"):
            report["run"]["protocol"][key] = ["bad"]
        result = declared_protocol_readiness(report)
        self.assertEqual(result["status"], "incomplete")

    def test_single_variant_is_incomplete(self):
        report = fixture()
        report["variants"].pop()
        result = declared_protocol_readiness(report)
        self.assertIn("at_least_two_variants_required", result["reason_codes"])

    def test_json_string_legacy_records_supported(self):
        import json
        report = fixture()
        report["run"]["protocol_json"] = json.dumps(report["run"].pop("protocol"))
        for variant in report["variants"]:
            variant["config_json"] = json.dumps(variant.pop("config"))
        self.assertEqual(declared_protocol_readiness(report)["status"], "declared_unverified")


if __name__ == "__main__":
    unittest.main()
