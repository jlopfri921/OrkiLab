"""B10.2: single control field; no model-file or execution claims."""
import copy
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from benchmark_b10_model_check import inspect_model_variants


def example(variable="lora"):
    kind, field = ("LoraLoader", "lora_name") if variable=="lora" else ("CheckpointLoaderSimple","ckpt_name")
    graph = {"3":{"class_type":kind,"inputs":{field:"base.safetensors","strength_model":0.8}},
             "7":{"class_type":"CLIPTextEncode","inputs":{"text":"igual"}},
             "8":{"class_type":"KSampler","inputs":{"seed":1234,"steps":18}}}
    variants = [
        {"id":"a","config":{"controlled_value":"a.safetensors"}},
        {"id":"b","config":{"controlled_value":"b.safetensors"}}]
    schema = {"input":{"required":{field:[["base.safetensors","a.safetensors","b.safetensors"]]}}}
    protocol={"schema":"orkilab-repro-v1","vary":variable}
    return graph,protocol,variants,schema


class B10ModelCheckTests(unittest.TestCase):
    def test_lora_candidates_change_only_single_literal_without_mutation(self):
        args=example()
        original=copy.deepcopy(args)
        result=inspect_model_variants(*args)
        self.assertEqual(result["status"],"static_candidate")
        self.assertEqual(result["target_node_count"],1)
        self.assertTrue(result["graph_single_field_change_verified"])
        self.assertTrue(result["all_choices_advertised"])
        self.assertFalse(result["models_loaded_verified"])
        self.assertFalse(result["file_bytes_verified"])
        self.assertFalse(result["workflow_execution_verified"])
        self.assertFalse(result["comparison_execution_authorized"])
        self.assertFalse(result["generation_submitted"])
        self.assertEqual(args,original)

    def test_checkpoint_selector_supported(self):
        graph,proto,variants,schema=example("checkpoint")
        self.assertEqual(inspect_model_variants(graph,proto,variants,schema)["status"],"static_candidate")

    def test_non_advertised_model_blocks_static_candidate(self):
        graph,proto,variants,schema=example()
        variants[1]["config"]["controlled_value"]="not-installed.safetensors"
        item=inspect_model_variants(graph,proto,variants,schema)
        self.assertEqual(item["status"],"not_established")
        self.assertFalse(item["all_choices_advertised"])
        self.assertIn("model_not_in_comfyui_node_choices",item["reason_codes"])

    def test_multiple_loader_nodes_are_ambiguous(self):
        graph,proto,variants,schema=example()
        graph["4"]=copy.deepcopy(graph["3"])
        item=inspect_model_variants(graph,proto,variants,schema)
        self.assertIn("exactly_one_model_loader_required",item["reason_codes"])
        self.assertFalse(item["comfyui_node_options_observed"])

    def test_custom_or_visual_workflow_is_not_auto_mapped(self):
        graph,proto,variants,schema=example()
        graph["3"]["class_type"]="CustomLoraLoader"
        item=inspect_model_variants(graph,proto,variants,schema)
        self.assertIn("exactly_one_model_loader_required",item["reason_codes"])
        self.assertIn("api_workflow_required", inspect_model_variants(
            {"nodes":[{"id":1}]},proto,variants,schema)["reason_codes"])

    def test_connected_model_selector_not_changed(self):
        graph,proto,variants,schema=example()
        graph["3"]["inputs"]["lora_name"]=["7",0]
        item=inspect_model_variants(graph,proto,variants,schema)
        self.assertIn("model_selector_must_be_literal",item["reason_codes"])

    def test_missing_schema_or_invalid_combo_fails_closed(self):
        graph,proto,variants,schema=example()
        self.assertIn("node_options_unavailable",
            inspect_model_variants(graph,proto,variants,{})["reason_codes"])
        schema["input"]["required"]["lora_name"]=["COMBO",{}]
        self.assertIn("node_options_unavailable",
            inspect_model_variants(graph,proto,variants,schema)["reason_codes"])

    def test_duplicate_variant_choices_rejected(self):
        graph,proto,variants,schema=example()
        variants[1]["config"]["controlled_value"]="a.safetensors"
        item=inspect_model_variants(graph,proto,variants,schema)
        self.assertFalse(item["all_choices_advertised"])

    def test_missing_or_unsupported_controlled_variable_no_success(self):
        graph,proto,variants,schema=example()
        proto["vary"]="image"
        self.assertIn("unsupported_controlled_variable",
            inspect_model_variants(graph,proto,variants,schema)["reason_codes"])


if __name__=="__main__":
    unittest.main()
