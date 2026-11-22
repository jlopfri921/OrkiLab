"""Official Multiview starter catalog, ZIP and local installation tests."""
import io
import json
import shutil
import sqlite3
import sys
import tempfile
import unittest
import zipfile
from contextlib import closing
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))


class OfficialWorkflowTests(unittest.TestCase):
    def setUp(self):
        try:
            from flask import Flask
            import workflow_library, multiview_official_workflows
        except ImportError as exc:
            if exc.name == "flask":
                self.skipTest("Flask required")
            raise
        self.module = multiview_official_workflows
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        folder = self.root / "workflows" / "multiview"
        folder.mkdir(parents=True)
        for p in (ROOT / "workflows" / "multiview").glob("*"):
            if p.is_file():
                shutil.copyfile(p, folder / p.name)
        cfg = self.root / "settings" / "orkilab"
        cfg.mkdir(parents=True)
        (cfg / "comfyui.json").write_text(
            json.dumps({"mode": "hybrid", "url": "http://127.0.0.1:8188"}), encoding="utf-8")
        app = Flask(__name__)
        app.config["TESTING"] = True
        workflow_library.register(app, self.root)
        self.module.register(app, self.root)
        self.client = app.test_client()
        self.cat = "/api/workspace/multiview/official-workflows"
        self.image = "orkilab_" + "a"*32 + "_" + "b"*16 + ".png"

    def test_catalog_local_only_and_fixed_templates(self):
        r = self.client.get(self.cat)
        self.assertEqual(r.status_code, 200, r.get_json())
        names = [x["name"] for x in r.get_json()["official"]]
        self.assertEqual(len(names), 3)
        self.assertTrue(all(name.startswith("OrkiLab ·") for name in names))
        self.assertTrue(all(x["core_only"] for x in r.get_json()["official"]))
        self.assertEqual(len(r.get_json()["upstream"]), 3)
        self.assertTrue(all(x["status"] == "upstream-unverified"
                            for x in r.get_json()["upstream"]))
        self.assertEqual(self.client.get(self.cat,
            environ_overrides={"REMOTE_ADDR": "192.168.0.2"}).status_code, 403)
        self.assertEqual(self.client.get(self.cat,
            headers={"Origin": "https://evil.example"}).status_code, 403)

    def test_downloadable_offline_zip_has_manifest_and_three_graphs(self):
        resp = self.client.get(self.cat + "/download")
        self.assertEqual(resp.status_code, 200)
        self.assertIn("application/zip", resp.mimetype)
        with zipfile.ZipFile(io.BytesIO(resp.data)) as z:
            members = z.namelist()
            self.assertIn("orkilab-multiview/README.md", members)
            self.assertIn("orkilab-multiview/manifest.json", members)
            graphfiles = [p for p in members if p.endswith("-api.json")]
            self.assertEqual(len(graphfiles), 3)
            manifest = json.loads(z.read("orkilab-multiview/manifest.json"))
            self.assertEqual(len(manifest["bundled"]), 3)
            for name in graphfiles:
                graph = json.loads(z.read(name))
                self.module.validate_official_graph(graph)

    def test_install_requires_confirmation_model_and_staged_photo(self):
        route = self.cat + "/install"
        request = {"confirm": True, "template_id": "core-preserve",
                   "checkpoint": "test.safetensors", "image_name": self.image}
        self.assertEqual(self.client.post(route, json={
            **request, "confirm": False}).status_code, 400)
        self.assertEqual(self.client.post(route, json={
            **request, "image_name": "../../unknown.jpg"}).status_code, 400)
        self.assertEqual(self.client.post(route, json={
            **request, "template_id": "flux3-klein-edit"}).status_code, 400)
        with patch.object(self.module, "checkpoint_choices",
                          return_value=["test.safetensors"]):
            first = self.client.post(route, json=request)
            self.assertEqual(first.status_code, 201, first.get_json())
            second = self.client.post(route, json=request)
        self.assertEqual(second.status_code, 200, second.get_json())
        self.assertEqual(first.get_json()["id"], second.get_json()["id"])
        db = self.root / "settings" / "orkilab" / "workflows.sqlite3"
        with closing(sqlite3.connect(db)) as conn:
            rows = conn.execute("SELECT name,graph FROM workflows").fetchall()
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0][0], "OrkiLab · Multiview · Core Preserve")
        graph = json.loads(rows[0][1])
        self.assertEqual(graph["1"]["inputs"]["image"], self.image)
        self.assertEqual(graph["2"]["inputs"]["ckpt_name"], "test.safetensors")
        self.assertEqual(graph["6"]["inputs"]["denoise"], 0.3)

    def test_unknown_checkpoint_rejected_and_native_mode_protects_all(self):
        route = self.cat + "/install"
        with patch.object(self.module, "checkpoint_choices",
                          return_value=["other.safetensors"]):
            x = self.client.post(route, json={
                "confirm": True, "template_id": "core-img2img",
                "checkpoint": "uninstalled.safetensors", "image_name": self.image})
        self.assertEqual(x.status_code, 409)
        (self.root / "settings" / "orkilab" / "comfyui.json").write_text(
            json.dumps({"mode": "native", "url": "http://127.0.0.1:8188"}), encoding="utf-8")
        self.assertEqual(self.client.get(self.cat).status_code, 409)
        self.assertEqual(self.client.get(self.cat + "/download").status_code, 409)
        self.assertEqual(self.client.get(self.cat + "/checkpoints").status_code, 409)
        self.assertEqual(self.client.post(route, json={
            "confirm": True, "template_id": "core-img2img",
            "checkpoint": "other.safetensors", "image_name": self.image}).status_code, 409)

    def test_upstream_links_are_not_implicitly_imported(self):
        catalog = self.module.catalog(self.root / "workflows" / "multiview")
        self.assertEqual({x["id"] for x in catalog},
                         {"core-img2img", "core-preserve", "core-variation"})
        self.assertFalse(any(x["id"].startswith("flux") or x["id"].startswith("qwen")
                             for x in catalog))


if __name__ == "__main__":
    unittest.main()
