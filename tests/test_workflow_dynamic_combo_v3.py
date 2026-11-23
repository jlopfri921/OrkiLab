"""Regression for ComfyUI V3 dynamic dropdowns in API-format workflows."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from workflow_conversion import validate_prompt


class DynamicComboV3Tests(unittest.TestCase):
    def setUp(self):
        self.schema = {
            "TextGenerate": {
                "input": {"required": {
                    "sampling_mode": ["COMFY_DYNAMICCOMBO_V3", {"options": [
                        {"key": "on", "inputs": {
                            "required": {
                                "temperature": ["FLOAT", {"min": 0.01, "max": 2.0}],
                                "top_k": ["INT", {"min": 0, "max": 1000}],
                            }, "optional": {"presence_penalty": ["FLOAT"]}}},
                        {"key": "off", "inputs": {"required": {}, "optional": {}}},
                    ]},
                    "text": ["STRING"],
                }},
                "output": ["STRING"],
                "output_node": True,
            }
        }

    def validate(self, inputs):
        validate_prompt({"30:16": {"class_type": "TextGenerate", "inputs": inputs}},
                        self.schema)

    def test_supported_off_branch_prepares_without_link(self):
        self.validate({"text": "hello", "sampling_mode": "off"})

    def test_supported_on_branch_checks_nested_required_values(self):
        self.validate({"text": "hello", "sampling_mode": "on",
                       "sampling_mode.temperature": 0.7, "sampling_mode.top_k": 64})

    def test_unadvertised_option_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "unavailable dynamic option"):
            self.validate({"text": "hello", "sampling_mode": "other"})

    def test_missing_required_child_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "missing input sampling_mode.temperature"):
            self.validate({"text": "hello", "sampling_mode": "on"})

    def test_unselected_branch_child_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "unknown input sampling_mode.temperature"):
            self.validate({"text": "hello", "sampling_mode": "off",
                           "sampling_mode.temperature": 0.7})

    def test_out_of_range_child_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "out of range sampling_mode.temperature"):
            self.validate({"text": "hello", "sampling_mode": "on",
                           "sampling_mode.temperature": 9.0, "sampling_mode.top_k": 64})

    def test_unadvertised_dynamic_schema_does_not_accept_arbitrary_scalar(self):
        self.schema["TextGenerate"]["input"]["required"]["sampling_mode"] = [
            "COMFY_DYNAMICCOMBO_V3", {"options": []}]
        with self.assertRaisesRegex(ValueError, "invalid dynamic dropdown"):
            self.validate({"text": "hello", "sampling_mode": "on"})
