"""B8.2d read-only Windows TCP port ownership vs NVIDIA GPU process IDs.

Does NOT establish job-level memory attribution, exact ComfyUI server
identity, or GPU isolation. Never exposes process command lines/secrets.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys

from benchmark_gpu_process_probe import discover

_PS = (
    "$ErrorActionPreference='Stop';"
    "$rows=@(Get-NetTCPConnection -LocalPort 8188 -State Listen -ErrorAction Stop);"
    "$items=@(foreach($r in $rows){"
    "$p=Get-CimInstance Win32_Process -Filter ('ProcessId='+[int]$r.OwningProcess) -ErrorAction Stop;"
    "[pscustomobject]@{pid=[int]$r.OwningProcess;executable=[string]$p.ExecutablePath;"
    "process_name=[string]$p.Name;local_address=[string]$r.LocalAddress}});"
    "ConvertTo-Json -InputObject $items -Compress -Depth 4"
)


def assess(port_entries: object, gpu_inventory: object) -> dict:
    if not isinstance(port_entries, list) or not isinstance(gpu_inventory, dict):
        raise ValueError("Expected Windows listener array and NVIDIA inventory")
    processes = gpu_inventory.get("processes")
    if not isinstance(processes, list):
        raise ValueError("Missing NVIDIA process inventory")
    result = []
    seen = set()
    for item in port_entries:
        if not isinstance(item, dict):
            raise ValueError("Malformed TCP listener")
        pid, executable, address = (
            item.get("pid"), item.get("executable"), item.get("local_address")
        )
        if (type(pid) is not int or pid <= 0 or pid > 2**32
                or not isinstance(executable, str) or len(executable) > 1024
                or not isinstance(address, str) or len(address) > 128):
            raise ValueError("Invalid listener identity")
        key = (pid, address)
        if key in seen:
            continue
        seen.add(key)
        hits = [p for p in processes if isinstance(p, dict) and p.get("pid") == pid]
        result.append({
            "pid": pid,
            "executable": executable,
            "local_address": address,
            "listed_by_nvidia": bool(hits),
            "gpu_uuids": sorted({p["gpu_uuid"] for p in hits
                                 if isinstance(p.get("gpu_uuid"), str)}),
        })
    return {
        "ok": True, "tcp_port": 8188, "listeners": result,
        "process_isolation_verified": False,
        "comfyui_process_verified": False,
        "attributable_to_generation": False,
        "peak_vram_bytes": None,
        "benchmark_database_modified": False,
        "limitations": (
            "Port ownership is only process correlation, not proof of ComfyUI "
            "ownership or per-job VRAM. Listening port may be a bridge/proxy; "
            "other NVIDIA processes may coexist; WDDM memory can be unavailable."
        ),
    }


def probe(*, runner=subprocess.run, discover_gpu=discover) -> dict:
    if sys.platform != "win32":
        return {"ok": False, "reason": "Windows Get-NetTCPConnection required"}
    try:
        proc = runner(["powershell.exe", "-NoProfile", "-NonInteractive",
                       "-Command", _PS], text=True, capture_output=True,
                      check=False, timeout=8)
        if proc.returncode != 0:
            return {"ok": False, "reason": "Unable to verify TCP listener",
                    "detail": (proc.stderr or "")[:200]}
        if len(proc.stdout) > 65536:
            raise ValueError("Unexpectedly large Windows process list")
        listeners = json.loads(proc.stdout)
        if isinstance(listeners, dict):
            listeners = [listeners]
        gpu = discover_gpu()
        if gpu.get("ok") is not True:
            return {"ok": False, "reason": "NVIDIA GPU process inventory unavailable"}
        return assess(listeners, gpu)
    except (OSError, subprocess.TimeoutExpired, ValueError, TypeError, KeyError) as exc:
        return {"ok": False, "reason": "Could not correlate GPU/TCP processes",
                "detail": str(exc)[:200]}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.parse_args()
    result = probe()
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
