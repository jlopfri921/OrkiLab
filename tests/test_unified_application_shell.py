"""Unified Workspace chrome regression contract (no browser/GPU dependency)."""
import re
import unittest
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGES = ("workspace.html", "queue.html", "dataset_studio.html")
CSS_PATH = "/assets/orkilab/orkilab-app-shell.css"
JS_PATH = "/assets/orkilab/orkilab-shell.js"


class Elements(HTMLParser):
    def __init__(self):
        super().__init__()
        self.css_links = []
        self.scripts = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "link" and attrs.get("rel") == "stylesheet":
            self.css_links.append(attrs.get("href"))
        if tag == "script" and attrs.get("src"):
            self.scripts.append(attrs["src"])


class UnifiedChromeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.css = (ROOT / "assets" / "orkilab" / "orkilab-app-shell.css").read_text(encoding="utf-8")
        cls.js = (ROOT / "assets" / "orkilab" / "orkilab-shell.js").read_text(encoding="utf-8")

    def test_every_main_page_loads_same_final_css_and_shell_controller(self):
        for name in PAGES:
            with self.subTest(page=name):
                html = (ROOT / "GUI" / name).read_text(encoding="utf-8")
                parsed = Elements()
                parsed.feed(html)
                self.assertEqual(parsed.css_links[-2:], [CSS_PATH, "/assets/orkilab/orkilab-light-theme.css"])
                self.assertEqual(parsed.css_links.count(CSS_PATH),1)
                self.assertIn("/assets/orkilab/orkilab-theme.js", parsed.scripts)
                self.assertIn(JS_PATH, parsed.scripts)
                self.assertEqual(parsed.scripts.count(JS_PATH), 1)

    def test_single_visual_source_for_header_nav_grid_context_and_footer(self):
        for needle in (
            "--orki-app-bg:", "--orki-app-panel:", "--orki-app-border:",
            "--orki-app-text:", "--orki-app-accent:", "--orki-app-gradient:",
            "--orki-app-width:1440px", "--orki-app-side:200px",
            "--orki-app-gap:24px", "--orki-app-radius:16px",
            ".orki-app-header", ".orki-app-nav", ".orki-app-context",
            ".orki-app-footer", ".queue-shell", ".studio-layout",
            "#home-navigation", "#comfy-navigation", "@media(max-width:760px)"
        ):
            with self.subTest(css=needle):
                self.assertIn(needle, self.css)

    def test_shell_is_installed_on_workspace_queue_dataset_and_comfyui(self):
        for needle in (
            "function unifiedFooter(", "function renderWorkspaceChrome(",
            'document.querySelector("#home-navigation")',
            'document.querySelector("#workspace-body")',
            'document.querySelector("#comfy-navigation")',
            'page === "queue" ? ".queue-sidebar" : ".studio-navigation"',
            'body.classList.add("orki-app-frame"',
            'unifiedFooter(content, names[locale])',
            'unifiedFooter(content, t)',
            'header.classList.add("orki-shell-header", "orki-app-header")',
            'canonical.className = ',
            'canonicalNav.cloneNode(true)',
            'nav.replaceWith(canonical)',
        ):
            with self.subTest(js=needle):
                self.assertIn(needle, self.js)

    def test_queue_and_dataset_headers_use_exact_workspace_markup(self):
        import re
        def first_header(page):
            html = (ROOT / "GUI" / page).read_text(encoding="utf-8")
            match = re.search(r"<header(?:[ ]+[^>]*)?>(.*?)</header>", html, re.DOTALL)
            self.assertIsNotNone(match, page)
            return match.group(1)
        original = first_header("workspace.html")
        for page in ("queue.html", "dataset_studio.html"):
            with self.subTest(page=page):
                self.assertEqual(first_header(page), original)
                html = (ROOT / "GUI" / page).read_text(encoding="utf-8")
                self.assertIn('class="orki-shell-header orki-app-header"', html)

    def test_navigation_returns_to_page_top_on_all_pages(self):
        workspace = (ROOT / "GUI" / "workspace.html").read_text(encoding="utf-8")
        for key in ("history.scrollRestoration", 'window.addEventListener("pageshow"',
                    'window.scrollTo(0,0)', 'document.addEventListener("click"'):
            with self.subTest(key=key):
                self.assertTrue(key in self.js or key in workspace)
        self.assertIn("scrollWorkspaceTop();", workspace)
        self.assertNotIn('<a href="/workspace" class="back-link">', workspace)

    def test_queue_job_rows_are_scoped_away_from_shared_header(self):
        queue = (ROOT / "GUI" / "queue.html").read_text(encoding="utf-8")
        style = queue.split("<style>", 1)[1].split("</style>", 1)[0]
        self.assertIn(".wrap .row { display: grid;", style)
        self.assertIn(".wrap .row:hover", style)
        self.assertIn(".wrap .row.hist", style)
        # A bare .row selector also targets the header's language/version group,
        # giving it a card background, padding, and grid columns.
        import re
        self.assertIsNone(re.search(r"(?<![\\w-])(?<!\\.wrap )\\.row(?:\\s|\\.|:|\\{)", style))
        self.assertIn('<header class="orki-shell-header orki-app-header">', queue)
        self.assertIn('<div class="row"><label><span>Language</span>', queue)
        for property in ("background:transparent;", "padding:0;",
                         "border:0;", "grid-template-columns:none;"):
            self.assertIn(property, self.css)

    def test_queue_does_not_acquire_a_second_language_selector(self):
        helper = (ROOT / "assets" / "orkilab" / "orkilab-ui.js").read_text(encoding="utf-8")
        self.assertIn("#ui-lang,#workspace-language,#orki-language,.queue-shell,.studio-layout", helper)
        self.assertIn('selector.id = "orki-shell-language"', self.js)
        self.assertIn('header.querySelector("#workspace-language")', self.js)

    def test_comfy_zone_keeps_only_its_own_menu(self):
        self.assertNotIn('home.cloneNode(true)', self.js)
        self.assertIn('document.querySelector("#comfy-navigation")', self.js)
        self.assertIn('comfy?.querySelectorAll(".orki-global-nav")', self.js)

    def test_aqua_menu_links_except_white_settings_and_shutdown(self):
        for token in (
            "body.orki-app-frame .orki-app-nav > a,",
            "body.orki-app-frame #home-navigation > a,",
            "body.orki-app-frame #comfy-navigation > a {",
            "color:#3cdbd0;",
            "body.orki-app-frame .orki-app-nav > button,",
            "body.orki-app-frame #home-navigation > button,",
            "color:#fff;",
            "body.orki-app-frame .orki-app-nav > a:is(:hover,[aria-current=\"page\"])",
        ):
            with self.subTest(token=token):
                self.assertIn(token, self.css)

    def test_comfyui_has_only_local_menu_and_first_back_link(self):
        workspace = (ROOT / "GUI" / "workspace.html").read_text(encoding="utf-8")
        start = workspace.index('<nav id="comfy-navigation"')
        end = workspace.index("</nav>", start)
        comfy = workspace[start:end]
        self.assertIn('href="/workspace"', comfy)
        self.assertIn("Main dashboard", comfy)
        self.assertLess(comfy.index('href="/workspace"'), comfy.index('href="#welcome"'))
        import json
        for lang in ("es", "pt", "fr", "de", "it", "ja", "ko"):
            with self.subTest(language=lang):
                strings = json.loads((ROOT / "GUI" / "locales" / (lang + ".json")).read_text(encoding="utf-8"))
                self.assertTrue(strings.get("Main dashboard"))
        es = json.loads((ROOT / "GUI" / "locales" / "es.json").read_text(encoding="utf-8"))
        self.assertEqual(es["Main dashboard"], "Panel principal")
        self.assertNotIn("orki-global-nav", comfy)
        self.assertNotIn('home.cloneNode(true)', self.js)
        self.assertIn('comfy?.querySelectorAll(".orki-global-nav")', self.js)

    def test_dataset_has_same_official_favicon_as_workspace(self):
        dataset = (ROOT / "GUI" / "dataset_studio.html").read_text(encoding="utf-8")
        workspace = (ROOT / "GUI" / "workspace.html").read_text(encoding="utf-8")
        icon = "/assets/orkilab/orkilab-icon.svg"
        self.assertIn('rel="icon" type="image/svg+xml" href="' + icon + '"', dataset)
        self.assertIn('rel="icon" href="' + icon + '"', workspace)

    def test_standalone_uses_actual_workspace_markup_not_an_alternate_menu(self):
        self.assertIn('source.querySelector("body > header")', self.js)
        self.assertIn('source.querySelector("#home-navigation")', self.js)
        self.assertIn('source.querySelector("#workspace-context")', self.js)
        self.assertIn('fetch("/workspace"', self.js)
        self.assertIn('I18N.apply(canonical)', self.js)
        self.assertIn('location.href = "/workspace?dialog=" + mode', self.js)
        self.assertIn('content.append(footer)', self.js)


if __name__ == "__main__":
    unittest.main()
