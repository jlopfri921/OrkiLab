"""Static Workspace UX regression checks; no GPU, browser or Flask required."""
import json
import unittest
from html.parser import HTMLParser
from pathlib import Path

HTML = Path(__file__).resolve().parents[1] / "GUI" / "workspace.html"


class Inspect(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids = []
        self.views = []
        self.nav = {}
        self.context = False

    def handle_starttag(self, tag, attributes):
        attrs = dict(attributes)
        if "id" in attrs:
            self.ids.append(attrs["id"])
        if attrs.get("data-home"):
            self.views.append(attrs["data-home"])
        if tag == "a" and attrs.get("href", "").startswith("#"):
            self.nav[attrs["href"]] = True
        if attrs.get("id") == "workspace-context":
            self.context = True


class WorkspaceNavigationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html = HTML.read_text(encoding="utf-8")
        cls.parsed = Inspect()
        cls.parsed.feed(cls.html)

    def test_unique_ids(self):
        self.assertEqual(len(self.parsed.ids), len(set(self.parsed.ids)))

    def test_main_sections_are_independent(self):
        self.assertEqual(set(self.parsed.views), {"overview", "projects", "engines", "trained-loras"})
        self.assertIn('id="gpu-manager"', self.html)
        self.assertIn('function routeHome()', self.html)
        for link in ("#overview", "#projects", "#engines", "#trained-loras", "#gpu-manager"):
            self.assertIn(link, self.parsed.nav)

    def test_root_launcher_navigation_and_dashboard_shortcuts(self):
        # Both / and /workspace serve the same modern interface.
        self.assertIn('["/","/workspace","/legacy"]', self.html)
        self.assertIn('function routeHome()', self.html)
        self.assertIn('id="overview-engine-list"', self.html)
        self.assertIn('renderEngineCards($("overview-engine-list"),engines.slice(0,6))', self.html)
        self.assertIn('href="#engines"', self.html)
        self.assertIn('href="#projects"', self.html)
        self.assertIn('href="#gpu-manager"', self.html)

    def test_control_center_modules(self):
        for widget in ('control-training', 'control-projects', 'control-gpu',
                       'control-comfy', 'control-workflows', 'control-loras',
                       'control-refresh'):
            self.assertIn('id="' + widget + '"', self.html)
        for endpoint in ('/api/status', '/api/workspace/projects?archived=0',
                         '/api/workspace/gpu/monitor', '/api/workspace/comfyui',
                         '/api/workspace/workflows'):
            self.assertIn(endpoint, self.html)
        self.assertIn('function controlVisibility()', self.html)
        self.assertIn('controlVisibility();', self.html)

    def test_dashboard_text_translated_into_supported_languages(self):
        locale_root = HTML.parents[0] / "locales"
        for language in ("es", "pt", "fr", "de", "it", "ja", "ko"):
            with self.subTest(language=language):
                strings = json.loads((locale_root / (language + ".json")).read_text(encoding="utf-8"))
                for key in (
                    "Create. Train. Explore.", "Explore training engines",
                    "Workspace status", "Everything at a glance",
                    "Pending jobs: {count}", "Updated {time}",
                    "GPU metrics unavailable", "ComfyUI connection disabled",
                ):
                    self.assertTrue(strings.get(key), (language, key))

    def test_ecosystem_promotion_is_nonintrusive(self):
        for field in ('orki-promotion', 'orki-promo-title', 'orki-promo-description',
                      'orki-promo-link', 'orki-promo-dismiss'):
            self.assertIn('id="' + field + '"', self.html)
        self.assertIn('api("/api/workspace/promotions"', self.html)
        self.assertIn('rel="noopener noreferrer"', self.html)
        self.assertIn('root.hidden=false', self.html)

    def test_launcher_root_and_legacy_routes_work(self):
        # The same HTML is served by / and /legacy, not just /workspace.
        self.assertIn('["/","/workspace","/legacy"]', self.html)
        self.assertIn('window.addEventListener("hashchange",routeHome)', self.html)
        self.assertIn('routeWorkspace();routeHome();', self.html)
        for section in ('overview', 'projects', 'engines', 'gpu-manager'):
            self.assertIn('"' + section + '"', self.html)

    def test_context_help_is_present(self):
        self.assertTrue(self.parsed.context)
        for value in ('id="context-toggle"', 'id="context-description"',
                      'aria-controls="context-description"', 'function updateWorkspaceContext('):
            self.assertIn(value, self.html)

    def test_gpu_manager_shows_multiple_cards_and_hardware_metrics(self):
        for needle in ('id="gpu-overview"', 'id="gpu-cards"', 'id="gpu-choose"',
                       'gpu.memory_utilization_percent', 'gpu.power_draw_w',
                       'gpu.fan_percent', 'gpu.graphics_clock_mhz',
                       'gpu.memory_clock_mhz', 'gpu.driver_version',
                       'gpu.temperature_c', 'gpu-selected',
                       'gpuList=val(2)?.gpus||[]'):
            self.assertIn(needle, self.html)
        self.assertIn('gpuStat("Highest GPU temperature"', self.html)

    def test_comfyui_remains_separate(self):
        self.assertIn('id="comfy-navigation"', self.html)
        self.assertIn('data-module="compare"', self.html)
        self.assertIn('data-module="history"', self.html)
        self.assertIn('/workspace/comfyui', self.html)


if __name__ == "__main__":
    unittest.main()
