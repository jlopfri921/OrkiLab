"""B10.1 offline comparison declaration checklist tests."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from benchmark_b10_preflight import inspect_comparison_plan


def sample():
    protocol = {
        "schema":"orkilab-repro-v1", "vary":"lora", "workflow_id":"wf1",
        "prompt_sha256":"a"*64,"negative_prompt_sha256":"b"*64,
        "input_sha256":"c"*64, "gpu_uuid":"GPU-123", "cache":"cold",
        "seed_policy":"fixed", "repetitions":3, "resolution":[1024,1024],
    }
    return {
        "run":{"id":"r1","protocol":protocol},
        "variants":[
            {"id":"v1","run_id":"r1","config":{"controlled_value":"lora-a"}},
            {"id":"v2","run_id":"r1","config":{"controlled_value":"lora-b"}},
        ],
    }


class B10ComparisonPreflightTests(unittest.TestCase):
    def test_complete_declaration_still_forbids_execution_or_rank(self):
        result = inspect_comparison_plan(sample())
        self.assertEqual(result["declaration_status"],"declared_only")
        self.assertEqual(result["controlled_variable"],"lora")
        self.assertEqual(result["variant_count"],2)
        self.assertFalse(result["comparison_execution_authorized"])
        self.assertFalse(result["generation_submitted"])
        self.assertFalse(result["ranking_eligible"])
        self.assertIsNone(result["best_variant"])
        self.assertFalse(result["database_modified"])

    def test_model_availability_graph_inputs_and_gpu_never_auto_verified(self):
        result = inspect_comparison_plan(sample())
        gate = {x["code"]:x["status"] for x in result["gates"]}
        for name in ("selected_models_exist","one_variable_only",
                     "prompt_and_input_match","seed_and_resolution_match",
                     "comfyui_idle_and_compatible","gpu_and_cache_equivalence"):
            self.assertEqual(gate[name], "pending")

    def test_incomplete_protocol_not_mislabeled_as_ready(self):
        report = sample()
        report["run"]["protocol"]["input_sha256"] = ""
        result = inspect_comparison_plan(report)
        self.assertEqual(result["declaration_status"],"incomplete")
        self.assertIn("missing_or_invalid_input_sha256",result["reason_codes"])

    def test_duplicate_variants_mark_declaration_incomplete(self):
        report = sample()
        report["variants"][1]["config"]["controlled_value"] = "lora-a"
        result = inspect_comparison_plan(report)
        self.assertEqual(result["declaration_status"],"incomplete")
        self.assertIn("variant_declarations_incomplete",result["reason_codes"])

    def test_legacy_protocol_never_authorizes_execution(self):
        report = sample()
        report["run"]["protocol"] = {}
        result = inspect_comparison_plan(report)
        self.assertEqual(result["declaration_status"],"incomplete")
        self.assertIsNone(result["controlled_variable"])
        self.assertFalse(result["comparison_execution_authorized"])

    def test_rejects_malformed_source(self):
        for obj in (None, {}, {"run": {}, "variants":{}}, []):
            with self.subTest(value=obj), self.assertRaises(ValueError):
                inspect_comparison_plan(obj)


if __name__ == "__main__":
    unittest.main()
