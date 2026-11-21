"""RC.1 missing-view references: explicit, local, project-scoped and immutable."""
import json
import sqlite3
import sys
import tempfile
import unittest
from contextlib import closing
from pathlib import Path
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))


class MultiviewMissingViewTests(unittest.TestCase):
    def setUp(self):
        try:
            from flask import Flask
            from PIL import Image
            import multiview_studio, multiview_generate_views, multiview_assist
        except ImportError as exc:
            if exc.name in ("flask","PIL"):
                self.skipTest("Flask/Pillow required")
            raise
        self.generator=multiview_generate_views
        self.assist=multiview_assist
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)
        self.settings=self.root/"settings"/"orkilab"
        self.settings.mkdir(parents=True)
        self.project="a"*32
        self.other="b"*32
        with closing(sqlite3.connect(self.settings/"projects.sqlite3")) as conn,conn:
            conn.execute("CREATE TABLE projects (id TEXT PRIMARY KEY, archived INTEGER DEFAULT 0, category TEXT)")
            conn.executemany("INSERT INTO projects VALUES (?,0,'image')",[(self.project,),(self.other,)])
        (self.settings/"comfyui.json").write_text(json.dumps({
            "mode":"hybrid","url":"http://127.0.0.1:8188"}),encoding="utf-8")
        app=Flask(__name__);app.config["TESTING"]=True
        multiview_studio.register(app,self.root)
        multiview_assist.register(app,self.root)
        self.generator.register(app,self.root)
        self.client=app.test_client()
        base="/api/workspace/multiview/projects/"+self.project
        sub=self.client.post(base+"/subjects",json={"name":"Sample"})
        self.assertEqual(sub.status_code,201,sub.get_json())
        self.sid=sub.get_json()["id"]
        self.image=self.root/"photo.png"
        Image.new("RGB",(230,150),(65,85,120)).save(self.image)
        self.source=self.image.read_bytes()
        cap=self.client.post(base+"/subjects/"+self.sid+"/captures",json={
            "path":str(self.image),"source_type":"real_photo","review":"approved"})
        self.assertEqual(cap.status_code,201,cap.get_json())
        self.cid=cap.get_json()["id"]
        self.target=base+"/subjects/"+self.sid+"/reference-upload"
        self.import_url=base+"/subjects/"+self.sid+"/generated"

    def request_body(self):
        return {"confirm":True,"capture_ids":[self.cid]}

    def test_stage_upload_does_not_generate_or_change_originals(self):
        with patch.object(self.generator,"upload_reference",return_value="orkilab_photo.png") as upload:
            result=self.client.post(self.target,json=self.request_body())
        self.assertEqual(result.status_code,200,result.get_json())
        self.assertEqual(result.get_json()["references"],[{
            "capture_id":self.cid,"comfy_name":"orkilab_photo.png"}])
        self.assertIn("No generation",result.get_json()["note"])
        self.assertEqual(upload.call_count,1)
        self.assertEqual(upload.call_args.args[0],"http://127.0.0.1:8188")
        self.assertEqual(upload.call_args.args[2],self.source)
        self.assertEqual(self.image.read_bytes(),self.source)

    def test_reject_without_consent_or_wrong_origin_or_project(self):
        self.assertEqual(self.client.post(self.target,json={"capture_ids":[self.cid]}).status_code,400)
        self.assertEqual(self.client.post(self.target,json=self.request_body(),
            headers={"Origin":"https://another.example"}).status_code,403)
        self.assertEqual(self.client.post(self.target,json=self.request_body(),
            environ_overrides={"REMOTE_ADDR":"198.51.100.25"}).status_code,403)
        self.assertEqual(self.client.post(self.target.replace(self.project,self.other),
            json=self.request_body()).status_code,404)
        self.assertEqual(self.client.post(self.target,json={"confirm":True,
            "capture_ids":[self.cid,self.cid]}).status_code,400)

    def test_changed_source_is_not_uploaded(self):
        self.image.write_bytes(self.source+b"other")
        with patch.object(self.generator,"upload_reference") as upload:
            self.assertNotEqual(self.client.post(self.target,json=self.request_body()).status_code,200)
        upload.assert_not_called()

    def test_native_mode_has_no_upload_side_effects(self):
        (self.settings/"comfyui.json").write_text(json.dumps({
            "mode":"native","url":"http://127.0.0.1:8188"}),encoding="utf-8")
        with patch.object(self.generator,"upload_reference") as upload:
            self.assertEqual(self.client.post(self.target,json=self.request_body()).status_code,409)
        upload.assert_not_called()

    def test_requested_target_metadata_with_actual_reference_graph(self):
        from generation_history import GenerationHistory
        job="f"*32
        with closing(sqlite3.connect(self.settings/"multiview.sqlite3")) as conn:
            digest=conn.execute("SELECT sha256 FROM mv_captures WHERE id=?",(self.cid,)).fetchone()[0]
        image_name="orkilab_"+self.cid+"_"+digest[:16]+".png"
        graph={"1":{"class_type":"LoadImage","inputs":{"image":image_name}},
               "2":{"class_type":"SaveImage","inputs":{"images":["1",0]}}}
        history=GenerationHistory(self.root)
        history.add(job,"http://127.0.0.1:8188","prompt-123",
                    "workflow-ref","Reference view workflow",graph)
        history.update(job,"completed",[
            dict(filename="view.png",subfolder="",type="output",mime="image/png")])
        request=dict(confirm=True,generation_id=job,output_index=0,
                     requested_direction="back_left",requested_elevation="level",
                     requested_distance="medium",reference_capture_ids=[self.cid],
                     view_name="Back left requested")
        with patch.object(self.assist,"read_image_output",return_value=self.source):
            response=self.client.post(self.import_url,json=request)
        self.assertEqual(response.status_code,201,response.get_json())
        captures=self.client.get("/api/workspace/multiview/projects/"+
            self.project+"/subjects/"+self.sid+"/captures").get_json()["captures"]
        synthetic=next(x for x in captures if x["source_type"]=="synthetic")
        self.assertEqual(synthetic["review"],"unreviewed")
        self.assertEqual(synthetic["provenance"],"workflow")
        self.assertIsNone(synthetic["azimuth_deg"])
        self.assertEqual(synthetic["requested_direction"],"back_left")
        self.assertEqual(synthetic["requested_elevation"],"level")
        self.assertEqual(synthetic["requested_distance"],"medium")
        self.assertEqual(json.loads(synthetic["reference_capture_ids_json"]),[self.cid])
        self.assertEqual(self.image.read_bytes(),self.source)

    def test_reject_fake_reference_lineage_from_text_only_job(self):
        from generation_history import GenerationHistory
        job="e"*32
        history=GenerationHistory(self.root)
        history.add(job,"http://127.0.0.1:8188","prompt-456",
                    "workflow-text","Text only",{"1":{"class_type":"SaveImage","inputs":{}}})
        history.update(job,"completed",[
            dict(filename="view.png",subfolder="",type="output",mime="image/png")])
        request=dict(confirm=True,generation_id=job,output_index=0,
                     reference_capture_ids=[self.cid],requested_direction="front")
        with patch.object(self.assist,"read_image_output",return_value=self.source) as read:
            response=self.client.post(self.import_url,json=request)
        self.assertEqual(response.status_code,400,response.get_json())
        read.assert_not_called()
        self.assertEqual(self.image.read_bytes(),self.source)

    def test_synthetic_metadata_schema_and_validation(self):
        # Migration is non-destructive and retains original capture records.
        with closing(sqlite3.connect(self.settings/"multiview.sqlite3")) as conn:
            columns={row[1] for row in conn.execute("PRAGMA table_info(mv_captures)")}
            self.assertTrue({"requested_direction","requested_elevation",
                "requested_distance","reference_capture_ids_json"} <= columns)
        # Import validation occurs before any synthetic image copy.
        bad=self.client.post(self.import_url,json={"confirm":True,
            "generation_id":"c"*32,"output_index":0,
            "requested_direction":"invalid-direction"})
        self.assertIn(bad.status_code,(400,409))
        self.assertEqual(self.image.read_bytes(),self.source)


if __name__=="__main__":
    unittest.main()
