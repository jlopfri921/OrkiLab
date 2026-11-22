"""OrkiLab 0.6 alpha.1: local, append-only benchmark results registry.

This module deliberately does not submit ComfyUI jobs, alter source files,
download models, or infer quality scores. Integrations must explicitly supply
measured observations from a completed job.
"""
from __future__ import annotations

import json
import math
import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

_SCHEMA = """
PRAGMA foreign_keys = ON;
CREATE TABLE IF NOT EXISTS benchmark_runs (
    id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL,
    name TEXT NOT NULL,
    state TEXT NOT NULL CHECK(state IN ('draft', 'running', 'completed', 'cancelled', 'failed')),
    protocol_json TEXT NOT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS benchmark_variants (
    id TEXT PRIMARY KEY,
    run_id TEXT NOT NULL REFERENCES benchmark_runs(id) ON DELETE RESTRICT,
    label TEXT NOT NULL,
    config_json TEXT NOT NULL,
    UNIQUE(run_id, label)
);
CREATE TABLE IF NOT EXISTS benchmark_observations (
    id TEXT PRIMARY KEY,
    run_id TEXT NOT NULL REFERENCES benchmark_runs(id) ON DELETE RESTRICT,
    variant_id TEXT NOT NULL REFERENCES benchmark_variants(id) ON DELETE RESTRICT,
    repetition INTEGER NOT NULL CHECK(repetition >= 0),
    status TEXT NOT NULL CHECK(status IN ('completed', 'failed', 'cancelled')),
    seed INTEGER,
    duration_ms INTEGER CHECK(duration_ms IS NULL OR duration_ms >= 0),
    peak_vram_bytes INTEGER CHECK(peak_vram_bytes IS NULL OR peak_vram_bytes >= 0),
    output_sha256 TEXT,
    error_message TEXT,
    recorded_at TEXT NOT NULL,
    UNIQUE(variant_id, repetition)
);
CREATE INDEX IF NOT EXISTS idx_benchmark_runs_project ON benchmark_runs(project_id);
CREATE INDEX IF NOT EXISTS idx_benchmark_observations_run ON benchmark_observations(run_id);
"""

def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")

def _canonical_json(value: dict[str, Any]) -> str:
    if not isinstance(value, dict):
        raise ValueError("Expected an object")
    def reject_constants(token: str) -> None:
        raise ValueError("Non-finite JSON number: " + token)
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)
    json.loads(encoded, parse_constant=reject_constants)
    return encoded

def _id() -> str:
    return str(uuid.uuid4())

class BenchmarkStore:
    """Standalone SQLite registry. Caller owns workflow execution and access control."""

    def __init__(self, db_path: str | Path):
        path = Path(db_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        self.db = sqlite3.connect(str(path))
        self.db.row_factory = sqlite3.Row
        self.db.execute("PRAGMA foreign_keys = ON")
        self.db.executescript(_SCHEMA)

    def close(self) -> None:
        self.db.close()

    def __enter__(self) -> "BenchmarkStore":
        return self

    def __exit__(self, *args: object) -> None:
        self.close()

    def create_run(self, project_id: str, name: str, protocol: dict[str, Any]) -> str:
        if not project_id.strip() or not name.strip():
            raise ValueError("Project and name are required")
        run_id, now = _id(), _utc_now()
        with self.db:
            self.db.execute(
                "INSERT INTO benchmark_runs VALUES (?, ?, ?, 'draft', ?, ?, ?)",
                (run_id, project_id.strip(), name.strip(), _canonical_json(protocol), now, now),
            )
        return run_id

    def add_variant(self, run_id: str, label: str, config: dict[str, Any]) -> str:
        if not label.strip():
            raise ValueError("Variant label required")
        variant_id = _id()
        with self.db:
            row = self.db.execute("SELECT state FROM benchmark_runs WHERE id=?", (run_id,)).fetchone()
            if row is None or row["state"] != "draft":
                raise ValueError("Variants can only be added to a draft run")
            self.db.execute(
                "INSERT INTO benchmark_variants VALUES (?, ?, ?, ?)",
                (variant_id, run_id, label.strip(), _canonical_json(config)),
            )
        return variant_id

    def transition(self, run_id: str, state: str) -> None:
        allowed = {
            "draft": {"running", "cancelled"},
            "running": {"completed", "cancelled", "failed"},
        }
        with self.db:
            row = self.db.execute("SELECT state FROM benchmark_runs WHERE id=?", (run_id,)).fetchone()
            if row is None or state not in allowed.get(row["state"], set()):
                raise ValueError("Invalid benchmark state transition")
            if state == "running" and not self.db.execute(
                "SELECT 1 FROM benchmark_variants WHERE run_id=? LIMIT 1", (run_id,)
            ).fetchone():
                raise ValueError("At least one variant is required")
            self.db.execute(
                "UPDATE benchmark_runs SET state=?, updated_at=? WHERE id=?",
                (state, _utc_now(), run_id),
            )

    def record(self, run_id: str, variant_id: str, repetition: int, status: str,
               *, seed: int | None = None, duration_ms: int | None = None,
               peak_vram_bytes: int | None = None, output_sha256: str | None = None,
               error_message: str | None = None) -> str:
        if status not in {"completed", "cancelled", "failed"}:
            raise ValueError("Invalid observation status")
        if not isinstance(repetition, int) or isinstance(repetition, bool) or repetition < 0:
            raise ValueError("Invalid repetition")
        if seed is not None and (not isinstance(seed, int) or isinstance(seed, bool)):
            raise ValueError("Seed must be an integer")
        for number in (duration_ms, peak_vram_bytes):
            if number is not None and (not isinstance(number, int) or isinstance(number, bool) or number < 0):
                raise ValueError("Measurements must be non-negative integers")
        if output_sha256 is not None and (len(output_sha256) != 64 or any(c not in "0123456789abcdef" for c in output_sha256)):
            raise ValueError("Output hash must be a lowercase SHA-256 hex digest")
        observation_id = _id()
        with self.db:
            run = self.db.execute("SELECT state FROM benchmark_runs WHERE id=?", (run_id,)).fetchone()
            variant = self.db.execute("SELECT run_id FROM benchmark_variants WHERE id=?", (variant_id,)).fetchone()
            if run is None or run["state"] != "running" or variant is None or variant["run_id"] != run_id:
                raise ValueError("Run must be active and variant must belong to it")
            self.db.execute(
                """INSERT INTO benchmark_observations
                   (id, run_id, variant_id, repetition, status, seed, duration_ms,
                    peak_vram_bytes, output_sha256, error_message, recorded_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (observation_id, run_id, variant_id, repetition, status, seed,
                 duration_ms, peak_vram_bytes, output_sha256, error_message, _utc_now()),
            )
        return observation_id

    def report(self, run_id: str) -> dict[str, Any]:
        row = self.db.execute("SELECT * FROM benchmark_runs WHERE id=?", (run_id,)).fetchone()
        if row is None:
            raise KeyError(run_id)
        variants = self.db.execute(
            "SELECT * FROM benchmark_variants WHERE run_id=? ORDER BY label, id", (run_id,)
        ).fetchall()
        observations = self.db.execute(
            "SELECT * FROM benchmark_observations WHERE run_id=? ORDER BY variant_id, repetition",
            (run_id,),
        ).fetchall()
        return {
            "schema_version": 1,
            "run": {**dict(row), "protocol": json.loads(row["protocol_json"])},
            "variants": [{**dict(v), "config": json.loads(v["config_json"])} for v in variants],
            "observations": [dict(o) for o in observations],
            "limitations": "Raw measurements only; no automatic quality or hardware equivalence claims.",
        }
