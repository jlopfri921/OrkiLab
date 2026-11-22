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

    def test_b10_2_explicit_model_check_is_integrated_and_bilingual(self):
        self.assertIn('id="b10-model-check"', self.benchmark)
        self.assertIn('id="b10-model-rows"', self.benchmark)
        self.assertIn('Comprobar variantes (solo lectura)', self.benchmark)
        self.assertIn('Check variants (read-only)', self.benchmark)
        self.assertIn('/api/workspace/benchmark/model-check?project_id=', self.benchmark)

    def test_b10_2_model_check_is_not_automatically_triggered(self):
        self.assertIn('addEventListener("click",async()=>{', self.benchmark)
        self.assertIn('if(seq!==b10CheckSeq||projectId!==$("project").value', self.benchmark)
        self.assertIn('No se comprueban los archivos ni se ejecuta el workflow', self.benchmark)
        self.assertIn('sin verificar archivos', self.benchmark)

    def test_b10_1_offline_comparison_gate_is_bilingual_and_visible(self):
        self.assertIn('id="b10-rows"', self.benchmark)
        self.assertIn('report.b10_comparison_preflight||{}', self.benchmark)
        self.assertIn('Preparación de comparación B10', self.benchmark)
        self.assertIn('B10 comparison preparation', self.benchmark)

    def test_b10_1_gates_do_not_claim_live_comfyui_preflight(self):
        self.assertIn('b10Gate_comfyui_idle_and_compatible', self.benchmark)
        self.assertIn('Revisión documental sin ejecutar ComfyUI.', self.benchmark)
        self.assertIn('b10Pending:"Pendiente de comprobar"', self.benchmark)

    def test_b9_10_closure_table_is_in_integrated_bilingual_ui(self):
        self.assertIn('id="b9-closure-rows"', self.benchmark)
        self.assertIn('report.b9_closure||{}', self.benchmark)
        self.assertIn('Estado de validación B9', self.benchmark)
        self.assertIn('B9 verification status', self.benchmark)
        self.assertIn('b9Check_hardware_and_cache_attestation', self.benchmark)

    def test_b9_10_does_not_claim_ranking_or_equal_conditions(self):
        self.assertIn('no demuestran igualdad de condiciones', self.benchmark)
        self.assertIn('Validación completa pendiente', self.benchmark)
        self.assertIn('Solo constancia documental', self.benchmark)

    def test_b9_9_local_history_table_is_bilingual_and_read_only(self):
        self.assertIn('id="saved-history-rows"', self.benchmark)
        self.assertIn('report.saved_history_consistency?.variants', self.benchmark)
        self.assertIn('Correspondencia con historial local', self.benchmark)
        self.assertIn('Local generation history consistency', self.benchmark)

    def test_b9_9_prompt_hash_evidence_label_does_not_claim_polarity(self):
        self.assertIn('savedPromptHashMatch:"Coincidencia de textos"', self.benchmark)
        self.assertIn('sin verificar polaridad', self.benchmark)
        self.assertIn('item.literal_prompt_evidence?.positive_digest_found_in_any_record', self.benchmark)

    def test_b9_9_no_remote_comfy_claim_or_raw_graph_in_ui(self):
        self.assertIn('Comprueba la coherencia de dos registros locales', self.benchmark)
        self.assertIn('Registros locales coherentes; contenido sin verificar', self.benchmark)
        self.assertIn('savedHistoryNotChecked', self.benchmark)

    def test_b9_8_recorded_execution_evidence_is_visible_in_zone(self):
        self.assertIn('data-i18n="executionEvidenceTitle"', self.benchmark)
        self.assertIn('id="execution-evidence-rows"', self.benchmark)
        self.assertIn('report.recorded_execution_evidence?.variants', self.benchmark)
        self.assertIn('Evidencias de ejecución registradas', self.benchmark)

    def test_b9_8_evidence_does_not_claim_models_or_prompts_verified(self):
        self.assertIn('Las huellas del grafo y los identificadores no acreditan', self.benchmark)
        self.assertIn('no_recorded_generation_lineage', self.benchmark)
        self.assertIn('workflow_mismatch', self.benchmark)
        self.assertIn('prompt_timing_identity_not_established', self.benchmark)

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
