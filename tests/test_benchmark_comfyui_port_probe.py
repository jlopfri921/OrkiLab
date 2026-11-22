"""B8.2d TCP-listener correlation; mock-only tests."""
import json
import sys
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import benchmark_comfyui_port_probe as port_probe


class ComfyuiPortProbeTests(unittest.TestCase):
    def test_matching_gpu_pid_is_correlation_not_ownership(self):
        report = port_probe.assess(
            [{"pid": 32808, "executable": "D:\\ComfyUI\\python.exe",
              "local_address": "127.0.0.1"}],
            {"processes": [{"pid": 32808, "gpu_uuid": "GPU-test",
                            "used_gpu_memory_bytes": None}]},
        )
        self.assertTrue(report["ok"])
        self.assertTrue(report["listeners"][0]["listed_by_nvidia"])
        self.assertEqual(report["listeners"][0]["gpu_uuids"], ["GPU-test"])
        self.assertFalse(report["comfyui_process_verified"])
        self.assertFalse(report["process_isolation_verified"])
        self.assertIsNone(report["peak_vram_bytes"])

    def test_proxy_listener_not_gpu_process(self):
        report = port_probe.assess(
            [{"pid": 123, "executable": "proxy.exe", "local_address": "::1"}],
            {"processes": [{"pid": 456, "gpu_uuid": "GPU-test"}]},
        )
        self.assertFalse(report["listeners"][0]["listed_by_nvidia"])

    def test_invalid_or_missing_identity_fails_closed(self):
        for listeners in (None, [{"pid": "not-a-pid", "executable": "python.exe",
                                  "local_address": "127.0.0.1"}]):
            with self.assertRaises(ValueError):
                port_probe.assess(listeners, {"processes": []})

    def test_windows_read_only_probe_and_failure(self):
        listeners = [{"pid": 32808, "executable": "python.exe",
                      "local_address": "127.0.0.1"}]
        captured = []

        def runner(command, **kwargs):
            captured.append((command, kwargs))
            return SimpleNamespace(returncode=0, stdout=json.dumps(listeners))

        with patch.object(port_probe.sys, "platform", "win32"):
            report = port_probe.probe(
                runner=runner, discover_gpu=lambda: {"ok": True, "processes": []}
            )
            self.assertTrue(report["ok"])
            self.assertEqual(captured[0][1]["timeout"], 8)
            self.assertEqual(captured[0][0][0], "powershell.exe")
            failed = port_probe.probe(
                runner=lambda cmd, **kw: SimpleNamespace(
                    returncode=1, stdout="", stderr="Access denied"
                ),
                discover_gpu=lambda: {"ok": True, "processes": []},
            )
            self.assertFalse(failed["ok"])


if __name__ == "__main__":
    unittest.main()
