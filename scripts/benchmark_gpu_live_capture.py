"""B8.2g — opt-in read-only VRAM observation while an EXISTING ComfyUI job runs.

No POST/submit/cancel, no SQLite writes and no process VRAM attribution.
Run from a separate terminal immediately after an explicit Generation Studio
submission. This script only monitors the identified job and exits on terminal
history or an explicit bounded timeout. Epoch samples share the localhost
ComfyUI host clock; the nvidia-smi subprocess reading gets midpoint timing.
"""
from __future__ import annotations

import argparse
import json
import math
import sqlite3
import time
from contextlib import closing
from pathlib import Path

from benchmark_gpu_generation_window import analyze_generation_window
from benchmark_gpu_memory_probe import sample_devices
from comfyui_connect import DEFAULT_SETTINGS, get_json, validate_settings


def _target(base: Path, generation_id: str) -> tuple[str, str]:
    if not isinstance(generation_id, str) or not 0 < len(generation_id) <= 200:
        raise ValueError("Invalid generation ID")
    folder = Path(base) / "settings" / "orkilab"
    db = folder / "generations.sqlite3"
    if not db.is_file():
        raise ValueError("Generation history is unavailable")
    with closing(sqlite3.connect(db.resolve().as_uri() + "?mode=ro", uri=True)) as con:
        row = con.execute(
            "SELECT prompt_id,state,url FROM generations WHERE id=?",
            (generation_id,),
        ).fetchone()
    if row is None:
        raise ValueError("Generation ID not found")
    prompt_id, state, recorded_url = row
    if state not in ("queued", "running"):
        raise ValueError("Monitor must begin while generation is queued or running")
    cfg = validate_settings(json.loads(
        (folder / "comfyui.json").read_text(encoding="utf-8")
    ), DEFAULT_SETTINGS)
    if cfg["mode"] == "native" or cfg["url"] != "http://127.0.0.1:8188":
        raise ValueError("Monitoring requires the configured localhost ComfyUI")
    if recorded_url != cfg["url"]:
        raise ValueError("Generation URL does not match configured ComfyUI")
    if not isinstance(prompt_id, str) or not 0 < len(prompt_id) <= 100:
        raise ValueError("Invalid prompt ID")
    return cfg["url"], prompt_id


def observe(
    base: Path, generation_id: str, *, gpu_uuid: str,
    samples_limit: int = 120, interval_seconds: float = 0.3,
    fetch=get_json, memory_sample=sample_devices,
    epoch_clock=time.time, clock=time.monotonic, sleep=time.sleep,
) -> dict:
    """Samples the GLOBAL GPU while reading existing prompt history.

    No persistence: output is returned to operator only. The first valid
    completed history is used for window analysis. If missed, return a
    bounded diagnostic with no inferred execution window/peak.
    """
    if type(samples_limit) is not int or not 2 <= samples_limit <= 120:
        raise ValueError("Sample limit must be between 2 and 120")
    if (type(interval_seconds) not in (float, int)
            or not math.isfinite(interval_seconds)
            or not 0.2 <= interval_seconds <= 5.0):
        raise ValueError("Interval must be between 0.2 and 5 seconds")
    if not isinstance(gpu_uuid, str) or not 0 < len(gpu_uuid) <= 128:
        raise ValueError("GPU UUID is required")
    url, prompt_id = _target(base, generation_id)
    snapshots = []
    entry = None
    saw_running = False
    end_reason = "sample_limit"
    for i in range(samples_limit):
        if i:
            sleep(interval_seconds)
        # GET only; no launcher status endpoint and no DB updates.
        history = fetch(url, "/history/" + prompt_id,
                        timeout=5, max_bytes=16_000_000)
        entry = history.get(prompt_id) if isinstance(history, dict) else None
        if isinstance(entry, dict):
            status = entry.get("status")
            if isinstance(status, dict):
                if status.get("completed") is True:
                    end_reason = "completed_history"
                    break
                if status.get("status_str") == "error":
                    end_reason = "error_history"
                    break
        queue = fetch(url, "/queue", timeout=5)
        if not isinstance(queue, dict) or any(
            not isinstance(queue.get(key), list)
            for key in ("queue_running", "queue_pending")
        ):
            raise ValueError("Cannot verify ComfyUI queue")
        # Seeing anything running is not sufficient to associate other work
        # with this job. This flag is diagnostic and not proof of exclusivity.
        saw_running = saw_running or bool(queue["queue_running"])
        t0 = epoch_clock()
        snapshot = memory_sample()
        t1 = epoch_clock()
        if not isinstance(snapshot, dict) or snapshot.get("ok") is not True:
            raise ValueError("GPU sampling failed; partial series discarded")
        devices = snapshot.get("devices")
        selected = [d for d in devices if isinstance(d, dict)
                    and d.get("uuid") == gpu_uuid] if isinstance(devices, list) else []
        if len(selected) != 1:
            raise ValueError("Expected exactly one matching GPU UUID")
        device = selected[0]
        if not all(type(device.get(key)) is int
                   for key in ("used_bytes", "total_bytes")):
            raise ValueError("Invalid GPU memory snapshot")
        snapshots.append({
            "epoch_ms": (t0 + t1) * 500,
            "gpu_uuid": gpu_uuid,
            "used_bytes": device["used_bytes"],
            "total_bytes": device["total_bytes"],
        })
    if not snapshots:
        return {
            "ok": True, "generation_id": generation_id,
            "prompt_id": prompt_id, "termination": end_reason,
            "sample_count": 0, "window_supported_by_server_events": False,
            "peak_vram_bytes": None, "attributable_to_generation": False,
            "benchmark_database_modified": False,
            "reason": "Execution finished before the first GPU sample",
        }
    analysis = analyze_generation_window(
        entry, prompt_id, snapshots, gpu_uuid=gpu_uuid,
        max_sampling_gap_ms=int(interval_seconds * 1000) + 1000,
        concurrent_gpu_activity_observed=None,
    )
    return {
        **analysis, "generation_id": generation_id,
        "termination": end_reason, "sample_count_total": len(snapshots),
        "queue_running_observed": saw_running,
        "sampling_ended_before_confirmed_terminal": end_reason == "sample_limit",
        "notes": (
            "Read-only global GPU observations within a previously submitted "
            "job window; does not establish process-exclusive VRAM usage."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--generation-id", required=True)
    parser.add_argument("--gpu-uuid", required=True)
    parser.add_argument("--samples", type=int, default=120)
    parser.add_argument("--interval", type=float, default=0.3)
    args = parser.parse_args()
    try:
        result = observe(
            Path(__file__).resolve().parents[1], args.generation_id,
            gpu_uuid=args.gpu_uuid, samples_limit=args.samples,
            interval_seconds=args.interval,
        )
    except (OSError, ValueError, TypeError, sqlite3.Error) as exc:
        result = {"ok": False, "reason": str(exc)[:200],
                  "peak_vram_bytes": None, "attributable_to_generation": False,
                  "benchmark_database_modified": False}
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
