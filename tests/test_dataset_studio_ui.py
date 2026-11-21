"""Dataset Studio UI integration invariants (no Flask, GPU or browser required)."""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


class DatasetStudioUiChecks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html = (ROOT / "GUI" / "dataset_studio.html").read_text(encoding="utf-8")
        cls.workspace = (ROOT / "GUI" / "workspace.html").read_text(encoding="utf-8")
        cls.routes = (ROOT / "scripts" / "workspace_routes.py").read_text(encoding="utf-8")

    def test_workspace_has_dataset_entry_and_backend_route(self):
        self.assertIn('href="/workspace/datasets"', self.workspace)
        self.assertIn('@app.get("/workspace/datasets")', self.routes)
        self.assertIn('dataset_studio.register(app, base)', self.routes)

    def test_common_navigation_shell_on_queue_and_datasets(self):
        queue = (ROOT / "GUI" / "queue.html").read_text(encoding="utf-8")
        shell_css = (ROOT / "assets" / "orkilab" / "orkilab-shell.css").read_text(encoding="utf-8")
        shell_js = (ROOT / "assets" / "orkilab" / "orkilab-shell.js").read_text(encoding="utf-8")
        for html in (self.html, queue):
            with self.subTest(page=html[:60]):
                self.assertIn('/assets/orkilab/orkilab-shell.css', html)
                self.assertIn('/assets/orkilab/orkilab-shell.js', html)
        self.assertIn('orki-shell-header', shell_css)
        self.assertIn('orki-shell-footer', shell_css)
        self.assertIn('aria-current', shell_js)
        self.assertIn('"/workspace/datasets"', shell_js)
        self.assertIn('"/queue"', shell_js)
        self.assertIn('orkilab:language-changed', shell_js)
        self.assertIn('id="nav-datasets"', self.html)

    def test_standalone_header_matches_workspace_context_pattern(self):
        shell = (ROOT / "assets" / "orkilab" / "orkilab-shell.js").read_text(encoding="utf-8")
        css = (ROOT / "assets" / "orkilab" / "orkilab-shell.css").read_text(encoding="utf-8")
        for token in ('orki-shell-language', 'orki-shell-version',
                      'orki-header-kofi', '/api/i18n',
                      '/api/workspace/overview', 'orki-shell-workspace-context',
                      'orki-shell-context-title', 'orki-shell-context-toggle',
                      'orki-shell-context-description', 'aria-expanded',
                      'aria-controls', 'aria-hidden', 'What can I do here?',
                      '¿Qué puedo hacer aquí?', 'Job queue', 'Dataset Studio'):
            with self.subTest(token=token):
                self.assertIn(token, shell)
        self.assertIn('.orki-shell-workspace-context', css)
        self.assertIn('#orki-shell-version', css)
        self.assertIn('.orki-shell-header', css)
        self.assertIn('document.body.insertBefore(head, layout)', shell)
        self.assertIn('content.prepend(context)', shell)
        self.assertIn('description.hidden = !opened', shell)

    def test_queue_and_dataset_menu_match_home_order_and_controls(self):
        from html.parser import HTMLParser

        class HomeMenu(HTMLParser):
            def __init__(self):
                super().__init__()
                self.collecting = False
                self.order = []

            def handle_starttag(self, tag, attrs):
                attrs = dict(attrs)
                if tag == "nav" and attrs.get("id") == "home-navigation":
                    self.collecting = True
                elif self.collecting and tag in ("a", "button"):
                    self.order.append(attrs.get("id") or attrs.get("href"))

            def handle_endtag(self, tag):
                if tag == "nav" and self.collecting:
                    self.collecting = False

        parser = HomeMenu()
        parser.feed(self.workspace)
        expected = [
            "#overview", "#projects", "#engines", "trained-loras-nav", "#gpu-manager",
            "settings-open", "shutdown-open", "/queue",
            "/workspace/comfyui", "/workspace/datasets"
        ]
        self.assertEqual(parser.order, expected)
        js = (ROOT / "assets" / "orkilab" / "orkilab-shell.js").read_text(encoding="utf-8")
        keys = ("overview", "projects", "engines", "gpu", "settings", "shutdown", "queue", "comfy", "datasets")
        fallback = [line.strip().split('"')[1] for line in js.splitlines()
                    if line.strip().startswith('["') and line.strip().split('"')[1] in keys]
        self.assertEqual(fallback, [
            "overview", "projects", "engines", "gpu", "settings",
            "shutdown", "queue", "comfy", "datasets"
        ])
        for contract in ('source.querySelector("#home-navigation")',
                         'canonicalNav.cloneNode(true)',
                         'nav.replaceWith(canonical)',
                         'location.href = "/workspace?dialog=" + mode',
                         'I18N.apply(canonical)'):
            self.assertIn(contract, js)

    def test_job_queue_visual_theme_is_shared(self):
        queue_theme = (ROOT / "assets" / "orkilab" / "orkilab-queue-theme.css").read_text(encoding="utf-8")
        for path in ("workspace.html", "dataset_studio.html"):
            html = (ROOT / "GUI" / path).read_text(encoding="utf-8")
            self.assertIn('href="/assets/orkilab/orkilab-queue-theme.css"', html)
            self.assertIn('orki-queue-theme', html)
        for token in ("--orki-queue-panel", "--orki-queue-border", "--orki-queue-grad",
                      "body.orki-queue-theme .panel", "body.orki-queue-theme .workspace-context"):
            self.assertIn(token, queue_theme)

    def test_settings_dialog_has_accessible_top_close(self):
        self.assertIn('id="settings-close-top"', self.workspace)
        self.assertIn('aria-label="Close settings"', self.workspace)
        self.assertIn('settings-dialog-head', self.workspace)
        self.assertIn('$("settings-close-top").onclick=()=>$("settings-dialog").close()', self.workspace)

    def test_compare_dialog_has_pairs_zoom_and_keyboard_close(self):
        self.assertIn('id="comparison"', self.html)
        self.assertIn('id="compare-left"', self.html)
        self.assertIn('id="compare-right"', self.html)
        self.assertIn('id="compare-zoom"', self.html)
        self.assertIn('id="compare-pair"', self.html)
        self.assertIn('dialog class="comparison-dialog"', self.html)
        self.assertIn('comparisonText={', self.html)
        self.assertIn('openComparison(item.id)', self.html)
        self.assertIn('showModal()', self.html)
        self.assertIn('removeAttribute("src")', self.html)

    def test_caption_sidecar_export_is_preflighted_and_explicit(self):
        for token in ('id="export-sidecars"', 'id="sidecar-export-dialog"',
                      'id="sidecar-export-confirm"', 'id="sidecar-export-files"',
                      'id="sidecar-export-download"', 'const sidecarExportText={',
                      'mode:"preview"', 'mode:"download"',
                      'confirm:true', 'URL.createObjectURL',
                      'URL.revokeObjectURL', 'exportIds=[...selected]',
                      'result.skipped_empty', 'exportReady=result.exportable>0'):
            with self.subTest(token=token):
                self.assertIn(token, self.html)
        for locale in ("en", "es", "pt", "fr", "de", "it", "ja", "ko"):
            self.assertIn(locale + ":[", self.html)
        backend = (ROOT / "scripts" / "dataset_captions.py").read_text(encoding="utf-8")
        self.assertIn('as_attachment=True', backend)
        self.assertIn('zipfile.ZipFile(output', backend)
        self.assertIn('body.get("confirm") is not True', backend)
        self.assertIn('if not local() or not valid_origin()', backend)

    def test_ollama_discovery_and_cancellation_are_available_in_caption_editor(self):
        for token in ('id="caption-ai-select"', 'id="caption-ai-refresh"',
                      'id="caption-ai-cancel"', 'id="caption-ai-discovery-status"',
                      'const visionExtraText={', 'refreshVisionModels();',
                      '"/api/workspace/ollama/vision-models"',
                      'function cancelVision(){', 'signal:controller.signal',
                      'request_id:requestId', 'suggest/cancel',
                      'visionController?.abort()', 'cancelVision();stopVisionClock();visionControls(false);++visionDiscovery'):
            with self.subTest(token=token):
                self.assertIn(token, self.html)
        backend = (ROOT / "scripts" / "dataset_caption_vision.py").read_text(encoding="utf-8")
        for token in ('def local_vision_models()', '"/api/tags"', '"/api/show"',
                      '"vision" in capabilities', 'def cancel_caption(',
                      'stream_caption(', 'socket.SHUT_RDWR',
                      'busy.acquire(blocking=False)', 'NoRedirects()'):
            with self.subTest(token=token):
                self.assertIn(token, backend)

    def test_opt_in_local_ollama_caption_has_review_and_separate_save(self):
        for token in ('id="caption-ai-model"', 'id="caption-ai-generate"',
                      'id="caption-ai-result"', 'id="caption-ai-apply"',
                      'readonly rows="4"', 'const localVisionText={',
                      'const visionTr=localVisionText[lang]',
                      'confirm:true', '/caption/suggest',
                      '$("caption-ai-apply").disabled=false',
                      '$("caption-text").value=$("caption-ai-result").value',
                      '$("caption-text").focus()'):
            with self.subTest(token=token):
                self.assertIn(token, self.html)
        backend = (ROOT / "scripts" / "dataset_caption_vision.py").read_text(encoding="utf-8")
        for token in ('http://127.0.0.1:11434/api/generate', 'keep_alive',
                      'NoRedirects', 'MAX_IMAGE_BYTES', 'MAX_PROMPT',
                      'saved=False', 'timeout=120', 'busy.acquire(blocking=False)'):
            with self.subTest(token=token):
                self.assertIn(token, backend)
        route = (ROOT / "scripts" / "dataset_studio.py").read_text(encoding="utf-8")
        self.assertIn("dataset_caption_vision.register(app, db, project_exists, local, valid_origin)", route)

    def test_caption_studio_modal_is_versioned_and_localized(self):
        for token in ('id="caption-dialog"', 'id="caption-close"',
                      'id="caption-text"', 'maxlength="2000"',
                      'id="caption-save"', 'id="caption-clear"',
                      'id="caption-history"', 'id="caption-restore"',
                      'captionVersions()', 'expected_revision:captionRevision',
                      'const capTr=captionsText[lang]', 'function openCaption(item)',
                      'openCaption(item)', 'captionActive=null',
                      'removeAttribute("src")'):
            with self.subTest(token=token):
                self.assertIn(token, self.html)
        backend = (ROOT / "scripts" / "dataset_captions.py").read_text(encoding="utf-8")
        routes = (ROOT / "scripts" / "dataset_studio.py").read_text(encoding="utf-8")
        self.assertIn("dataset_captions.register(app, db, project_exists, local, valid_origin)", routes)
        self.assertIn('MAX_CAPTION_CHARS = 2000', backend)
        self.assertIn('MAX_HISTORY = 25', backend)
        self.assertIn('return jsonify(error="Caption changed in another tab", current=current), 409', backend)

    def test_selection_filters_and_localized_ui_present(self):
        for selector in ("project", "folder", "search", "review-filter", "sort",
                         "select-all", "select-none", "approve", "reject", "reset", "remove"):
            with self.subTest(selector=selector):
                self.assertIn('id="' + selector + '"', self.html)
        for locale in ("en", "es", "pt", "fr", "de", "it", "ja", "ko"):
            self.assertIn(chr(10) + locale + ":[", self.html)
        self.assertIn('id="quality-filter"', self.html)
        self.assertIn('quality:$("quality-filter").value', self.html)
        self.assertIn('item.near_duplicate', self.html)
        self.assertIn('item.possible_blur', self.html)
        self.assertIn('qualityTexts={', self.html)
        self.assertIn('I18N.lang', self.html)
        self.assertIn('batch("remove"', self.html)
        self.assertIn('batch("review"', self.html)
        self.assertIn('selected=new Set()', self.html)
        self.assertNotIn('innerHTML=', self.html)
        self.assertIn('textContent=item.name', self.html)


if __name__ == "__main__":
    unittest.main()
