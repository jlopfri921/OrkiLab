"""B8.2a — read-only NVIDIA GPU memory inventory, NOT per-job telemetry.

Uses nvidia-smi once with a hard timeout. Reports device-wide memory already
allocated, which may include ComfyUI cache and other programs. No benchmark
observation is modified, and no peak_vram_bytes is attributed to a job.
"""
from __future__ import annotations

import argparse
import csv
import io
import json
import subprocess
from typing import Any

FIELDS = ("index", "uuid", "name", "memory.total", "memory.used", "memory.free")
COMMAND = (
    "nvidia-smi", "--query-gpu=" + ",".join(FIELDS),
    "--format=csv,noheader,nounits",
)


def parse_gpu_memory_csv(output: str) -> list[dict[str, Any]]:
    if not isinstance(output, str) or len(output) > 65536:
        raise ValueError("Unexpected NVIDIA device inventory")
    devices = []
    for record in csv.reader(io.StringIO(output)):
        if not record or not any(part.strip() for part in record):
            continue
        if len(record) != len(FIELDS) or len(devices) >= 16:
            raise ValueError("Invalid GPU inventory column count")
        index_raw, uuid, name, total_raw, used_raw, free_raw = [p.strip() for p in record]
        if not (index_raw.isdecimal() and total_raw.isdecimal()
                and used_raw.isdecimal() and free_raw.isdecimal()):
            raise ValueError("GPU memory inventory contains non-numeric quantities")
        index, total, used, free = map(int, (index_raw, total_raw, used_raw, free_raw))
        if (total <= 0 or used > total or free > total or used + free > total + 1
                or not uuid or len(uuid) > 128 or not name or len(name) > 160):
            raise ValueError("GPU device values out of range")
        devices.append({
            "index": index, "uuid": uuid, "name": name,
            "total_bytes": total * 1024 * 1024,
            "used_bytes": used * 1024 * 1024,
            "free_bytes": free * 1024 * 1024,
        })
    if not devices or len({d["index"] for d in devices}) != len(devices):
        raise ValueError("No unique NVIDIA GPU devices found")
    return devices


def sample_devices(*, runner=subprocess.run) -> dict[str, Any]:
    try:
        process = runner(
            list(COMMAND), capture_output=True, text=True, timeout=5, check=False
        )
        if process.returncode != 0:
            return {"ok": False, "reason": "nvidia-smi did not complete successfully"}
        return {
            "ok": True, "devices": parse_gpu_memory_csv(process.stdout),
            "scope": "device_global_snapshot",
            "unit": "bytes",
            "attributable_to_generation": False,
            "peak_vram_bytes": None,
            "benchmark_database_modified": False,
            "limitations": (
                "Single global GPU memory snapshot only. Includes other processes "
                "and cached allocations; not a per-job peak or GPU delta."
            ),
        }
    except (OSError, subprocess.TimeoutExpired, ValueError, TypeError) as exc:
        return {
            "ok": False,
            "reason": "Could not obtain valid NVIDIA GPU memory inventory",
            "detail": str(exc)[:200],
        }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.parse_args()
    result = sample_devices()
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
