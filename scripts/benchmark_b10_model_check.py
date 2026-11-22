"""B10.2: preflight a *single* model selector in a saved API workflow.

ComfyUI node option lists are reported evidence of model availability,
not file-content attestation or proof the workflow will execute. Never write
to a workflow, run a job, download weights, or attribute GPU metrics.
"""
from __future__ import annotations

import copy
import json
from typing import Any

from workflow_conversion import combo_choices

_TARGETS = {
    "checkpoint": ("CheckpointLoaderSimple", "ckpt_name"),
    "lora": ("LoraLoader", "lora_name"),
}
_MAX_GRAPH_NODES = 2000


def inspect_model_variants(graph: Any, protocol: Any, variants: Any, schema: Any) -> dict:
    result = {
        "status": "not_established",
        "reason_codes": [],
        "target_node_count": 0,
        "variants": [],
        "graph_single_field_change_verified": False,
        "all_choices_advertised": False,
        "comfyui_node_options_observed": False,
        "file_bytes_verified": False,
        "models_loaded_verified": False,
        "workflow_execution_verified": False,
        "generation_submitted": False,
        "database_modified": False,
        "comparison_execution_authorized": False,
    }
    if isinstance(protocol, str):
        protocol = json.loads(protocol)
    if not isinstance(protocol, dict) or not isinstance(variants, list):
        raise ValueError("Invalid protocol or variants")
    variable = protocol.get("vary")
    if variable not in ("checkpoint", "lora"):
        result["reason_codes"].append("unsupported_controlled_variable")
        return result
    if not isinstance(graph, dict) or "nodes" in graph or not 0 < len(graph) <= _MAX_GRAPH_NODES:
        result["reason_codes"].append("api_workflow_required")
        return result
    if (not all(isinstance(k, str) and isinstance(v, dict)
                and isinstance(v.get("class_type"), str)
                and isinstance(v.get("inputs"), dict)
                for k, v in graph.items())):
        result["reason_codes"].append("invalid_api_graph")
        return result
    kinds = ("CheckpointLoaderSimple",) if variable == "checkpoint" else ("LoraLoader", "LoraLoaderModelOnly")
    field = "ckpt_name" if variable == "checkpoint" else "lora_name"
    candidates = [(node_id, node) for node_id, node in graph.items()
                  if node["class_type"] in kinds]
    result["target_node_count"] = len(candidates)
    if len(candidates) != 1:
        result["reason_codes"].append("exactly_one_model_loader_required")
        return result
    node_id, node = candidates[0]
    baseline = node["inputs"].get(field)
    if not isinstance(baseline, str):
        result["reason_codes"].append("model_selector_must_be_literal")
        return result
    if not isinstance(schema, dict) or not isinstance(schema.get("input"), dict):
        result["reason_codes"].append("node_options_unavailable")
        return result
    inputs = schema["input"]
    descriptor = inputs.get("required", {}).get(field) if isinstance(inputs.get("required"), dict) else None
    if descriptor is None and isinstance(inputs.get("optional"), dict):
        descriptor = inputs["optional"].get(field)
    choices = combo_choices(descriptor)
    if choices is None or not all(isinstance(x, str) for x in choices):
        result["reason_codes"].append("node_options_unavailable")
        return result
    result["comfyui_node_options_observed"] = True
    if not 2 <= len(variants) <= 20:
        result["reason_codes"].append("invalid_variant_count")
        return result
    declared = set()
    all_found = True
    for variant in variants:
        if not isinstance(variant, dict) or not isinstance(variant.get("id"), str):
            raise ValueError("Invalid variant")
        configuration = variant.get("config", variant.get("config_json", {}))
        if isinstance(configuration, str):
            configuration = json.loads(configuration)
        if not isinstance(configuration, dict):
            raise ValueError("Invalid variant configuration")
        name = configuration.get("controlled_value")
        valid_name = isinstance(name, str) and 0 < len(name) <= 200 and name not in declared
        advertised = valid_name and name in choices
        if valid_name:
            declared.add(name)
        if not advertised:
            all_found = False
        result["variants"].append({
            "variant_id": variant["id"],
            "model_choice_advertised": bool(advertised),
            "status": "advertised_option" if advertised else "not_found_in_advertised_options",
        })
    result["all_choices_advertised"] = all_found
    if not all_found:
        result["reason_codes"].append("model_not_in_comfyui_node_choices")
        return result

    # Build one isolated in-memory copy per variant and ensure the full graph
    # differs in exactly the intended scalar selector, not any other field.
    fixed = copy.deepcopy(graph)
    fixed[node_id]["inputs"].pop(field)
    for variant, info in zip(variants, result["variants"]):
        configuration = variant.get("config", variant.get("config_json", {}))
        if isinstance(configuration, str):
            configuration = json.loads(configuration)
        proposal = copy.deepcopy(graph)
        proposal[node_id]["inputs"][field] = configuration["controlled_value"]
        comparison = copy.deepcopy(proposal)
        value = comparison[node_id]["inputs"].pop(field)
        if comparison != fixed or value != configuration["controlled_value"]:
            result["reason_codes"].append("uncontrolled_graph_difference")
            return result
    result["graph_single_field_change_verified"] = True
    result["status"] = "static_candidate"
    # In particular, static_candidate must NEVER mean that models are loaded
    # or available as file bytes, or that a ComfyUI run can proceed.
    return result
