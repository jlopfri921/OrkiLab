"""Contract tests for the isolated 0.6 alpha benchmark persistence layer."""
import json
import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from benchmark_store import BenchmarkStore


class BenchmarkStoreTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = Path(self.tmp.name) / "nested" / "benchmarks.sqlite3"
        self.store = BenchmarkStore(self.path)

    def tearDown(self):
        self.store.close()
        self.tmp.cleanup()

    def test_persists_reproducible_configs_and_observations(self):
        run = self.store.create_run("project-1", "LoRA sweep", {"prompt": "object", "seed": 42})
        variant = self.store.add_variant(run, "strength-0.7", {"lora_weight": 0.7, "model": "local"})
        self.store.transition(run, "running")
        self.store.record(run, variant, 0, "completed", seed=42,
                          duration_ms=18200, peak_vram_bytes=12_000_000_000,
                          output_sha256="a" * 64)
        self.store.transition(run, "completed")
        before = self.store.report(run)
        self.store.close()
        self.store = BenchmarkStore(self.path)
        after = self.store.report(run)
        self.assertEqual(before, after)
        self.assertEqual(after["run"]["protocol"]["seed"], 42)
        self.assertEqual(after["observations"][0]["peak_vram_bytes"], 12_000_000_000)

    def test_draft_requires_variant_and_terminal_runs_are_immutable(self):
        run = self.store.create_run("p", "name", {})
        with self.assertRaises(ValueError):
            self.store.transition(run, "running")
        v = self.store.add_variant(run, "first", {})
        self.store.transition(run, "running")
        with self.assertRaises(ValueError):
            self.store.add_variant(run, "second", {})
        self.store.transition(run, "cancelled")
        with self.assertRaises(ValueError):
            self.store.record(run, v, 0, "completed")
        with self.assertRaises(ValueError):
            self.store.transition(run, "running")

    def test_reject_cross_run_observations_and_duplicates(self):
        a = self.store.create_run("a", "a", {})
        b = self.store.create_run("b", "b", {})
        va = self.store.add_variant(a, "v", {})
        self.store.add_variant(b, "v", {})
        self.store.transition(a, "running")
        self.store.transition(b, "running")
        with self.assertRaises(ValueError):
            self.store.record(b, va, 0, "completed")
        self.store.record(a, va, 0, "failed", error_message="test error")
        with self.assertRaises(sqlite3.IntegrityError):
            self.store.record(a, va, 0, "failed")

    def test_reject_bad_inputs(self):
        with self.assertRaises(ValueError):
            self.store.create_run("", "name", {})
        with self.assertRaises(ValueError):
            self.store.create_run("p", "name", {"bad": float("nan")})
        run = self.store.create_run("p", "name", {})
        v = self.store.add_variant(run, "v", {})
        self.store.transition(run, "running")
        with self.assertRaises(ValueError):
            self.store.record(run, v, -1, "completed")
        with self.assertRaises(ValueError):
            self.store.record(run, v, 0, "completed", duration_ms=-1)
        with self.assertRaises(ValueError):
            self.store.record(run, v, 0, "completed", output_sha256="not-a-hash")


if __name__ == "__main__":
    unittest.main()
