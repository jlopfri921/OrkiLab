"""B8.2e read-only identity cross-check: mocked HTTP/port paths only."""
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from benchmark_comfyui_identity_probe import assess_identity, check


def port(pid=32808):
    return {"ok": True, "listeners": [{
        "pid": pid, "listed_by_nvidia": True,
        "gpu_uuids": ["GPU-rtx3090"], "local_address": "0.0.0.0",
    }]}


class ComfyuiIdentityProbeTests(unittest.TestCase):
    def setUp(self):
        self.cfg = {"mode": "hybrid", "url": "http://127.0.0.1:8188"}
        self.stats = {"system": {"comfyui_version": "0.46.2",
                                 "deploy_environment": "local-desktop2-standalone"},
                      "devices": [{"name": "cuda:0 NVIDIA RTX 3090"}]}

    def test_correlates_http_port_gpu_but_not_memory(self):
        result = assess_identity(self.cfg, self.stats, port())
        self.assertTrue(result["ok"])
        self.assertTrue(result["http_comfyui_confirmed"])
        self.assertTrue(result["http_tcp_gpu_correlated"])
        self.assertEqual(result["tcp_listener_pid"], 32808)
        self.assertEqual(result["comfyui_version"], "0.46.2")
        self.assertFalse(result["comfyui_process_verified"])
        self.assertFalse(result["attributable_to_generation"])
        self.assertIsNone(result["peak_vram_bytes"])

    def test_invalid_http_or_unmatched_pid_fails_closed(self):
        self.assertFalse(assess_identity(self.cfg, {}, port())["ok"])
        self.assertFalse(assess_identity(
            self.cfg, self.stats, {"ok": True, "listeners": []}
        )["ok"])
        bad = port()
        bad["listeners"][0]["listed_by_nvidia"] = False
        self.assertFalse(assess_identity(self.cfg, self.stats, bad)["ok"])

    def test_unconfigured_endpoint_makes_no_http_calls(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp) / "settings" / "orkilab"
            folder.mkdir(parents=True)
            (folder / "comfyui.json").write_text(
                json.dumps({"mode": "hybrid", "url": "http://127.0.0.1:8189"}),
                encoding="utf-8",
            )
            def forbidden(*args, **kwargs):
                raise AssertionError("Should not contact a different endpoint")
            self.assertFalse(check(Path(tmp), http_get=forbidden,
                                   port_check=forbidden)["ok"])

    def test_live_check_calls_only_read_endpoints(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp) / "settings" / "orkilab"
            folder.mkdir(parents=True)
            (folder / "comfyui.json").write_text(json.dumps(self.cfg), encoding="utf-8")
            calls = []
            def fake_http(url, path, **kwargs):
                calls.append((url, path))
                return self.stats
            result = check(Path(tmp), http_get=fake_http, port_check=lambda: port())
            self.assertTrue(result["ok"])
            self.assertEqual(calls, [("http://127.0.0.1:8188", "/system_stats")])


if __name__ == "__main__":
    unittest.main()
