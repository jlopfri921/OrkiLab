"""B9.1 — factual read-only benchmark summary; no scoring or invented metrics.

Takes the existing BenchmarkStore.report() output, not a database connection.
Aggregates only confirmed completed observations with numeric measured
duration. Never conflates cached work with a cold inference or global GPU
memory with per-job VRAM.
"""
from __future__ import annotations

from statistics import median
from typing import Any


def summarize_benchmark_report(report: Any) -> dict:
    if not isinstance(report, dict) or report.get("schema_version") != 1:
        raise ValueError("Unsupported benchmark report")
    run = report.get("run")
    variants, observations = report.get("variants"), report.get("observations")
    if not isinstance(run, dict) or not isinstance(variants, list) or not isinstance(observations, list):
        raise ValueError("Invalid benchmark report")
    run_id = run.get("id")
    if not isinstance(run_id, str) or not run_id:
        raise ValueError("Invalid benchmark run")
    unique = set()
    grouped = {}
    for variant in variants:
        if not isinstance(variant, dict) or not isinstance(variant.get("id"), str) or variant.get("run_id") != run_id:
            raise ValueError("Invalid benchmark variant")
        ident = variant["id"]
        if ident in unique:
            raise ValueError("Duplicate benchmark variant")
        unique.add(ident)
        grouped[ident] = {"variant_id": ident, "label": variant.get("label"),
                          "completed": 0, "failed": 0, "cancelled": 0,
                          "measured_duration_count": 0, "duration_ms_median": None,
                          "duration_ms_min": None, "duration_ms_max": None,
                          "missing_duration_count": 0,
                          "per_job_peak_vram_count": 0,
                          "missing_per_job_peak_vram_count": 0,
                          "measured_vram_peak_bytes_max": None,
                          "duration_comparability": "not_established"}
    durations = {ident: [] for ident in unique}
    peaks = {ident: [] for ident in unique}
    seen = set()
    for observation in observations:
        if not isinstance(observation, dict):
            raise ValueError("Invalid benchmark observation")
        vid = observation.get("variant_id")
        repetition = observation.get("repetition")
        if (vid not in grouped or observation.get("run_id") != run_id
                or type(repetition) is not int or repetition < 0
                or (vid, repetition) in seen):
            raise ValueError("Invalid or duplicate benchmark observation")
        seen.add((vid, repetition))
        status = observation.get("status")
        if status not in ("completed", "failed", "cancelled"):
            raise ValueError("Invalid benchmark observation status")
        item = grouped[vid]
        item[status] += 1
        # A failed/cancelled job is not a completed benchmark measurement.
        if status != "completed":
            continue
        duration = observation.get("duration_ms")
        if duration is None:
            item["missing_duration_count"] += 1
        elif type(duration) is int and duration >= 0:
            durations[vid].append(duration)
        else:
            raise ValueError("Invalid duration measurement")
        peak = observation.get("peak_vram_bytes")
        if peak is None:
            item["missing_per_job_peak_vram_count"] += 1
        elif type(peak) is int and peak >= 0:
            peaks[vid].append(peak)
        else:
            raise ValueError("Invalid job VRAM measurement")
    result = []
    for variant in variants:
        ident = variant["id"]
        item = grouped[ident]
        ds, ps = durations[ident], peaks[ident]
        item["measured_duration_count"] = len(ds)
        item["per_job_peak_vram_count"] = len(ps)
        if ds:
            item["duration_ms_median"] = median(ds)
            item["duration_ms_min"] = min(ds)
            item["duration_ms_max"] = max(ds)
        if ps:
            item["measured_vram_peak_bytes_max"] = max(ps)
        result.append(item)
    return {
        "schema_version": 1, "run_id": run_id,
        "run_state": run.get("state"),
        "variant_count": len(result),
        "observation_count": len(observations),
        "variants": result,
        "ranking": None,
        "best_variant": None,
        "benchmark_database_modified": False,
        "interpretation": (
            "Descriptive statistics of recorded completed observations only. "
            "Duration comparability is not established across variants; "
            "cache/warmth, workflow, model, GPU and seed controls must be "
            "verified independently. Missing VRAM measurements stay unknown. "
            "Device-global GPU samples are never substituted for per-job VRAM."
        ),
    }
