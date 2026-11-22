"""B6c offline tests for safe binding of exact submission and generation IDs."""
import json
import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from benchmark_store import BenchmarkStore
from benchmark_job_binding import bind_submitted_generation, persist_bound_generation


class BenchmarkJobBindingTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.store = BenchmarkStore(Path(self.tmp.name) / "benchmark.sqlite3")
        self.run = self.store.create_run("project-a", "test", {})
        self.variant = self.store.add_variant(self.run, "strength 0.5", {})
        self.store.transition(self.run, "running")
        self.record = {
            "id": "gen-a", "workflow_id": "workflow-a", "prompt_id": "comfy-a",
            "state": "completed", "graph": json.dumps({"1": {"class_type": "SaveImage", "inputs": {}}}),
            "outputs": "[]",
        }

    def tearDown(self):
        self.store.close()
        self.tmp.cleanup()

    def bind(self, **changes):
        args = dict(store=self.store, project_id="project-a", run_id=self.run,
                    variant_id=self.variant, repetition=0, generation_id="gen-a",
                    workflow_id="workflow-a")
        args.update(changes)
        return bind_submitted_generation(**args)

    def test_binding_and_persistence_survive_restart(self):
        self.bind()
        self.store.close()
        self.store = BenchmarkStore(Path(self.tmp.name) / "benchmark.sqlite3")
        persist_bound_generation(self.store, project_id="project-a", generation_record=self.record)
        observation = self.store.report(self.run)["observations"][0]
        self.assertEqual(observation["generation_lineage"]["generation_id"], "gen-a")
        self.assertIsNone(observation["duration_ms"])

    def test_unbound_history_cannot_be_imported(self):
        with self.assertRaises(PermissionError):
            persist_bound_generation(self.store, project_id="project-a",
                                     generation_record=self.record)
        self.assertEqual(self.store.report(self.run)["observations"], [])

    def test_wrong_project_and_workflow_are_rejected(self):
        with self.assertRaises(PermissionError):
            self.bind(project_id="project-b")
        self.bind()
        with self.assertRaises(PermissionError):
            persist_bound_generation(self.store, project_id="project-b",
                                     generation_record=self.record)
        bad = dict(self.record, workflow_id="workflow-b")
        with self.assertRaises(ValueError):
            persist_bound_generation(self.store, project_id="project-a",
                                     generation_record=bad)

    def test_one_generation_cannot_bind_twice_even_across_runs(self):
        self.bind()
        other = self.store.create_run("project-a", "other", {})
        other_variant = self.store.add_variant(other, "variant", {})
        self.store.transition(other, "running")
        with self.assertRaises(sqlite3.IntegrityError):
            self.bind(run_id=other, variant_id=other_variant)

    def test_running_result_rejected_and_duplicate_completion_rejected(self):
        self.bind()
        with self.assertRaises(ValueError):
            persist_bound_generation(self.store, project_id="project-a",
                                     generation_record=dict(self.record, state="running"))
        persist_bound_generation(self.store, project_id="project-a",
                                 generation_record=self.record)
        with self.assertRaises(sqlite3.IntegrityError):
            persist_bound_generation(self.store, project_id="project-a",
                                     generation_record=self.record)


if __name__ == "__main__":
    unittest.main()
