"""Recover one explicitly selected, terminal Generation Studio job into Benchmark.

This is an operator-only local CLI, not an HTTP endpoint. Dry-run by default.
It never calls ComfyUI or changes GenerationHistory. It verifies the exact
project/run/variant/repetition, selected generation, and expected workflow;
writes only after --confirm. A linked result is stored with truthful NULL
performance metrics until telemetry is separately implemented.
"""
from __future__ import annotations

import argparse
import json
import sqlite3
from pathlib import Path

from benchmark_store import BenchmarkStore
from benchmark_job_binding import bind_submitted_generation, persist_bound_generation
from generation_history import GenerationHistory
from workspace_store import ProjectStore


def recover(base: Path, *, project_id: str, run_id: str,
            variant_id: str, repetition: int, generation_id: str,
            workflow_id: str, confirmed: bool = False) -> dict:
    """Inspect then (optionally) recover a specific record with fail-closed guards."""
    base = Path(base)
    folder = base / "settings" / "orkilab"
    db_path = folder / "benchmarks.sqlite3"
    hist_path = folder / "generations.sqlite3"
    projects_path = folder / "projects.sqlite3"
    if not all(p.is_file() for p in (db_path, hist_path, projects_path)):
        raise ValueError("Existing project, benchmark and generation databases are required")
    if type(repetition) is not int or repetition < 0:
        raise ValueError("Invalid repetition")
    projects = ProjectStore(projects_path).list()
    if not any(p["id"] == project_id for p in projects):
        raise PermissionError("Selected project must exist and be active")
    record = GenerationHistory(base).get(generation_id)
    if record is None:
        raise ValueError("Generation not found")
    if record["state"] not in ("completed", "error", "cancelled"):
        raise ValueError("Cannot recover a nonterminal generation")
    if record["workflow_id"] != workflow_id:
        raise ValueError("Selected workflow does not match actual generation")
    with BenchmarkStore(db_path) as store:
        run = store.db.execute(
            "SELECT state,project_id FROM benchmark_runs WHERE id=?", (run_id,)
        ).fetchone()
        variant = store.db.execute(
            "SELECT run_id FROM benchmark_variants WHERE id=?", (variant_id,)
        ).fetchone()
        if run is None or run["state"] != "running" or run["project_id"] != project_id:
            raise PermissionError("Benchmark run is not active or belongs to another project")
        if variant is None or variant["run_id"] != run_id:
            raise ValueError("Variant is not in the selected benchmark run")
        exists = store.db.execute(
            "SELECT generation_id FROM benchmark_generation_bindings "
            "WHERE generation_id=? OR (variant_id=? AND repetition=?)",
            (generation_id, variant_id, repetition)
        ).fetchone()
        if exists is not None:
            raise ValueError("Generation or repetition already bound; do not duplicate")
        observation = store.db.execute(
            "SELECT 1 FROM benchmark_observations WHERE variant_id=? AND repetition=?",
            (variant_id, repetition)
        ).fetchone()
        if observation is not None:
            raise ValueError("Observation already exists for this repetition")
        result = {
            "ready": True, "dry_run": not confirmed,
            "generation_id": generation_id, "generation_state": record["state"],
            "project_id": project_id, "run_id": run_id,
            "variant_id": variant_id, "repetition": repetition,
            "workflow_id": workflow_id,
        }
        if not confirmed:
            return result
        # Both writes share the same SQLite connection. Revert the binding if
        # observation ingestion fails. Neither action touches ComfyUI/history.
        try:
            bind_submitted_generation(
                store, project_id=project_id, run_id=run_id,
                variant_id=variant_id, repetition=repetition,
                generation_id=generation_id, workflow_id=workflow_id,
            )
            observation_id = persist_bound_generation(
                store, project_id=project_id, generation_record=record,
            )
        except Exception:
            with store.db:
                store.db.execute(
                    "DELETE FROM benchmark_generation_bindings "
                    "WHERE generation_id=? AND run_id=? AND variant_id=? "
                    "AND repetition=?",
                    (generation_id, run_id, variant_id, repetition)
                )
            raise
        result["dry_run"] = False
        result["observation_id"] = observation_id
        return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-id", required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--variant-id", required=True)
    parser.add_argument("--repetition", type=int, default=0)
    parser.add_argument("--generation-id", required=True)
    parser.add_argument("--workflow-id", required=True)
    parser.add_argument("--confirm", action="store_true",
                        help="Write the already-consented recovery to the local Benchmark DB")
    args = parser.parse_args()
    try:
        result = recover(
            Path(__file__).resolve().parents[1],
            project_id=args.project_id, run_id=args.run_id,
            variant_id=args.variant_id, repetition=args.repetition,
            generation_id=args.generation_id, workflow_id=args.workflow_id,
            confirmed=args.confirm,
        )
    except (OSError, sqlite3.Error, ValueError, PermissionError) as exc:
        print(json.dumps({"ready": False, "error": str(exc)}, ensure_ascii=False))
        return 1
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
