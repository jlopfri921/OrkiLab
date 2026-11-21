"""ComfyUI LoRA directory persistence: saved on the host, restored across requests."""
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
try:
    from flask import Flask
    from comfyui_connect import register, validate_settings, DEFAULT_SETTINGS
except ImportError:
    Flask = None

@unittest.skipIf(Flask is None, "Flask unavailable")
class ComfyuiLoraFolderPersistence(unittest.TestCase):
    def test_validate_existing_legacy_config(self):
        legacy = {"mode": "hybrid", "url": "http://127.0.0.1:8188", "model_folder": ""}
        result = validate_settings(legacy, DEFAULT_SETTINGS)
        self.assertEqual(result["lora_folder"], "")

    def test_save_reload_and_preserve_other_settings(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            app = Flask(__name__)
            register(app, base)
            client = app.test_client()
            data = {"mode": "hybrid", "url": "http://127.0.0.1:8188",
                    "model_folder": "D:/Models", "lora_folder": "D:/ComfyUI/models/loras"}
            response = client.post("/api/workspace/comfyui", json=data,
                                   environ_overrides={"REMOTE_ADDR": "127.0.0.1"})
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.get_json()["lora_folder"], data["lora_folder"])
            # New app instance simulates restarting the launcher.
            app2 = Flask(__name__ + "_reload")
            register(app2, base)
            loaded = app2.test_client().get("/api/workspace/comfyui",
                         environ_overrides={"REMOTE_ADDR": "127.0.0.1"}).get_json()
            self.assertEqual(loaded, data)

    def test_reject_control_characters_in_directory(self):
        with self.assertRaises(ValueError):
            validate_settings({"lora_folder": "C:/models/loras\nunsafe"}, DEFAULT_SETTINGS)

    def test_comparator_restores_saved_path(self):
        html = (Path(__file__).resolve().parents[1] / "GUI" / "workspace.html").read_text(encoding="utf-8")
        self.assertIn('value=d.lora_folder||""', html)
        self.assertIn('await rememberComfyLoraFolder(result.directory)', html)
