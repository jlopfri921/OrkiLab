"""Generation history remains readable as jobs accumulate."""
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
class CollapsedHistoryUiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.page=(ROOT/"GUI"/"workspace.html").read_text(encoding="utf-8")

    def test_each_history_entry_is_a_collapsed_details_card(self):
        for token in ('const card=el("details",undefined,"panel history-job history-entry")',
                      'const heading=el("summary",undefined,"history-entry-summary")',
                      'card.open=expandedHistoryIds.has(job.id)',
                      'card.addEventListener("toggle"',
                      'expandedHistoryIds.add(job.id)',
                      'expandedHistoryIds.delete(job.id)'):
            self.assertIn(token,self.page)

    def test_media_and_graph_loaded_only_on_open(self):
        start=self.page.index("async function loadGenerationHistory(){")
        end=self.page.index('$("history-refresh").onclick=loadGenerationHistory;',start)
        source=self.page[start:end]
        self.assertIn("function renderExpanded()",source)
        self.assertIn("if(rendered)return",source)
        self.assertIn("renderGenerationMedia(media,job.id,job.outputs)",source)
        self.assertIn("if(card.open)renderExpanded()",source)
        self.assertIn('if(details.open)try{pre.textContent=JSON.stringify(await fetchGraph()',source)
        self.assertIn('historyOffset+=100',self.page)

    def test_can_expand_using_keyboard_accessible_native_details(self):
        self.assertIn(".history-entry-summary:focus-visible",self.page)
        self.assertNotIn('const card=el("article",undefined,"panel history-job")',self.page)

if __name__=="__main__":
    unittest.main()
