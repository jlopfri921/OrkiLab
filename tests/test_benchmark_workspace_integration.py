"""Regression checks for the Benchmark Studio navigation/design/i18n integration.

Static, side-effect-free assertions for the shipped UI, no browser or GPU.
"""
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class BenchmarkWorkspaceIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.workspace = (ROOT / "GUI" / "workspace.html").read_text(encoding="utf-8")
        cls.benchmark = (ROOT / "GUI" / "benchmark_reports.html").read_text(encoding="utf-8")
        cls.routes = (ROOT / "scripts" / "workspace_routes.py").read_text(encoding="utf-8")

    def test_benchmark_is_a_comfy_zone_navigation_module(self):
        self.assertIn('href="#benchmark"', self.workspace)
        self.assertIn('data-module="benchmark"', self.workspace)
        self.assertIn('"compare","benchmark"', self.workspace)
        self.assertIn('"welcome","comfyui","benchmark"', self.workspace)

    def test_embedded_frame_uses_shell_and_no_duplicate_header(self):
        self.assertIn('id="benchmark-frame"', self.workspace)
        self.assertIn('data-src="/workspace/benchmark?embed=1"', self.workspace)
        self.assertIn('body.embedded header{display:none}', self.benchmark)
        self.assertIn('--accent:#3cdbd0', self.benchmark)
        self.assertIn('orkilab-benchmark-height', self.workspace)
        self.assertIn('orkilab-benchmark-language', self.benchmark)

    def test_direct_benchmark_url_redirects_to_comfy_zone(self):
        self.assertIn('request.args.get("embed") != "1"', self.routes)
        self.assertIn('redirect("/workspace/comfyui#benchmark"', self.routes)

    def test_workspace_navigation_regex_must_be_valid_js(self):
        # Prior regression: /\\\\/$/ was parsed as a closed regex + bad flags,
        # preventing all Workspace JavaScript, including language controls.
        self.assertNotIn('location.pathname.replace(/\\\\/$/', self.workspace)
        self.assertIn('location.pathname.replace(/\\/$/', self.workspace)

    def test_confirmed_lost_accent_run_name_is_repaired_only_on_display(self):
        # The original ? cannot be reconstructed generically: only a known
        # exact legacy phrase is corrected; database values stay untouched.
        self.assertIn('vinculaci\\?n autom\\?tica/gi', self.benchmark)
        self.assertIn('"Vinculación automática"', self.benchmark)
        self.assertIn('const corrected=text.replace(', self.benchmark)

    def test_b9_6_inventory_controls_select_real_references(self):
        self.assertIn('id="draft-workflow-pick"', self.benchmark)
        self.assertIn('id="draft-gpu-pick"', self.benchmark)
        self.assertIn('/api/workspace/benchmark/draft-options?project_id=', self.benchmark)
        self.assertIn('if(value)$("draft-workflow").value=value;', self.benchmark)
        self.assertIn('if(value)$("draft-gpu").value=value;', self.benchmark)

    def test_b9_6_missing_inventory_does_not_invent_device_or_workflow(self):
        self.assertIn('No se ha detectado ninguna GPU NVIDIA.', self.benchmark)
        self.assertIn('No hay workflows importados.', self.benchmark)
        self.assertIn('No UUID will be invented.', self.benchmark)
        self.assertIn('if(seq!==optionsSeq||projectId!==$("project").value)return;', self.benchmark)

    def test_b9_7_local_hashing_uses_exact_utf8_and_browser_subtle(self):
        self.assertIn('new TextEncoder().encode(source)', self.benchmark)
        self.assertIn('globalThis.crypto.subtle.digest("SHA-256",bytes)', self.benchmark)
        self.assertIn('function hexDigest(bytes)', self.benchmark)
        self.assertNotIn('source.trim()', self.benchmark)
        self.assertNotIn('source.normalize(', self.benchmark)

    def test_b9_7_file_hash_is_bounded_and_requires_explicit_click(self):
        self.assertIn('id="draft-input-file" type="file"', self.benchmark)
        self.assertIn('const HASH_FILE_LIMIT=20*1024*1024;', self.benchmark)
        self.assertIn('if(file.size>HASH_FILE_LIMIT)', self.benchmark)
        self.assertIn('const bytes=await file.arrayBuffer();', self.benchmark)
        self.assertIn('addEventListener("click",hashSelectedFile)', self.benchmark)

    def test_b9_7_source_edit_invalidates_digest_and_confirmation(self):
        self.assertIn('hashGeneration[kind]++;', self.benchmark)
        self.assertIn('if(generation!==hashGeneration[kind])return;', self.benchmark)
        self.assertIn('if(generation!==hashGeneration.input)return;', self.benchmark)
        self.assertIn('$("draft-confirm").checked=false;', self.benchmark)
        self.assertIn('$("draft-"+kind).value="";', self.benchmark)

    def test_b9_7_bilingual_local_only_data_disclosure(self):
        self.assertIn('solo sus huellas se incorporan al borrador', self.benchmark)
        self.assertIn('only their hashes are included in the draft', self.benchmark)
        self.assertIn('Los textos y el archivo se procesan exclusivamente en este navegador', self.benchmark)
        self.assertIn('Este navegador no admite SHA-256 local mediante Web Crypto', self.benchmark)

    def test_run_picker_repairs_only_displayed_legacy_encoding(self):
        self.assertIn('function readableName(value)', self.benchmark)
        self.assertIn('new TextDecoder("utf-8",{fatal:true})', self.benchmark)
        self.assertIn('option(readableName(run.name)+" · "+stateName(run.state),run.id)', self.benchmark)
        self.assertIn('option(readableName(p.name),p.id)', self.benchmark)
        self.assertIn('textContent=readableName(report.name)', self.benchmark)

    def test_spanish_run_placeholder_is_correctly_encoded(self):
        self.assertIn('chooseRun:"Selecciona una ejecución"', self.benchmark)
        self.assertIn('<meta charset="utf-8">', self.benchmark)
        self.assertNotIn('Selecciona una ejecuciÃ', self.benchmark)

    def test_spanish_accents_and_readable_diagnostics(self):
        self.assertIn('<meta charset="utf-8">', self.benchmark)
        for word in ("Comparabilidad", "Ejecución", "Política", "Resolución",
                     "No se ha acreditado", "generación", "caché", "semillas"):
            with self.subTest(word=word):
                self.assertIn(word, self.benchmark)
        self.assertIn('function reasons(values)', self.benchmark)
        self.assertIn('reasonText[lang][code]', self.benchmark)


if __name__ == "__main__":
    unittest.main()
