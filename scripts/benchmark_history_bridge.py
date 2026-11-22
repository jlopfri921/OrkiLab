"""B6 phase 1: explicit read-through of OrkiLab's existing generation history.

This adapter does not create a queue, submit or cancel ComfyUI work, or
change the GenerationHistory database. The future HTTP endpoint must check
launcher-local origin and project authorization before using this module.
"""
from __future__ import annotations

from typing import Any

from benchmark_generation_import import prepare_terminal_observation, persist_terminal_observation
from benchmark_store import BenchmarkStore
from generation_history import GenerationHistory


def prepare_history_observation(history: GenerationHistory, generation_id: str) -> dict[str, Any]:
    if not isinstance(generation_id, str) or not 0 < len(generation_id) <= 200:
        raise ValueError("Invalid generation ID")
    row = history.get(generation_id)
    if row is None:
        raise KeyError("Generation history entry not found")
    return prepare_terminal_observation(row)


def attach_history_generation(
    history: GenerationHistory,
    store: BenchmarkStore,
    *,
    project_id: str,
    run_id: str,
    variant_id: str,
    repetition: int,
    generation_id: str,
    confirmed: bool = False,
) -> str:
    """Explicit user-selected association, never project inference from history.

    Project ownership is checked by the underlying store import method. Caller
    must check launcher-local access, trust and project authorization before
    invoking this non-HTTP helper. ComfyUI is never called or interrupted.
    """
    if confirmed is not True:
        raise PermissionError("Explicit association confirmation is required")
    if not isinstance(generation_id, str) or not 0 < len(generation_id) <= 200:
        raise ValueError("Invalid generation ID")
    record = history.get(generation_id)
    if record is None:
        raise KeyError("Generation history entry not found")
    return persist_terminal_observation(
        store, run_id, variant_id, repetition, record,
        authorized_project_id=project_id, confirmed=True,
    )
