"""Multiview beta.2: deterministic grouped export, integrity and non-destructive ZIP."""
import hashlib
import io
import json
import sqlite3
import sys
import tempfile
import unittest
import zipfile
from contextlib import closing
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))

from multiview_export import split_for_subject, request_options, ExportError


class SplitTests(unittest.TestCase):
    def test_deterministic_independent_of_capture_count(self):
        subjects=["%032x"%i for i in range(100)]
        assignments=[split_for_subject(i,42,20) for i in subjects]
        self.assertEqual(assignments,[split_for_subject(i,42,20) for i in reversed(subjects)][::-1])
        self.assertTrue(set(assignments)=={"train","validation"})
        self.assertEqual(split_for_subject(subjects[2],42,0),"train")
        self.assertNotEqual(
            [split_for_subject(i,42,20) for i in subjects],
            [split_for_subject(i,43,20) for i in subjects])

    def test_invalid_options_and_no_unconfirmed_export(self):
        for changes in ({"validation_percent":60},{"validation_percent":True},
                        {"seed":-1},{"seed":1.2},{"include_synthetic":"yes"},
                        {"mode":"foobar"},{"mode":"download","confirm":False}):
            with self.subTest(changes=changes),self.assertRaises(ExportError):
                request_options(changes)
        self.assertEqual(request_options({"mode":"download","confirm":True})["seed"],42)


