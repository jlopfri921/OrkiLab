"""B6e: terminal status finalization through existing Generation History."""
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from benchmark_store import BenchmarkStore
from benchmark_job_binding import (
    bind_submitted_generation, finalize_bound_history_generation,
)
from generation_history import GenerationHistory


class BenchmarkTerminalFinalizerTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.store = BenchmarkStore(Path(self.tmp.name) / "benchmark.sqlite3")
        self.history = GenerationHistory(self.tmp.name)
        self.run = self.store.create_run("project-a", "test", {})
        self.variant = self.store.add_variant(self.run, "variant", {})
        self.store.transition(self.run, "running")
        self.history.add("gen-a", "http://127.0.0.1:8188", "prompt-a",
                         "workflow-a", "fixture",
                         {"1": {"class_type": "SaveImage", "inputs": {}}})

    def tearDown(self):
        self.store.close()
        self.tmp.cleanup()

    def bind(self):
        bind_submitted_generation(
            self.store, project_id="project-a", run_id=self.run,
            variant_id=self.variant, repetition=0, generation_id="gen-a",
            workflow_id="workflow-a",
        )

    def finalize(self, generation_id="gen-a"):
        return finalize_bound_history_generation(self.store, self.history, generation_id)

    def test_unbound_is_ignored(self):
        self.history.update("gen-a", "completed", [])
        self.assertEqual(self.finalize(), "unbound")
        self.assertEqual(self.store.report(self.run)["observations"], [])

    def test_queued_is_pending(self):
        self.bind()
        self.assertEqual(self.finalize(), "pending")
        self.assertEqual(self.store.report(self.run)["observations"], [])

    def test_completed_is_recorded_once_and_restart_safe(self):
        self.bind()
        self.history.update("gen-a", "completed", [])
        self.assertEqual(self.finalize(), "recorded")
        self.assertEqual(self.finalize(), "already_recorded")
        self.store.close()
        self.store = BenchmarkStore(Path(self.tmp.name) / "benchmark.sqlite3")
        self.assertEqual(self.finalize(), "already_recorded")
        observations = self.store.report(self.run)["observations"]
        self.assertEqual(len(observations), 1)
        self.assertEqual(observations[0]["generation_lineage"]["generation_id"], "gen-a")

    def test_failure_is_recorded_as_failure(self):
        self.bind()
        self.history.update("gen-a", "error", [])
        self.assertEqual(self.finalize(), "recorded")
        self.assertEqual(self.store.report(self.run)["observations"][0]["status"], "failed")

    def test_cancellation_is_recorded_as_cancellation(self):
        self.bind()
        self.history.update("gen-a", "cancelled", [])
        self.assertEqual(self.finalize(), "recorded")
        self.assertEqual(self.store.report(self.run)["observations"][0]["status"], "cancelled")

    def test_unavailable_generation_is_pending(self):
        self.assertEqual(self.finalize("unknown"), "unbound")
        self.bind()
        self.assertEqual(self.finalize("gen-a"), "pending")


if __name__ == "__main__":
    unittest.main()
