"""B9.8: verify strictly what saved ComfyUI history snapshots actually prove.

This checks *recorded* workflow IDs, submitted-graph SHA-256 fingerprints,
and timing-source prompt IDs against an optional declared protocol. It does
not infer hashes of prompts, source files, models, seeds or GPU identity from
the graph fingerprint. No DB writes, ComfyUI calls or inferred rankings.
"""
from __future__ import annotations

import json
import re
from typing import Any

_SHA256 = re.compile(r"^[0-9a-f]{64}$")
_SOURCE = "comfyui_history_status_messages"


def _object(value: Any) -> dict:
    if isinstance(value, str):
        value = json.loads(value)
    if not isinstance(value, dict):
        raise ValueError("Invalid stored protocol JSON")
    return value


def verify_recorded_execution_evidence(report: Any) -> dict:
    if not isinstance(report, dict) or not isinstance(report.get("run"), dict):
        raise ValueError("Invalid benchmark report")
    run = report["run"]
    run_id = run.get("id")
    variants = report.get("variants")
    observations = report.get("observations")
    if (not isinstance(run_id, str) or not run_id
            or not isinstance(variants, list) or not isinstance(observations, list)):
        raise ValueError("Invalid benchmark report shape")
    protocol = _object(run.get("protocol", run.get("protocol_json", {})))
    declared_workflow = (protocol.get("workflow_id")
                         if protocol.get("schema") == "orkilab-repro-v1" else None)
    if not isinstance(declared_workflow, str) or not declared_workflow:
        declared_workflow = None
    known = {}
    for variant in variants:
        if (not isinstance(variant, dict) or not isinstance(variant.get("id"), str)
                or variant.get("run_id") != run_id or variant["id"] in known):
            raise ValueError("Invalid or repeated variant")
        known[variant["id"]] = []
    for observation in observations:
        if (not isinstance(observation, dict) or observation.get("run_id") != run_id
                or observation.get("variant_id") not in known):
            raise ValueError("Invalid observation scope")
        known[observation["variant_id"]].append(observation)
    summaries = []
    for variant in variants:
        items = known[variant["id"]]
        reasons = []
        observed_graphs = set()
        recorded = 0
        workflow_matching = 0
        prompt_timing_matching = 0
        valid_graph_hashes = 0
        for observation in items:
            lineage = observation.get("generation_lineage")
            if not isinstance(lineage, dict) or not lineage:
                reasons.append("no_recorded_generation_lineage")
                continue
            recorded += 1
            workflow = lineage.get("workflow_id")
            if declared_workflow is None:
                reasons.append("no_declared_workflow_for_match")
            elif not isinstance(workflow, str) or not workflow:
                reasons.append("recorded_workflow_missing")
            elif workflow != declared_workflow:
                reasons.append("workflow_mismatch")
            else:
                workflow_matching += 1
            fingerprint = lineage.get("submitted_graph_sha256")
            if isinstance(fingerprint, str) and _SHA256.fullmatch(fingerprint):
                valid_graph_hashes += 1
                observed_graphs.add(fingerprint)
            else:
                reasons.append("no_submitted_graph_fingerprint")
            timing = lineage.get("execution_timing")
            if isinstance(timing, dict):
                # timing provenance can be associated to the same ComfyUI prompt,
                # but this does not prove full inference, cold cache or equal GPU.
                snap_prompt = lineage.get("comfyui_prompt_id")
                event_prompt = timing.get("prompt_id")
                if (timing.get("source") == _SOURCE
                        and isinstance(snap_prompt, str) and bool(snap_prompt)
                        and event_prompt == snap_prompt):
                    prompt_timing_matching += 1
                elif timing.get("source") == _SOURCE:
                    reasons.append("prompt_timing_identity_not_established")
                else:
                    reasons.append("unverified_execution_timing_source")
            else:
                reasons.append("no_execution_timing_evidence")
        if recorded < len(items):
            reasons.append("incomplete_generation_lineage")
        if len(observed_graphs) > 1:
            reasons.append("different_submitted_graph_fingerprints")
        if not items:
            reasons.append("no_observations")
        if recorded and prompt_timing_matching < recorded:
            reasons.append("timing_provenance_incomplete")
        if recorded and workflow_matching < recorded and declared_workflow is not None:
            reasons.append("declared_workflow_not_confirmed_for_all")
        summaries.append({
            "variant_id": variant["id"],
            "status": "mismatch" if "workflow_mismatch" in reasons
                else "partially_verified" if recorded
                else "no_execution_evidence",
            "observations": len(items),
            "lineage_records": recorded,
            "workflow_id_matches": workflow_matching,
            "submitted_graph_fingerprints_recorded": valid_graph_hashes,
            "consistent_graph_fingerprint": bool(observed_graphs) and len(observed_graphs) == 1
                and valid_graph_hashes == recorded and recorded == len(items),
            "timing_prompt_id_matches": prompt_timing_matching,
            "reason_codes": sorted(set(reasons)),
            "prompt_content_verified": False,
            "input_content_verified": False,
            "gpu_equivalence_verified": False,
            "full_inference_verified": False,
        })
    return {
        "schema_version": 1,
        "run_id": run_id,
        "status": "mismatch" if any(x["status"] == "mismatch" for x in summaries)
            else "partially_verified" if any(x["lineage_records"] for x in summaries)
            else "no_execution_evidence",
        "variants": summaries,
        "ranking_eligible": False,
        "best_variant": None,
        "database_modified": False,
        "limitations": ("Checks recorded ComfyUI execution provenance only. "
                        "A matching workflow ID and submitted graph fingerprint "
                        "do not verify declared prompt/input content, model file "
                        "identity, hardware equivalence or full inference."),
    }
