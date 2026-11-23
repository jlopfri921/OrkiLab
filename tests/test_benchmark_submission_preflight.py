"""B6d: validate optional benchmark submission target before ComfyUI is called."""
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from benchmark_store import BenchmarkStore
from benchmark_job_binding import preflight_submission_binding, bind_submitted_generation


class BenchmarkSubmissionPreflightTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.store = BenchmarkStore(Path(self.tmp.name) / "benchmarks.sqlite3")
        self.run = self.store.create_run("project-1", "benchmark", {})
        self.variant = self.store.add_variant(self.run, "strength 0.5", {})
        self.store.transition(self.run, "running")

    def tearDown(self):
        self.store.close()
        self.tmp.cleanup()

    def preflight(self, **overrides):
        data = dict(store=self.store, project_id="project-1", run_id=self.run,
                    variant_id=self.variant, repetition=0)
        data.update(overrides)
        return preflight_submission_binding(**data)

    def test_allows_active_variant_without_side_effects(self):
        self.preflight()
        count = self.store.db.execute(
            "SELECT count(*) FROM benchmark_generation_bindings"
        ).fetchone()[0]
        self.assertEqual(count, 0)

    def test_rejects_wrong_project_or_variant(self):
        with self.assertRaises(PermissionError):
            self.preflight(project_id="project-x")
        with self.assertRaises(PermissionError):
            self.preflight(variant_id="nonexistent")

    def test_rejects_terminal_run_and_invalid_repetition(self):
        with self.assertRaises(ValueError):
            self.preflight(repetition=True)
        self.store.transition(self.run, "cancelled")
        with self.assertRaises(ValueError):
            self.preflight()

    def test_rejects_reused_variant_repetition(self):
        bind_submitted_generation(
            self.store, project_id="project-1", run_id=self.run,
            variant_id=self.variant, repetition=0, generation_id="job-1",
            workflow_id="workflow-1",
        )
        with self.assertRaises(ValueError):
            self.preflight()


if __name__ == "__main__":
    unittest.main()
