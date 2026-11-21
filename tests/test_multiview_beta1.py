"""Multiview beta.1 acceptance: opt-in generated output import and provenance."""
import json
import sqlite3
import sys
import tempfile
import unittest
import uuid
from contextlib import closing
from pathlib import Path
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))

class BetaOneTests(unittest.TestCase):
    def setUp(self):
        try:
            from flask import Flask
            from PIL import Image
            import multiview_studio, multiview_assist
            from generation_history import GenerationHistory
        except ImportError as exc:
            if exc.name in ("flask","PIL"): self.skipTest("Flask/Pillow not available")
            raise
        self.multiview_assist=multiview_assist
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)
        self.project="a"*32;self.other="b"*32
        directory=self.root/"settings"/"orkilab";directory.mkdir(parents=True)
        with closing(sqlite3.connect(directory/"projects.sqlite3")) as conn,conn:
            conn.execute("CREATE TABLE projects(id TEXT PRIMARY KEY, archived INTEGER NOT NULL DEFAULT 0, category TEXT NOT NULL)")
            conn.executemany("INSERT INTO projects(id,category) VALUES (?,?)",[
                (self.project,"image"),(self.other,"image")])
        (directory/"comfyui.json").write_text(
            json.dumps({"mode":"hybrid","url":"http://127.0.0.1:8188"}),encoding="utf-8")
        self.photo=self.root/"real.png"
        Image.new("RGB",(600,600),(25,45,85)).save(self.photo)
        self.original=self.photo.read_bytes()
        app=Flask(__name__);app.config["TESTING"]=True
        multiview_studio.register(app,self.root)
        multiview_assist.register(app,self.root)
        self.client=app.test_client()
        self.base="/api/workspace/multiview/projects/"+self.project
        response=self.client.post(self.base+"/subjects",json={"name":"Sample sculpture"})
        self.assertEqual(response.status_code,201,response.get_json())
        self.sid=response.get_json()["id"]
        self.endpoint=self.base+"/subjects/"+self.sid+"/generated"
        self.job=uuid.uuid4().hex
        self.output=[dict(filename="output.png",subfolder="",type="output",
                          mime="image/png",kind="images")]
        self.graph={"1":{"class_type":"KSampler","inputs":{"seed":455,"steps":20}}}
        history=GenerationHistory(self.root)
        history.add(self.job,"http://127.0.0.1:8188","prompt-123",
                    "workflow-1","Reference workflow",self.graph)
        history.update(self.job,"completed",self.output)

    def import_body(self,**overrides):
        return dict(confirm=True,generation_id=self.job,output_index=0,
                    view_name="Generated right side",azimuth_deg=90,**overrides)

    def test_confirmed_output_is_synthetic_and_original_untouched(self):
        with patch.object(self.multiview_assist,"read_image_output",return_value=self.original) as media:
            result=self.client.post(self.endpoint,json=self.import_body())
        self.assertEqual(result.status_code,201,result.get_json())
        media.assert_called_once()
        cid=result.get_json()["id"]
        captures=self.client.get(self.base+"/subjects/"+self.sid+"/captures").get_json()["captures"]
        self.assertEqual(len(captures),1)
        c=captures[0]
        self.assertEqual((c["source_type"],c["provenance"],c["review"]),
                         ("synthetic","workflow","unreviewed"))
        self.assertEqual(c["azimuth_deg"],90)
        self.assertTrue(Path(c["path"]).exists())
        self.assertNotEqual(Path(c["path"]),self.photo)
        self.assertEqual(Path(c["path"]).read_bytes(),self.original)
        self.assertEqual(self.photo.read_bytes(),self.original)
        lineage=self.client.get(self.endpoint).get_json()["generated"]
        self.assertEqual(len(lineage),1)
        self.assertEqual(lineage[0]["capture_id"],cid)
        self.assertEqual(lineage[0]["generation_id"],self.job)
        self.assertEqual(json.loads(lineage[0]["seeds_json"]),[455])
        self.assertEqual(len(lineage[0]["workflow_sha256"]),64)

    def test_repeated_output_to_same_subject_rejected_without_extra_reference(self):
        with patch.object(self.multiview_assist,"read_image_output",return_value=self.original):
            self.assertEqual(self.client.post(self.endpoint,json=self.import_body()).status_code,201)
            self.assertEqual(self.client.post(self.endpoint,json=self.import_body()).status_code,409)
        self.assertEqual(self.client.get(self.base+"/subjects/"+self.sid+"/captures").get_json()["total"],1)

    def test_explicit_confirmation_and_completed_job_required(self):
        self.assertEqual(self.client.post(self.endpoint,json={
            "generation_id":self.job,"output_index":0}).status_code,400)
        no_confirm=self.import_body();no_confirm["confirm"]=False
        self.assertEqual(self.client.post(self.endpoint,json=no_confirm).status_code,400)
        from generation_history import GenerationHistory
        history=GenerationHistory(self.root)
        waiting=uuid.uuid4().hex
        history.add(waiting,"http://127.0.0.1:8188","prompt-new",
                    "workflow-1","Pending",self.graph)
        body=self.import_body()
        body["generation_id"]=waiting
        self.assertEqual(self.client.post(self.endpoint,json=body).status_code,409)

    def test_remote_cross_origin_and_project_isolation(self):
        result=self.client.post(self.endpoint,json=self.import_body(),
                                environ_overrides={"REMOTE_ADDR":"192.168.1.100"})
        self.assertEqual(result.status_code,403)
        result=self.client.post(self.endpoint,json=self.import_body(),
                                headers={"Origin":"https://example.org"})
        self.assertEqual(result.status_code,403)
        other="/api/workspace/multiview/projects/"+self.other+"/subjects/"+self.sid+"/generated"
        self.assertEqual(self.client.post(other,json=self.import_body()).status_code,404)

    def test_bad_output_index_and_non_image_rejected(self):
        body=self.import_body();body["output_index"]=1
        self.assertEqual(self.client.post(self.endpoint,json=body).status_code,404)
        from generation_history import GenerationHistory
        history=GenerationHistory(self.root)
        changed=[dict(self.output[0],mime="video/mp4")]
        generation=uuid.uuid4().hex
        history.add(generation,"http://127.0.0.1:8188","prompt-video","workflow-video","Video",self.graph)
        history.update(generation,"completed",changed)
        body=self.import_body();body["generation_id"]=generation
        self.assertEqual(self.client.post(self.endpoint,json=body).status_code,400)

    def test_fails_closed_if_endpoint_changes(self):
        (self.root/"settings"/"orkilab"/"comfyui.json").write_text(
            json.dumps({"mode":"native","url":"http://127.0.0.1:8188"}),encoding="utf-8")
        self.assertEqual(self.client.post(self.endpoint,json=self.import_body()).status_code,409)

    def test_seed_and_media_descriptor_validation(self):
        from multiview_assist import seed_from_graph,read_image_output
        self.assertEqual(seed_from_graph(self.graph),[455])
        self.assertEqual(seed_from_graph({"1":{"inputs":{"seed":"455"}}}),[])
        with self.assertRaises(ValueError):
            read_image_output("http://127.0.0.1:8188",dict(self.output[0],filename="../secret.png"))
        with self.assertRaises(ValueError):
            read_image_output("http://127.0.0.1:8188",dict(self.output[0],subfolder="../private"))
        with self.assertRaises(ValueError):
            read_image_output("http://127.0.0.1:8188",dict(self.output[0],type="temp"))

if __name__=="__main__": unittest.main()
