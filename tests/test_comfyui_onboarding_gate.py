"""Connection-gated ComfyUI Zone has an accessible welcome page."""
import json
import unittest
from pathlib import Path
from html.parser import HTMLParser

ROOT=Path(__file__).resolve().parents[1]
HTML=(ROOT/"GUI"/"workspace.html").read_text(encoding="utf-8")

class MenuParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links=[]
        self.inside=False
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if tag=="nav" and a.get("id")=="comfy-navigation":
            self.inside=True
        if tag=="a" and self.inside:
            self.links.append(a)
    def handle_endtag(self,tag):
        if tag=="nav":
            self.inside=False

class ComfyWelcomeTests(unittest.TestCase):
    def test_onboarding_available_and_tools_gated(self):
        parsed=MenuParser();parsed.feed(HTML)
        hrefs={a["href"]:a for a in parsed.links}
        self.assertIn("#welcome",hrefs)
        self.assertIn("#comfyui",hrefs)
        for h in ("#models","#nodes","#workflows","#generation","#history","#compare"):
            with self.subTest(module=h):
                self.assertEqual(hrefs[h].get("data-requires-comfy"),"true")
                self.assertIn("hidden",hrefs[h])
        for h in ("#welcome","#comfyui"):
            self.assertNotIn("data-requires-comfy",hrefs[h])
        self.assertIn('data-module="welcome"',HTML)
        self.assertIn('id="comfy-welcome-status"',HTML)
        self.assertIn('id="comfy-welcome-recheck"',HTML)
        self.assertIn('href="#comfyui">Configure ComfyUI connection',HTML)

    def test_server_verified_navigation_and_deep_link_fallback(self):
        for snippet in ('let comfyConnectionVerified=false',
                        'async function loadComfy()',
                        'post("/api/workspace/comfyui/check",{})',
                        'updateComfyAccess(true)',
                        'updateComfyAccess(false)',
                        'const comfyModules=["welcome","comfyui"',
                        '!comfyConnectionVerified&&!["welcome","comfyui","benchmark"].includes(selected)',
                        'if(comfyConnectionReady)history.replaceState(null,"",location.pathname+"#welcome")',
                        'link.hidden=!verified'):
            with self.subTest(snippet=snippet):
                self.assertIn(snippet,HTML)

    def test_translations_all_languages(self):
        root=ROOT/"GUI"/"locales"
        for lang in ("es","pt","fr","de","it","ja","ko"):
            data=json.loads((root/f"{lang}.json").read_text(encoding="utf-8"))
            for key in ("Welcome","Discover ComfyUI in OrkiLab","Generate and experiment",
                        "ComfyUI is connected. All tools are available.",
                        "ComfyUI is not connected. Configure and test the connection to unlock the tools."):
                self.assertTrue(data.get(key), (lang,key))

if __name__=="__main__":
    unittest.main()
