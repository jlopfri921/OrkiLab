"""B9.3 conservative, evidence-based benchmark comparability diagnostics.

No comparability is *verified* from a shared run, a matching workflow ID,
duration, or a missing cache event alone. Only explicit contradictions can
block comparisons; everything else remains unverified.
"""
from __future__ import annotations

from typing import Any

CACHE_BLOCKERS = {"sampler_cached_not_comparable", "cached"}
KNOWN_SOURCE = "comfyui_history_status_messages"


def assess_duration_comparability(report: Any) -> dict:
    if not isinstance(report, dict) or not isinstance(report.get("run"), dict):
        raise ValueError("Invalid benchmark report")
    run_id = report["run"].get("id")
    variants = report.get("variants")
    observations = report.get("observations")
    if not isinstance(run_id, str) or not run_id or not isinstance(variants, list) or not isinstance(observations, list):
        raise ValueError("Invalid benchmark report structure")
    result = []
    groups = {}
    for variant in variants:
        if not isinstance(variant, dict) or not isinstance(variant.get("id"), str) or variant.get("run_id") != run_id:
            raise ValueError("Invalid benchmark variant")
        ident = variant["id"]
        if ident in groups:
            raise ValueError("Duplicate benchmark variant")
        groups[ident] = []
    for observation in observations:
        if not isinstance(observation, dict) or observation.get("variant_id") not in groups or observation.get("run_id") != run_id:
            raise ValueError("Invalid benchmark observation")
        groups[observation["variant_id"]].append(observation)
    for variant in variants:
        ident = variant["id"]
        completed = [o for o in groups[ident] if o.get("status") == "completed"]
        timed = [o for o in completed if type(o.get("duration_ms")) is int and o["duration_ms"] >= 0]
        reasons = []
        blocking = False
        if not timed:
            reasons.append("no_completed_measured_duration")
        if len(timed) < len(completed):
            reasons.append("incomplete_duration_coverage")
        workflow_ids, graph_hashes = set(), set()
        provenances = []
        for observation in timed:
            snap = observation.get("generation_lineage")
            if not isinstance(snap, dict):
                reasons.append("missing_generation_lineage")
                continue
            wid = snap.get("workflow_id")
            sha = snap.get("submitted_graph_sha256")
            if isinstance(wid, str) and wid:
                workflow_ids.add(wid)
            else:
                reasons.append("missing_workflow_identity")
            if isinstance(sha, str) and len(sha) == 64:
                graph_hashes.add(sha)
            else:
                reasons.append("missing_graph_fingerprint")
            timing = snap.get("execution_timing")
            if not isinstance(timing, dict):
                reasons.append("missing_timing_provenance")
                continue
            if timing.get("source") != KNOWN_SOURCE:
                reasons.append("unverified_timing_source")
            if timing.get("comparability") == "sampler_cached_not_comparable" or timing.get("sampler_cache_status") == "cached":
                blocking = True
                reasons.append("cached_sampler_observed")
            elif timing.get("comparability") not in (
                "sampler_cache_miss_partial_cache", "sampler_cache_unverified",
                "unverified",
            ):
                reasons.append("unclassified_sampler_cache")
            if timing.get("full_inference_verified") is not True:
                reasons.append("full_inference_not_verified")
            provenances.append(timing)
        if len(workflow_ids) > 1:
            blocking = True
            reasons.append("different_workflows_within_variant")
        if len(graph_hashes) > 1:
            # A changed graph might be a legitimate deliberate variable, so
            # it is *not* proof of incompatibility, but requires review.
            reasons.append("graph_changed_between_repetitions")
        if timed:
            reasons.extend(["hardware_equivalence_not_verified",
                            "seed_and_warmth_controls_not_verified"])
        result.append({
            "variant_id": ident,
            "status": "blocked" if blocking else "not_established",
            "measured_observations": len(timed),
            "completed_observations": len(completed),
            "reason_codes": sorted(set(reasons)),
            "ranking_eligible": False,
            "factual_speed_comparison_verified": False,
        })
    return {
        "schema_version": 1,
        "run_id": run_id,
        "status": "blocked" if any(x["status"] == "blocked" for x in result)
                  else "not_established",
        "variants": result,
        "ranking_eligible": False,
        "best_variant": None,
        "benchmark_database_modified": False,
        "limitations": (
            "No automatic speed winner: shared benchmark run and recorded "
            "execution duration do not prove equivalent hardware, workflow, "
            "seed, cache state or full inference. A cached sampler is a "
            "blocking observation. Missing evidence remains unverified."
        ),
    }
