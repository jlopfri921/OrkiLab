"""Curated LoRA library regression tests: only Best/Final, metadata and one final."""
import sqlite3
from contextlib import closing
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
try:
    import checkpoint_reviews as reviews
except ImportError:
    reviews = None

@unittest.skipIf(reviews is None, "Flask not installed")
class CheckpointReviewsTests(unittest.TestCase):
    def setUp(self):
        temp=tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.base=Path(temp.name)
        self.project="d"*32
        settings=self.base/"settings"/"orkilab"
        settings.mkdir(parents=True)
        with closing(sqlite3.connect(settings/"projects.sqlite3")) as con, con:
            con.execute("CREATE TABLE projects(id TEXT PRIMARY KEY,name TEXT,engine TEXT,category TEXT,archived INTEGER)")
            con.execute("INSERT INTO projects VALUES (?,?,?,?,0)",(self.project,"Prueba","flux3klein","image"))
        output=self.base/"Outputs"/("flux3klein_lora_output_orkilab_"+self.project[:12])
        output.mkdir(parents=True)
        for step in (100,300):
            (output/f"Flux3Klein_LoRA_step_{step}.safetensors").write_bytes(b"checkpoint")
        with closing(sqlite3.connect(settings/"workflows.sqlite3")) as con, con:
            con.execute("CREATE TABLE workflows(id TEXT PRIMARY KEY,name TEXT)")
            con.execute("INSERT INTO workflows VALUES ('wf1','Flux.3 comparison')")
        self.first="Flux3Klein_LoRA_step_100.safetensors"
        self.second="Flux3Klein_LoRA_step_300.safetensors"

    def test_ratings_alone_do_not_create_catalog_entries(self):
        reviews.save_review(self.base,self.project,self.first,rating=5,notes="High quality")
        self.assertEqual(reviews.catalog(self.base),[])

    def test_best_or_final_creates_metadata_card(self):
        reviews.save_review(self.base,self.project,self.first,rating=5,is_best=True,is_final=True,
            base_model="FLUX.3 Klein",workflow_id="wf1",duration_minutes=18.5,
            gpu_name="RTX 3090",gpu_vram_gb=24,peak_vram_gb=19.2,peak_ram_gb=34.5)
        models=reviews.catalog(self.base)
        self.assertEqual(len(models),1)
        model=models[0]
        self.assertEqual(model["step"],100)
        self.assertEqual(model["engine"],"flux3klein")
        self.assertEqual(model["base_model"],"FLUX.3 Klein")
        self.assertEqual(model["workflow_name"],"Flux.3 comparison")
        self.assertEqual(model["gpu_name"],"RTX 3090")
        self.assertEqual(model["metrics_source"],"user_supplied")
        self.assertTrue(model["source_path"].endswith(self.first))
        self.assertTrue(Path(model["source_path"]).exists())

    def test_only_one_final_per_project(self):
        reviews.save_review(self.base,self.project,self.first,rating=5,is_best=True,is_final=True)
        reviews.save_review(self.base,self.project,self.second,rating=3,is_final=True)
        models=reviews.catalog(self.base)
        self.assertEqual(len(models),2)
        self.assertEqual([m["step"] for m in models if m["is_final"]],[300])
        self.assertTrue(any(m["step"]==100 and m["is_best"] for m in models))

    def test_unmark_removes_from_library_without_deleting_original(self):
        reviews.save_review(self.base,self.project,self.first,is_best=True)
        reviews.save_review(self.base,self.project,self.first,is_best=False)
        self.assertEqual(reviews.catalog(self.base),[])
        self.assertTrue((self.base/"Outputs"/("flux3klein_lora_output_orkilab_"+self.project[:12])/self.first).exists())

    def test_missing_metrics_stay_unrecorded(self):
        reviews.save_review(self.base,self.project,self.first,is_final=True)
        item=reviews.catalog(self.base)[0]
        self.assertIsNone(item["duration_minutes"])
        self.assertIsNone(item["peak_ram_gb"])
        self.assertEqual(item["metrics_source"],"not_recorded")

    def test_reference_image_requires_curated_model(self):
        import base64
        image = b"\x89PNG\r\n\x1a\n" + b"0"*24
        with self.assertRaises(ValueError):
            reviews.set_reference_image(self.base,self.project,self.first,base64.b64encode(image).decode("ascii"))

    def test_reference_image_is_saved_and_returned_only_for_curated_model(self):
        import base64
        image = b"\x89PNG\r\n\x1a\n" + b"0"*24
        reviews.save_review(self.base,self.project,self.first,rating=5,is_final=True)
        ext=reviews.set_reference_image(self.base,self.project,self.first,base64.b64encode(image).decode("ascii"))
        self.assertEqual(ext,".png")
        model=reviews.catalog(self.base)[0]
        self.assertIn("/api/workspace/trained-loras/reference/",model["reference_url"])
        path=reviews.reference_file(self.base,self.project,self.first,ext)
        self.assertEqual(path.read_bytes(),image)
        self.assertTrue(Path(model["source_path"]).exists())

    def test_reference_image_rejects_malformed_or_large_files(self):
        import base64
        reviews.save_review(self.base,self.project,self.first,is_best=True)
        for data in ("not base64!",base64.b64encode(b"invalid").decode("ascii")):
            with self.assertRaises(ValueError):
                reviews.set_reference_image(self.base,self.project,self.first,data)
        with self.assertRaises(ValueError):
            reviews.set_reference_image(self.base,self.project,self.first,base64.b64encode(b"x"*2_000_001).decode("ascii"))

    def test_rejects_unknown_workflow(self):
        with self.assertRaises(ValueError):
            reviews.save_review(self.base,self.project,self.first,is_best=True,workflow_id="fake")
