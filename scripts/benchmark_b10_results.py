"""B10.4 — descriptive cross-variant measured results, not a speed ranking.

All differences are arithmetic descriptions of observed durations, NEVER
comparability, a speedup, a winner or a cold-inference attribution.
"""
from __future__ import annotations

from itertools import combinations
from typing import Any

_MAX_VARIANTS = 20


def describe_cross_variant_measurements(summary: Any, comparability: Any) -> dict:
    if (not isinstance(summary, dict) or not isinstance(comparability, dict)
            or not isinstance(summary.get("run_id"), str)
            or summary.get("run_id") != comparability.get("run_id")
            or not isinstance(summary.get("variants"), list)
            or not isinstance(comparability.get("variants"), list)):
        raise ValueError("Invalid cross-variant report scope")
    variants = summary["variants"]
    if len(variants) > _MAX_VARIANTS:
        raise ValueError("Too many variants for pairwise presentation")
    assessments = {}
    for item in comparability["variants"]:
        if not isinstance(item, dict) or not isinstance(item.get("variant_id"), str):
            raise ValueError("Invalid comparability item")
        if item["variant_id"] in assessments:
            raise ValueError("Duplicate comparability variant")
        assessments[item["variant_id"]] = item
    seen = set()
    for item in variants:
        if not isinstance(item, dict) or not isinstance(item.get("variant_id"), str):
            raise ValueError("Invalid summary variant")
        if item["variant_id"] in seen or item["variant_id"] not in assessments:
            raise ValueError("Invalid/duplicated variant scope")
        seen.add(item["variant_id"])
    if seen != set(assessments):
        raise ValueError("Comparability and summary variants differ")
    pairs = []
    for a, b in combinations(variants, 2):
        na, nb = a.get("measured_duration_count"), b.get("measured_duration_count")
        ma, mb = a.get("duration_ms_median"), b.get("duration_ms_median")
        valid = (
            type(na) is int and na > 0 and type(nb) is int and nb > 0
            and type(ma) in (int, float) and ma >= 0
            and type(mb) in (int, float) and mb >= 0
        )
        blocked = any(assessments[v["variant_id"]].get("status") == "blocked"
                      for v in (a, b))
        if valid:
            # Signed B minus A, a factual difference in recorded median ms.
            # Never divide by zero, invent a percent, or label a faster model.
            difference = mb - ma
            status = "observed_difference_blocked" if blocked else "observed_difference_unverified"
        else:
            difference = None
            status = "insufficient_measurements"
        pairs.append({
            "variant_a_id": a["variant_id"],
            "variant_b_id": b["variant_id"],
            "median_a_ms": ma if valid else None,
            "median_b_ms": mb if valid else None,
            "median_b_minus_a_ms": difference,
            "measured_a": na if type(na) is int else 0,
            "measured_b": nb if type(nb) is int else 0,
            "status": status,
            "measured_comparability_verified": False,
            "hardware_equivalence_verified": False,
            "full_inference_verified": False,
        })
    return {
        "schema_version": 1,
        "run_id": summary["run_id"],
        "status": "descriptive_only",
        "pairs": pairs,
        "pair_count": len(pairs),
        "ranking_eligible": False,
        "best_variant": None,
        "speedup_claim_allowed": False,
        "database_modified": False,
        "generation_submitted": False,
        "limitations": (
            "Pairwise median differences describe only available recorded completed "
            "timings. They do not establish controlled comparisons or model superiority. "
            "Cached samplers, unknown inference provenance, seed, GPU, model, input and "
            "warmth conditions prevent a validated speed ranking."
        ),
    }
