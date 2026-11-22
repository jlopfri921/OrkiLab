"""Read-only preparation of benchmark observations from terminal ComfyUI history.

No job submission, queue manipulation, SQLite writes, or metadata loss.
Persistence is deliberately deferred until atomic provenance/lineage storage
and launcher-local authorization are implemented and tested.
"""
from __future__ import annotations

from typing import Any
from benchmark_generation_adapter import snapshot_generation


def prepare_terminal_observation(generation_record: dict[str, Any]) -> dict[str, Any]:
    """Build a factual observation proposal with its complete source snapshot.

    The returned structure is for a future explicitly confirmed transaction,
    not a stored observation. Unknown metrics are intentionally NULL.
    """
    snap = snapshot_generation(generation_record)
    return {
        "status": snap["status"],
        "seed": None,
        "duration_ms": None,
        "peak_vram_bytes": None,
        "output_sha256": None,
        "error_message": None if snap["status"] == "completed"
                         else "Generation history status: " + snap["status"],
        "source_snapshot": snap,
        "persisted": False,
        "requires": "Atomic provenance lineage, authorization and explicit confirmation",
    }
