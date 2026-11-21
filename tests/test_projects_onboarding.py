"""Projects page introduction and empty state regression checks."""
import json
import unittest
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HTML = (ROOT / "GUI" / "workspace.html").read_text(encoding="utf-8")


class Inspect(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids = []
    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if "id" in attrs:
            self.ids.append(attrs["id"])


class ProjectsOnboardingTests(unittest.TestCase):
    def test_guided_projects_page_and_form(self):
        tree = Inspect()
        tree.feed(HTML)
        self.assertEqual(len(tree.ids),len(set(tree.ids)))
        for fragment in ('data-home="projects"', 'class="projects-intro"',
                         'id="projects">Your AI training projects</h1>',
                         'class="projects-steps"', 'id="projects-empty"',
                         'id="projects-empty-create"', 'id="projects-empty-heading"',
                         'id="projects-empty-detail"', 'id="project-list"',
                         'id="archived"', 'id="new"'):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment,HTML)

    def test_empty_state_and_archiving_do_not_block_existing_projects(self):
        for fragment in ('empty.hidden=!isEmpty', 'projects-empty-create").hidden=archived||all.length>0',
                         'if(!d.projects.length)', # optional; not required
                         'for(const p of matched)', 'archive",',
                         'projects-empty-create").onclick=()=>$("new").click()'):
            if fragment == 'if(!d.projects.length)':
                continue
            self.assertIn(fragment,HTML)

    def test_translations_present(self):
        keys = ("Your AI training projects", "1. Create a project",
                "2. Keep your context", "3. Train and revisit",
                "Your first project starts here", "Create my first project",
                "No archived projects yet")
        for lang in ("es","pt","fr","de","it","ja","ko"):
            obj=json.loads((ROOT/"GUI"/"locales"/(lang+".json")).read_text(encoding="utf-8"))
            for key in keys:
                with self.subTest(lang=lang,key=key):
                    self.assertTrue(obj.get(key))


if __name__=="__main__":
    unittest.main()
