"""B7 preflight: read-only ComfyUI readiness check; NEVER submits a job.

Usage (from repository root, with project's virtualenv):
    .\\venv\\Scripts\\python.exe scripts/benchmark_comfyui_preflight.py

Makes GET requests only to /system_stats and /queue at the configured private
ComfyUI URL. Refuses live benchmarking if a training task or ComfyUI job exists.
No files/models/queues are altered; no benchmark database is created.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

from comfyui_connect import DEFAULT_SETTINGS, get_json, validate_settings
import project_layout


def assess_preflight(
    config: dict[str, Any],
    *,
    training_active: bool,
    system_stats: dict[str, Any],
    queue: dict[str, Any],
) -> dict[str, Any]:
    """Pure, fail-closed readiness check from already-fetched data."""
    if config["mode"] == "native":
        return {"ready": False, "reason": "ComfyUI disabled in native mode"}
    if not isinstance(system_stats, dict) or not isinstance(system_stats.get("system"), dict):
        return {"ready": False, "reason": "Invalid ComfyUI system statistics"}
    if not isinstance(system_stats.get("devices"), list):
        return {"ready": False, "reason": "No ComfyUI device inventory returned"}
    if not isinstance(queue, dict) or not all(
        isinstance(queue.get(key), list) for key in ("queue_running", "queue_pending")
    ):
        return {"ready": False, "reason": "Cannot verify ComfyUI queue"}
    if training_active:
        return {"ready": False, "reason": "OrkiLab training active"}
    running = len(queue["queue_running"])
    pending = len(queue["queue_pending"])
    if running or pending:
        return {
            "ready": False,
            "reason": "ComfyUI queue is occupied",
            "queue_running": running,
            "queue_pending": pending,
        }
    return {
        "ready": True,
        "reason": "Read-only checks passed; inference NOT yet tested",
        "queue_running": 0,
        "queue_pending": 0,
        "devices": [
            str(device.get("name", ""))[:160]
            for device in system_stats["devices"][:16]
            if isinstance(device, dict)
        ],
        "comfyui_version": str(system_stats["system"].get("comfyui_version", ""))[:80],
    }


def check_live(base: Path, *, fetch=get_json, is_training=None) -> dict[str, Any]:
    """Queries allowed GET endpoints only. No GPU inference, queue or DB writes."""
    base = Path(base)
    if is_training is None:
        is_training = project_layout.training_in_progress
    file = base / "settings" / "orkilab" / "comfyui.json"
    try:
        data = json.loads(file.read_text(encoding="utf-8"))
        config = validate_settings(data, DEFAULT_SETTINGS)
        if config["mode"] == "native":
            return {"ready": False, "reason": "ComfyUI disabled in native mode"}
        if is_training(base):
            return {"ready": False, "reason": "OrkiLab training active"}
        stats = fetch(config["url"], "/system_stats", timeout=5)
        queue = fetch(config["url"], "/queue", timeout=5)
        return assess_preflight(
            config, training_active=False, system_stats=stats, queue=queue
        )
    except (OSError, ValueError, TypeError, KeyError) as exc:
        return {
            "ready": False,
            "reason": "Could not verify ComfyUI readiness",
            "detail": str(exc)[:200],
        }


def main() -> int:
    base = Path(__file__).resolve().parents[1]
    result = check_live(base)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["ready"] else 1


if __name__ == "__main__":
    sys.exit(main())
