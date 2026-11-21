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
