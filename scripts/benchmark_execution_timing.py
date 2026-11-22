"""B8.1: measured prompt execution duration from ComfyUI history events.

Use only server-issued execution_start and execution_success event timestamps
for this exact prompt. Do not replace absent events with polling/wall time,
queue delay or estimates. No HTTP or side effects.
"""
from __future__ import annotations

import math
from typing import Any



def cache_evidence(entry: Any, prompt_id: str) -> dict:
    """Inspect cache events belonging only to this ComfyUI prompt.

    Cached node IDs are diagnostic evidence, not proof that other nodes ran.
    Missing cache events mean *unknown*, not confirmed cache-free.
    """
    result = {"execution_cached_event_observed": False,
              "cached_node_ids": [], "cache_status": "undetermined",
              "full_inference_verified": False}
    if not isinstance(entry, dict) or not isinstance(prompt_id, str) or not prompt_id:
        return result
    status = entry.get("status")
    messages = status.get("messages") if isinstance(status, dict) else None
    if not isinstance(messages, list) or len(messages) > 10000:
        return result
    nodes = set()
    for item in messages:
        if not isinstance(item, (list, tuple)) or len(item) != 2:
            continue
        kind, details = item
        if (kind != "execution_cached" or not isinstance(details, dict)
                or details.get("prompt_id") != prompt_id):
            continue
        result["execution_cached_event_observed"] = True
        values = details.get("nodes")
        if isinstance(values, list) and len(values) <= 10000:
            for node in values:
                if isinstance(node, (str, int)) and not isinstance(node, bool):
                    value = str(node)
                    if 0 < len(value) <= 200:
                        nodes.add(value)
    result["cached_node_ids"] = sorted(nodes)
    if result["execution_cached_event_observed"]:
        result["cache_status"] = "cache_event_observed"
    return result


def measured_execution_timing(entry: Any, prompt_id: str) -> dict | None:
    if not isinstance(entry, dict) or not isinstance(prompt_id, str) or not prompt_id:
        return None
    status = entry.get("status")
    if not isinstance(status, dict) or status.get("completed") is not True:
        return None
    messages = status.get("messages")
    if not isinstance(messages, list) or len(messages) > 10000:
        return None

    start = None
    end = None
    cache_observed = cache_evidence(entry, prompt_id)["execution_cached_event_observed"]
    for message in messages:
        if not isinstance(message, (list, tuple)) or len(message) != 2:
            continue
        kind, details = message
        if kind not in ("execution_start", "execution_success", "execution_cached"):
            continue
        if not isinstance(details, dict) or details.get("prompt_id") != prompt_id:
            continue
        if kind == "execution_cached":
            continue
        timestamp = details.get("timestamp")
        if (type(timestamp) not in (int, float)
                or not math.isfinite(timestamp)
                or not 1_000_000_000_000 <= timestamp <= 9_999_999_999_999):
            return None
        if kind == "execution_start":
            if start is not None:
                return None
            start = timestamp
        else:
            if end is not None:
                return None
            end = timestamp
    if start is None or end is None or end < start:
        return None
    duration = int(round(end - start))
    # Reject unreasonable durations and clock discontinuities instead of
    # silently claiming extreme measurements are meaningful.
    if duration < 0 or duration > 7 * 24 * 60 * 60 * 1000:
        return None
    return {
        "duration_ms": duration,
        "source": "comfyui_history_status_messages",
        "start_event": "execution_start",
        "end_event": "execution_success",
        "start_timestamp_ms": start,
        "end_timestamp_ms": end,
        "prompt_id": prompt_id,
        "includes_queue_wait": False,
        "execution_cached_event_observed": cache_observed,
        "full_inference_verified": False,
    }
