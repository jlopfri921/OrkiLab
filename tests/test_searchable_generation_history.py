"""Generation history filtering works before pagination, with safe ordering."""
import sqlite3
from contextlib import closing
import sys
import tempfile
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from generation_history import GenerationHistory

class SearchableGenerationHistoryTests(unittest.TestCase):
    def setUp(self):
        temp=tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.history=GenerationHistory(temp.name)
        with closing(self.history.connect()) as con, con:
            for i in range(145):
                name="Flux3 Test" if i%10==0 else ("Alpha" if i%2 else "Beta")
                state="completed" if i%3 else "error"
                con.execute("INSERT INTO generations VALUES (?,?,?,?,?,?,?,?,?,?)",
                    (f"id-{i:03d}","http://127.0.0.1:8188",f"prompt-{i}","workflow-1",name,"{}",float(i+1),float(i+1),state,"[]"))

    def test_search_matches_entire_database_before_pagination(self):
        d=self.history.search(limit=5,query="Flux3")
        self.assertEqual(d["total"],15)
        self.assertEqual(len(d["jobs"]),5)
        self.assertTrue(all(x["name"]=="Flux3 Test" for x in d["jobs"]))

    def test_status_filter_and_sort(self):
        d=self.history.search(state="error",sort="oldest")
        self.assertEqual(d["total"],49)
        self.assertEqual(d["jobs"][0]["id"],"id-000")
        d=self.history.search(sort="name_asc",limit=10)
        self.assertEqual(d["jobs"][0]["name"],"Alpha")

    def test_paginated_results_and_total(self):
        a=self.history.search(limit=100)
        b=self.history.search(limit=100,offset=100)
        self.assertEqual(a["total"],145)
        self.assertEqual(len(a["jobs"]),100)
        self.assertEqual(len(b["jobs"]),45)
        self.assertFalse(set(x["id"] for x in a["jobs"]) & set(x["id"] for x in b["jobs"]))

    def test_rejects_arbitrary_sql_sort(self):
        with self.assertRaises(ValueError):
            self.history.search(sort="DROP TABLE generations")
        with self.assertRaises(ValueError):
            self.history.search(state="random")

    def test_wildcards_treated_as_literal(self):
        self.assertEqual(self.history.search(query="%")["total"],0)
        self.assertEqual(self.history.search(query="_")["total"],0)
