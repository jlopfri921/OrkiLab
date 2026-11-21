"""Mobile navigation remains available on all screens without a top menu."""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]

class MobileNavigationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.shell = (ROOT / "assets" / "orkilab" / "orkilab-shell.js").read_text(encoding="utf-8")
        cls.css = (ROOT / "assets" / "orkilab" / "orkilab-app-shell.css").read_text(encoding="utf-8")

    def test_bottom_navigation_is_shared_and_accessible(self):
        for token in (
            "function setupMobileNavigation()",
            'root.id = "orki-mobile-navigation"',
            'bar.setAttribute("aria-label", "Mobile navigation")',
            'sheet.setAttribute("role", "dialog")',
            'sheet.setAttribute("aria-modal", "true")',
            'el.setAttribute("aria-current","page")',
            'el.setAttribute("aria-controls","orki-mobile-sheet")',
            'event.key==="Escape"',
            "focusables.at(-1).focus()",
            'lastFocus.focus()',
        ):
            with self.subTest(token=token):
                self.assertIn(token, self.shell)

    def test_mobile_tabs_have_more_sheet_with_real_menu_actions(self):
        for token in (
            '["/workspace#overview",0,"home"]',
            '["/workspace#projects",1,"projects"]',
            '["/workspace/datasets",2,"datasets"]',
            '[null,3,"more"]',
            '["/workspace/comfyui#comfyui",5,"connect"]',
            '["/workspace/comfyui#generation",6,"generate"]',
            'source.querySelectorAll(":scope > a, :scope > button")',
            'if (action === "settings-open") location.assign("/workspace?dialog=settings")',
            'else if (action === "shutdown-open") location.assign("/workspace?dialog=shutdown")',
            'function menuSource()',
            'if (isComfy()) return document.querySelector("#comfy-navigation");',
        ):
            with self.subTest(token=token):
                self.assertIn(token,self.shell)

    def test_sidebar_hidden_only_on_mobile_and_bottom_space_reserved(self):
        self.assertIn("@media(max-width:760px)",self.css)
        self.assertIn("body.orki-app-frame .orki-mobile-bar",self.css)
        self.assertIn("body.orki-app-frame .orki-mobile-sheet",self.css)
        self.assertIn("body.orki-app-frame .orki-mobile-options",self.css)
        self.assertIn("body.orki-app-frame .orki-app-nav,",self.css)
        self.assertIn("display:none!important;",self.css)
        self.assertIn("env(safe-area-inset-bottom,0px)",self.css)
        self.assertIn("padding-bottom:calc(92px + env(safe-area-inset-bottom,0px))",self.css)
        self.assertIn("body.orki-app-frame #orki-mobile-navigation{display:none}",self.css)

    def test_existing_navigation_is_preserved(self):
        self.assertIn('        setupMobileNavigation();',self.shell)
        self.assertIn('nav.replaceWith(canonical)',self.shell)
        self.assertIn('placeVersionBelowMenu(canonical, versionInHeader)',self.shell)
        self.assertIn('unifiedFooter(content, t)',self.shell)

if __name__ == "__main__":
    unittest.main()
