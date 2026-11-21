"""Projects and curated LoRA search controls and i18n coverage."""
import json
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

class CatalogFiltersTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html=(ROOT/"GUI"/"workspace.html").read_text(encoding="utf-8")

    def test_projects_search_filters_and_sort(self):
        for marker in ('id="projects-search"','id="projects-category"','id="projects-engine"',
            'id="projects-sort"','id="projects-clear"','id="projects-filter-status"',
            'cachedProjectData','const matched=all.filter(',"matched.sort(",
            'projects(true).catch(e=>notice(e.message))'):
            with self.subTest(marker=marker):
                self.assertIn(marker,self.html)

    def test_lora_search_filters_and_sort(self):
        for marker in ('id="trained-loras-search"','id="trained-loras-designation"',
            'id="trained-loras-engine"','id="trained-loras-sort"','id="trained-loras-clear"',
            'trainedLoraCache','function renderTrainedLoras(models)','const selected=models.filter(',
            'if(sort==="score")','if(sort==="steps_asc")','if(sort==="steps_desc")',
            'loadTrainedLoras(true)'):
            with self.subTest(marker=marker):
                self.assertIn(marker,self.html)

    def test_translations_available_for_all_languages(self):
        keys=("Search projects","Training engine filter","Sort projects",
              "Search trained LoRAs","Model designation","Sort trained LoRAs","Clear filters")
        for lang in ("es","pt","fr","de","it","ja","ko"):
            locale=json.loads((ROOT/"GUI"/"locales"/(lang+".json")).read_text(encoding="utf-8"))
            for key in keys:
                with self.subTest(language=lang,key=key):
                    self.assertTrue(locale.get(key))

    def test_library_has_own_navigation(self):
        self.assertIn('data-home="trained-loras"',self.html)
        self.assertIn('href="#engines" class="back-link"',self.html)
        self.assertIn('href="#trained-loras" id="trained-loras-nav"',self.html)
