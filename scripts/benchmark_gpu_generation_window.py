"""B8.2f: classify device-level VRAM samples inside a measured ComfyUI window.

This module has no I/O and never attributes device memory to a generation.
A measured server window uses UNIX epoch milliseconds; snapshots MUST use
the same clock family, unlike the older monotonic-only standalone series.
"""
from __future__ import annotations

import math
from typing import Any

from benchmark_execution_timing import measured_execution_timing


def _millis(value: Any) -> bool:
    return (type(value) in (int, float) and math.isfinite(value)
            and 1_000_000_000_000 <= value <= 9_999_999_999_999)


def analyze_generation_window(
    entry: Any, prompt_id: str, samples: Any, *,
    gpu_uuid: str, max_sampling_gap_ms: int = 1000,
    concurrent_gpu_activity_observed: bool | None = None,
) -> dict:
    """Filter independent global VRAM samples against exact server event bounds.

    Preconditions: samples include epoch_ms timestamps from the SAME clock
    family as the ComfyUI events. Caller provides concurrency evidence or None.
    No claim is made that a sampler captured a continuous peak or a process.
    """
    if not isinstance(gpu_uuid, str) or not 0 < len(gpu_uuid) <= 128:
        raise ValueError("Target GPU UUID required")
    if type(max_sampling_gap_ms) is not int or not 100 <= max_sampling_gap_ms <= 60000:
        raise ValueError("Invalid sampling cadence")
    if concurrent_gpu_activity_observed not in (None, True, False):
        raise ValueError("Invalid concurrency flag")
    if not isinstance(samples, list) or not 1 <= len(samples) <= 7200:
        raise ValueError("One or more bounded samples required")
    timing = measured_execution_timing(entry, prompt_id)
    result = {
        "ok": True, "prompt_id": prompt_id, "gpu_uuid": gpu_uuid,
        "scope": "generation_window_device_global_samples",
        "window_supported_by_server_events": timing is not None,
        "sample_count_in_window": 0,
        "max_observed_global_used_bytes": None,
        "observed_global_increase_bytes": None,
        "window_coverage": "unverified",
        "concurrent_gpu_activity_observed": concurrent_gpu_activity_observed,
        "peak_vram_bytes": None,
        "attributable_to_generation": False,
        "benchmark_database_modified": False,
        "limitations": (
            "Device-wide samples inside a ComfyUI server event window only; "
            "not process/job allocations or an instantaneous true VRAM peak. "
            "Other GPU users, caching and unsampled spikes remain possible."
        ),
    }
    if timing is None:
        return result
    start, end = timing["start_timestamp_ms"], timing["end_timestamp_ms"]
    parsed = []
    previous = None
    for sample in samples:
        if not isinstance(sample, dict):
            raise ValueError("Invalid sample")
        stamp, uuid = sample.get("epoch_ms"), sample.get("gpu_uuid")
        used, total = sample.get("used_bytes"), sample.get("total_bytes")
        if (not _millis(stamp) or (previous is not None and stamp < previous)
                or uuid != gpu_uuid or type(used) is not int
                or type(total) is not int or total <= 0 or not 0 <= used <= total):
            raise ValueError("Invalid timestamp, GPU identity, or memory")
        previous = stamp
        parsed.append((stamp, used, total))
    if len({p[2] for p in parsed}) != 1:
        raise ValueError("GPU capacity changed during capture")
    inside = [(stamp, used) for stamp, used, _ in parsed if start <= stamp <= end]
    result["sample_count_in_window"] = len(inside)
    if not inside:
        result["window_coverage"] = "no_samples_in_window"
        return result
    result["max_observed_global_used_bytes"] = max(x[1] for x in inside)
    result["observed_global_increase_bytes"] = max(
        0, result["max_observed_global_used_bytes"] - inside[0][1]
    )
    # A finite series never proves continuous coverage. Flag insufficient
    # cadence or endpoints as incomplete, otherwise call it sampled coverage.
    gaps = ([inside[0][0] - start]
            + [b[0] - a[0] for a, b in zip(inside, inside[1:])]
            + [end - inside[-1][0]])
    result["window_coverage"] = (
        "sampled_within_configured_gap" if all(
            gap <= max_sampling_gap_ms for gap in gaps
        ) else "incomplete_sampling"
    )
    return result
