"""ComfyUI V3 autogrow regression: Qwen 2.1 may use zero image references."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from workflow_conversion import validate_prompt


class AutoGrowV3Tests(unittest.TestCase):
    def setUp(self):
        self.schema = {
            "TextEncodeQwenImage21": {
                "input": {
                    "required": {
                        "prompt": ["STRING"],
                        "negative_prompt": ["STRING"],
                        "resolution": ["INT"],
                        "clip": ["CLIP"],
                        "images": ["COMFY_AUTOGROW_V3", {
                            "template": {
                                "min": 0,
                                "max": 16,
                                "names": ["image_" + str(i) for i in range(1, 17)],
                            },
                        }],
                    },
                },
                "output": ["CONDITIONING", "CONDITIONING", "LATENT"],
                "output_node": True,
            },
            "ClipSource": {
                "input": {"required": {}},
                "output": ["CLIP"],
                "output_node": False,
            },
        }
        self.graph = {
            "10": {"class_type": "ClipSource", "inputs": {}},
            "520": {"class_type": "TextEncodeQwenImage21", "inputs": {
                "prompt": "test", "negative_prompt": "",
                "resolution": 1024, "clip": ["10", 0],
            }},
        }

    def test_zero_reference_images_permitted_by_declared_min_zero(self):
        validate_prompt(self.graph, self.schema)

    def test_min_one_still_requires_images(self):
        self.schema["TextEncodeQwenImage21"]["input"]["required"]["images"][1]["template"]["min"] = 1
        with self.assertRaisesRegex(ValueError, "missing input images"):
            validate_prompt(self.graph, self.schema)

    def test_absent_min_is_not_assumed_optional(self):
        del self.schema["TextEncodeQwenImage21"]["input"]["required"]["images"][1]["template"]["min"]
        with self.assertRaisesRegex(ValueError, "missing input images"):
            validate_prompt(self.graph, self.schema)

    def test_other_missing_required_inputs_still_block(self):
        del self.graph["520"]["inputs"]["prompt"]
        with self.assertRaisesRegex(ValueError, "missing input prompt"):
            validate_prompt(self.graph, self.schema)
