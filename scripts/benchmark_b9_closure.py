"""B9.10 benchmark diagnostic closure; never infer a winner or verified equality.

Combines the existing independently scoped diagnostics into a concise
read-only checklist. All negative/unknown outcomes remain explicit.
"""
from __future__ import annotations

from typing import Any

def summarize_b9_closure(report: Any) -> dict:
    if not isinstance(report, dict):
        raise ValueError("Invalid benchmark diagnostics")
    names = ("reproducibility_protocol", "comparability",
             "recorded_execution_evidence", "saved_history_consistency")
    sections = {}
    for name in names:
        item = report.get(name)
        if not isinstance(item, dict) or not isinstance(item.get("variants"), list):
            raise ValueError("Required benchmark diagnostic is missing")
        sections[name] = item

    protocol = sections["reproducibility_protocol"]
    comparability = sections["comparability"]
    execution = sections["recorded_execution_evidence"]
    history = sections["saved_history_consistency"]

    checks = [
        ("protocol_declaration",
         protocol.get("status") == "declared_unverified",
         "protocol_not_declared_or_incomplete"),
        ("duration_comparability",
         False, "execution_conditions_not_verified"),
        ("recorded_lineage",
         execution.get("status") == "partially_verified"
         and all(v.get("status") == "partially_verified" and
                 v.get("lineage_records") == v.get("observations")
                 and v.get("observations", 0) > 0
                 for v in execution["variants"])
         and len(execution["variants"]) > 0,
         "recorded_lineage_not_complete"),
        ("local_history",
         not history.get("history_check_truncated")
         and len(history["variants"]) > 0
         and all(v.get("status") == "local_records_consistent"
                 and v.get("observations", 0) > 0 for v in history["variants"]),
         "local_generation_history_not_complete"),
        ("prompt_and_input_attestation", False, "prompt_and_input_not_attested"),
        ("hardware_and_cache_attestation", False, "hardware_and_cache_not_attested"),
    ]

    contradiction = (
        comparability.get("status") == "blocked"
        or execution.get("status") == "mismatch"
        or any(v.get("status") == "mismatch" for v in history["variants"])
    )
    return {
        "schema_version": 1,
        "status": "contradiction_detected" if contradiction else "not_fully_verified",
        "checks": [{"code": name, "status": "recorded_only" if proven else "pending",
                    "reason_code": "" if proven else code}
                   for name, proven, code in checks],
        "recorded_evidence_is_not_experimental_proof": True,
        "comparability_verified": False,
        "execution_verified": False,
        "ranking_eligible": False,
        "best_variant": None,
        "database_modified": False,
        "generation_submitted": False,
        "limitations": (
            "A declared protocol, local lineage consistency, valid graph hashes "
            "and observed timing do not verify equivalence of model weights, "
            "input bytes, positive/negative roles, GPU, seeds, sampler cache "
            "or complete ComfyUI inference. No ranking is allowed."
        ),
    }
