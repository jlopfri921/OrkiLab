"""Project -> selected trainer dataset handoff without global settings changes."""
import json
import sqlite3
import sys
import tempfile
import unittest
from contextlib import closing
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from project_dataset_handoff import HandoffError, make_draft


class ProjectHandoffTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.project = "a" * 32
        self.settings = self.root / "settings"
        self.settings.mkdir()
        db = self.settings / "orkilab" / "projects.sqlite3"
        db.parent.mkdir()
        with closing(sqlite3.connect(db)) as connection, connection:
            connection.execute("CREATE TABLE projects(id TEXT PRIMARY KEY, name TEXT, engine TEXT, "
                               "category TEXT, dataset TEXT, archived INTEGER)")
            connection.execute("INSERT INTO projects VALUES(?,?,?,?,?,0)",
                               (self.project, "Sample", "flux1", "image", ""))
        self.projects_db = db
        self.dataset_db = self.settings / "orkilab" / "datasets.sqlite3"
        self.prepared = self.root / "Datasets" / "OrkiLab" / self.project / ("b" * 32)
        self.prepared.mkdir(parents=True)
        (self.prepared / "test.png").write_bytes(b"test image")
        (self.prepared / "test.txt").write_text("subject", encoding="utf-8")
        (self.prepared / "manifest.json").write_text(
            json.dumps({"project_id": self.project, "format": "flat_image_txt",
                        "items": [{"image": "test.png", "caption": "test.txt"}]}),
            encoding="utf-8")
        with closing(sqlite3.connect(self.dataset_db)) as connection, connection:
            connection.execute("CREATE TABLE dataset_preparations (id TEXT PRIMARY KEY, "
                               "project_id TEXT, path TEXT)")
            connection.execute("INSERT INTO dataset_preparations VALUES (?,?,?)",
                               ("b" * 32, self.project, str(self.prepared)))

    def test_selected_engine_inherits_prepared_dataset_without_modifying_shared_settings(self):
        original = {"dataset_path": "D:/old", "learning_rate": 0.0001}
        config = self.settings / "pre_cache_settings_flux1.json"
        config.write_text(json.dumps(original), encoding="utf-8")
        draft, info = make_draft(self.root, self.project, "flux1")
        self.assertEqual(info["dataset_origin"], "prepared")
        for section in ("pre_cache", "train"):
            self.assertEqual(Path(draft[section]["dataset_path"]).resolve(), self.prepared.resolve())
            self.assertEqual(draft[section]["project_name"], "orkilab_" + self.project[:12])
        self.assertEqual(draft["pre_cache"]["learning_rate"], 0.0001)
        self.assertEqual(json.loads(config.read_text(encoding="utf-8")), original)

    def test_wrong_engine_never_launches(self):
        with self.assertRaisesRegex(HandoffError, "does not match"):
            make_draft(self.root, self.project, "sdxl")

    def test_missing_prepared_folder_fails_closed(self):
        (self.prepared / "manifest.json").unlink()
        with self.assertRaises(HandoffError):
            make_draft(self.root, self.project, "flux1")

    def test_other_modality_can_use_explicit_project_directory(self):
        dataset = self.root / "audio_data"
        dataset.mkdir()
        with closing(sqlite3.connect(self.projects_db)) as connection, connection:
            connection.execute("UPDATE projects SET engine='yue2',category='audio',dataset=? "
                               "WHERE id=?", (str(dataset), self.project))
        draft, info = make_draft(self.root, self.project, "yue2")
        self.assertEqual(info["dataset_origin"], "project_path")
        self.assertEqual(Path(draft["pre_cache"]["dataset_path"]).resolve(), dataset.resolve())
        self.assertEqual(Path(draft["train"]["dataset_path"]).resolve(), dataset.resolve())

    def test_missing_caption_in_prepared_folder_blocks_training(self):
        (self.prepared / "test.txt").unlink()
        with self.assertRaisesRegex(HandoffError, "incomplete"):
            make_draft(self.root, self.project, "flux1")

    def test_tampered_manifest_project_and_traversal_are_rejected(self):
        manifest_file = self.prepared / "manifest.json"
        valid = json.loads(manifest_file.read_text(encoding="utf-8"))
        cases = [
            dict(valid, project_id="c" * 32),
            dict(valid, items=[{"image": "../outside.png", "caption": "test.txt"}]),
            dict(valid, items=[{"image": "test.png", "caption": "../escape.txt"}]),
            dict(valid, items=[{"image": "test.png", "caption": "wrong.txt"}]),
            dict(valid, items=[]),
            dict(valid, items=[{"image": "test.png", "caption": "test.txt"}] * 201),
        ]
        for data in cases:
            with self.subTest(data=data):
                manifest_file.write_text(json.dumps(data), encoding="utf-8")
                with self.assertRaises(HandoffError):
                    make_draft(self.root, self.project, "flux1")
        manifest_file.write_text(json.dumps(valid), encoding="utf-8")
        self.assertEqual(make_draft(self.root, self.project, "flux1")[1]["dataset_origin"], "prepared")

    def test_symlink_in_prepared_dataset_blocks_training(self):
        source = self.root / "external_caption.txt"
        source.write_text("unexpected", encoding="utf-8")
        (self.prepared / "test.txt").unlink()
        try:
            (self.prepared / "test.txt").symlink_to(source)
        except (OSError, NotImplementedError):
            self.skipTest("Symlink creation not supported by this test runner")
        with self.assertRaisesRegex(HandoffError, "incomplete"):
            make_draft(self.root, self.project, "flux1")



if __name__ == "__main__":
    unittest.main()
