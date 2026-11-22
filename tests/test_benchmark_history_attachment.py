"""B6b: explicit association with existing GenerationHistory records."""
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from generation_history import GenerationHistory
from benchmark_store import BenchmarkStore
from benchmark_history_bridge import attach_history_generation


class BenchmarkHistoryAttachmentTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.history = GenerationHistory(self.tmp.name)
        self.store = BenchmarkStore(Path(self.tmp.name) / "benchmarks.sqlite3")
        self.run = self.store.create_run("project-one", "Test", {"source": "fixture"})
        self.variant = self.store.add_variant(self.run, "variant-one", {"weight": 0.5})
        self.store.transition(self.run, "running")
        self.history.add("gen1", "http://127.0.0.1:8188", "prompt1", "workflow1",
                         "fixture", {"1": {"class_type": "SaveImage", "inputs": {}}})

    def tearDown(self):
        self.store.close()
        self.tmp.cleanup()

    def attach(self, **changes):
        arguments = dict(
            history=self.history, store=self.store, project_id="project-one",
            run_id=self.run, variant_id=self.variant, repetition=0,
            generation_id="gen1", confirmed=True,
        )
        arguments.update(changes)
        return attach_history_generation(**arguments)

    def test_confirmed_terminal_generation_retains_history_lineage(self):
        self.history.update("gen1", "completed", [])
        before = self.history.get("gen1")
        self.attach()
        record = self.store.report(self.run)["observations"][0]
        self.assertEqual(record["generation_lineage"]["generation_id"], "gen1")
        self.assertEqual(record["generation_lineage"]["comfyui_prompt_id"], "prompt1")
        self.assertIsNone(record["peak_vram_bytes"])
        self.assertEqual(self.history.get("gen1"), before)

    def test_denies_cross_project_and_no_confirmation(self):
        self.history.update("gen1", "completed", [])
        with self.assertRaises(PermissionError):
            self.attach(project_id="project-other")
        with self.assertRaises(PermissionError):
            self.attach(confirmed=False)
        self.assertEqual(self.store.report(self.run)["observations"], [])

    def test_rejects_running_history_without_writing(self):
        with self.assertRaises(ValueError):
            self.attach()
        self.assertEqual(self.store.report(self.run)["observations"], [])

    def test_uses_exact_generation_id_no_implicit_discovery(self):
        self.history.update("gen1", "completed", [])
        with self.assertRaises(KeyError):
            self.attach(generation_id="another")
        self.assertEqual(self.store.report(self.run)["observations"], [])

    def test_duplicate_same_history_generation_is_rejected(self):
        self.history.update("gen1", "completed", [])
        self.attach()
        from sqlite3 import IntegrityError
        with self.assertRaises(IntegrityError):
            self.attach(repetition=1)
        self.assertEqual(len(self.store.report(self.run)["observations"]), 1)


if __name__ == "__main__":
    unittest.main()