class ExportAPITests(unittest.TestCase):
    def setUp(self):
        try:
            from flask import Flask
            from PIL import Image
            import multiview_studio,multiview_export
        except ImportError as exc:
            if exc.name in ("flask","PIL"):
                self.skipTest("Flask or Pillow unavailable")
            raise
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base=Path(self.temp.name)
        self.project="a"*32
        self.other="b"*32
        settings=self.base/"settings"/"orkilab"
        settings.mkdir(parents=True)
        with closing(sqlite3.connect(settings/"projects.sqlite3")) as con,con:
            con.execute("CREATE TABLE projects(id TEXT PRIMARY KEY,category TEXT NOT NULL, name TEXT NOT NULL, archived INTEGER NOT NULL DEFAULT 0)")
            con.executemany("INSERT INTO projects(id,category,name) VALUES(?,?,?)",
                [(self.project,"image","Test multiview"),(self.other,"image","Other")])
        self.photos=[]
        for i in range(4):
            path=self.base/("image"+str(i)+".png")
            Image.new("RGB",(600+i,620+i),(20+i*10,40+i*4,60+i)).save(path)
            self.photos.append((path,path.read_bytes()))
        app=Flask(__name__);app.config["TESTING"]=True
        multiview_studio.register(app,self.base)
        multiview_export.register(app,self.base)
        self.client=app.test_client()
        self.url="/api/workspace/multiview/projects/"+self.project+"/export"
        self.subjects=[]
        for i in range(2):
            result=self.client.post("/api/workspace/multiview/projects/"+self.project+"/subjects",
                                     json={"name":"Subject "+str(i)})
            self.assertEqual(result.status_code,201,result.get_json())
            self.subjects.append(result.get_json()["id"])
        self.captures=[]
        for i in range(4):
            path,_=self.photos[i]
            sid=self.subjects[i//2]
            result=self.client.post(
                "/api/workspace/multiview/projects/"+self.project+
                "/subjects/"+sid+"/captures",
                json=dict(path=str(path),view_name="View "+str(i),
                          azimuth_deg=90*i,source_type="synthetic" if i==3 else "real_photo",
                          provenance="manual",review="approved" if i!=2 else "unreviewed"))
            self.assertEqual(result.status_code,201,result.get_json())
            self.captures.append(result.get_json()["id"])

    def post(self,data):
        return self.client.post(self.url,json=data)

    def test_preflight_filters_approved_and_synthetic(self):
        result=self.post(dict(mode="preview",seed=42,validation_percent=20))
        self.assertEqual(result.status_code,200,result.get_json())
        report=result.get_json()
        self.assertTrue(report["ready"])
        self.assertEqual(report["summary"]["captures"],2)
        self.assertEqual(report["summary"]["subjects"],1)
        self.assertEqual(report["summary"]["source_types"]["synthetic"],0)
        included=self.post(dict(mode="preview",include_synthetic=True))
        self.assertEqual(included.status_code,200,included.get_json())
        self.assertEqual(included.get_json()["summary"]["captures"],3)
        self.assertEqual(included.get_json()["summary"]["subjects"],2)

    def test_zip_repeatability_subject_groups_hashes_and_original_integrity(self):
        body=dict(mode="download",seed=1234,validation_percent=50,include_synthetic=True,confirm=True)
        first=self.post(body);second=self.post(body)
        self.assertEqual(first.status_code,200,first.get_json() if first.mimetype=="application/json" else None)
        self.assertEqual(second.status_code,200)
        self.assertEqual(first.data,second.data)
        with zipfile.ZipFile(io.BytesIO(first.data)) as archive:
            names=archive.namelist()
            self.assertEqual(names[0],"manifest.json")
            self.assertEqual(names[-1],"checksums.sha256")
            manifest=json.loads(archive.read("manifest.json"))
            self.assertEqual(manifest["format"],"orkilab-multiview-v1")
            self.assertEqual(len(manifest["captures"]),3)
            self.assertEqual(len({c["capture_id"] for c in manifest["captures"]}),3)
            for entry in manifest["captures"]:
                self.assertTrue(entry["filename"].startswith("images/"))
                self.assertEqual(hashlib.sha256(archive.read(entry["filename"])).hexdigest(),entry["sha256"])
                self.assertNotIn("path",entry)
            splits={}
            for e in manifest["captures"]:
                splits.setdefault(e["subject_id"],set()).add(e["split"])
            self.assertTrue(all(len(groups)==1 for groups in splits.values()))
            checks=archive.read("checksums.sha256").decode()
            self.assertEqual(len(checks.strip().splitlines()),4)
        for path,before in self.photos:
            self.assertEqual(path.read_bytes(),before)
        self.assertFalse((self.base/"settings"/"orkilab"/"exports").exists())

    def test_cross_origin_remote_and_other_project(self):
        self.assertEqual(self.client.post(self.url,json={"mode":"preview"},
            environ_overrides={"REMOTE_ADDR":"192.168.1.21"}).status_code,403)
        self.assertEqual(self.client.post(self.url,json={"mode":"download","confirm":True},
            headers={"Origin":"https://evil.example"}).status_code,403)
        other="/api/workspace/multiview/projects/"+self.other+"/export"
        report=self.client.post(other,json={"mode":"preview"})
        self.assertEqual(report.status_code,200)
        self.assertFalse(report.get_json()["ready"])
        self.assertEqual(report.get_json()["summary"]["captures"],0)
        self.assertEqual(self.client.post("/api/workspace/multiview/projects/"+("c"*32)+"/export",
            json={"mode":"preview"}).status_code,409)

    def test_changed_source_refuses_download_and_preview(self):
        path,original=self.photos[0]
        path.write_bytes(b"changed photo")
        for mode in ("preview","download"):
            body=dict(mode=mode,confirm=True)
            result=self.post(body)
            self.assertEqual(result.status_code,409,result.get_json())
            self.assertIn("changed",result.get_json()["error"].lower())
        self.assertEqual(path.read_bytes(),b"changed photo")
        self.assertNotEqual(path.read_bytes(),original)

    def test_unapproved_capture_cannot_be_exported(self):
        for cid in (self.captures[0],self.captures[1],self.captures[3]):
            result=self.client.patch("/api/workspace/multiview/projects/"+self.project+
                    "/captures/"+cid,json={"review":"rejected"})
            self.assertEqual(result.status_code,200)
        preview=self.post({"mode":"preview","include_synthetic":True})
        self.assertEqual(preview.status_code,200)
        self.assertFalse(preview.get_json()["ready"])
        self.assertEqual(self.post({"mode":"download","confirm":True,"include_synthetic":True}).status_code,409)

if __name__=="__main__":
    unittest.main()
