"""B8.2h opt-in GPU monitor contract; no external jobs/GPU calls."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from benchmark_gpu_monitor_contract import (
    monitoring_receipt, validate_gpu_monitor_option,
)


class MonitorContractTests(unittest.TestCase):
    def test_absent_monitor_leaves_existing_submission_path_unchanged(self):
        self.assertIsNone(validate_gpu_monitor_option(None))

    def test_explicit_consent_and_bounds(self):
        item = validate_gpu_monitor_option({
            "confirm": True, "gpu_uuid": "GPU-test",
            "samples": 40, "interval": 0.3,
        })
        self.assertEqual(item, {"gpu_uuid": "GPU-test",
                                "samples_limit": 40, "interval_seconds": 0.3})

    def test_rejects_incomplete_unconsented_or_unbounded_monitor(self):
        invalid = [
            {}, {"confirm": False, "gpu_uuid": "GPU-test",
                 "samples": 5, "interval": 0.3},
            {"confirm": True, "gpu_uuid": "GPU-test",
             "samples": 1, "interval": 0.3},
            {"confirm": True, "gpu_uuid": "GPU-test",
             "samples": 5, "interval": float("nan")},
            {"confirm": True, "gpu_uuid": "bad",
             "samples": 5, "interval": 0.3},
            {"confirm": True, "gpu_uuid": "GPU-test",
             "samples": 5, "interval": 0.3, "other": True},
        ]
        for item in invalid:
            with self.subTest(item=item), self.assertRaises(ValueError):
                validate_gpu_monitor_option(item)

    def test_receipt_never_claims_peak_or_database_writes(self):
        for state in ("scheduled", "running", "completed", "partial", "failed"):
            receipt = monitoring_receipt(state)
            self.assertFalse(receipt["attributable_to_generation"])
            self.assertIsNone(receipt["peak_vram_bytes"])
            self.assertFalse(receipt["benchmark_database_modified"])

    def test_receipt_unknown_state_refused(self):
        with self.assertRaises(ValueError):
            monitoring_receipt("ready")


if __name__ == "__main__":
    unittest.main()
