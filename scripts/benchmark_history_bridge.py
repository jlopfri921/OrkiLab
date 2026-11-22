"""B6 phase 1: explicit read-through of OrkiLab's existing generation history.

This adapter does not create a queue, submit or cancel ComfyUI work, or
change the GenerationHistory database. The future HTTP endpoint must check
launcher-local origin and project authorization before using this module.
"""
from __future__ import annotations

from typing import Any

from benchmark_generation_import import prepare_terminal_observation
from generation_history import GenerationHistory


def prepare_history_observation(history: GenerationHistory, generation_id: str) -> dict[str, Any]:
    if not isinstance(generation_id, str) or not 0 < len(generation_id) <= 200:
        raise ValueError("Invalid generation ID")
    row = history.get(generation_id)
    if row is None:
        raise KeyError("Generation history entry not found")
    return prepare_terminal_observation(row)
