"""Safety and naming tests for local ComfyUI checkpoint management."""
import json
import sqlite3
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

try:
    from scripts import managed_checkpoints
except ImportError:
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
    try:
        import managed_checkpoints
    except ImportError:
        managed_checkpoints = None

@unittest.skipIf(managed_checkpoints is None, "Flask unavailable")
class ManagedCheckpointTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name) / "orkilab"
        self.base.mkdir()
        self.project = "a" * 32
        cfg = self.base / "settings" / "orkilab"
        cfg.mkdir(parents=True)
        with sqlite3.connect(cfg / "projects.sqlite3") as db:
            db.execute("CREATE TABLE projects(id TEXT, engine TEXT, category TEXT, archived INTEGER)")
            db.execute("INSERT INTO projects VALUES(?,?,?,0)", (self.project, "flux3klein", "image"))
        self.outputs = self.base / "Outputs" / ("flux3klein_lora_output_orkilab_" + self.project[:12])
        self.outputs.mkdir(parents=True)
        self.checkpoint = "Flux3Klein_LoRA_step_300.safetensors"
        (self.outputs / self.checkpoint).write_bytes(b"original checkpoint")
        self.folder = Path(self.tmp.name) / "ComfyUI" / "models" / "loras"
        self.folder.mkdir(parents=True)
        self.alias = managed_checkpoints.model_name(self.project, self.checkpoint)
        self.target = self.folder / self.alias

    def manage(self, action):
        return managed_checkpoints.manage(self.base, self.project, str(self.folder), [self.checkpoint], action)

    def test_install_status_and_uninstall_preserve_original(self):
        result = self.manage("install")
        self.assertTrue(result["checkpoints"][0]["installed"])
        self.assertTrue(self.target.name.startswith("OrkiLab_"))
        self.assertEqual(self.target.read_bytes(), b"original checkpoint")
        self.assertTrue(self.manage("status")["checkpoints"][0]["managed"])
        self.manage("uninstall")
        self.assertFalse(self.target.exists())
        self.assertEqual((self.outputs / self.checkpoint).read_bytes(), b"original checkpoint")

    def test_install_does_not_overwrite_unowned_file(self):
        self.target.write_bytes(b"another user model")
        with self.assertRaises(FileExistsError):
            self.manage("install")
        self.assertEqual(self.target.read_bytes(), b"another user model")

    def test_uninstall_refuses_modifications(self):
        self.manage("install")
        self.target.write_bytes(b"modified after installation")
        with self.assertRaises(ValueError):
            self.manage("uninstall")
        self.assertEqual(self.target.read_bytes(), b"modified after installation")

    def test_uninstall_refuses_unmanaged_file(self):
        self.target.write_bytes(b"someone else's file")
        with self.assertRaises(ValueError):
            self.manage("uninstall")
        self.assertTrue(self.target.exists())

    def test_rejects_arbitrary_destination(self):
        other = Path(self.tmp.name) / "other"
        other.mkdir()
        with self.assertRaises(ValueError):
            managed_checkpoints.manage(self.base, self.project, str(other), [self.checkpoint], "install")
