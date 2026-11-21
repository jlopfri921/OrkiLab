"""Shared footer and version placement stay consistent between Workspace tools."""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]

class FooterAndVersionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.workspace=(ROOT/"GUI"/"workspace.html").read_text(encoding="utf-8")
        cls.shell=(ROOT/"assets"/"orkilab"/"orkilab-shell.js").read_text(encoding="utf-8")
        cls.styles=(ROOT/"assets"/"orkilab"/"orkilab-app-shell.css").read_text(encoding="utf-8")

    def test_footer_has_exact_project_link_and_safe_external_attributes(self):
        self.assertIn("https://github.com/jlopfri921/OrkiLab-LoRA-TrainerStudio",self.shell)
        self.assertIn('github.target = "_blank"',self.shell)
        self.assertIn('github.rel = "noopener noreferrer"',self.shell)
        self.assertIn('footer.append(notice, home, document.createTextNode(" · "), github)',self.shell)

    def test_workspace_version_moves_into_active_left_menu(self):
        self.assertIn('const versionIndicator=$("version")',self.workspace)
        self.assertIn('(onZone?$("comfy-navigation"):$("home-navigation")).append(versionIndicator)',self.workspace)
        self.assertIn('placeVersionBelowMenu(location.pathname',self.shell)
        self.assertIn('document.querySelector("#version")',self.shell)
        self.assertIn('versionIndicator',self.workspace)
        self.assertIn('$("version").textContent=d.version',self.workspace)

    def test_standalone_menu_keeps_version_on_canonical_navigation_replacement(self):
        self.assertIn('placeVersionBelowMenu(nav, document.querySelector("#version")',self.shell)
        self.assertIn('placeVersionBelowMenu(canonical, versionInHeader)',self.shell)
        self.assertIn('nav.replaceWith(canonical)',self.shell)
        self.assertIn('const version = document.getElementById("version")',self.shell)

    def test_version_is_metadata_not_sidebar_menu_action(self):
        self.assertIn('body.orki-app-frame .orki-nav-version',self.styles)
        self.assertIn('body.orki-app-frame .orki-app-footer .orki-footer-github',self.styles)

if __name__=="__main__":
    unittest.main()
