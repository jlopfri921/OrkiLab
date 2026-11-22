"""B10.5 web light/dark regression checks; static, browser/GPU free."""
import unittest
from pathlib import Path


ROOT=Path(__file__).resolve().parents[1]


class OrkiLabThemeIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        assets=ROOT/"assets"/"orkilab"
        cls.js=(assets/"orkilab-theme.js").read_text(encoding="utf-8")
        cls.css=(assets/"orkilab-light-theme.css").read_text(encoding="utf-8")
        cls.shell=(assets/"orkilab-shell.js").read_text(encoding="utf-8")

    def test_main_web_modules_include_persistent_theme_resources(self):
        for page in ("workspace.html","benchmark_reports.html",
                     "dataset_studio.html","queue.html"):
            with self.subTest(page=page):
                text=(ROOT/"GUI"/page).read_text(encoding="utf-8")
                self.assertIn("/assets/orkilab/orkilab-light-theme.css",text)
                self.assertIn("/assets/orkilab/orkilab-theme.js",text)

    def test_shared_shell_loads_theme_once_for_other_modules(self):
        self.assertIn("querySelector('link[href=",self.shell)
        self.assertIn("querySelector('script[src=",self.shell)
        self.assertIn("/assets/orkilab/orkilab-light-theme.css",self.shell)
        self.assertIn("/assets/orkilab/orkilab-theme.js",self.shell)

    def test_theme_persists_without_server_or_network(self):
        self.assertIn('orkilab.ui.theme.v1',self.js)
        self.assertIn('localStorage.setItem(KEY,chosen)',self.js)
        self.assertIn('localStorage.getItem(KEY)',self.js)
        self.assertIn('window.addEventListener("storage"',self.js)
        self.assertNotIn("fetch(",self.js)

    def test_theme_has_accessible_control_and_dark_fallback(self):
        self.assertIn('button.type="button"',self.js)
        self.assertIn('aria-label',self.js)
        self.assertIn('aria-pressed',self.js)
        self.assertIn('className="orki-theme-toggle no-i18n"',self.js)
        self.assertIn('return "dark"',self.js)
        self.assertIn("orkilab-logo-light.svg",self.js)
        self.assertIn("orkilab-logo-dark.svg",self.js)

    def test_theme_toggle_supports_all_eight_languages(self):
        for lang in ("es","en","pt","fr","de","it","ja","ko"):
            with self.subTest(lang=lang):
                self.assertIn(lang+":[",self.js)
        self.assertIn('orkilab:language-changed',self.js)
        self.assertIn('select#language',self.js)
        self.assertIn('select#workspace-language',self.js)

    def test_light_mode_changes_shell_form_tables_and_benchmark_iframe(self):
        for piece in ('[data-orki-theme="light"]',
                      'color-scheme:light','--orki-app-bg:',
                      '--orki-queue-bg:',"button,input,select,textarea",
                      '#benchmark-frame','.orki-theme-toggle:focus-visible'):
            with self.subTest(piece=piece):
                self.assertIn(piece,self.css)


if __name__=="__main__":
    unittest.main()
