"""Project checkpoint inventory and ComfyUI comparator UI regression."""
import sqlite3
from contextlib import closing
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
try:
    import project_checkpoints
except ModuleNotFoundError:
    project_checkpoints = None


@unittest.skipIf(project_checkpoints is None, "Flask unavailable")
class ProjectCheckpointInventoryTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.base = Path(temp.name)
        self.project = "c" * 32
        db = self.base / "settings" / "orkilab" / "projects.sqlite3"
        db.parent.mkdir(parents=True)
        with closing(sqlite3.connect(db)) as conn, conn:
            conn.execute("CREATE TABLE projects(id TEXT PRIMARY KEY, engine TEXT, category TEXT, name TEXT, archived INTEGER)")
            conn.execute("INSERT INTO projects VALUES (?,?,?,?,0)", (self.project, "flux3klein", "image", "Prueba"))
        self.output = self.base / "Outputs" / ("flux3klein_lora_output_orkilab_" + self.project[:12])
        self.output.mkdir(parents=True)
        for step in (500, 100, 300, 700, 1000):
            (self.output / ("Flux3Klein_LoRA_step_%d.safetensors" % step)).write_bytes(b"weights")
        (self.output / "unrelated.safetensors").write_bytes(b"x")
        (self.output / "Flux3Klein_LoRA_step_200.txt").write_text("other")

    def test_sorted_project_scoped_checkpoints(self):
        result = project_checkpoints.inventory(self.base, self.project)
        self.assertEqual(result["engine"], "flux3klein")
        self.assertEqual(result["project_name"], "Prueba")
        self.assertTrue(all(c["comfy_name"].startswith("OrkiLab_Prueba_") for c in result["checkpoints"]))
        self.assertEqual([c["step"] for c in result["checkpoints"]], [100, 300, 500, 700, 1000])
        self.assertEqual(len(result["checkpoints"]), 5)
        self.assertTrue(all(c["size_bytes"] > 0 for c in result["checkpoints"]))
        self.assertEqual(len(list(self.output.iterdir())), 7)

    def test_unknown_archived_and_nonimage_projects_rejected(self):
        with self.assertRaises(LookupError):
            project_checkpoints.inventory(self.base, "d" * 32)
        with closing(sqlite3.connect(self.base / "settings" / "orkilab" / "projects.sqlite3")) as conn, conn:
            conn.execute("UPDATE projects SET archived=1")
        with self.assertRaises(LookupError):
            project_checkpoints.inventory(self.base, self.project)
        with self.assertRaises(ValueError):
            project_checkpoints.inventory(self.base, "../bad")

    def test_inventory_rejects_symlink_and_zero_size_entries(self):
        (self.output / "Extra_step_400.safetensors").write_bytes(b"")
        symlink = self.output / "Extra_step_800.safetensors"
        try:
            symlink.symlink_to(self.output / "Flux3Klein_LoRA_step_100.safetensors")
        except (OSError, NotImplementedError):
            pass
        steps = [x["step"] for x in project_checkpoints.inventory(self.base, self.project)["checkpoints"]]
        self.assertNotIn(400, steps)
        self.assertNotIn(800, steps)


class ProjectCheckpointUiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html = (ROOT / "GUI" / "workspace.html").read_text(encoding="utf-8")
        cls.code = (ROOT / "scripts" / "generation_studio.py").read_text(encoding="utf-8")
        cls.routes = (ROOT / "scripts" / "workspace_routes.py").read_text(encoding="utf-8")

    def test_ui_supports_checkpoint_selection_and_same_graph_comparison(self):
        for marker in (
            'id="compare-mode"', 'id="compare-checkpoint-project"',
            'id="compare-checkpoint-list"', 'id="compare-checkpoint-status"',
            'id="compare-checkpoint-refresh"', 'function loadProjectCheckpoints()',
            'function chosenCheckpoints()', '/checkpoints',
            '/api/workspace/generation/compare/checkpoints', 'checkpointMode',
            'compare.href="/workspace/comfyui?checkpoint_project="',
        ):
            with self.subTest(marker=marker):
                self.assertIn(marker, self.html)

    def test_backend_ensures_only_lora_filename_changes(self):
        for marker in (
            'def compare_project_checkpoints():',
            'project_checkpoints.inventory(base, project_id)',
            'node.get("class_type") not in ("LoraLoader", "LoraLoaderModelOnly")',
            'f["name"]=="lora_name"', '"name":"lora_name","value":selected_models[name]',
            'validate_prompt(graph,schemas)',
            'Checkpoints not installed in ComfyUI/models/loras',
            'fresh_schema = node_schema(cfg["url"], node["class_type"], get_json)',
        ):
            with self.subTest(marker=marker):
                self.assertIn(marker, self.code)
        self.assertIn("project_checkpoints.register(app, base)", self.routes)
        self.assertIn('entry.comfy_name||entry.name', self.html)


if __name__ == "__main__":
    unittest.main()
