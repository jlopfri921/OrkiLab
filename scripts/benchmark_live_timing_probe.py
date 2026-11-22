"""B8.1 read-only live ComfyUI timing probe for a known Generation Studio ID.

No queue mutation, benchmark writes, inference or output downloading. Reports
server event measurements only; missing events remain explicitly unknown.
"""
from __future__ import annotations

import argparse
import json
import sqlite3
from contextlib import closing
from pathlib import Path

from benchmark_execution_timing import measured_execution_timing
from comfyui_connect import DEFAULT_SETTINGS, get_json, validate_settings


def inspect(base: Path, generation_id: str, *, fetch=get_json) -> dict:
    if not isinstance(generation_id, str) or not 0 < len(generation_id) <= 200:
        return {"ok": False, "reason": "Invalid generation ID"}
    folder = Path(base) / "settings" / "orkilab"
    history_file = folder / "generations.sqlite3"
    config_file = folder / "comfyui.json"
    if not history_file.is_file() or not config_file.is_file():
        return {"ok": False, "reason": "Local generation history or ComfyUI configuration missing"}
    try:
        with closing(sqlite3.connect(history_file.resolve().as_uri() + "?mode=ro", uri=True)) as con:
            row = con.execute(
                "SELECT prompt_id,state,url FROM generations WHERE id=?",
                (generation_id,),
            ).fetchone()
        if row is None:
            return {"ok": False, "reason": "Generation not found"}
        prompt_id, state, recorded_url = row
        if state != "completed":
            return {"ok": False, "reason": "Generation is not completed", "state": state}
        cfg = validate_settings(json.loads(config_file.read_text(encoding="utf-8")), DEFAULT_SETTINGS)
        if cfg["mode"] == "native" or recorded_url != cfg["url"]:
            return {"ok": False, "reason": "Recorded ComfyUI endpoint does not match current configuration"}
        # GET is read-only. No ComfyUI work is submitted or cancelled.
        history = fetch(cfg["url"], "/history/" + prompt_id, timeout=10, max_bytes=16_000_000)
        entry = history.get(prompt_id) if isinstance(history, dict) else None
        timing = measured_execution_timing(entry, prompt_id)
        # History events do not necessarily expose node execution or cache
        # reuse. Report only observed evidence; never label a tiny duration
        # as a valid *full inference* benchmark without that evidence.
        messages = (entry.get("status", {}).get("messages")
                    if isinstance(entry, dict)
                    and isinstance(entry.get("status"), dict) else None)
        event_names = [
            item[0] for item in messages
            if isinstance(item, (list, tuple)) and len(item) == 2
            and isinstance(item[0], str)
        ] if isinstance(messages, list) else []
        cache_event_observed = "execution_cached" in event_names
        result = {
            "ok": True,
            "generation_id": generation_id,
            "prompt_id": prompt_id,
            "state": state,
            "measured": timing is not None,
            "duration_ms": timing["duration_ms"] if timing else None,
            "duration_seconds": timing["duration_ms"] / 1000 if timing else None,
            "source": timing["source"] if timing else None,
            "queue_time_included": False if timing else None,
            "benchmark_database_modified": False,
            "execution_cached_event_observed": cache_event_observed,
            "cache_status": "cache_event_observed" if cache_event_observed else "undetermined",
            "full_inference_verified": False,
            "interpretation": (
                "Measured server event interval only; does not establish full "
                "image inference or absence of cached node outputs."
            ),
        }
        if timing is None:
            result["reason"] = "ComfyUI history has no valid paired execution timestamps for this prompt"
        return result
    except (OSError, ValueError, TypeError, KeyError, sqlite3.Error) as exc:
        return {"ok": False, "reason": "Could not inspect ComfyUI history",
                "detail": str(exc)[:200]}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--generation-id", required=True)
    args = parser.parse_args()
    result = inspect(Path(__file__).resolve().parents[1], args.generation_id)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
