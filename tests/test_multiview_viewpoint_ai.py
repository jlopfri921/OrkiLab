"""Local viewpoint inference is a read-only opt-in guess, never measured camera geometry."""
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


class ViewpointSuggestionTests(unittest.TestCase):
    def setUp(self):
        try:
            from flask import Flask
            from PIL import Image
            import multiview_studio, multiview_viewpoint_ai
        except ImportError as exc:
            if exc.name in ("flask","PIL"):
                self.skipTest("Flask/Pillow not installed")
            raise
        self.ai=multiview_viewpoint_ai
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)
        settings=self.root/"settings"/"orkilab";settings.mkdir(parents=True)
        self.project="a"*32
        self.other="b"*32
        with closing(sqlite3.connect(settings/"projects.sqlite3")) as conn,conn:
            conn.execute("CREATE TABLE projects(id TEXT PRIMARY KEY, archived INTEGER DEFAULT 0, category TEXT)")
            conn.executemany("INSERT INTO projects(id,category) VALUES (?,?)",[(self.project,"image"),(self.other,"image")])
        self.image=self.root/"photo.png"
        Image.new("RGB",(160,110),(80,120,160)).save(self.image)
        self.original=self.image.read_bytes()
        app=Flask(__name__);app.config["TESTING"]=True
        multiview_studio.register(app,self.root)
        multiview_viewpoint_ai.register(app,self.root)
        self.client=app.test_client()
        base="/api/workspace/multiview/projects/"+self.project
        sub=self.client.post(base+"/subjects",json={"name":"Sculpture"})
        self.assertEqual(sub.status_code,201,sub.get_json())
        sid=sub.get_json()["id"]
        add=self.client.post(base+"/subjects/"+sid+"/captures",json={"path":str(self.image)})
        self.assertEqual(add.status_code,201,add.get_json())
        self.cid=add.get_json()["id"]
        self.endpoint=base+"/captures/"+self.cid+"/viewpoint/suggest"
        self.detail=base+"/subjects/"+sid+"/captures"
        self.payload={"confirm":True,"model":"local-vision:latest"}

    def test_preview_does_not_save_any_metadata_or_change_original(self):
        calls=[]
        def mock_ollama(path,payload=None,timeout=4):
            calls.append((path,payload))
            if path=="/api/show":
                return {"capabilities":["vision","completion"]}
            return {"response":json.dumps({
                "direction":"front_right","elevation":"above","distance":"medium",
                "confidence":"low"})}
        with patch.object(self.ai,"ollama_json",side_effect=mock_ollama):
            result=self.client.post(self.endpoint,json=self.payload)
        self.assertEqual(result.status_code,200,result.get_json())
        self.assertEqual(result.get_json()["direction"],"front_right")
        self.assertEqual(result.get_json()["provenance"],"estimated")
        self.assertFalse(result.get_json()["saved"])
        self.assertIsNone(result.get_json()["azimuth_deg"])
        self.assertEqual(calls[1][0],"/api/generate")
        self.assertTrue(calls[1][1]["images"][0])
        self.assertFalse(calls[1][1]["stream"])
        row=self.client.get(self.detail).get_json()["captures"][0]
        self.assertEqual(row["view_name"],"")
        self.assertEqual(row["provenance"],"unknown")
        self.assertEqual(row["review"],"unreviewed")
        self.assertIsNone(row["azimuth_deg"])
        self.assertEqual(self.image.read_bytes(),self.original)

    def test_permission_consent_and_project_isolation(self):
        self.assertEqual(self.client.post(self.endpoint,json={"model":"local-vision:latest"}).status_code,400)
        self.assertEqual(self.client.post(self.endpoint,json=self.payload,
            headers={"Origin":"https://evil.example"}).status_code,403)
        self.assertEqual(self.client.post(self.endpoint,json=self.payload,
            environ_overrides={"REMOTE_ADDR":"192.0.2.10"}).status_code,403)
        self.assertEqual(self.client.post(self.endpoint,json={"confirm":True,"model":"vision:cloud"}).status_code,400)
        other=self.endpoint.replace(self.project,self.other)
        self.assertEqual(self.client.post(other,json=self.payload).status_code,404)

    def test_invalid_model_response_and_nonvision_model(self):
        from multiview_viewpoint_ai import parse_suggestion
        for raw in ('{"direction":"north"}','{"direction":"front","confidence":"high"}',
                    '{"direction":"front","elevation":"above","distance":"far","confidence":"certain"}'):
            with self.subTest(raw=raw):
                with self.assertRaises(ValueError):parse_suggestion(raw)
        with patch.object(self.ai,"ollama_json",return_value={"capabilities":["completion"]}):
            result=self.client.post(self.endpoint,json=self.payload)
        self.assertEqual(result.status_code,400)

    def test_changed_image_is_not_analyzed(self):
        self.image.write_bytes(self.original+b" ")
        with patch.object(self.ai,"ollama_json") as mock:
            result=self.client.post(self.endpoint,json=self.payload)
        self.assertEqual(result.status_code,409)
        mock.assert_not_called()

    def test_busy_analysis_is_rejected_without_file_write(self):
        self.assertTrue(self.ai._lock.acquire(blocking=False))
        try:
            result=self.client.post(self.endpoint,json=self.payload)
            self.assertEqual(result.status_code,409)
        finally:
            self.ai._lock.release()
        self.assertEqual(self.image.read_bytes(),self.original)


if __name__=="__main__":
    unittest.main()
