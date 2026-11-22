"""B8.2h explicit opt-in contract for experimental generation GPU sampling.

Only validated requests may start passive telemetry. This module does not
submit jobs, read GPU counters, change ComfyUI or write SQLite.
"""
from __future__ import annotations

import math


def validate_gpu_monitor_option(option: object) -> dict | None:
    if option is None:
        return None
    if not isinstance(option, dict) or set(option) != {
        "confirm", "gpu_uuid", "samples", "interval"
    } or option.get("confirm") is not True:
        raise ValueError("Explicit, complete GPU monitoring consent required")
    uuid = option.get("gpu_uuid")
    samples, interval = option.get("samples"), option.get("interval")
    if not isinstance(uuid, str) or not uuid.startswith("GPU-") or len(uuid) > 128:
        raise ValueError("Select a valid NVIDIA GPU UUID")
    if type(samples) is not int or not 2 <= samples <= 120:
        raise ValueError("GPU monitoring samples must be 2–120")
    if (type(interval) not in (int, float) or not math.isfinite(interval)
            or not 0.2 <= interval <= 5.0):
        raise ValueError("GPU monitoring interval must be 0.2–5 seconds")
    return {"gpu_uuid": uuid, "samples_limit": samples,
            "interval_seconds": float(interval)}


def monitoring_receipt(state: str) -> dict:
    """Never conflate a queued monitor with an observed GPU metric."""
    if state not in ("scheduled", "running", "completed", "failed"):
        raise ValueError("Invalid experimental monitor state")
    return {
        "state": state,
        "scope": "device_global_generation_window",
        "attributable_to_generation": False,
        "peak_vram_bytes": None,
        "benchmark_database_modified": False,
    }
