"""B8.2c — read-only NVIDIA compute process discovery (not job attribution).

Windows WDDM drivers may return N/A for per-process memory. This is recorded
as unavailable, never converted to zero. Empty/unsupported results cannot
prove ComfyUI GPU isolation or a GPU process's absence.
"""
from __future__ import annotations

import csv
import io
import json
import subprocess
from typing import Any

COMMAND = ("nvidia-smi", "--query-compute-apps=pid,process_name,gpu_uuid,used_gpu_memory",
           "--format=csv,noheader,nounits")


def parse_compute_processes(output: str) -> list[dict[str, Any]]:
    if not isinstance(output, str) or len(output) > 65536:
        raise ValueError("Invalid process inventory size")
    result = []
    for parts in csv.reader(io.StringIO(output)):
        if not parts or not any(x.strip() for x in parts):
            continue
        if len(result) >= 256 or len(parts) != 4:
            raise ValueError("Unexpected process inventory fields")
        pid_text, name, uuid, usage = [x.strip() for x in parts]
        if (not pid_text.isdecimal() or int(pid_text) <= 0 or int(pid_text) > 2**32
                or not 0 < len(name) <= 512 or not 0 < len(uuid) <= 128):
            raise ValueError("Invalid compute process identity")
        if usage in ("N/A", "[N/A]", "Not Supported", ""):
            used_bytes = None
        elif usage.isdecimal():
            used_bytes = int(usage) * 1024 * 1024
        else:
            raise ValueError("Invalid per-process memory field")
        result.append({
            "pid": int(pid_text), "process_name": name, "gpu_uuid": uuid,
            "used_gpu_memory_bytes": used_bytes,
            "memory_reading_available": used_bytes is not None,
        })
    return result


def discover(*, runner=subprocess.run) -> dict:
    try:
        proc = runner(list(COMMAND), capture_output=True, text=True,
                      timeout=5, check=False)
        if proc.returncode != 0:
            return {
                "ok": False, "availability": "unsupported_or_error",
                "processes": [], "process_isolation_verified": False,
                "attributable_to_generation": False, "peak_vram_bytes": None,
                "benchmark_database_modified": False,
                "reason": "Compute process query unavailable on this driver",
            }
        processes = parse_compute_processes(proc.stdout)
        return {
            "ok": True, "availability": "reported",
            "processes": processes,
            "process_count": len(processes),
            "memory_values_available_for_all_reported_processes": bool(processes)
                and all(p["memory_reading_available"] for p in processes),
            "process_isolation_verified": False,
            "attributable_to_generation": False,
            "peak_vram_bytes": None,
            "benchmark_database_modified": False,
            "limitations": (
                "Compute-process listing is not a complete inventory of all "
                "GPU users, especially under Windows WDDM. PID without verified "
                "process ownership cannot identify ComfyUI or a specific job; "
                "N/A GPU memory is unknown, not zero."
            ),
        }
    except (OSError, subprocess.TimeoutExpired, ValueError, TypeError) as exc:
        return {
            "ok": False, "availability": "unsupported_or_error",
            "processes": [], "process_isolation_verified": False,
            "attributable_to_generation": False, "peak_vram_bytes": None,
            "benchmark_database_modified": False,
            "reason": "Could not obtain reliable compute process inventory",
            "detail": str(exc)[:200],
        }


def main() -> int:
    result = discover()
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
