"""B5: atomic, explicit, project-scoped ComfyUI benchmark lineage import."""
import json
import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from benchmark_store import BenchmarkStore
from benchmark_generation_import import persist_terminal_observation


class AtomicLineageTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.db_path = Path(self.directory.name) / "bench.sqlite3"
        self.store = BenchmarkStore(self.db_path)
        self.run = self.store.create_run("project-a", "test", {"seed": 42})
        self.variant = self.store.add_variant(self.run, "checkpoint-100", {"weight": 0.7})
        self.store.transition(self.run, "running")
        self.generation = {
            "id": "generation-a", "workflow_id": "workflow-a",
            "prompt_id": "comfy-id-a", "state": "completed",
            "graph": json.dumps({"1": {"class_type": "SaveImage", "inputs": {}}}),
            "outputs": "[]",
        }

    def tearDown(self):
        self.store.close()
        self.directory.cleanup()

    def save(self, repetition=0, **kw):
        return persist_terminal_observation(
            self.store, self.run, self.variant, repetition, self.generation,
            authorized_project_id=kw.get("project", "project-a"),
            confirmed=kw.get("confirmed", True),
        )

    def test_atomic_persistence_and_restart(self):
        observation_id = self.save()
        self.store.close()
        self.store = BenchmarkStore(self.db_path)
        records = self.store.report(self.run)["observations"]
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]["id"], observation_id)
        self.assertEqual(records[0]["generation_lineage"]["generation_id"], "generation-a")
        self.assertEqual(records[0]["generation_lineage"]["comfyui_prompt_id"], "comfy-id-a")
        self.assertIsNone(records[0]["duration_ms"])
        self.assertIsNone(records[0]["peak_vram_bytes"])

    def test_denies_missing_confirmation_and_cross_project(self):
        with self.assertRaises(PermissionError):
            self.save(confirmed=False)
        with self.assertRaises(PermissionError):
            self.save(project="project-b")
        self.assertEqual(self.store.report(self.run)["observations"], [])

    def test_duplicate_generation_rolls_back_observation(self):
        self.save()
        with self.assertRaises(sqlite3.IntegrityError):
            self.save(repetition=1)
        report = self.store.report(self.run)
        self.assertEqual(len(report["observations"]), 1)
        self.assertEqual(self.store.db.execute(
            "SELECT count(*) FROM benchmark_generation_lineage"
        ).fetchone()[0], 1)

    def test_reject_bad_variant_without_orphan(self):
        with self.assertRaises(ValueError):
            persist_terminal_observation(
                self.store, self.run, "wrong-variant", 0, self.generation,
                authorized_project_id="project-a", confirmed=True,
            )
        self.assertEqual(self.store.db.execute(
            "SELECT count(*) FROM benchmark_generation_lineage"
        ).fetchone()[0], 0)

    def test_terminal_failure_preserves_status(self):
        self.generation["state"] = "error"
        self.save()
        result = self.store.report(self.run)["observations"][0]
        self.assertEqual(result["status"], "failed")
        self.assertEqual(result["generation_lineage"]["status"], "failed")
        self.assertIsNone(result["output_sha256"])

if __name__ == "__main__":
    unittest.main()
