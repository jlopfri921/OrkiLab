"""Regression tests for B7.2 manual recovery; isolated DBs and no ComfyUI."""
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from benchmark_store import BenchmarkStore
from benchmark_recover_binding import recover
from generation_history import GenerationHistory
from workspace_store import ProjectStore


class RecoveryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.base = Path(self.temp.name)
        folder = self.base / "settings" / "orkilab"
        folder.mkdir(parents=True)
        p = ProjectStore(folder / "projects.sqlite3").create(
            {"name": "Sample", "engine": "flux3klein", "category": "image"}, {"flux3klein"}
        )
        self.project_id = p["id"]
        self.db_path = folder / "benchmarks.sqlite3"
        with BenchmarkStore(self.db_path) as bench:
            self.run_id = bench.create_run(self.project_id, "Sample", {})
            self.variant_id = bench.add_variant(self.run_id, "Variant", {})
            bench.transition(self.run_id, "running")
        hist = GenerationHistory(self.base)
        hist.add("generation", "http://127.0.0.1:8188", "prompt", "workflow",
                 "sample", {"1": {"class_type": "SaveImage", "inputs": {}}})
        hist.update("generation", "completed", [])

    def tearDown(self):
        self.temp.cleanup()

    def run_recovery(self, **overrides):
        kw = dict(
            base=self.base, project_id=self.project_id, run_id=self.run_id,
            variant_id=self.variant_id, repetition=0,
            generation_id="generation", workflow_id="workflow",
        )
        kw.update(overrides)
        return recover(**kw)

    def test_dry_run_never_writes(self):
        result = self.run_recovery()
        self.assertTrue(result["dry_run"])
        with BenchmarkStore(self.db_path) as store:
            self.assertEqual(store.report(self.run_id)["observations"], [])
            self.assertEqual(store.db.execute(
                "SELECT COUNT(*) FROM benchmark_generation_bindings"
            ).fetchone()[0], 0)

    def test_explicit_recovery_records_lineage_once(self):
        result = self.run_recovery(confirmed=True)
        self.assertTrue(result["observation_id"])
        with BenchmarkStore(self.db_path) as store:
            report = store.report(self.run_id)
            self.assertEqual(len(report["observations"]), 1)
            self.assertEqual(report["observations"][0]["generation_lineage"]["generation_id"], "generation")
            self.assertIsNone(report["observations"][0]["duration_ms"])
        with self.assertRaises(ValueError):
            self.run_recovery(confirmed=True)

    def test_wrong_workflow_and_project_rejected(self):
        with self.assertRaises(ValueError):
            self.run_recovery(workflow_id="other", confirmed=True)
        with self.assertRaises(PermissionError):
            self.run_recovery(project_id="other", confirmed=True)
        with BenchmarkStore(self.db_path) as store:
            self.assertEqual(store.report(self.run_id)["observations"], [])

    def test_nonterminal_generation_rejected(self):
        hist = GenerationHistory(self.base)
        hist.add("running", "http://127.0.0.1:8188", "prompt2", "workflow",
                 "sample", {"1": {"class_type": "SaveImage", "inputs": {}}})
        with self.assertRaises(ValueError):
            self.run_recovery(generation_id="running", confirmed=True)


if __name__ == "__main__":
    unittest.main()
