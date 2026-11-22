"""B9.9 read-only cross-check of recorded Benchmark lineage and local history.

The history graph is the saved submitted API graph; matching it confirms
consistency between two *local records*, not original ComfyUI server contents,
models, input images or original prompt text.
"""
from __future__ import annotations

from typing import Any

from benchmark_generation_adapter import snapshot_generation


def compare_saved_generation(snapshot: Any, history: Any) -> dict:
    if not isinstance(snapshot, dict):
        raise ValueError("Snapshot must be an object")
    if history is None:
        return {"status": "history_missing", "reason_codes": ["generation_history_missing"],
                "record_consistent": False, "input_content_verified": False,
                "prompt_content_verified": False, "remote_execution_verified": False}
    if not isinstance(history, dict):
        raise ValueError("Invalid history record")
    try:
        regenerated = snapshot_generation(history)
    except (ValueError, TypeError, KeyError, OverflowError):
        return {"status": "history_invalid", "reason_codes": ["generation_history_unusable"],
                "record_consistent": False, "input_content_verified": False,
                "prompt_content_verified": False, "remote_execution_verified": False}
    checks = {
        "generation_id": regenerated["generation_id"] == snapshot.get("generation_id"),
        "comfyui_prompt_id": regenerated["comfyui_prompt_id"] == snapshot.get("comfyui_prompt_id"),
        "workflow_id": regenerated["workflow_id"] == snapshot.get("workflow_id"),
        "submitted_graph_sha256": regenerated["submitted_graph_sha256"] ==
                                  snapshot.get("submitted_graph_sha256"),
        "status": regenerated["status"] == snapshot.get("status"),
    }
    reasons = ["history_record_" + key + "_mismatch" for key, ok in checks.items() if not ok]
    return {
        "status": "local_record_match" if not reasons else "local_record_mismatch",
        "reason_codes": reasons,
        "record_consistent": not reasons,
        "checked_fields": len(checks),
        "input_content_verified": False,
        "prompt_content_verified": False,
        "remote_execution_verified": False,
    }


def summarize_saved_history_matches(report: Any, history_records: Any, *, truncated: bool = False) -> dict:
    if (not isinstance(report, dict) or not isinstance(report.get("run"), dict)
            or not isinstance(report.get("observations"), list)
            or not isinstance(report.get("variants"), list)
            or not isinstance(history_records, dict)):
        raise ValueError("Invalid report/history source")
    run_id = report["run"].get("id")
    if not isinstance(run_id, str) or not run_id:
        raise ValueError("Invalid run ID")
    group = {}
    for v in report["variants"]:
        if (not isinstance(v, dict) or not isinstance(v.get("id"), str)
                or v.get("run_id") != run_id or v["id"] in group):
            raise ValueError("Invalid variant scope")
        group[v["id"]] = []
    for o in report["observations"]:
        if (not isinstance(o, dict) or o.get("run_id") != run_id
                or o.get("variant_id") not in group):
            raise ValueError("Invalid observation scope")
        group[o["variant_id"]].append(o)
    result = []
    for v in report["variants"]:
        results = []
        for observation in group[v["id"]]:
            snap = observation.get("generation_lineage")
            if not isinstance(snap, dict) or not isinstance(snap.get("generation_id"), str):
                results.append("lineage_missing")
                continue
            generation_id = snap["generation_id"]
            # The caller queries by exact generation IDs from the scoped report.
            if generation_id not in history_records:
                results.append("history_missing")
            else:
                results.append(compare_saved_generation(snap, history_records[generation_id])["status"])
        counts = {state: results.count(state) for state in
                  ("local_record_match", "local_record_mismatch", "history_missing",
                   "history_invalid", "lineage_missing")}
        result.append({"variant_id": v["id"], "observations": len(group[v["id"]]),
                       "counts": counts,
                       "status": "not_checked" if truncated else (
                           "mismatch" if counts["local_record_mismatch"] else
                           "local_records_consistent" if results and counts["local_record_match"] == len(results)
                           else "incomplete"),
                       "input_content_verified": False,
                       "prompt_content_verified": False})
    return {"schema_version": 1, "run_id": run_id, "variants": result,
            "history_check_truncated": bool(truncated), "ranking_eligible": False,
            "remote_execution_verified": False, "database_modified": False,
            "limitations": "Only compares local persisted record copies. Never verifies original ComfyUI execution, model files, image bytes, prompt contents or hardware."}
