"""B6c: immutable generation-to-benchmark binding before result ingestion.

Caller must invoke bind_submitted_generation only with the token returned by
the same authorized Generation Studio submission flow. An arbitrary entry in
history is not evidence of project ownership. No queue/API operations here.
"""
from __future__ import annotations

from benchmark_store import BenchmarkStore, _utc_now
from benchmark_generation_adapter import snapshot_generation
from benchmark_generation_import import prepare_terminal_observation


def bind_submitted_generation(
    store: BenchmarkStore, *, project_id: str, run_id: str, variant_id: str,
    repetition: int, generation_id: str, workflow_id: str,
) -> None:
    """Claim a submission ID once, inside the trusted submission transaction."""
    if not isinstance(project_id, str) or not project_id:
        raise PermissionError("Authorized project required")
    if any(not isinstance(x, str) or not 0 < len(x) <= 200
           for x in (run_id, variant_id, generation_id, workflow_id)):
        raise ValueError("Invalid binding identifier")
    if type(repetition) is not int or repetition < 0:
        raise ValueError("Invalid repetition")
    with store.db:
        row = store.db.execute(
            """SELECT r.project_id, r.state, v.run_id AS variant_run
               FROM benchmark_runs r
               JOIN benchmark_variants v ON v.id=?
               WHERE r.id=?""", (variant_id, run_id)
        ).fetchone()
        if row is None or row["project_id"] != project_id:
            raise PermissionError("Benchmark does not belong to authorized project")
        if row["state"] != "running" or row["variant_run"] != run_id:
            raise ValueError("Binding requires an active run and its own variant")
        store.db.execute(
            """INSERT INTO benchmark_generation_bindings
               (generation_id,run_id,variant_id,repetition,workflow_id,bound_at)
               VALUES (?,?,?,?,?,?)""",
            (generation_id, run_id, variant_id, repetition, workflow_id, _utc_now())
        )


def persist_bound_generation(store: BenchmarkStore, *, project_id: str,
                             generation_record: dict) -> str:
    """Persist a terminal history record only if previously bound.

    Rechecks project, workflow, terminal state and duplicate observations.
    The binding is intentionally retained as an audit record after completion.
    Caller must validate trusted history source and launcher authorization.
    """
    if not isinstance(generation_record, dict):
        raise ValueError("Invalid generation record")
    generation_id = generation_record.get("id")
    if not isinstance(generation_id, str):
        raise ValueError("Invalid generation ID")
    bound = store.db.execute(
        "SELECT * FROM benchmark_generation_bindings WHERE generation_id=?",
        (generation_id,)
    ).fetchone()
    if bound is None:
        raise PermissionError("Generation was never bound to a benchmark")
    run = store.db.execute(
        "SELECT project_id FROM benchmark_runs WHERE id=?", (bound["run_id"],)
    ).fetchone()
    if run is None or not isinstance(project_id, str) or run["project_id"] != project_id:
        raise PermissionError("Project mismatch")
    if generation_record.get("workflow_id") != bound["workflow_id"]:
        raise ValueError("Generation workflow mismatch")
    proposal = prepare_terminal_observation(generation_record)
    return store.record(
        bound["run_id"], bound["variant_id"], bound["repetition"], proposal["status"],
        seed=proposal["seed"], duration_ms=proposal["duration_ms"],
        peak_vram_bytes=proposal["peak_vram_bytes"],
        output_sha256=proposal["output_sha256"], error_message=proposal["error_message"],
        source_snapshot=proposal["source_snapshot"],
    )
