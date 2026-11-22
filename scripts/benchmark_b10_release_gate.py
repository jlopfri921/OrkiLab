"""B10.5 conservative 0.6 candidate-readiness report.

Read-only snapshot of technical diagnostics. A successful unit-test suite,
declared protocol or saved history MUST NOT automatically authorize a release.
Manual Windows/Linux, real GPU, backup, security and maintainer signoff remain
outside the scope of local benchmark observation.
"""
from __future__ import annotations

from typing import Any

RELEASE_CHECKS = (
    ("benchmark_safety", "automated", "review_required"),
    ("windows_regression", "operator", "pending"),
    ("linux_ci", "ci", "pending"),
    ("comfyui_real_gpu", "operator", "pending"),
    ("run_scope_and_privacy", "review", "pending"),
    ("non_destructive_storage", "review", "pending"),
    ("other_modules_regression", "operator", "pending"),
    ("multilingual_mobile", "operator", "pending"),
    ("release_docs_and_version", "review", "pending"),
    ("explicit_release_authorization", "maintainer", "pending"),
)


def summarize_b10_release_readiness(report: Any) -> dict:
    if not isinstance(report, dict):
        raise ValueError("Invalid Benchmark release report")
    closure, preflight, results = (report.get("b9_closure"),
                                   report.get("b10_comparison_preflight"),
                                   report.get("b10_results"))
    if (not isinstance(closure, dict) or not isinstance(preflight, dict)
            or not isinstance(results, dict)
            or not isinstance(closure.get("checks"), list)
            or not isinstance(preflight.get("gates"), list)
            or not isinstance(results.get("pairs"), list)):
        raise ValueError("Missing required Benchmark diagnostic sections")
    contradictions = (
        closure.get("status") == "contradiction_detected"
        or results.get("ranking_eligible") is True
        or results.get("best_variant") is not None
        or results.get("speedup_claim_allowed") is True
        or preflight.get("comparison_execution_authorized") is True
    )
    if contradictions:
        diagnostic_status = "review_blocked"
    else:
        diagnostic_status = "diagnostics_present_unverified"
    checks = [
        {"code": code, "evidence_type": kind, "status": status}
        for code, kind, status in RELEASE_CHECKS
    ]
    if contradictions:
        checks[0] = {**checks[0], "status": "blocked"}
    return {
        "schema_version": 1,
        "status": "not_ready",
        "diagnostic_status": diagnostic_status,
        "checks": checks,
        "release_authorized": False,
        "candidate_tag_authorized": False,
        "merge_authorized": False,
        "ranking_eligible": False,
        "full_inference_verified": False,
        "best_variant": None,
        "generation_submitted": False,
        "database_modified": False,
        "limitations": (
            "This per-run report cannot establish release readiness. The release "
            "requires independent Windows/Linux CI, full-app regression, real "
            "ComfyUI/GPU and operator review, verified privacy/storage, documentation "
            "and explicit maintainer approval. No automated tagging or merge."
        ),
    }
