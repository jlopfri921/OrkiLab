"""B9.1 aggregation tests, synthetic and without GPU/DB/files."""
import copy
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from benchmark_report_summary import summarize_benchmark_report


def fixture():
    return {
        "schema_version": 1,
        "run": {"id": "run-a", "state": "running"},
        "variants": [
            {"id": "v1", "run_id": "run-a", "label": "A"},
            {"id": "v2", "run_id": "run-a", "label": "B"},
        ],
        "observations": [
            {"id": "o1", "run_id": "run-a", "variant_id": "v1",
             "repetition": 0, "status": "completed",
             "duration_ms": 1200, "peak_vram_bytes": None},
            {"id": "o2", "run_id": "run-a", "variant_id": "v1",
             "repetition": 1, "status": "completed",
             "duration_ms": 1000, "peak_vram_bytes": None},
            {"id": "o3", "run_id": "run-a", "variant_id": "v2",
             "repetition": 0, "status": "failed",
             "duration_ms": None, "peak_vram_bytes": None},
        ],
    }


class BenchmarkReportSummaryTests(unittest.TestCase):
    def test_completed_measurements_not_ranked(self):
        report = fixture()
        original = copy.deepcopy(report)
        summary = summarize_benchmark_report(report)
        first, second = summary["variants"]
        self.assertEqual(first["duration_ms_median"], 1100)
        self.assertEqual(first["measured_duration_count"], 2)
        self.assertEqual(second["failed"], 1)
        self.assertEqual(second["measured_duration_count"], 0)
        self.assertIsNone(summary["best_variant"])
        self.assertIsNone(summary["ranking"])
        self.assertEqual(report, original)

    def test_absent_memory_stays_unknown(self):
        result = summarize_benchmark_report(fixture())["variants"][0]
        self.assertEqual(result["missing_per_job_peak_vram_count"], 2)
        self.assertIsNone(result["measured_vram_peak_bytes_max"])
        self.assertEqual(result["per_job_peak_vram_count"], 0)

    def test_partial_duration_is_not_fabricated(self):
        report = fixture()
        report["observations"][0]["duration_ms"] = None
        first = summarize_benchmark_report(report)["variants"][0]
        self.assertEqual(first["duration_ms_median"], 1000)
        self.assertEqual(first["missing_duration_count"], 1)

    def test_cancelled_or_failed_numbers_do_not_count_as_measurement(self):
        report = fixture()
        report["observations"][2]["duration_ms"] = 10
        result = summarize_benchmark_report(report)["variants"][1]
        self.assertEqual(result["failed"], 1)
        self.assertIsNone(result["duration_ms_median"])

    def test_explicit_per_job_measurement_kept_separate(self):
        report = fixture()
        report["observations"][0]["peak_vram_bytes"] = 100
        result = summarize_benchmark_report(report)["variants"][0]
        self.assertEqual(result["per_job_peak_vram_count"], 1)
        self.assertEqual(result["measured_vram_peak_bytes_max"], 100)
        self.assertEqual(result["missing_per_job_peak_vram_count"], 1)

    def test_invalid_cross_run_or_duplicate_observations_rejected(self):
        for change in ("cross", "duplicate", "bad_duration", "bad_peak"):
            report = fixture()
            if change == "cross":
                report["observations"][0]["run_id"] = "other"
            if change == "duplicate":
                report["observations"][1]["repetition"] = 0
            if change == "bad_duration":
                report["observations"][0]["duration_ms"] = True
            if change == "bad_peak":
                report["observations"][0]["peak_vram_bytes"] = -1
            with self.subTest(change=change), self.assertRaises(ValueError):
                summarize_benchmark_report(report)

    def test_empty_run_and_variant_are_valid(self):
        report = fixture()
        report["observations"] = []
        first = summarize_benchmark_report(report)["variants"][0]
        self.assertEqual(first["completed"], 0)
        self.assertIsNone(first["duration_ms_median"])

    def test_rejects_malformed_report(self):
        for report in (None, {}, {"schema_version": 2}, {"schema_version": 1,
                        "run": {"id": "x"}, "variants": "wrong",
                        "observations": []}):
            with self.assertRaises(ValueError):
                summarize_benchmark_report(report)


if __name__ == "__main__":
    unittest.main()
