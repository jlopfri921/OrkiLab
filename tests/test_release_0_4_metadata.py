"""Current release metadata consistency and historical 0.4 RC documentation."""
import json
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

class Release04CandidateTests(unittest.TestCase):
    def test_launcher_version_and_readme_badge_match(self):
        version=(ROOT/"VERSION_ARKILAB").read_text(encoding="utf-8").strip()
        launcher=json.loads((ROOT/"GUI"/"launcher.json").read_text(encoding="utf-8"))
        readme=(ROOT/"README.md").read_text(encoding="utf-8")
        self.assertRegex(version,r"^\d+\.\d+\.\d+(?:-(?:alpha|beta|rc)\.\d+)?$")
        self.assertEqual(launcher["arkilab_version"],version)
        self.assertIn("alt=\"Version "+version+"\"",readme)
        self.assertIn("version-"+version.replace("-","--"),readme)
        self.assertIn("0.4.0-rc.1",readme)  # prior published prerelease retained

    def test_readiness_notes_are_explicit_and_do_not_claim_stable(self):
        note=(ROOT/"docs"/"arkilab"/"RC_0_4_0_READINESS.md").read_text(encoding="utf-8")
        self.assertIn("**Release state:**",note)
        self.assertIn("stable",note.lower())
        self.assertIn("NOT VERIFIED END TO END",note)
        self.assertIn("train/validation split",note)
        self.assertIn("Windows",note)
        self.assertIn("Ubuntu",note)

    def test_changelog_and_roadmap_show_candidate_and_stable_gates(self):
        changelog=(ROOT/"CHANGELOG_ARKILAB.md").read_text(encoding="utf-8")
        roadmap=(ROOT/"docs"/"arkilab"/"ROADMAP.md").read_text(encoding="utf-8")
        self.assertIn("## 0.4.0-rc.1",changelog)
        self.assertIn("## Current milestone: 0.5.0-rc.1",roadmap)
        self.assertIn("## Previous milestone: 0.4.0-rc.1",roadmap)
        self.assertIn("## 0.5.0-rc.1",changelog)
        self.assertIn("RC_0_5_0_READINESS.md",roadmap)
        self.assertIn("Stable 0.4.0 gate (not yet met)",roadmap)

if __name__=="__main__":
    unittest.main()
