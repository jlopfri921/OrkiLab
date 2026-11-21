"""Trained-LoRA library cards are compact, rated and display explicit reference images."""
import json
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

class TrainedLoraCardUiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html=(ROOT/"GUI"/"workspace.html").read_text(encoding="utf-8")
        cls.backend=(ROOT/"scripts"/"checkpoint_reviews.py").read_text(encoding="utf-8")

    def test_card_collapses_and_shows_stars_in_summary(self):
        source=self.html[self.html.index('function renderTrainedLoras(models)'):self.html.index('async function loadTrainedLoras(',self.html.index('function renderTrainedLoras(models)'))]
        for marker in ('const card=el("details",undefined,"panel trained-lora-card")',
                       'const summary=el("summary",undefined,"trained-lora-summary")',
                       '"★".repeat(m.rating)+"☆".repeat(5-m.rating)',
                       'summary.append(title,small,stars)',
                       'card.open=expandedTrainedLoraIds.has(key)',
                       'card.addEventListener("toggle"'):
            with self.subTest(marker=marker):
                self.assertIn(marker,source)

    def test_image_is_loaded_only_after_expanding(self):
        source=self.html[self.html.index('function renderTrainedLoras(models)'):self.html.index('async function loadTrainedLoras(',self.html.index('function renderTrainedLoras(models)'))]
        for marker in ('function renderExpanded(){','if(rendered)return','if(m.reference_url)',
                       'image.loading="lazy"', 'input.accept="image/png,image/jpeg,image/webp"',
                       'image_base64:btoa(binary)', 'if(card.open)renderExpanded()'):
            with self.subTest(marker=marker):
                self.assertIn(marker,source)
        self.assertIn('def set_reference_image(',self.backend)
        self.assertIn('def read_trained_lora_reference(',self.backend)

    def test_reference_image_translations(self):
        for locale in ("es","pt","fr","de","it","ja","ko"):
            data=json.loads((ROOT/"GUI"/"locales"/(locale+".json")).read_text(encoding="utf-8"))
            for label in ("Reference image","No reference image uploaded yet.","Save reference image","Unrated"):
                with self.subTest(locale=locale,label=label):
                    self.assertTrue(data.get(label))

if __name__=="__main__":
    unittest.main()
