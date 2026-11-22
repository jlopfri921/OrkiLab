"""Stable release guard: no accidental promotion of a release candidate."""
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class Stable05ReleaseGuards(unittest.TestCase):
    def test_stable_release_publisher_is_explicit_and_hardware_gated(self):
        path = ROOT / ".github" / "workflows" / "publish-0-5-stable.yml"
        source = path.read_text(encoding="utf-8")
        self.assertIn("workflow_dispatch:", source)
        self.assertNotIn("workflow_run:", source)
        self.assertIn("PUBLISH ORKILAB 0.5.0 STABLE", source)
        self.assertIn('test "$ACCEPTED_SHA" = "$CURRENT_SHA"', source)
        self.assertIn("RC_0_5_0_STABLE_ACCEPTANCE.md", source)
        self.assertIn('assert "| **PASS** (operator-confirmed;" in row', source)
        self.assertIn("**Status: RELEASE APPROVED", source)
        self.assertIn("OrkiLab foundation checks", source)
        self.assertIn("OrkiLab RC validation", source)
        self.assertIn("gh release create", source)
        self.assertIn('gh release view "v0.5.0"', source)
        self.assertNotIn("--prerelease", source)

    def test_stable_gate_is_signed_off_by_operator(self):
        doc = (ROOT / "docs" / "orkilab" / "RC_0_5_0_STABLE_ACCEPTANCE.md").read_text(encoding="utf-8")
        self.assertIn("stable publication acceptance", doc.lower())
        self.assertIn("v0.5.0-rc.1", doc)
        for n in range(1, 8):
            self.assertIn(f"| H{n} |", doc)
        self.assertIn("Qwen", doc)
        self.assertIn("FLUX", doc)
        self.assertIn("0.6.0", doc)
        self.assertIn("**Status: RELEASE APPROVED", doc)
        self.assertIn("operator additionally confirmed", doc.lower())

    def test_release_notes_do_not_claim_universal_gpu_compatibility(self):
        doc = (ROOT / ".github" / "RELEASE_0_5_0.md").read_text(encoding="utf-8")
        self.assertIn("0.5.0", doc)
        self.assertIn("three starter workflows", doc)
        self.assertIn("not universally validated", doc)
        self.assertIn("RC_0_5_0_STABLE_ACCEPTANCE.md", doc)


if __name__ == "__main__":
    unittest.main()
