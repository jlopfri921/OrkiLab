"""Read-only preparation and explicitly confirmed persistence of terminal history.

No job submission or queue manipulation; API endpoint authorization remains
separate from the project-scope and confirmation checks in this module.
"""
from __future__ import annotations

from typing import Any
from benchmark_generation_adapter import snapshot_generation
from benchmark_store import BenchmarkStore


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


def persist_terminal_observation(
    store: BenchmarkStore,
    run_id: str,
    variant_id: str,
    repetition: int,
    generation_record: dict[str, Any],
    *,
    authorized_project_id: str,
    confirmed: bool = False,
) -> str:
    """Explicitly persist a terminal result and complete lineage atomically.

    This Python API is not an HTTP endpoint. The future caller must perform
    launcher-local and origin authorization *before* calling it. Project
    scope is checked again here, and no ComfyUI request is made.
    """
    if confirmed is not True:
        raise PermissionError("Explicit benchmark import confirmation required")
    if not isinstance(authorized_project_id, str) or not authorized_project_id:
        raise PermissionError("Project authorization required")
    run = store.db.execute(
        "SELECT project_id FROM benchmark_runs WHERE id=?", (run_id,)
    ).fetchone()
    if run is None or run["project_id"] != authorized_project_id:
        raise PermissionError("Benchmark does not belong to authorized project")
    proposal = prepare_terminal_observation(generation_record)
    return store.record(
        run_id, variant_id, repetition, proposal["status"],
        seed=proposal["seed"],
        duration_ms=proposal["duration_ms"],
        peak_vram_bytes=proposal["peak_vram_bytes"],
        output_sha256=proposal["output_sha256"],
        error_message=proposal["error_message"],
        source_snapshot=proposal["source_snapshot"],
    )
