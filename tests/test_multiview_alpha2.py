"""Multiview alpha.2 tests: angle coverage, unknowns, duplicates, quality, migration."""
import sqlite3
import sys
import tempfile
import unittest
from contextlib import closing
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))

from multiview_analysis import angle_sector, analyze


def record(n, angle=None, review="unreviewed", sha=None, width=800, height=600,
           sharpness_score=25.0):
    return dict(id=f"id{n}", name=f"photo{n}.png", view_name="", source_type="real_photo",
                review=review, azimuth_deg=angle, elevation_deg=None, distance_m=None,
                width=width, height=height, sha256=sha or f"hash{n}",
                sharpness_score=sharpness_score)


class PureCoverageTests(unittest.TestCase):
    def test_wrap_and_nearest_sectors(self):
        self.assertEqual([angle_sector(x) for x in (0,14.99,15,29.9,344.99,345,359.999)],
                         [0,0,1,1,11,0,0])

    def test_unknown_not_invented_and_rejected_not_counted(self):
        report=analyze([record(1,0,"approved"),record(2,90),
                        record(3,None),record(4,180,"rejected")])
        self.assertEqual(report["unknown_angles"],1)
        self.assertEqual(report["rejected_with_angles"],1)
        self.assertEqual(report["occupied_sectors"],[0,90])
        self.assertEqual(report["missing_sectors"],[30,60,120,150,180,210,240,270,300,330])
        self.assertEqual(report["coverage_percent"],16.7)
        self.assertEqual(report["approved_coverage_percent"],8.3)
        self.assertEqual(report["sectors"][3]["provisional"],1)
        self.assertEqual(report["reviews"],dict(unreviewed=2,approved=1,rejected=1))
        self.assertIsNone(report["captures"][2]["sector_center_deg"])

    def test_quality_heuristics_and_duplicate_groups(self):
        values=[record(1,0,sha="same",width=300,height=900,sharpness_score=0),
                record(2,30,sha="same",sharpness_score=23),
                record(3,None,sharpness_score=None)]
        report=analyze(values)
        quality=report["quality"]
        self.assertEqual(quality["exact_duplicate_groups"],[["id1","id2"]])
        self.assertEqual(quality["exact_duplicate_captures"],2)
        self.assertEqual(quality["possibly_blurry"],1)
        self.assertEqual(quality["low_resolution"],1)
        self.assertEqual(quality["sharpness_unavailable"],1)
        self.assertEqual([c["exact_duplicate"] for c in report["captures"]],
                         [True,True,False])

    def test_empty_and_12_sector_coverage(self):
        empty=analyze([])
        self.assertEqual(empty["coverage_percent"],0)
        self.assertEqual(len(empty["missing_sectors"]),12)
        full=analyze([record(i,30*i,"approved") for i in range(12)])
        self.assertEqual(full["coverage_percent"],100)
        self.assertEqual(full["approved_coverage_percent"],100)
        self.assertEqual(full["missing_sectors"],[])

    def test_limited_points_not_limited_totals(self):
        from multiview_analysis import MAX_CAPTURE_POINTS
        report=analyze([record(i,None) for i in range(MAX_CAPTURE_POINTS+1)])
        self.assertTrue(report["limited"])
        self.assertEqual(report["total"],MAX_CAPTURE_POINTS+1)
        self.assertEqual(report["unknown_angles"],MAX_CAPTURE_POINTS+1)
        self.assertEqual(len(report["captures"]),MAX_CAPTURE_POINTS)


