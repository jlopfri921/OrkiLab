"""Explicit import of terminal ComfyUI history into a running benchmark.

No ComfyUI HTTP calls or automatic queuing. Callers must independently verify
launcher-local access, project ownership and a trusted history record.
"""
from __future__ import annotations

import json
from typing import Any

from benchmark_generation_adapter import snapshot_generation
from benchmark_store import BenchmarkStore


def import_terminal_generation(
    store: BenchmarkStore,
    run_id: str,
    variant_id: str,
    repetition: int,
    generation_record: dict[str, Any],
) -> dict[str, Any]:
    """Record one terminal generation, preserving factual provenance.

    This is an explicit, caller-triggered operation, never an automatic
    scanner of all generation history. Unknown duration, peak VRAM,
    output digest and effective seed are stored as NULL.
    """
    snap = snapshot_generation(generation_record)

    # The benchmark protocol's structured config identifies the generation.
    # Avoid adding an unverified seed or recording a graph digest as an image hash.
    observation_id = store.record(
        run_id,
        variant_id,
        repetition,
        snap["status"],
        seed=None,
        duration_ms=None,
        peak_vram_bytes=None,
        output_sha256=None,
        error_message=None if snap["status"] == "completed"
                      else "Generation history status: " + snap["status"],
    )
    return {
        "observation_id": observation_id,
        "generation_snapshot": snap,
        "note": (
            "Record accepted; provenance snapshot is returned to caller but "
            "not persisted within this minimal schema. "
            "An immutable lineage field/table is required before production integration."
        ),
    }
