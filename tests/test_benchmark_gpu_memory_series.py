"""Mocked B8.2b series tests; no real GPU is queried."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from benchmark_gpu_memory_series import capture, summarize_samples


def sample(used, *, uuid="GPU-test", total=24_000):
    return {"ok": True, "devices": [
        {"uuid": uuid, "used_bytes": used, "total_bytes": total},
    ]}


class MemorySeriesTests(unittest.TestCase):
    def test_bounded_series_reports_global_max_without_job_attribution(self):
        values = iter((sample(6000), sample(7000), sample(6500)))
        stamps = iter((10., 10.5, 11.))
        sleeps = []
        result = capture(target_uuid="GPU-test", sample_count=3,
                         interval_seconds=0.5, sampler=lambda: next(values),
                         clock=lambda: next(stamps), sleeper=sleeps.append)
        self.assertEqual(result["sample_count"], 3)
        self.assertEqual(result["max_observed_used_bytes"], 7000)
        self.assertEqual(result["max_observed_increase_over_baseline_bytes"], 1000)
        self.assertEqual(result["duration_seconds_observed"], 1.0)
        self.assertEqual(sleeps, [0.5, 0.5])
        self.assertIsNone(result["peak_vram_bytes"])
        self.assertFalse(result["attributable_to_generation"])

    def test_target_gpu_isolation_and_missing_uuid(self):
        data = [dict(sample(5000), monotonic_seconds=0.),
                dict(sample(5500, uuid="GPU-other"), monotonic_seconds=1.)]
        with self.assertRaises(ValueError):
            summarize_samples(data, target_uuid="GPU-test")

    def test_failed_measurement_discarded(self):
        calls = iter((sample(1000), {"ok": False, "reason": "not available"}))
        with self.assertRaises(ValueError):
            capture(target_uuid="GPU-test", sample_count=2, interval_seconds=0.5,
                    sampler=lambda: next(calls), clock=lambda: 1.0,
                    sleeper=lambda _: None)

    def test_reject_invalid_intervals_samples_and_device_memory(self):
        for n, interval in ((1, 0.5), (121, 0.5), (2, 0.1), (2, 6.0)):
            with self.subTest(n=n, interval=interval):
                with self.assertRaises(ValueError):
                    capture(target_uuid="GPU-test", sample_count=n,
                            interval_seconds=interval, sampler=lambda: sample(100),
                            sleeper=lambda _: None)
        with self.assertRaises(ValueError):
            summarize_samples([dict(sample(25000), monotonic_seconds=0.)],
                              target_uuid="GPU-test")

    def test_reject_reversed_time_and_changing_capacity(self):
        for sequence in (
            [dict(sample(5000), monotonic_seconds=2.),
             dict(sample(7000), monotonic_seconds=1.)],
            [dict(sample(5000), monotonic_seconds=1.),
             dict(sample(7000, total=48_000), monotonic_seconds=2.)],
        ):
            with self.assertRaises(ValueError):
                summarize_samples(sequence, target_uuid="GPU-test")


if __name__ == "__main__":
    unittest.main()
