"""B8.2a GPU memory diagnostics: no hardware, queue, or DB operations."""
import sys
import unittest
from pathlib import Path
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from benchmark_gpu_memory_probe import COMMAND, parse_gpu_memory_csv, sample_devices


class GpuMemoryProbeTests(unittest.TestCase):
    def test_csv_parses_two_devices_without_attributing_job_memory(self):
        output = (
            "0, GPU-aaaa, NVIDIA RTX 3090, 24576, 10322, 14254\n"
            "1, GPU-bbbb, NVIDIA RTX 3060, 12288, 800, 11488\n"
        )
        calls = []

        def runner(command, **kwargs):
            calls.append((command, kwargs))
            return SimpleNamespace(returncode=0, stdout=output)

        result = sample_devices(runner=runner)
        self.assertTrue(result["ok"])
        self.assertEqual(len(result["devices"]), 2)
        self.assertEqual(result["devices"][0]["used_bytes"], 10322 * 1024 * 1024)
        self.assertEqual(result["devices"][1]["index"], 1)
        self.assertIsNone(result["peak_vram_bytes"])
        self.assertFalse(result["attributable_to_generation"])
        self.assertFalse(result["benchmark_database_modified"])
        self.assertEqual(calls[0][0], list(COMMAND))
        self.assertEqual(calls[0][1]["timeout"], 5)

    def test_rejects_invalid_or_duplicate_memory_entries(self):
        bad = (
            "", "0, GPU-a, NVIDIA, 24576, 30000, 0\n",
            "0, GPU-a, NVIDIA, 24576, 4, 24571\n0, GPU-b, NVIDIA, 24576, 8, 24568\n",
            "0, GPU-a, NVIDIA, 24576, N/A, 1\n",
            "0, GPU-a, NVIDIA, 24576, 12\n",
        )
        for raw in bad:
            with self.subTest(raw=raw):
                with self.assertRaises(ValueError):
                    parse_gpu_memory_csv(raw)

    def test_command_failure_returns_no_metric(self):
        def fail(command, **kwargs):
            return SimpleNamespace(returncode=1, stdout="", stderr="GPU unavailable")
        result = sample_devices(runner=fail)
        self.assertFalse(result["ok"])
        self.assertNotIn("devices", result)
        self.assertNotIn("peak_vram_bytes", result)

    def test_valid_csv_is_global_snapshot_not_per_job_peak(self):
        result = sample_devices(runner=lambda command, **kwargs: SimpleNamespace(
            returncode=0, stdout="0, GPU-a, NVIDIA, 24576, 12000, 12576"
        ))
        self.assertTrue(result["ok"])
        self.assertEqual(result["scope"], "device_global_snapshot")
        self.assertIn("other processes", result["limitations"])


if __name__ == "__main__":
    unittest.main()
