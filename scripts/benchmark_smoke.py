"""Offline alpha.1 smoke test: no ComfyUI, models or GPU required.

From the repository root:
    python scripts/benchmark_smoke.py

This creates an isolated temporary SQLite DB, writes a sample benchmark and
prints its factual stored report. Sample values are synthetic fixtures, not
real performance measurements.
"""
from __future__ import annotations

import json
import tempfile
from pathlib import Path

from benchmark_store import BenchmarkStore


def main() -> None:
    with tempfile.TemporaryDirectory(prefix="orkilab-benchmark-smoke-") as workdir:
        with BenchmarkStore(Path(workdir) / "benchmark.sqlite3") as store:
            run_id = store.create_run(
                "offline-fixture-project",
                "Offline benchmark registry test",
                {"prompt": "fixture only", "seed": 42, "source": "test-fixture"},
            )
            variant_id = store.add_variant(
                run_id, "no-lora-fixture", {"model": "fixture", "lora_strength": 0.0}
            )
            store.transition(run_id, "running")
            store.record(run_id, variant_id, 0, "completed", seed=42,
                         duration_ms=100, peak_vram_bytes=None)
            store.transition(run_id, "completed")
            report = store.report(run_id)
            assert report["run"]["state"] == "completed"
            assert len(report["observations"]) == 1
            print(json.dumps(report, indent=2, ensure_ascii=False))
    print("PASS: offline benchmark registry smoke test (synthetic fixture, no GPU)")


if __name__ == "__main__":
    main()
