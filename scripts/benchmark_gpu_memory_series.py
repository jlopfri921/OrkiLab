"""B8.2b — bounded, opt-in GPU memory series; diagnostic only.

Records sampled device-wide VRAM, never a job's peak. Sampling is read-only.
Caller explicitly starts it; no training/ComfyUI jobs are launched or stopped.
"""
from __future__ import annotations

import argparse
import json
import math
import time
from typing import Callable

from benchmark_gpu_memory_probe import sample_devices


def summarize_samples(samples: list[dict], *, target_uuid: str) -> dict:
    """Pure analysis. Samples carry their own timestamps and device readings."""
    if not isinstance(target_uuid, str) or not target_uuid or len(target_uuid) > 128:
        raise ValueError("A specific target GPU UUID is required")
    if not isinstance(samples, list) or not 1 <= len(samples) <= 7200:
        raise ValueError("One or more bounded memory samples required")
    selected = []
    last_time = None
    for sample in samples:
        if not isinstance(sample, dict) or sample.get("ok") is not True:
            raise ValueError("Missing or failed VRAM sample")
        timestamp = sample.get("monotonic_seconds")
        if (type(timestamp) not in (int, float) or not math.isfinite(timestamp)
                or timestamp < 0 or (last_time is not None and timestamp < last_time)):
            raise ValueError("Invalid sample chronology")
        last_time = timestamp
        devices = sample.get("devices")
        if not isinstance(devices, list):
            raise ValueError("Missing GPU inventory")
        matches = [item for item in devices if isinstance(item, dict)
                   and item.get("uuid") == target_uuid]
        if len(matches) != 1:
            raise ValueError("Target GPU is missing or ambiguous")
        device = matches[0]
        total, used = device.get("total_bytes"), device.get("used_bytes")
        if (type(total) is not int or type(used) is not int
                or total <= 0 or not 0 <= used <= total):
            raise ValueError("Untrusted GPU memory values")
        selected.append({"monotonic_seconds": timestamp,
                         "used_bytes": used, "total_bytes": total})
    totals = {s["total_bytes"] for s in selected}
    if len(totals) != 1:
        raise ValueError("GPU memory total changed during capture")
    start = selected[0]["used_bytes"]
    return {
        "ok": True,
        "target_gpu_uuid": target_uuid,
        "scope": "device_global_sample_series",
        "sample_count": len(selected),
        "duration_seconds_observed": selected[-1]["monotonic_seconds"] - selected[0]["monotonic_seconds"],
        "baseline_used_bytes": start,
        "max_observed_used_bytes": max(s["used_bytes"] for s in selected),
        "max_observed_increase_over_baseline_bytes": max(
            max(s["used_bytes"] - start, 0) for s in selected
        ),
        "samples": selected,
        "peak_vram_bytes": None,
        "attributable_to_generation": False,
        "benchmark_database_modified": False,
        "limitations": (
            "Device-global sample maxima, not a true instantaneous peak or an "
            "attributable ComfyUI job metric. Concurrent GPU use, persistent "
            "model caching, and unsampled spikes are not excluded."
        ),
    }


def capture(*, target_uuid: str, sample_count: int = 10,
            interval_seconds: float = 0.5,
            sampler: Callable = sample_devices,
            clock: Callable = time.monotonic,
            sleeper: Callable = time.sleep) -> dict:
    """Explicit bounded collection. No GPU work or database mutations."""
    if type(sample_count) is not int or not 2 <= sample_count <= 120:
        raise ValueError("sample_count must be between 2 and 120")
    if (type(interval_seconds) not in (int, float)
            or not math.isfinite(interval_seconds)
            or not 0.2 <= interval_seconds <= 5.0):
        raise ValueError("interval_seconds must be between 0.2 and 5.0")
    if not isinstance(target_uuid, str) or not 0 < len(target_uuid) <= 128:
        raise ValueError("Explicit target GPU UUID required")
    samples = []
    for i in range(sample_count):
        if i:
            sleeper(interval_seconds)
        measurement = sampler()
        if measurement.get("ok") is not True:
            raise ValueError("Memory sampling failed; partial capture discarded")
        samples.append({**measurement, "monotonic_seconds": clock()})
    return summarize_samples(samples, target_uuid=target_uuid)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--gpu-uuid", required=True)
    parser.add_argument("--samples", type=int, default=10)
    parser.add_argument("--interval", type=float, default=0.5)
    args = parser.parse_args()
    try:
        result = capture(target_uuid=args.gpu_uuid, sample_count=args.samples,
                         interval_seconds=args.interval)
    except (ValueError, OSError) as exc:
        print(json.dumps({"ok": False, "reason": str(exc)[:200]}, ensure_ascii=False))
        return 1
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
