"""0.6.0 stable-source metadata and retained RC evidence checks.

Tests do not authorize a release or independently certify operator GPU testing.
"""
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VERSION = "0.6.0"


class BenchmarkRcMetadataTests(unittest.TestCase):
    def test_version_metadata_is_staged_consistently(self):
        self.assertEqual((ROOT / "VERSION_ORKILAB").read_text(encoding="utf-8").strip(), VERSION)
        launcher = json.loads((ROOT / "GUI" / "launcher.json").read_text(encoding="utf-8"))
        self.assertEqual(launcher["orkilab_version"], VERSION)

    def test_readme_distinguishes_published_rc_and_unpublished_stable(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("Version 0.6.0 stable candidate, not published", readme)
        self.assertIn("v0.6.0-rc1", readme)
        self.assertIn("Stable 0.6.0 source candidate", readme)
        self.assertIn("RC_0_6_0_STABLE_ACCEPTANCE.md", readme)
        self.assertIn("Apache--2.0%20%2B%20MIT", readme)
        self.assertEqual(readme.count("## Version history — all phases (0.1.0 to 0.6.0)"), 1)

    def test_release_notes_and_stable_gates(self):
        notes = (ROOT / ".github" / "RELEASE_0_6_0.md").read_text(encoding="utf-8")
        self.assertIn("NOT YET PUBLISHED", notes)
        self.assertIn("Benchmark Studio", notes)
        self.assertIn("Partial ComfyUI", notes) if "Partial ComfyUI" in notes else self.assertIn("Partial", notes)
        self.assertIn("Apache-2.0", notes)
        self.assertIn("MIT", notes)
        acceptance = (ROOT / "docs" / "orkilab" / "RC_0_6_0_STABLE_ACCEPTANCE.md").read_text(encoding="utf-8")
        self.assertIn("35/35 PASS communicated", acceptance)
        for suite, total in (("E1", 5), ("E2", 6), ("E3", 6), ("E4", 6), ("E5", 6), ("E6", 6)):
            self.assertIn(f"| {suite} ({total}) |", acceptance)
        self.assertIn("NOT RELEASED OR TAGGED", acceptance)
        workflow = (ROOT / ".github" / "workflows" / "publish-0-6-stable.yml").read_text(encoding="utf-8")
        self.assertIn("PUBLISH ORKILAB 0.6.0 STABLE", workflow)
        self.assertIn("accepted_sha", workflow)
        self.assertIn("--latest", workflow)
        self.assertIn('tag="v0.6.0"', workflow)

    def test_published_rc1_historical_notes_preserved(self):
        notes = (ROOT / ".github" / "RELEASE_0_6_0_RC1.md").read_text(encoding="utf-8")
        self.assertIn("Benchmark Studio", notes)
        self.assertIn("prerelease", notes)
        self.assertIn("RTX 3090", notes)
        self.assertIn("ComfyUI", notes)

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
