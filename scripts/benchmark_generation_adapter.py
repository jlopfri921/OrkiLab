"""Read-only adapter between completed ComfyUI generation history and Benchmark.

No ComfyUI calls, mutations, queue control, inferred GPU measurements, or
automatic job submissions occur here. The caller must authenticate and scope
the generation record before passing it to this function.
"""
from __future__ import annotations

import hashlib
import json
from typing import Any

_TERMINAL = {"completed": "completed", "error": "failed", "cancelled": "cancelled"}

def _load_json(raw: Any, expected: type) -> Any:
    if isinstance(raw, str):
        value = json.loads(raw)
    else:
        value = raw
    if not isinstance(value, expected):
        raise ValueError("Unexpected generation record JSON shape")
    return value

def snapshot_generation(record: dict[str, Any]) -> dict[str, Any]:
    """Return factual, bounded metadata for one terminal generation record.

    Results intentionally leave hardware performance, seed and output hashes
    unknown because the current history schema does not guarantee them.
    """
    if not isinstance(record, dict):
        raise ValueError("Generation record must be an object")
    status = _TERMINAL.get(record.get("state"))
    if not status:
        raise ValueError("Generation must be in a terminal state")
    token = record.get("id")
    workflow_id = record.get("workflow_id")
    prompt_id = record.get("prompt_id")
    if not all(isinstance(v, str) and 0 < len(v) <= 200 for v in (token, workflow_id, prompt_id)):
        raise ValueError("Invalid generation identifiers")
    graph = _load_json(record.get("graph"), dict)
    outputs = _load_json(record.get("outputs"), list)
    if len(outputs) > 100:
        raise ValueError("Generation outputs exceed the supported snapshot limit")
    # The hash represents the *submitted API graph*, not original model file bytes.
    packed = json.dumps(graph, sort_keys=True, ensure_ascii=False,
                        separators=(",", ":"), allow_nan=False).encode("utf-8")
    return {
        "generation_id": token,
        "comfyui_prompt_id": prompt_id,
        "workflow_id": workflow_id,
        "status": status,
        "submitted_graph_sha256": hashlib.sha256(packed).hexdigest(),
        "output_count": len(outputs),
        "duration_ms": None,
        "peak_vram_bytes": None,
        "seed": None,
        "output_sha256": None,
        "limitations": "Read-only history snapshot. No per-job GPU/time metrics or output file hashes are inferred.",
    }
