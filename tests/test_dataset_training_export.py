"""Training dataset export smoke and non-destructive behavior."""
import io
import hashlib
import json
import os
import sqlite3
import sys
import tempfile
import unittest
import zipfile
from contextlib import closing
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))


class TrainingDatasetExportTests(unittest.TestCase):
    def setUp(self):
        try:
            from flask import Flask
            import dataset_studio
        except ModuleNotFoundError as exc:
            if exc.name == "flask":
                self.skipTest("Flask unavailable")
            raise
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        folder = self.root / "images"
        folder.mkdir()
        self.image = folder / "test.png"
        self.original = b"\x89PNG\r\n\x1a\n" + b"X" * 128
        self.image.write_bytes(self.original)
        self.project_id = "a" * 32
        db = self.root / "settings" / "orkilab" / "projects.sqlite3"
        db.parent.mkdir(parents=True)
        with closing(sqlite3.connect(db)) as connection, connection:
            connection.execute("CREATE TABLE projects (id TEXT PRIMARY KEY, archived INTEGER NOT NULL)")
            connection.execute("INSERT INTO projects VALUES (?, 0)", (self.project_id,))
        app = Flask(__name__)
        app.config["TESTING"] = True
        dataset_studio.register(app, self.root)
        self.client = app.test_client()
        self.path = "/api/workspace/datasets/" + self.project_id
        self.assertEqual(self.client.post(self.path, json={"folder": str(folder)}).status_code, 200)
        self.image_id = self.client.get(self.path).get_json()["images"][0]["id"]
        self.export = self.path + "/training-export"

    def test_caption_pair_and_unchanged_source(self):
        missing = self.client.post(self.export, json={
            "mode": "preview", "image_ids": [self.image_id]}).get_json()
        self.assertEqual(missing["ready"], 0)
        self.assertEqual(missing["skipped"][0]["reason"], "missing_caption")
        caption_url = self.path + "/" + self.image_id + "/caption"
        saved = self.client.put(caption_url, json={
            "caption": "person in red", "expected_revision": 0})
        self.assertEqual(saved.status_code, 200)
        preview = self.client.post(self.export, json={
            "mode": "preview", "image_ids": [self.image_id]})
        self.assertEqual(preview.get_json()["ready"], 1)
        self.assertFalse(preview.get_json()["trainer_ready"])
        self.assertEqual(self.client.post(self.export, json={
            "mode": "download", "image_ids": [self.image_id]}).status_code, 400)
        result = self.client.post(self.export, json={
            "mode": "download", "image_ids": [self.image_id], "confirm": True})
        self.assertEqual(result.status_code, 200)
        with zipfile.ZipFile(io.BytesIO(result.data)) as archive:
            self.assertEqual(archive.read("dataset/test.png"), self.original)
            self.assertEqual(archive.read("dataset/test.txt"), b"person in red")
            self.assertIn("manifest.json", archive.namelist())
        self.assertEqual(self.image.read_bytes(), self.original)
        self.assertFalse(self.image.with_suffix(".txt").exists())

    def test_local_preparation_is_isolated_and_never_overwrites(self):
        no_caption = self.client.post(self.export, json={
            "mode": "prepare", "image_ids": [self.image_id], "confirm": True})
        self.assertEqual(no_caption.status_code, 409)
        caption = self.path + "/" + self.image_id + "/caption"
        self.assertEqual(self.client.put(caption, json={
            "caption": "test subject", "expected_revision": 0}).status_code, 200)
        not_confirmed = self.client.post(self.export, json={
            "mode": "prepare", "image_ids": [self.image_id]})
        self.assertEqual(not_confirmed.status_code, 400)
        payload = {"mode": "prepare", "image_ids": [self.image_id], "confirm": True}
        first = self.client.post(self.export, json=payload)
        second = self.client.post(self.export, json=payload)
        self.assertEqual(first.status_code, 200)
        self.assertEqual(second.status_code, 200)
        first_path = Path(first.get_json()["path"])
        second_path = Path(second.get_json()["path"])
        self.assertNotEqual(first_path, second_path)
        self.assertEqual((first_path / "test.png").read_bytes(), self.original)
        self.assertEqual((first_path / "test.txt").read_text(encoding="utf-8"), "test subject")
        self.assertTrue((first_path / "manifest.json").is_file())
        self.assertFalse(first.get_json()["trainer_ready"])
        self.assertEqual(self.image.read_bytes(), self.original)
        self.assertFalse(self.image.with_suffix(".txt").exists())

    def test_invalid_cross_project_and_changed_source(self):
        invalid = self.client.post(self.export, json={
            "mode": "preview", "image_ids": ["b" * 32]})
        self.assertEqual(invalid.status_code, 409)
        self.image.write_bytes(b"changed")
        changed = self.client.post(self.export, json={
            "mode": "preview", "image_ids": [self.image_id]}).get_json()
        self.assertEqual(changed["ready"], 0)
        self.assertEqual(changed["skipped"][0]["reason"], "missing_caption")

    def _save_caption(self, image_id, caption):
        return self.client.put(self.path + "/" + image_id + "/caption",
                               json={"caption": caption, "expected_revision": 0})

    def test_manifest_round_trip_and_repeated_preparation_preserve_sources(self):
        original_hash = hashlib.sha256(self.image.read_bytes()).hexdigest()
        self.assertEqual(self._save_caption(self.image_id, "scene with person").status_code, 200)
        request = {"mode": "prepare", "image_ids": [self.image_id], "confirm": True}
        first = self.client.post(self.export, json=request)
        second = self.client.post(self.export, json=request)
        self.assertEqual((first.status_code, second.status_code), (200, 200))
        first_dir, second_dir = Path(first.get_json()["path"]), Path(second.get_json()["path"])
        self.assertNotEqual(first_dir, second_dir)
        for prepared in (first_dir, second_dir):
            manifest = json.loads((prepared / "manifest.json").read_text(encoding="utf-8"))
            self.assertEqual(manifest["project_id"], self.project_id)
            self.assertEqual(manifest["format"], "flat_image_txt")
            self.assertEqual(manifest["items"], [
                {"id": self.image_id, "image": "test.png", "caption": "test.txt"}
            ])
            self.assertEqual(hashlib.sha256((prepared / "test.png").read_bytes()).hexdigest(), original_hash)
            self.assertEqual((prepared / "test.txt").read_text(encoding="utf-8"), "scene with person")
            self.assertEqual({x.name for x in prepared.iterdir()}, {"test.png", "test.txt", "manifest.json"})
        self.assertEqual(hashlib.sha256(self.image.read_bytes()).hexdigest(), original_hash)
        self.assertFalse(self.image.with_suffix(".txt").exists())

    def test_changed_source_after_caption_is_rejected_before_prepare(self):
        self.assertEqual(self._save_caption(self.image_id, "test subject").status_code, 200)
        self.image.write_bytes(self.original + b"changed")
        preview = self.client.post(self.export, json={
            "mode": "preview", "image_ids": [self.image_id]})
        self.assertEqual(preview.status_code, 200)
        self.assertEqual(preview.get_json()["skipped"][0]["reason"], "changed_or_oversized")
        prepared = self.client.post(self.export, json={
            "mode": "prepare", "image_ids": [self.image_id], "confirm": True})
        self.assertEqual(prepared.status_code, 409)
        self.assertFalse((self.root / "Datasets" / "OrkiLab" / self.project_id).exists())

    def test_preparation_rejects_managed_destination_symlink(self):
        self.assertEqual(self._save_caption(self.image_id, "test subject").status_code, 200)
        foreign = self.root / "foreign"
        foreign.mkdir()
        link = self.root / "Datasets"
        try:
            link.symlink_to(foreign, target_is_directory=True)
        except (OSError, NotImplementedError):
            self.skipTest("Creating directory symlinks requires platform privileges")
        result = self.client.post(self.export, json={
            "mode": "prepare", "image_ids": [self.image_id], "confirm": True})
        self.assertEqual(result.status_code, 409)
        self.assertFalse((foreign / "OrkiLab").exists())
        self.assertEqual(self.image.read_bytes(), self.original)

    def test_preparation_rejects_rejected_image_and_keeps_source(self):
        self.assertEqual(self._save_caption(self.image_id, "test subject").status_code, 200)
        dataset_db = self.root / "settings" / "orkilab" / "datasets.sqlite3"
        with closing(sqlite3.connect(dataset_db)) as conn, conn:
            conn.execute("UPDATE dataset_images SET review='rejected' WHERE id=?", (self.image_id,))
        preview = self.client.post(self.export, json={
            "mode": "preview", "image_ids": [self.image_id]})
        self.assertEqual(preview.status_code, 200)
        self.assertEqual(preview.get_json()["skipped"][0]["reason"], "rejected")
        prepared = self.client.post(self.export, json={
            "mode": "prepare", "image_ids": [self.image_id], "confirm": True})
        self.assertEqual(prepared.status_code, 409)
        self.assertEqual(self.image.read_bytes(), self.original)



if __name__ == "__main__":
    unittest.main()
