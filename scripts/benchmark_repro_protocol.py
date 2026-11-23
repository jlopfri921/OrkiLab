"""B9.4 opt-in reproducibility protocol contract and readiness inspection.

Reads existing run.protocol_json and variant.config_json; never changes legacy
records or implies that a declared protocol was actually followed at runtime.
Values are declarations, NOT verified execution provenance.
"""
from __future__ import annotations

import json
import re
from typing import Any

HEX64 = re.compile(r"^[0-9a-f]{64}$")
ALLOWED_VARIABLES = {"checkpoint", "lora"}
ALLOWED_CACHE = {"cold", "warm_sampler"}
ALLOWED_SEED = {"fixed", "enumerated"}


def _obj(raw: Any) -> dict:
    if isinstance(raw, str):
        raw = json.loads(raw)
    if not isinstance(raw, dict):
        raise ValueError("Protocol and variant configurations must be JSON objects")
    return raw


def declared_protocol_readiness(report: Any) -> dict:
    """Explain declaration completeness, not experimental comparability."""
    if not isinstance(report, dict) or not isinstance(report.get("run"), dict) or not isinstance(report.get("variants"), list):
        raise ValueError("Invalid benchmark report")
    run = report["run"]
    protocol = _obj(run.get("protocol", run.get("protocol_json", {})))
    variants = report["variants"]
    if protocol.get("schema") != "orkilab-repro-v1":
        return {"status": "legacy_unverified", "schema": None,
                "reason_codes": ["no_versioned_reproducibility_protocol"],
                "variants": [], "execution_verified": False,
                "ranking_eligible": False, "benchmark_database_modified": False}
    reasons = []
    def bad(name):
        reasons.append(name)
    variable = protocol.get("vary")
    if not isinstance(variable, str) or variable not in ALLOWED_VARIABLES:
        bad("invalid_controlled_variable")
    wf = protocol.get("workflow_id")
    if not isinstance(wf, str) or not 0 < len(wf) <= 200:
        bad("missing_workflow_id")
    for name in ("prompt_sha256", "negative_prompt_sha256", "input_sha256"):
        x = protocol.get(name)
        if not isinstance(x, str) or not HEX64.fullmatch(x):
            bad("missing_or_invalid_" + name)
    gpu = protocol.get("gpu_uuid")
    if not isinstance(gpu, str) or not gpu.startswith("GPU-") or len(gpu) > 128:
        bad("missing_gpu_identity")
    cache = protocol.get("cache")
    if not isinstance(cache, str) or cache not in ALLOWED_CACHE:
        bad("missing_cache_policy")
    seed = protocol.get("seed_policy")
    if not isinstance(seed, str) or seed not in ALLOWED_SEED:
        bad("missing_seed_policy")
    repetitions = protocol.get("repetitions")
    if type(repetitions) is not int or not 1 <= repetitions <= 100:
        bad("invalid_repetitions")
    resolution = protocol.get("resolution")
    if (not isinstance(resolution, list) or len(resolution) != 2
            or any(type(x) is not int or not 64 <= x <= 16384 for x in resolution)):
        bad("invalid_resolution")
    result = []
    selections = set()
    for v in variants:
        if not isinstance(v, dict) or not isinstance(v.get("id"), str):
            raise ValueError("Invalid variant")
        cfg = _obj(v.get("config", v.get("config_json", {})))
        value = cfg.get("controlled_value")
        errors = []
        if not isinstance(value, str) or not value.strip() or len(value) > 200:
            errors.append("missing_controlled_value")
        elif value in selections:
            errors.append("duplicate_controlled_value")
        else:
            selections.add(value)
        # An explicit full graph override defeats a one-variable declaration;
        # require independent graph inspection in a future protocol.
        if "graph_override" in cfg:
            errors.append("graph_override_requires_independent_review")
        if cfg.get("vary") is not None and cfg.get("vary") != variable:
            errors.append("variant_variable_mismatch")
        result.append({"variant_id": v["id"],
                       "status": "declared" if not errors else "incomplete",
                       "reason_codes": errors})
    if len(result) < 2:
        bad("at_least_two_variants_required")
    if any(v["status"] != "declared" for v in result):
        bad("variant_declarations_incomplete")
    return {"schema": "orkilab-repro-v1",
            "status": "declared_unverified" if not reasons else "incomplete",
            "reason_codes": sorted(set(reasons)), "variants": result,
            "controlled_variable": variable if isinstance(variable, str) and variable in ALLOWED_VARIABLES else None,
            "execution_verified": False, "ranking_eligible": False,
            "benchmark_database_modified": False,
            "limitations": ("Declarations are not execution evidence: ComfyUI "
                            "history, cache behaviour, model identity and GPU "
                            "conditions must be independently verified.")}
