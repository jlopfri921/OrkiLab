"""0.6.0-rc1 staging metadata checks.

Source metadata only. Passing these checks does not authorize a release,
reconcile main, verify CI, or certify real GPU workflows.
"""
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VERSION = "0.6.0-rc1"


class BenchmarkRcMetadataTests(unittest.TestCase):
    def test_version_metadata_is_staged_consistently(self):
        self.assertEqual((ROOT / "VERSION_ORKILAB").read_text(encoding="utf-8").strip(), VERSION)
        launcher = json.loads((ROOT / "GUI" / "launcher.json").read_text(encoding="utf-8"))
        self.assertEqual(launcher["orkilab_version"], VERSION)

    def test_readme_labels_rc1_unpublished(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("0.6.0-rc1 staged", readme)
        self.assertIn("NOT published", readme)
        self.assertIn("0.6.0--rc1%20staged", readme)
        self.assertIn("RC_0_6_0_READINESS.md", readme)
        self.assertIn("Apache--2.0%20%2B%20MIT", readme)

    def test_release_notes_prohibit_premature_tagging(self):
        notes = (ROOT / ".github" / "RELEASE_0_6_0_RC1_DRAFT.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("DRAFT ONLY", notes)
        self.assertIn("not published", notes)
        self.assertIn("No tag or GitHub Release is authorized", notes)
        self.assertIn("283 Benchmark unit checks operator-reported PASS", notes)
        self.assertIn("ComfyUI", notes)

    def test_acceptance_register_keeps_manual_release_gates(self):
        acceptance = (
            ROOT / "docs" / "orkilab" / "RC_0_6_0_READINESS.md"
        ).read_text(encoding="utf-8")
        self.assertIn("283 benchmark tests operator-reported PASS", acceptance)
        for marker in ("B10.5-B", "B10.5-C", "B10.5-F", "B10.5-I", "B10.5-J"):
            self.assertIn(marker, acceptance)
        self.assertIn("No release tag, GitHub Release", acceptance)

    def test_original_mit_and_apache2_provenance_retained(self):
        apache = (ROOT / "LICENSE").read_text(encoding="utf-8")
        mit = (ROOT / "LICENSES" / "MIT-ORIGINAL").read_text(encoding="utf-8")
        policy = (ROOT / "LICENSING.md").read_text(encoding="utf-8")
        self.assertIn("Apache License", apache)
        self.assertIn("Version 2.0", apache)
        self.assertIn("MIT License", mit)
        self.assertIn("Academia SD", mit)
        self.assertIn("Apache", policy)
        self.assertIn("MIT", policy)


if __name__ == "__main__":
    unittest.main()
