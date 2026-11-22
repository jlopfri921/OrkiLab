"""JavaScript syntax smoke check for the inline Workspace app (not only external JS)."""
from html.parser import HTMLParser
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]

class InlineScripts(HTMLParser):
    def __init__(self):
        super().__init__()
        self.scripts=[]
        self.capture=False
    def handle_starttag(self,tag,attrs):
        if tag=="script":
            self.capture=not dict(attrs).get("src")
    def handle_data(self,data):
        if self.capture:
            self.scripts.append(data)
    def handle_endtag(self,tag):
        if tag=="script":
            self.capture=False

class WorkspaceJavaScriptSyntaxTests(unittest.TestCase):
    @unittest.skipUnless(shutil.which("node"),"Node.js not installed")
    def test_multiview_local_viewpoint_assistant_compiles_and_is_wired(self):
        path=ROOT/"assets"/"orkilab"/"multiview-viewpoint-ai.js"
        result=subprocess.run([shutil.which("node"),"--check",str(path)],
                              capture_output=True,text=True,timeout=15)
        self.assertEqual(result.returncode,0,result.stderr)
        html=(ROOT/"GUI"/"multiview_studio.html").read_text(encoding="utf-8")
        self.assertIn('src="/assets/orkilab/multiview-viewpoint-ai.js"',html)
        self.assertIn("OrkiViewpointAI.mount(",html)
        self.assertIn("capture.id,api,refresh,capture",html)

    def test_missing_view_copy_before_workflow_validation(self):
        source=(ROOT/"assets"/"orkilab"/"multiview-generate-view.js").read_text(encoding="utf-8")
        self.assertIn('stage.onclick=async()=>{',source)
        self.assertIn('prepareCopy.onclick=async()=>{',source)
        self.assertIn('transfer_mode:mode',source)
        copy=source.index('const result=await post(api,u(originalProject,"/subjects/"+subjectId+"/reference-upload")')
        prep=source.index('const p=await post(api,"/api/workspace/generation/prepare"')
        self.assertLess(copy,prep)
        self.assertIn('"/api/workspace/multiview/comfyui-input/browse"',source)
        self.assertIn('f.multiview_reference?.likely_compatible',source)

    @unittest.skipUnless(shutil.which("node"),"Node.js not installed")
    def test_missing_view_and_mode_help_scripts_compile(self):
        for name in ("multiview-generate-view.js","orkilab-mode-help.js"):
            with self.subTest(name=name):
                script=ROOT/"assets"/"orkilab"/name
                result=subprocess.run([shutil.which("node"),"--check",str(script)],
                                     capture_output=True,text=True,timeout=15)
                self.assertEqual(result.returncode,0,result.stderr)
        html=(ROOT/"GUI"/"multiview_studio.html").read_text(encoding="utf-8")
        self.assertIn('src="/assets/orkilab/multiview-generate-view.js"',html)
        self.assertIn("OrkiMultiviewGenerateViews.mount(",html)
        shell=(ROOT/"assets"/"orkilab"/"orkilab-shell.js").read_text(encoding="utf-8")
        self.assertIn('modeHelp.src="/assets/orkilab/orkilab-mode-help.js"',shell)
        self.assertIn('"/workspace/guide"',shell)

    def test_multiview_all_supported_locales_cover_visible_fields(self):
        import json
        import re
        page=(ROOT/"GUI"/"multiview_studio.html").read_text(encoding="utf-8")
        keys=set(re.findall(r'\bt\(\s*"([^"]+)"',page))
        keys.update(re.findall(r'\b(?:field|selector)\(\s*"([^"]+)"',page))
        keys.update(re.findall(
            r'\[\s*"(?:real_photo|video_frame|synthetic|unknown|manual|workflow|embedded_exif|estimated|unreviewed|approved|rejected|newest|oldest|name|azimuth|distance)"\s*,\s*"([^"]+)"',page))
        # Dynamic statuses (projectLabels) are translated inside their own module.
        keys-={"project","loading","found","none","archived","other","missing","error","remote","video_frame"}
        keys.update((
            "Organize multiple photographs of a subject by viewpoint, angle and distance. Real and synthetic sources are clearly distinguished. Your original files are never changed.",
            "Choose a project","Manage projects","Use an existing image project. Multiview metadata belongs to this project only.",
            "Subjects","Subject name","Create subject","Search subjects","Sort subjects",
            "Most photographs","Multiview Studio"))
        for lang in ("es","pt","fr","de","it","ja","ko"):
            with self.subTest(language=lang):
                translations=json.loads((ROOT/"GUI"/"locales"/(lang+".json")).read_text(encoding="utf-8"))
                missing=sorted(k for k in keys if not translations.get(k))
                self.assertEqual(missing,[],f"{lang}: untranslated Multiview UI labels: {missing}")
        self.assertIn('localize(capture.requested_direction)',page)
        rc=(ROOT/"assets"/"orkilab"/"multiview-rc1.js").read_text(encoding="utf-8")
        self.assertIn('status.textContent=t("limit30")',rc)

    def test_optional_multiview_ai_panels_support_all_eight_languages(self):
        languages=("es","en","pt","fr","de","it","ja","ko")
        for filename in ("multiview-viewpoint-ai.js","multiview-generate-view.js"):
            with self.subTest(module=filename):
                source=(ROOT/"assets"/"orkilab"/filename).read_text(encoding="utf-8")
                for locale in languages:
                    self.assertIn(" "+locale+":{",source)
                self.assertIn("I18N.lang",source)
                self.assertNotIn('I18N.lang==="es"?"es":"en"',source)
        generator=(ROOT/"assets"/"orkilab"/"multiview-generate-view.js").read_text(encoding="utf-8")
        self.assertIn("window.OrkiMultiviewGenerateViews={mount,translate:t}",generator)
        self.assertIn('status(t("max4"))',generator)
        recovery=(ROOT/"assets"/"orkilab"/"multiview-rc1.js").read_text(encoding="utf-8")
        self.assertIn('status.textContent=t("limit30")',recovery)
        for locale in languages:
            self.assertIn(locale+":{",recovery)
        page=(ROOT/"GUI"/"multiview_studio.html").read_text(encoding="utf-8")
        self.assertIn('translate("requestedLabel")',page)

    @unittest.skipUnless(shutil.which("node"),"Node.js not installed")
    def test_guide_eight_languages_and_menu_version_order(self):
        script=ROOT/"assets"/"orkilab"/"orkilab-guide-i18n.js"
        result=subprocess.run([shutil.which("node"),"--check",str(script)],
                              capture_output=True,text=True,timeout=15)
        self.assertEqual(result.returncode,0,result.stderr)
        source=script.read_text(encoding="utf-8")
        page=(ROOT/"GUI"/"orkilab_guide.html").read_text(encoding="utf-8")
        self.assertIn('src="/assets/orkilab/orkilab-guide-i18n.js"',page)
        self.assertNotIn('const lang=locale==="es"?"es":"en"',page)
        for lang in ("pt","fr","de","it","ja","ko"):
            self.assertIn(lang+":{",source)
        for section in ("hero","nav","flow","modules","multiview","modes","faq"):
            self.assertIn(section+":",source)
        self.assertIn('document.documentElement.lang=lang',source)
        shell=(ROOT/"assets"/"orkilab"/"orkilab-shell.js").read_text(encoding="utf-8")
        self.assertLess(shell.index('["guide", "/workspace/guide"'),
                        shell.index("const names ="))
        mode=(ROOT/"assets"/"orkilab"/"orkilab-mode-help.js").read_text(encoding="utf-8")
        self.assertIn('nav.insertBefore(a,version)',mode)
        self.assertIn('nav.append(indicator)',mode)

    def test_multiview_semi_automatic_input_upload_controls(self):
        source=(ROOT/"assets"/"orkilab"/"multiview-generate-view.js").read_text(encoding="utf-8")
        self.assertIn('t("copyPhotos")',source)
        self.assertIn('t("prepareCopied")',source)
        self.assertIn('inputPath.type="text"',source)
        self.assertIn('t("browse")',source)
        self.assertIn('transferMode.add(new Option(t("direct"),"folder"))',source)
        self.assertIn('mapMode.add(new Option(t("auto"),"auto"))',source)
        self.assertIn('mapMode.add(new Option(t("semi"),"semi"))',source)
        self.assertIn('mapMode.value==="auto"',source)
        self.assertIn('ComfyUI/input/',source)
        self.assertIn('transferTitle.hidden=false',source)
        self.assertIn('status(t("chooseNode"))',source)
        self.assertIn('if(!window.confirm(t("confirmCopy")',source)
        self.assertLess(source.index('stage.onclick=async()=>{'),source.index('prepareCopy.onclick=async()=>{'))
        for lang in ("es","en","pt","fr","de","it","ja","ko"):
            self.assertIn(' '+lang+':{',source)

    def test_multiview_official_workflows_are_in_creation_interface(self):
        source=(ROOT/"assets"/"orkilab"/"multiview-generate-view.js").read_text(encoding="utf-8")
        self.assertIn('officialPanel=elt("details")',source)
        self.assertIn('officialPanel.open=true',source)
        self.assertIn('officialSelect=elt("select")',source)
        self.assertIn('officialText("zip")',source)
        self.assertIn('officialText("import")',source)
        self.assertIn('"/api/workspace/multiview/official-workflows/download"',source)
        self.assertIn('"/api/workspace/multiview/official-workflows/install"',source)
        self.assertIn('"/api/workspace/multiview/official-workflows/checkpoints"',source)
        self.assertIn('if(upload.length!==1)',source)
        self.assertIn('checkpoints.value',source)
        self.assertIn('result.installed?"done":"already"',source)
        self.assertIn('https://github.com/jlopfri921/OrkiLab-LoRA-TrainerStudio/tree/main/workflows/multiview',source)
        for lang in ("es","en","pt","fr","de","it","ja","ko"):
            self.assertIn(lang+":{",source)

    def test_overview_help_explains_whole_app_in_all_eight_languages(self):
        html=(ROOT/"GUI"/"orkilab_guide.html").read_text(encoding="utf-8")
        js=(ROOT/"assets"/"orkilab"/"orkilab-guide-i18n.js").read_text(encoding="utf-8")
        for text in ('id="about"','href="#about"','OrkiLab: qué es, por qué existe',
                     "Su filosofía:", "La visión de conjunto", "Qwen-Image y FLUX/Klein",
                     "not released features"):
            self.assertIn(text,html)
        self.assertIn('const anchors=["about","flow","sections","multiview","modes","faq"]',js)
        self.assertIn("renderOverview(main)",js)
        self.assertIn("overviewContent[lang].nav",js)
        for lang in ("pt","fr","de","it","ja","ko"):
            self.assertIn('"'+lang+'":{"title":',js)
        self.assertIn('data.guideSection="about"',js)
        self.assertIn('document.documentElement.lang=lang',js)

    def test_multiview_readme_and_future_model_ui_are_explicit(self):
        readme=(ROOT/"workflows"/"multiview"/"README.md").read_text(encoding="utf-8")
        interface=(ROOT/"assets"/"orkilab"/"multiview-generate-view.js").read_text(encoding="utf-8")
        self.assertIn("## Qué aporta esta biblioteca a OrkiLab",readme)
        self.assertIn("Core Preserve",readme)
        self.assertIn("Qwen-Image 2.1 Edit",readme)
        self.assertIn("FLUX.3 Klein Image Edit",readme)
        self.assertIn("Pendiente de próximas revisiones",readme)
        self.assertIn("mejora futura no disponible en OrkiLab",interface)
        self.assertIn("future improvement not available in OrkiLab",interface)
        self.assertIn('officialText("upstream")',interface)
        self.assertIn('officialText("externalHint")',interface)

    def test_general_guide_page_exists(self):
        page=(ROOT/"GUI"/"orkilab_guide.html").read_text(encoding="utf-8")
        for section in ('id="flow"','id="sections"','id="multiview"',
                        'id="modes"','id="faq"'):
            self.assertIn(section,page)
        self.assertIn('data-lang="es"',page)
        self.assertIn('data-lang="en"',page)

    def test_guide_uses_unified_shell_css_and_navigation(self):
        page=(ROOT/"GUI"/"orkilab_guide.html").read_text(encoding="utf-8")
        styles=["orkilab-queue-theme.css","orkilab-shell.css","orkilab-app-shell.css"]
        locations=[page.index('href="/assets/orkilab/'+name+'"') for name in styles]
        self.assertEqual(locations,sorted(locations))
        self.assertIn('class="orki-queue-theme orki-app-frame orki-standalone-shell"',page)
        self.assertIn('class="studio-layout"',page)
        self.assertIn('class="studio-navigation"',page)
        self.assertIn('class="studio-content orki-guide-content"',page)
        self.assertIn('href="/workspace/guide" aria-current="page"',page)
        self.assertNotIn('.studio-navigation{display:none}',page)
        self.assertIn('src="/assets/orkilab/orkilab-shell.js"',page)
        shell=(ROOT/"assets"/"orkilab"/"orkilab-shell.js").read_text(encoding="utf-8")
        self.assertIn('page === "guide" ?',shell)
        self.assertIn('a[href="/workspace/guide"]',shell)

    def test_alpha_badges_removed_from_studio_menu(self):
        workspace=(ROOT/"GUI"/"workspace.html").read_text(encoding="utf-8")
        dataset=(ROOT/"GUI"/"dataset_studio.html").read_text(encoding="utf-8")
        for text in ("Dataset Studio <small>0.4 alpha</small>",
                     "Multiview Studio <small>0.5 alpha</small>"):
            self.assertNotIn(text,workspace)
        self.assertIn('href="/workspace/datasets" class="zone-entry">Dataset Studio</a>',workspace)
        self.assertIn('href="/workspace/multiview" class="zone-entry">Multiview Studio</a>',workspace)
        self.assertNotIn('Dataset Studio <small class="muted">0.4 alpha</small>',dataset)

    def test_generation_context_help_is_localized_to_spanish(self):
        workspace=(ROOT/"GUI"/"workspace.html").read_text(encoding="utf-8")
        self.assertIn('I18N.lang==="es"&&key==="generation"',workspace)
        self.assertIn('title="Laboratorio de generación"',workspace)
        self.assertIn('Prepararlo no inicia ninguna generación.',workspace)
        self.assertIn('document.addEventListener("orkilab:language-changed"',workspace)

    @unittest.skipUnless(shutil.which("node"),"Node.js not installed")
    def test_multiview_rc1_recovery_script_compiles_and_is_wired(self):
        script=ROOT/"assets"/"orkilab"/"multiview-rc1.js"
        result=subprocess.run([shutil.which("node"),"--check",str(script)],
                              capture_output=True,text=True,timeout=15)
        self.assertEqual(result.returncode,0,result.stderr)
        html=(ROOT/"GUI"/"multiview_studio.html").read_text(encoding="utf-8")
        self.assertIn('src="/assets/orkilab/multiview-rc1.js"',html)
        self.assertIn('id="mv-recovery"',html)
        self.assertIn("OrkiMultiviewRecovery.mount(",html)
        self.assertIn("0.5.0-rc.1",html)
        self.assertIn('old._assistant?.dispose()',html)

    @unittest.skipUnless(shutil.which("node"),"Node.js not installed")
    def test_multiview_beta2_export_compiles_and_is_wired(self):
        path=ROOT/"assets"/"orkilab"/"multiview-beta2.js"
        result=subprocess.run([shutil.which("node"),"--check",str(path)],
                              capture_output=True,text=True,timeout=15)
        self.assertEqual(result.returncode,0,result.stderr)
        html=(ROOT/"GUI"/"multiview_studio.html").read_text(encoding="utf-8")
        self.assertIn('src="/assets/orkilab/multiview-beta2.js"',html)
        self.assertIn("OrkiMultiviewExport.mount(",html)
        self.assertIn('id="mv-export"',html)
        self.assertIn("OrkiMultiviewExport.mount(",html)

    @unittest.skipUnless(shutil.which("node"),"Node.js not installed")
    def test_multiview_beta1_assist_compiles_and_is_wired(self):
        path=ROOT/"assets"/"orkilab"/"multiview-beta1.js"
        result=subprocess.run([shutil.which("node"),"--check",str(path)],
                              capture_output=True,text=True,timeout=15)
        self.assertEqual(result.returncode,0,result.stderr)
        html=(ROOT/"GUI"/"multiview_studio.html").read_text(encoding="utf-8")
        self.assertIn('src="/assets/orkilab/multiview-beta1.js"',html)
        self.assertIn("OrkiMultiviewAssist.mount(",html)
        self.assertIn("old._assistant?.dispose()",html)

    @unittest.skipUnless(shutil.which("node"),"Node.js not installed")
    def test_multiview_alpha2_external_javascript_compiles(self):
        path=ROOT/"assets"/"orkilab"/"multiview-alpha2.js"
        result=subprocess.run([shutil.which("node"),"--check",str(path)],
                              capture_output=True,text=True,timeout=15)
        self.assertEqual(result.returncode,0,result.stderr)
        html=(ROOT/"GUI"/"multiview_studio.html").read_text(encoding="utf-8")
        self.assertIn('src="/assets/orkilab/multiview-alpha2.js"',html)
        self.assertIn("OrkiMultiviewCoverage.mount(",html)
        self.assertIn('await coverage.refresh()',html)
        self.assertNotIn('await loadCaptures(subject.id,body)',html)

    @unittest.skipUnless(shutil.which("node"),"Node.js not installed")
    def test_multiview_inline_javascript_compiles(self):
        parser=InlineScripts()
        parser.feed((ROOT/"GUI"/"multiview_studio.html").read_text(encoding="utf-8"))
        self.assertTrue(parser.scripts,"Multiview Studio must have an interactive script")
        for index,source in enumerate(parser.scripts):
            with self.subTest(script=index):
                with tempfile.TemporaryDirectory() as directory:
                    path=Path(directory)/"multiview-inline.js"
                    path.write_text(source,encoding="utf-8")
                    result=subprocess.run([shutil.which("node"),"--check",str(path)],
                        capture_output=True,text=True,timeout=15)
                    self.assertEqual(result.returncode,0,result.stderr)

    @unittest.skipUnless(shutil.which("node"),"Node.js not installed")
    def test_inline_workspace_javascript_compiles(self):
        parser=InlineScripts()
        parser.feed((ROOT/"GUI"/"workspace.html").read_text(encoding="utf-8"))
        self.assertTrue(parser.scripts,"Workspace must contain inline JS")
        for index,source in enumerate(parser.scripts):
            with self.subTest(script=index):
                with tempfile.TemporaryDirectory() as directory:
                    path=Path(directory)/"workspace-inline.js"
                    path.write_text(source,encoding="utf-8")
                    result=subprocess.run([shutil.which("node"),"--check",str(path)],
                        capture_output=True,text=True,timeout=15)
                    self.assertEqual(result.returncode,0,result.stderr)