class CoverageApiTests(unittest.TestCase):
    def setUp(self):
        try:
            from flask import Flask
            from PIL import Image
            import multiview_studio
        except ImportError as exc:
            if exc.name in ("flask","PIL"):
                self.skipTest("Flask/Pillow unavailable")
            raise
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)
        self.project="a"*32
        self.other="b"*32
        dbpath=self.root/"settings"/"orkilab"
        dbpath.mkdir(parents=True)
        with closing(sqlite3.connect(dbpath/"projects.sqlite3")) as conn, conn:
            conn.execute("CREATE TABLE projects(id TEXT PRIMARY KEY, archived INTEGER NOT NULL DEFAULT 0)")
            conn.executemany("INSERT INTO projects(id) VALUES (?)",
                             [(self.project,),(self.other,)])
        self.photo=self.root/"front.png"
        Image.new("RGB",(640,480),(40,60,90)).save(self.photo)
        self.original=self.photo.read_bytes()
        app=Flask(__name__)
        app.config["TESTING"]=True
        multiview_studio.register(app,self.root)
        self.client=app.test_client()
        self.base="/api/workspace/multiview/projects/"+self.project
        response=self.client.post(self.base+"/subjects",json={"name":"Statue"})
        self.assertEqual(response.status_code,201,response.get_json())
        self.sid=response.get_json()["id"]
        self.url=self.base+"/subjects/"+self.sid+"/coverage"

    def add_capture(self,filename=None,**meta):
        return self.client.post(self.base+"/subjects/"+self.sid+"/captures",
            json={"path":str(filename or self.photo),
                  "source_type":"real_photo","provenance":"manual",**meta})

    def test_endpoint_coverage_and_manual_review_update(self):
        r=self.add_capture(azimuth_deg=359.9,review="approved")
        self.assertEqual(r.status_code,201,r.get_json())
        capture_id=r.get_json()["id"]
        coverage=self.client.get(self.url)
        self.assertEqual(coverage.status_code,200)
        data=coverage.get_json()
        self.assertEqual(data["occupied_sectors"],[0])
        self.assertEqual(data["approved_coverage_percent"],8.3)
        self.assertEqual(data["total"],1)
        self.assertIsNotNone(data["captures"][0]["sharpness_score"])
        self.assertEqual(self.client.patch(self.base+"/captures/"+capture_id,
            json={"review":"rejected"}).status_code,200)
        data=self.client.get(self.url).get_json()
        self.assertEqual(data["occupied_sectors"],[])
        self.assertEqual(data["rejected_with_angles"],1)
        self.assertEqual(self.photo.read_bytes(),self.original)

    def test_project_isolation_unknowns_and_duplicates(self):
        r=self.add_capture()
        self.assertEqual(r.status_code,201,r.get_json())
        photo2=self.root/"back.png"
        photo2.write_bytes(self.original)
        r=self.add_capture(photo2,azimuth_deg=180)
        self.assertEqual(r.status_code,201,r.get_json())
        data=self.client.get(self.url).get_json()
        self.assertEqual(data["unknown_angles"],1)
        self.assertEqual(data["quality"]["exact_duplicate_captures"],2)
        self.assertEqual(data["occupied_sectors"],[180])
        forbidden=self.client.get(self.url,environ_overrides={"REMOTE_ADDR":"192.168.1.25"})
        self.assertEqual(forbidden.status_code,403)
        other=self.client.get("/api/workspace/multiview/projects/"+self.other+
                              "/subjects/"+self.sid+"/coverage")
        self.assertEqual(other.status_code,404)
        self.assertEqual(self.photo.read_bytes(),self.original)

    def test_existing_alpha1_sqlite_migrates_without_wiping_references(self):
        self.assertEqual(self.add_capture(azimuth_deg=30).status_code,201)
        database=self.root/"settings"/"orkilab"/"multiview.sqlite3"
        with closing(sqlite3.connect(database)) as conn:
            conn.execute("UPDATE mv_captures SET sharpness_score=NULL")
            conn.commit()
        result=self.client.get(self.url).get_json()
        self.assertEqual(result["quality"]["sharpness_unavailable"],1)
        self.assertEqual(result["occupied_sectors"],[30])
        with closing(sqlite3.connect(database)) as conn:
            self.assertIn("sharpness_score",
                [c[1] for c in conn.execute("PRAGMA table_info(mv_captures)")])
            self.assertEqual(conn.execute("SELECT COUNT(*) FROM mv_captures").fetchone()[0],1)


if __name__=="__main__":
    unittest.main()
