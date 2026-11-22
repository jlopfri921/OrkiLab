"""B8.2c process inventory tests: pure mocks, no NVIDIA hardware."""
import sys
import unittest
from pathlib import Path
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from benchmark_gpu_process_probe import COMMAND, discover, parse_compute_processes


class GpuProcessProbeTests(unittest.TestCase):
    def test_two_processes_and_wddm_missing_memory_not_zero(self):
        csv_data = (
            "1234, C:\\Python\\python.exe, GPU-a, N/A\n"
            "4321, comfy.exe, GPU-a, 8192\n"
        )
        calls = []

        def runner(command, **kwargs):
            calls.append((command, kwargs))
            return SimpleNamespace(returncode=0, stdout=csv_data)

        result = discover(runner=runner)
        self.assertTrue(result["ok"])
        self.assertEqual(result["process_count"], 2)
        self.assertIsNone(result["processes"][0]["used_gpu_memory_bytes"])
        self.assertEqual(result["processes"][1]["used_gpu_memory_bytes"], 8192 * 1024 * 1024)
        self.assertFalse(result["memory_values_available_for_all_reported_processes"])
        self.assertFalse(result["process_isolation_verified"])
        self.assertIsNone(result["peak_vram_bytes"])
        self.assertEqual(calls[0][0], list(COMMAND))
        self.assertEqual(calls[0][1]["timeout"], 5)

    def test_empty_compute_listing_is_not_proof_of_isolation(self):
        result = discover(runner=lambda command, **kwargs: SimpleNamespace(
            returncode=0, stdout=""
        ))
        self.assertTrue(result["ok"])
        self.assertEqual(result["processes"], [])
        self.assertFalse(result["process_isolation_verified"])
        self.assertFalse(result["memory_values_available_for_all_reported_processes"])

    def test_invalid_pid_and_memory_rejected(self):
        for raw in ("oops, python.exe, GPU-a, 100\n",
                    "1234, python.exe, GPU-a, bad-memory\n",
                    "1234, python.exe, GPU-a\n"):
            with self.subTest(raw=raw):
                with self.assertRaises(ValueError):
                    parse_compute_processes(raw)

    def test_unsupported_query_fails_without_inventing_metrics(self):
        result = discover(runner=lambda command, **kwargs: SimpleNamespace(
            returncode=1, stdout="", stderr="Not supported"
        ))
        self.assertFalse(result["ok"])
        self.assertEqual(result["availability"], "unsupported_or_error")
        self.assertFalse(result["attributable_to_generation"])
        self.assertIsNone(result["peak_vram_bytes"])


if __name__ == "__main__":
    unittest.main()
