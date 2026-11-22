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

    def test_missing_view_preflight_before_reference_upload(self):
        source=(ROOT/"assets"/"orkilab"/"multiview-generate-view.js").read_text(encoding="utf-8")
        self.assertIn("function connectedImageInputs(p)",source)
        self.assertIn("function editablePromptFields(p)",source)
        self.assertIn("connectedImageInputs(inspected).length<ids.length",source)
        self.assertIn("editablePromptFields(inspected).length",source)
        stage=source.split("stage.onclick=async()=>{",1)[1].split("function makePrompt",1)[0]
        self.assertLess(stage.index('const inspected=await post(api,"/api/workspace/generation/prepare"'),
                        stage.index('const result=await post(api,u(originalProject,"/subjects/"+subjectId+"/reference-upload")'))
        self.assertLess(stage.index('const result=await post(api,u(originalProject,"/subjects/"+subjectId+"/reference-upload")'),
                        stage.index('const p=await post(api,"/api/workspace/generation/prepare"'))

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
