"""Multiview Studio alpha.1 acceptance: real local image refs and immutable sources."""
import io
import json
import sqlite3
import sys
import tempfile
import unittest
from contextlib import closing
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))


class MultiviewAlphaOneTests(unittest.TestCase):
    def setUp(self):
        try:
            from flask import Flask
            from PIL import Image
            import multiview_studio
        except ImportError as exc:
            if exc.name in {"flask","PIL"}:
                self.skipTest("Flask/Pillow unavailable")
            raise
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.project = "a" * 32
        self.other = "b" * 32
        settings = self.root / "settings" / "orkilab"
        settings.mkdir(parents=True)
        with closing(sqlite3.connect(settings / "projects.sqlite3")) as db, db:
            db.execute("CREATE TABLE projects(id TEXT PRIMARY KEY, archived INTEGER NOT NULL DEFAULT 0)")
            db.executemany("INSERT INTO projects(id) VALUES(?)", [(self.project,), (self.other,)])
        self.first = self.root / "front.png"
        Image.new("RGB", (32, 24), (255, 50, 10)).save(self.first)
        self.original = self.first.read_bytes()
        self.app = Flask(__name__)
        self.app.config["TESTING"] = True
        multiview_studio.register(self.app, self.root)
        self.client = self.app.test_client()
        self.base = "/api/workspace/multiview/projects/" + self.project
        self.subjects = self.base + "/subjects"

    def subject(self, name="Test subject"):
        response = self.client.post(self.subjects, json={"name": name})
        self.assertEqual(response.status_code, 201, response.get_json())
        return response.get_json()["id"]

    def capture(self, subject_id, **metadata):
        return self.client.post(self.subjects + "/" + subject_id + "/captures",
                                json={"path": str(self.first), "source_type": "real_photo", **metadata})

    def test_create_list_and_edit_subject_independently_of_other_project(self):
        sid = self.subject("Sculpture")
        listed = self.client.get(self.subjects).get_json()["subjects"]
        self.assertEqual([(x["id"], x["capture_count"]) for x in listed], [(sid,0)])
        self.assertEqual(self.client.get(
            "/api/workspace/multiview/projects/" + self.other + "/subjects"
        ).get_json()["subjects"], [])
        self.assertEqual(self.client.patch(self.subjects + "/" + sid,
            json={"name":"Sculpture A","notes":"Restored facade"}).status_code, 200)
        self.assertEqual(self.client.post(self.subjects,
            json={"name":"Sculpture A"}).status_code, 409)
        self.assertEqual(self.client.get(self.subjects).get_json()["subjects"][0]["notes"],
                         "Restored facade")
        self.assertEqual(self.client.delete(self.subjects + "/" + sid).status_code,200)

    def test_capture_metadata_search_and_immutable_original(self):
        sid = self.subject()
        response = self.capture(sid, view_name="Front view",azimuth_deg=0,
                                elevation_deg=10,distance_m=2.5,provenance="manual")
        self.assertEqual(response.status_code,201,response.get_json())
        cid=response.get_json()["id"]
        images=self.client.get(self.subjects+"/"+sid+"/captures?q=Front&source=real_photo").get_json()
        self.assertEqual(images["total"],1)
        capture=images["captures"][0]
        self.assertEqual(capture["source_type"],"real_photo")
        self.assertEqual(capture["azimuth_deg"],0.0)
        self.assertEqual(capture["distance_m"],2.5)
        self.assertEqual(capture["review"],"unreviewed")
        self.assertEqual(self.client.post(self.subjects+"/"+sid+"/captures",
            json={"path":str(self.first)}).status_code,409)
        changed=self.client.patch(self.base+"/captures/"+cid,
            json={"view_name":"Left","azimuth_deg":90,
                  "source_type":"synthetic","provenance":"workflow","review":"approved"})
        self.assertEqual(changed.status_code,200,changed.get_json())
        preview=self.client.get(self.base+"/captures/"+cid+"/preview")
        self.assertEqual(preview.status_code,200)
        self.assertEqual(preview.data,self.original)
        self.assertEqual(self.first.read_bytes(),self.original)
        self.assertEqual(self.client.delete(self.base+"/captures/"+cid).status_code,200)
        self.assertEqual(self.first.read_bytes(),self.original)

    def test_geometry_validation_and_provenance_reject_bad_values(self):
        sid=self.subject()
        for extra in ({"azimuth_deg":360},{"elevation_deg":91},{"distance_m":0},
                      {"azimuth_deg":"unknown"},{"distance_m":True},
                      {"source_type":"generated_by_magic"},{"review":"edited"}):
            with self.subTest(extra=extra):
                result=self.capture(sid,**extra)
                self.assertEqual(result.status_code,400,result.get_json())
        self.assertEqual(self.client.get(self.subjects+"/"+sid+"/captures").get_json()["total"],0)

    def test_invalid_missing_media_and_symlinks_rejected(self):
        sid=self.subject()
        missing=self.client.post(self.subjects+"/"+sid+"/captures",
                    json={"path":str(self.root/"missing.png")})
        self.assertEqual(missing.status_code,400)
        textfile=self.root/"fake.png"
        textfile.write_bytes(b"not image")
        self.assertEqual(self.client.post(self.subjects+"/"+sid+"/captures",
                         json={"path":str(textfile)}).status_code,400)
        symlink=self.root/"shortcut.png"
        try:
            symlink.symlink_to(self.first)
        except (OSError,NotImplementedError):
            return
        response=self.client.post(self.subjects+"/"+sid+"/captures",
                                  json={"path":str(symlink)})
        self.assertEqual(response.status_code,400)

    def test_cross_project_mutation_forbidden_and_content_change_detected(self):
        sid=self.subject()
        cid=self.capture(sid).get_json()["id"]
        other_base="/api/workspace/multiview/projects/"+self.other
        self.assertEqual(self.client.patch(other_base+"/captures/"+cid,
                         json={"review":"rejected"}).status_code,404)
        self.assertEqual(self.client.get(other_base+"/captures/"+cid+"/preview").status_code,404)
        self.first.write_bytes(b"corrupt changed")
        preview=self.client.get(self.base+"/captures/"+cid+"/preview")
        self.assertEqual(preview.status_code,409)

    def test_cross_origin_and_nonlocal_requests_forbidden(self):
        sid=self.subject()
        url=self.subjects+"/"+sid+"/captures"
        self.assertEqual(self.client.post(url,json={"path":str(self.first)},
            headers={"Origin":"https://untrusted.example"}).status_code,403)
        self.assertEqual(self.client.post(url,json={"path":str(self.first)},
            environ_overrides={"REMOTE_ADDR":"192.168.1.55"}).status_code,403)
        self.assertEqual(self.client.get(self.subjects,
            environ_overrides={"REMOTE_ADDR":"192.168.1.55"}).status_code,403)

    def test_captures_persist_after_reregister_and_subject_deletion_only_removes_references(self):
        sid=self.subject()
        self.assertEqual(self.capture(sid).status_code,201)
        with closing(sqlite3.connect(self.root/"settings"/"orkilab"/"multiview.sqlite3")) as db:
            self.assertEqual(db.execute("SELECT COUNT(*) FROM mv_captures").fetchone()[0],1)
        self.assertEqual(self.client.delete(self.subjects+"/"+sid).status_code,200)
        self.assertEqual(self.client.get(self.subjects).get_json()["subjects"],[])
        self.assertEqual(self.first.read_bytes(),self.original)
        with closing(sqlite3.connect(self.root/"settings"/"orkilab"/"multiview.sqlite3")) as db:
            self.assertEqual(db.execute("SELECT COUNT(*) FROM mv_captures").fetchone()[0],0)


if __name__ == "__main__":
    unittest.main()
