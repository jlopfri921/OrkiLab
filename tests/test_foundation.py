"""Dependency-free foundation checks: no network, no GPU."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
BAT = "Update_LoRAlab-TrainerStudio.bat"
SH = "Update_LoRAlab-TrainerStudio.sh"


class BrandingTests(unittest.TestCase):
    def test_branding(self):
        html = (ROOT / "GUI/launcher.html").read_text(encoding="utf-8")
        cfg = json.loads((ROOT / "GUI/launcher.json").read_text(encoding="utf-8"))
        version = (ROOT / "VERSION_ORKILAB").read_text().strip()
        self.assertEqual(cfg["orkilab_version"], version)
        self.assertIn(version, (ROOT / "README.md").read_text(encoding="utf-8"))
        self.assertIn("orkilab-version", html)
        for name in ("orkilab-icon.svg", "orkilab-logo-dark.svg", "orkilab-logo-light.svg"):
            path = ROOT / "assets/orkilab" / name
            self.assertTrue(ET.parse(path).getroot().tag.endswith("svg"))
        self.assertIn("/assets/orkilab/orkilab-icon.svg", html)
        self.assertIn("/assets/orkilab/orkilab-logo-dark.svg", html)
        self.assertIn("Apache License", (ROOT / "LICENSE").read_text(encoding="utf-8"))
        self.assertIn("Academia SD", (ROOT / "LICENSES/MIT-ORIGINAL").read_text(encoding="utf-8"))
        self.assertIn("AcademiaSD LoRAlab Trainer Studio", html)

    def test_updater_guards(self):
        for name in (BAT, SH):
            text = (ROOT / name).read_text(encoding="utf-8").lower()
            for pattern in ("git reset --hard", "git remote set-url", "git checkout -f"):
                self.assertNotIn(pattern, text)
            for pattern in ("git merge --ff-only", "git diff --quiet", "git diff --cached --quiet", "--deps"):
                self.assertIn(pattern, text)


@unittest.skipUnless(shutil.which("git") and (os.name == "nt" or shutil.which("bash")), "Git and platform shell required")
class UpdaterTests(unittest.TestCase):
    def git(self, cwd, *args):
        return subprocess.run(["git", *args], cwd=cwd, check=True,
                              capture_output=True, text=True).stdout.strip()

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        root = Path(self.tmp.name)
        self.remote = root / "remote.git"
        self.source = root / "source"
        self.local = root / "local"
        self.git(root, "init", "--bare", str(self.remote))
        self.git(root, "init", "-b", "main", str(self.source))
        self.git(self.source, "config", "user.email", "test@example.invalid")
        self.git(self.source, "config", "user.name", "Test")
        for name in (BAT, SH):
            shutil.copyfile(ROOT / name, self.source / name)
        (self.source / "data.txt").write_text("base")
        self.git(self.source, "add", ".")
        self.git(self.source, "commit", "-m", "initial")
        self.git(self.source, "remote", "add", "origin", str(self.remote))
        self.git(self.source, "push", "-u", "origin", "main")
        self.git(root, "clone", "-b", "main", str(self.remote), str(self.local))
        self.git(self.local, "config", "user.email", "test@example.invalid")
        self.git(self.local, "config", "user.name", "Test")
        self.origin = self.git(self.local, "remote", "get-url", "origin")
        (self.source / "data.txt").write_text("remote update")
        self.git(self.source, "commit", "-am", "remote update")
        self.git(self.source, "push")

    def update(self):
        cmd = ["cmd", "/d", "/c", BAT] if os.name == "nt" else ["bash", SH]
        result = subprocess.run(cmd, cwd=self.local, input="\n", capture_output=True, text=True, timeout=30)
        self.assertEqual(self.origin, self.git(self.local, "remote", "get-url", "origin"))
        return result

    def test_fast_forward(self):
        result = self.update()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual((self.local / "data.txt").read_text(), "remote update")

    def test_dirty(self):
        (self.local / "data.txt").write_text("keep local")
        self.assertNotEqual(self.update().returncode, 0)
        self.assertEqual((self.local / "data.txt").read_text(), "keep local")

    def test_staged(self):
        (self.local / "data.txt").write_text("staged")
        self.git(self.local, "add", "data.txt")
        self.assertNotEqual(self.update().returncode, 0)
        self.assertEqual((self.local / "data.txt").read_text(), "staged")

    def test_diverged(self):
        (self.local / "data.txt").write_text("local commit")
        self.git(self.local, "commit", "-am", "local commit")
        old = self.git(self.local, "rev-parse", "HEAD")
        self.assertNotEqual(self.update().returncode, 0)
        self.assertEqual(old, self.git(self.local, "rev-parse", "HEAD"))

    def test_detached(self):
        self.git(self.local, "checkout", "--detach")
        self.assertNotEqual(self.update().returncode, 0)




class TrainerBrandingTests(unittest.TestCase):
    def test_trainer_branding_and_assets(self):
        cfg = json.loads((ROOT / "GUI/launcher.json").read_text(encoding="utf-8"))
        for trainer in cfg["trainers"]:
            cover = ROOT / trainer["image"]
            self.assertTrue(cover.is_file(), str(cover))
            self.assertIn("OrkiLab", cover.read_text(encoding="utf-8"))
            for name in ("orkilab-logo.svg", "orkilab-icon.svg"):
                self.assertTrue(ET.parse(cover.parent / name).getroot().tag.endswith("svg"))
        for html in (ROOT / "GUI").glob("trainer_ui_*.html"):
            content = html.read_text(encoding="utf-8")
            self.assertIn("OrkiLab", content, str(html))
            self.assertNotIn("https://www.youtube.com/@Academia_SD", content)
            self.assertNotIn('src="/assets/logo.jpg"', content)


class RetiredArtworkTests(unittest.TestCase):
    def test_no_legacy_promotional_assets(self):
        assets = ROOT / "assets"
        for name in ("AcademiaSD_LoRAlab_TrainerStudio_github.mp4", "banner_LoRAlab.png", "launcher_LoRAlab.jpg", "portada_LoRAlab.png"):
            self.assertFalse((assets / name).exists(), name)
        for name in ("portada.jpg", "logo.jpg", "logo_128.png", "interface.jpg"):
            self.assertFalse(list(assets.glob("*/" + name)), name)

if __name__ == "__main__":
    unittest.main()
