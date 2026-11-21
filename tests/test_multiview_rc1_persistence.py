"""RC.1 integration acceptance: persistent project and photo links across restart."""
import json
import sqlite3
import sys
import tempfile
import unittest
from contextlib import closing
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))


class RecoveryIntegrationTests(unittest.TestCase):
    def setUp(self):
        try:
            from flask import Flask
            from PIL import Image
            import multiview_studio, multiview_recovery
            from workspace_store import ProjectStore
        except ImportError as exc:
            if exc.name in ("flask","PIL"):
                self.skipTest("Flask and Pillow required for RC1 integration")
            raise
        self.mv=multiview_studio
        self.recovery=multiview_recovery
        self.root=tempfile.TemporaryDirectory()
        self.addCleanup(self.root.cleanup)
        self.base=Path(self.root.name)
        self.settings=self.base/"settings"/"orkilab"
        self.settings.mkdir(parents=True)
        self.store=ProjectStore(self.settings/"projects.sqlite3")
        self.project=self.store.create(
            dict(name="Multiview saved project",category="image",engine="image-demo"),
            {"image-demo"})["id"]
        self.other=self.store.create(
            dict(name="Different project",category="image",engine="image-demo"),
            {"image-demo"})["id"]
        self.image=self.base/"image.png"
        Image.new("RGB",(600,580),(66,88,120)).save(self.image)
        self.source=self.image.read_bytes()
        self.missing=self.base/"missing.png"
        self.photo_id="c"*32
        self.bad_id="d"*32
        with closing(sqlite3.connect(self.settings/"datasets.sqlite3")) as con,con:
            con.execute("""CREATE TABLE dataset_images(
                id TEXT PRIMARY KEY,project_id TEXT,path TEXT,name TEXT,
                review TEXT NOT NULL DEFAULT 'unreviewed')""")
            con.executemany(
                "INSERT INTO dataset_images VALUES (?,?,?,?,?)",
                [(self.photo_id,self.project,str(self.image),"Front photo","approved"),
                 (self.bad_id,self.project,str(self.missing),"Missing photo","unreviewed"),
                 ("e"*32,self.other,str(self.image),"Other project photo","approved")])
        self.client=self.new_client()
        self.baseurl="/api/workspace/multiview/projects/"+self.project
        subject=self.client.post(self.baseurl+"/subjects",json={"name":"Statue"})
        self.assertEqual(subject.status_code,201,subject.get_json())
        self.sid=subject.get_json()["id"]
        self.recovery_url=self.baseurl+"/recovery"
        self.link_url=self.baseurl+"/subjects/"+self.sid+"/link-dataset"

    def new_client(self):
        from flask import Flask
        app=Flask(__name__)
        app.config["TESTING"]=True
        self.mv.register(app,self.base)
        self.recovery.register(app,self.base)
        return app.test_client()

    def test_project_saved_before_restart_remains_the_same(self):
        first=self.store.list()
        self.assertEqual({p["id"] for p in first},{self.project,self.other})
        second=self.new_client()
        self.assertEqual(second.get(self.recovery_url).status_code,200)
        self.assertEqual(self.store.list(),first)
        subjects=second.get(self.baseurl+"/subjects").get_json()["subjects"]
        self.assertEqual([s["id"] for s in subjects],[self.sid])

    def test_empty_multiview_but_dataset_photos_found_and_safe_link(self):
        status=self.client.get(self.recovery_url)
        self.assertEqual(status.status_code,200,status.get_json())
        data=status.get_json()
        self.assertEqual(data["multiview_subjects"],1)
        self.assertEqual(data["multiview_captures"],0)
        self.assertEqual(data["dataset_images"],2)
        self.assertEqual([x["available"] for x in data["candidates"]],[True,False])
        payload=dict(confirm=True,image_ids=[self.photo_id])
        linked=self.client.post(self.link_url,json=payload)
        self.assertEqual(linked.status_code,200,linked.get_json())
        self.assertEqual(linked.get_json()["linked"],1)
        self.assertEqual(self.client.post(self.link_url,json=payload).get_json()["linked"],0)
        restarted=self.new_client()
        saved=restarted.get(self.baseurl+"/subjects/"+self.sid+"/captures").get_json()
        self.assertEqual(saved["total"],1)
        entry=saved["captures"][0]
        self.assertEqual(entry["review"],"unreviewed")
        self.assertEqual(entry["source_type"],"unknown")
        self.assertEqual(entry["provenance"],"unknown")
        self.assertIsNone(entry["azimuth_deg"])
        self.assertEqual(entry["path"],str(self.image))
        self.assertEqual(restarted.get(self.recovery_url).get_json()["multiview_captures"],1)
        self.assertEqual(self.image.read_bytes(),self.source)

    def test_invalid_ids_missing_files_and_project_isolation(self):
        self.assertEqual(self.client.post(self.link_url,json={
            "confirm":True,"image_ids":[self.bad_id]}).status_code,400)
        self.assertEqual(self.client.post(self.link_url,json={
            "confirm":True,"image_ids":["e"*32]}).status_code,404)
        self.assertEqual(self.client.post(self.link_url,json={
            "confirm":True,"image_ids":[self.photo_id,self.photo_id]}).status_code,400)
        self.assertEqual(self.client.post(self.link_url,json={
            "confirm":False,"image_ids":[self.photo_id]}).status_code,400)
        self.assertEqual(self.client.post(self.link_url,json={
            "confirm":True,"image_ids":[self.photo_id]},
            headers={"Origin":"https://attacker.invalid"}).status_code,403)
        self.assertEqual(self.client.post(self.link_url,json={
            "confirm":True,"image_ids":[self.photo_id]},
            environ_overrides={"REMOTE_ADDR":"192.168.1.77"}).status_code,403)
        self.assertEqual(self.client.get(self.recovery_url,
            environ_overrides={"REMOTE_ADDR":"192.168.1.77"}).status_code,403)
        self.assertEqual(self.client.get(
            "/api/workspace/multiview/projects/"+self.other+"/recovery"
            ).get_json()["dataset_images"],1)
        self.assertEqual(self.image.read_bytes(),self.source)
        self.assertEqual(self.client.get(self.baseurl+"/subjects/"+self.sid+"/captures"
            ).get_json()["total"],0)

    def test_archive_only_hides_project_and_recovers_after_restore(self):
        self.assertTrue(self.store.archive(self.project,True))
        self.assertEqual(self.client.get(self.recovery_url).status_code,404)
        self.assertEqual(self.client.post(self.link_url,json={
            "confirm":True,"image_ids":[self.photo_id]}).status_code,404)
        self.assertTrue(self.store.archive(self.project,False))
        self.assertEqual(self.new_client().get(self.recovery_url).status_code,200)

    def test_missing_original_detected_without_mutating_db(self):
        self.assertEqual(self.client.post(self.link_url,json={
            "confirm":True,"image_ids":[self.photo_id]}).status_code,200)
        self.image.unlink()
        response=self.new_client().get(self.recovery_url)
        self.assertEqual(response.status_code,200)
        self.assertEqual(response.get_json()["missing_originals"],1)
        self.assertEqual(response.get_json()["multiview_captures"],1)


if __name__=="__main__":
    unittest.main()
