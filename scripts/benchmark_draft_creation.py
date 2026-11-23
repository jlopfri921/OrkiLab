"""B9.5 explicitly confirmed, atomic draft creation (no execution).

Validates the exact v1 reproducibility declaration before opening any SQLite
writer. Stores two or more uniquely declared variants in one transaction.
Never submits ComfyUI work, creates generated observations, or modifies
existing benchmark runs.
"""
from __future__ import annotations

import uuid
from pathlib import Path

from benchmark_repro_protocol import declared_protocol_readiness
from benchmark_store import BenchmarkStore, _canonical_json, _utc_now


def validate_draft_payload(payload: object) -> dict:
    if not isinstance(payload, dict) or set(payload) != {
        "project_id", "name", "protocol", "variants", "confirm"
    } or payload.get("confirm") is not True:
        raise ValueError("Explicit, complete benchmark draft confirmation required")
    project_id, name = payload["project_id"], payload["name"]
    if not isinstance(project_id, str) or not 0 < len(project_id) <= 200:
        raise ValueError("Project ID required")
    if not isinstance(name, str) or not 0 < len(name.strip()) <= 120:
        raise ValueError("Benchmark name required")
    protocol = payload["protocol"]
    variants = payload["variants"]
    if not isinstance(protocol, dict) or set(protocol) != {
        "schema", "vary", "workflow_id", "prompt_sha256",
        "negative_prompt_sha256", "input_sha256", "gpu_uuid",
        "cache", "seed_policy", "repetitions", "resolution",
    }:
        raise ValueError("Complete v1 protocol is required")
    if (not isinstance(variants, list) or not 2 <= len(variants) <= 20
            or any(not isinstance(v, dict) or set(v) != {"label", "controlled_value"}
                   for v in variants)):
        raise ValueError("Between 2 and 20 complete variants are required")
    for v in variants:
        if (not isinstance(v["label"], str) or not 0 < len(v["label"].strip()) <= 120
                or not isinstance(v["controlled_value"], str)
                or not 0 < len(v["controlled_value"].strip()) <= 200):
            raise ValueError("Invalid variant label or controlled value")
    labels = [v["label"].strip() for v in variants]
    if len(set(labels)) != len(labels):
        raise ValueError("Variant labels must be unique")
    test_report = {
        "run": {"id": "preview", "protocol": protocol},
        "variants": [
            {"id": str(i), "run_id": "preview",
             "config": {"controlled_value": item["controlled_value"].strip()}}
            for i, item in enumerate(variants)
        ],
    }
    ready = declared_protocol_readiness(test_report)
    if ready["status"] != "declared_unverified":
        raise ValueError("Incomplete reproducibility declaration: " +
                         ", ".join(ready["reason_codes"] +
                             [reason for v in ready["variants"]
                              for reason in v["reason_codes"]])[:400])
    # Validate serialization, without opening a database.
    _canonical_json(protocol)
    for v in variants:
        _canonical_json({"controlled_value": v["controlled_value"].strip()})
    return {"project_id": project_id, "name": name.strip(),
            "protocol": protocol,
            "variants": [{"label": v["label"].strip(),
                          "controlled_value": v["controlled_value"].strip()}
                         for v in variants]}


def create_confirmed_draft(base: Path, payload: object, *, authorized_project_id: str) -> str:
    draft = validate_draft_payload(payload)
    if (not isinstance(authorized_project_id, str)
            or authorized_project_id != draft["project_id"]):
        raise PermissionError("Benchmark draft project mismatch")
    run_id, now = uuid.uuid4().hex, _utc_now()
    db = Path(base) / "settings" / "orkilab" / "benchmarks.sqlite3"
    with BenchmarkStore(db) as store:
        with store.db:
            store.db.execute(
                "INSERT INTO benchmark_runs VALUES (?, ?, ?, 'draft', ?, ?, ?)",
                (run_id, draft["project_id"], draft["name"],
                 _canonical_json(draft["protocol"]), now, now),
            )
            for item in draft["variants"]:
                store.db.execute(
                    "INSERT INTO benchmark_variants VALUES (?, ?, ?, ?)",
                    (uuid.uuid4().hex, run_id, item["label"],
                     _canonical_json({"controlled_value": item["controlled_value"]})),
                )
    return run_id
