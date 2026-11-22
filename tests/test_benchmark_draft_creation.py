"""B9.5 draft authoring: atomically persist a plan, without running ComfyUI."""
import copy
import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from benchmark_draft_creation import validate_draft_payload, create_confirmed_draft
from benchmark_store import BenchmarkStore


def payload():
    return {"confirm": True, "project_id": "project-a", "name": "Compare models",
            "protocol": {
                "schema": "orkilab-repro-v1", "vary": "checkpoint",
                "workflow_id": "workflow-1", "prompt_sha256": "a" * 64,
                "negative_prompt_sha256": "b" * 64, "input_sha256": "c" * 64,
                "gpu_uuid": "GPU-test", "cache": "warm_sampler",
                "seed_policy": "fixed", "repetitions": 3,
                "resolution": [1024, 1024]},
            "variants": [
                {"label": "First model", "controlled_value": "model-a"},
                {"label": "Second model", "controlled_value": "model-b"}]}


class BenchmarkDraftCreationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)

    def test_valid_payload_has_no_mutation(self):
        data = payload()
        original = copy.deepcopy(data)
        prepared = validate_draft_payload(data)
        self.assertEqual(prepared["project_id"], "project-a")
        self.assertEqual(data, original)
        self.assertFalse((self.base / "settings").exists())

    def test_confirmed_creation_is_atomic_and_inactive(self):
        run_id = create_confirmed_draft(self.base, payload(),
                                        authorized_project_id="project-a")
        with BenchmarkStore(self.base / "settings" / "orkilab" / "benchmarks.sqlite3") as db:
            report = db.report(run_id)
        self.assertEqual(report["run"]["state"], "draft")
        self.assertEqual(len(report["variants"]), 2)
        self.assertEqual(report["observations"], [])

    def test_explicit_confirmation_required(self):
        data = payload()
        data["confirm"] = False
        with self.assertRaises(ValueError):
            create_confirmed_draft(self.base, data,
                                   authorized_project_id="project-a")
        self.assertFalse((self.base / "settings").exists())

    def test_project_scope_enforced_before_db_created(self):
        with self.assertRaises(PermissionError):
            create_confirmed_draft(self.base, payload(),
                                   authorized_project_id="different")
        self.assertFalse((self.base / "settings").exists())

    def test_duplicate_labels_and_values_rejected_before_db_created(self):
        for key in ("label", "controlled_value"):
            data = payload()
            data["variants"][1][key] = data["variants"][0][key]
            with self.subTest(key=key), self.assertRaises(ValueError):
                create_confirmed_draft(self.base, data,
                                       authorized_project_id="project-a")
        self.assertFalse((self.base / "settings").exists())

    def test_extra_fields_and_single_variant_rejected(self):
        for changed in ("extra", "single"):
            data = payload()
            if changed == "extra":
                data["evil"] = True
            else:
                data["variants"] = data["variants"][:1]
            with self.subTest(changed=changed), self.assertRaises(ValueError):
                validate_draft_payload(data)

    def test_invalid_version_or_resolution_rejected(self):
        for field, value in (("schema", "unknown"), ("resolution", [0, 0])):
            data = payload()
            data["protocol"][field] = value
            with self.subTest(field=field), self.assertRaises(ValueError):
                validate_draft_payload(data)


if __name__ == "__main__":
    unittest.main()
