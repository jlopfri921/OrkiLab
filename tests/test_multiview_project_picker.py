"""Regression guards for the missing Multiview project selector incident."""
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]


class MultiviewProjectPickerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.studio=(ROOT/"GUI"/"multiview_studio.html").read_text(encoding="utf-8")
        cls.workspace=(ROOT/"GUI"/"workspace.html").read_text(encoding="utf-8")
        cls.backend=(ROOT/"scripts"/"workspace_routes.py").read_text(encoding="utf-8")

    def test_select_only_active_image_projects_from_canonical_registry(self):
        self.assertIn('api("/api/workspace/projects?archived=0")',self.studio)
        self.assertIn('all.filter(p=>p.category==="image")',self.studio)
        self.assertIn('api("/api/workspace/projects?archived=1")',self.studio)
        self.assertIn('if(available)select.value=previous;',self.studio)
        self.assertIn('else if(images.length===1)select.value=images[0].id;',self.studio)
        self.assertIn("await loadSubjects();",self.studio)
        self.assertIn('feedback.textContent=projectText("error")',self.studio)

    def test_empty_state_archived_and_remote_errors_visible(self):
        self.assertIn('id="mv-project-feedback"',self.studio)
        self.assertIn('role="status" aria-live="polite"',self.studio)
        for token in ('projectText("none")','projectText("archived")',
                      'projectText("other")','projectText("missing")',
                      'projectText("remote")'):
            with self.subTest(token=token):
                self.assertIn(token,self.studio)

    def test_workspace_links_to_exact_saved_project_id(self):
        self.assertIn('multiviewLink.href="/workspace/multiview?project="+encodeURIComponent(p.id)',self.workspace)
        self.assertIn('actions.append(multiviewLink)',self.workspace)
        self.assertIn('href="/workspace/multiview"',self.workspace)
        self.assertIn('request.args.get("archived") == "1"',self.backend)

if __name__=="__main__":
    unittest.main()
