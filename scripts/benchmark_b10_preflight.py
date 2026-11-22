"""B10.1 offline, read-only comparison plan preflight.

This is a checklist of declarations and controlled variable candidates, NOT
an execution authorization, model compatibility proof, or engine preflight.
"""
from __future__ import annotations

from typing import Any

from benchmark_repro_protocol import declared_protocol_readiness


def inspect_comparison_plan(report: Any) -> dict:
    if (not isinstance(report, dict) or not isinstance(report.get("run"), dict)
            or not isinstance(report.get("variants"), list)):
        raise ValueError("Invalid comparison plan")
    protocol_check = declared_protocol_readiness(report)
    variants = report["variants"]
    complete = protocol_check["status"] == "declared_unverified"
    reason_codes = list(protocol_check["reason_codes"])
    variable = protocol_check.get("controlled_variable")
    if variable not in ("checkpoint", "lora"):
        reason_codes.append("comparison_variable_unknown")
    # The variant declaration must never be interpreted as confirmation that
    # the checkpoint or LoRA actually exists in ComfyUI.
    if complete and len(variants) >= 2:
        declaration_status = "declared_only"
    else:
        declaration_status = "incomplete"
    return {
        "schema_version": 1,
        "declaration_status": declaration_status,
        "controlled_variable": variable,
        "variant_count": len(variants),
        "reason_codes": sorted(set(reason_codes)),
        "gates": [
            {"code": "protocol_fields", "status": "declared_only" if complete else "pending"},
            {"code": "variants_unique", "status": "declared_only" if complete else "pending"},
            {"code": "selected_models_exist", "status": "pending"},
            {"code": "one_variable_only", "status": "pending"},
            {"code": "prompt_and_input_match", "status": "pending"},
            {"code": "seed_and_resolution_match", "status": "pending"},
            {"code": "comfyui_idle_and_compatible", "status": "pending"},
            {"code": "gpu_and_cache_equivalence", "status": "pending"},
        ],
        "comparison_execution_authorized": False,
        "generation_submitted": False,
        "ranking_eligible": False,
        "best_variant": None,
        "database_modified": False,
        "limitations": ("This offline declaration check never verifies graph transformations, "
                        "checkpoint/LoRA availability, GPU state, seeds, cache, live ComfyUI readiness "
                        "or experimental comparability."),
    }
