"""B7: inspect a Generation Studio result and optional benchmark linkage.

Read-only SQLite inspection. Does not contact ComfyUI, submit jobs, modify
history, trigger inference or create any DB files.

    python scripts/benchmark_live_audit.py
    python scripts/benchmark_live_audit.py --generation-id <id>
"""
from __future__ import annotations

import argparse
import json
import sqlite3
from contextlib import closing
from pathlib import Path


def audit(base: Path, generation_id: str | None = None) -> dict:
    """Inspect only existing files through SQLite URI mode=ro."""
    folder = Path(base) / "settings" / "orkilab"
    history_db = folder / "generations.sqlite3"
    if not history_db.is_file():
        return {"ok": False, "reason": "No Generation Studio history database exists"}
    with closing(sqlite3.connect(history_db.resolve().as_uri() + "?mode=ro", uri=True)) as con:
        con.row_factory = sqlite3.Row
        if generation_id is None:
            row = con.execute(
                "SELECT id,prompt_id,workflow_id,name,state,outputs,created,updated "
                "FROM generations ORDER BY created DESC,id DESC LIMIT 1"
            ).fetchone()
        else:
            row = con.execute(
                "SELECT id,prompt_id,workflow_id,name,state,outputs,created,updated "
                "FROM generations WHERE id=?", (generation_id,)
            ).fetchone()
    if row is None:
        return {"ok": False, "reason": "Generation not found"}
    try:
        outputs = json.loads(row["outputs"])
    except (TypeError, ValueError):
        outputs = []
    result = {
        "ok": True,
        "generation_id": row["id"],
        "prompt_id": row["prompt_id"],
        "workflow_id": row["workflow_id"],
        "workflow_name": row["name"],
        "state": row["state"],
        "output_count": len(outputs) if isinstance(outputs, list) else None,
        "benchmark_binding": "none",
        "benchmark_observation": "none",
    }
    benchmark_db = folder / "benchmarks.sqlite3"
    if not benchmark_db.is_file():
        return result
    with closing(sqlite3.connect(benchmark_db.resolve().as_uri() + "?mode=ro", uri=True)) as con:
        con.row_factory = sqlite3.Row
        tables = {item[0] for item in con.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        )}
        if "benchmark_generation_bindings" not in tables:
            return result
        binding = con.execute(
            "SELECT run_id,variant_id,repetition,workflow_id "
            "FROM benchmark_generation_bindings WHERE generation_id=?",
            (row["id"],)
        ).fetchone()
        if binding is None:
            return result
        result["benchmark_binding"] = "bound"
        result["benchmark_run_id"] = binding["run_id"]
        result["benchmark_variant_id"] = binding["variant_id"]
        result["benchmark_repetition"] = binding["repetition"]
        result["binding_workflow_matches"] = binding["workflow_id"] == row["workflow_id"]
        if "benchmark_generation_lineage" in tables:
            observation = con.execute(
                "SELECT observation_id FROM benchmark_generation_lineage "
                "WHERE run_id=? AND generation_id=?",
                (binding["run_id"], row["id"])
            ).fetchone()
            result["benchmark_observation"] = (
                "recorded" if observation else "missing"
            )
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--generation-id", default=None)
    args = parser.parse_args()
    result = audit(Path(__file__).resolve().parents[1], args.generation_id)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
