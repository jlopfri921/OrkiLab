"""B8.2e: correlate configured localhost ComfyUI HTTP identity with TCP PID/GPU.

This is a read-only diagnostic, NOT cryptographic process ownership proof,
GPU isolation, or an attributable per-generation VRAM measurement.
"""
from __future__ import annotations

import json
from pathlib import Path

from benchmark_comfyui_port_probe import probe as port_probe
from comfyui_connect import DEFAULT_SETTINGS, get_json, validate_settings


def assess_identity(settings: dict, stats: object, ports: object) -> dict:
    result = {
        "ok": False,
        "http_comfyui_confirmed": False,
        "http_tcp_gpu_correlated": False,
        "comfyui_process_verified": False,
        "process_isolation_verified": False,
        "attributable_to_generation": False,
        "peak_vram_bytes": None,
        "benchmark_database_modified": False,
    }
    if not isinstance(settings, dict) or settings.get("mode") == "native":
        return {**result, "reason": "ComfyUI not configured"}
    if settings.get("url") != "http://127.0.0.1:8188":
        return {**result, "reason": "This Windows diagnostic requires exact localhost:8188"}
    system = stats.get("system") if isinstance(stats, dict) else None
    devices = stats.get("devices") if isinstance(stats, dict) else None
    if not isinstance(system, dict) or not isinstance(devices, list):
        return {**result, "reason": "Invalid ComfyUI HTTP system stats"}
    version, environment = system.get("comfyui_version"), system.get("deploy_environment")
    if not isinstance(version, str) or not 0 < len(version) <= 100:
        return {**result, "reason": "No valid ComfyUI version"}
    if not isinstance(ports, dict) or ports.get("ok") is not True:
        return {**result, "reason": "TCP/GPU PID correlation unavailable"}
    listeners = ports.get("listeners")
    if not isinstance(listeners, list) or len(listeners) != 1:
        return {**result, "reason": "No unique TCP listener"}
    listener = listeners[0]
    if (not isinstance(listener, dict)
            or type(listener.get("pid")) is not int
            or not listener.get("listed_by_nvidia")
            or not listener.get("gpu_uuids")):
        return {**result, "reason": "TCP owner not found in NVIDIA inventory"}
    return {
        **result,
        "ok": True,
        "http_comfyui_confirmed": True,
        "http_tcp_gpu_correlated": True,
        "comfyui_version": version,
        "deploy_environment": str(environment or "")[:100],
        "tcp_listener_pid": listener["pid"],
        "tcp_listener_address": listener.get("local_address"),
        "gpu_uuids": listener["gpu_uuids"],
        "limitations": (
            "HTTP identity, TCP listener PID and NVIDIA device UUID correlate, "
            "but do not cryptographically establish process ownership or GPU "
            "exclusivity; process VRAM is unavailable under this Windows WDDM setup."
        ),
    }


def check(base: Path, *, http_get=get_json, port_check=port_probe) -> dict:
    try:
        cfg_file = Path(base) / "settings" / "orkilab" / "comfyui.json"
        cfg = validate_settings(json.loads(cfg_file.read_text(encoding="utf-8")),
                                DEFAULT_SETTINGS)
        if cfg["mode"] == "native" or cfg["url"] != "http://127.0.0.1:8188":
            return assess_identity(cfg, None, None)
        stats = http_get(cfg["url"], "/system_stats", timeout=5, max_bytes=2_000_000)
        ports = port_check()
        return assess_identity(cfg, stats, ports)
    except (OSError, ValueError, TypeError, KeyError) as exc:
        return {"ok": False, "reason": "Identity diagnostic unavailable",
                "detail": str(exc)[:200], "attributable_to_generation": False,
                "peak_vram_bytes": None, "benchmark_database_modified": False}


def main() -> int:
    result = check(Path(__file__).resolve().parents[1])
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
