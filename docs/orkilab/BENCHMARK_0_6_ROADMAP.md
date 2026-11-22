# OrkiLab 0.6.0 — Benchmark Studio delivery plan

**Status:** alpha.1 first isolated persistence slice on feature branch; **not released or integrated into Workspace**. The documented 0.5.0 stable acceptance gates remain independent and must be completed before claiming a stable 0.6.0.

## Goal and boundaries

Benchmark a model/LoRA combination with reproducible prompt, seeds, workflow, weights and recorded observations; distinguish raw measurements from qualitative judgments. A useful benchmark must preserve the precise execution protocol and make clear when model-family parameters cannot be compared directly. Baseline: [OrkiLab roadmap](ROADMAP.md).

## Alpha.1 — isolated engine foundation

- `scripts/benchmark_store.py`: local SQLite registry for project-linked benchmark runs, variants and immutable observations.
- One canonical JSON representation per protocol and variant configuration. Inputs record model/workflow details **only when supplied by a caller**.
- Explicit lifecycle: draft → running → completed/failed/cancelled, or draft → cancelled. A run must have a variant to start.
- Each variant/repetition pair records at most one completed, cancelled or failed observation. Seed, duration (milliseconds), peak GPU VRAM (bytes), SHA-256 of output and error text are optional, never invented.
- Reports expose raw stored observations as JSON-like dictionaries. SQLite foreign keys prevent attaching observations to another run.
- No checkpoint/LoRA/source image deletion or mutation. No model download, GPU scheduling, ComfyUI submission, implicit resumption, benchmark scoring, API route or UI is provided by this slice.
- This store is **not a web endpoint**: authorization, project ownership, local-only restrictions and input-size limits must be enforced in the later HTTP integration.

### Acceptance tests

Run `python -m unittest discover -s tests -p 'test_benchmark_store.py'` and `python scripts/benchmark_smoke.py` from repository root. The smoke runner uses synthetic fixture measurements and **does not run ComfyUI or benchmark a real GPU**. Tests cover persisted reopening, lifecycle rules, project/run isolation, unique repetitions and validation of numeric/hash inputs. CI and actual Windows/Linux results must be recorded before describing alpha.1 as validated.

## 2026-11-22 — Operator-reported Windows / Python 3.13 acceptance

**Environment:** Windows PowerShell, Python 3.13, local checkout `D:\\orkilab\\orkilab-lora-trainerstudio`, branch `feat/0.6-benchmark-core`.

| ID | Command / assertion | Reported result | Evidence boundary |
| --- | --- | --- | --- |
| B1 | `python scripts/benchmark_smoke.py` | **PASS**, one completed synthetic run with a variant and observation | Fixture duration 100 ms, VRAM and image hash `null`; no GPU or ComfyUI |
| B2.1 | Lifecycle / immutable completed runs | **PASS** | Python unittest on Windows |
| B2.2 | Persistence and report after SQLite reopen | **PASS** | Python unittest on Windows |
| B2.3 | Reject invalid inputs | **PASS** | Python unittest on Windows |
| B2.4 | Reject cross-run observations and duplicate repetitions | **PASS** | Python unittest on Windows |

The operator reported `Ran 4 tests in 0.108s — OK` for `python -m unittest discover -s tests -p "test_benchmark_store.py" -v`. These are **five checks across two commands**, not five independent test suites, and are not evidence of CI or real RTX 3090 inference.

**Still required before merging or claiming alpha.1 complete:** review state and schema boundaries, CI on the PR head for Windows/Linux, database migration strategy, safe authorization for any exposed API, and representative ComfyUI adapter/GPU acceptance. The source still implements an isolated persistence store, not an integrated benchmark feature.

## Next incremental slice — read-only ComfyUI history adapter (operator validation pending)

- `scripts/benchmark_generation_adapter.py` provides `snapshot_generation(record)` for a **terminal** entry returned by the existing `GenerationHistory.get()` record schema.
- It produces a stable SHA-256 fingerprint of the final submitted API graph and preserves the generation ID, ComfyUI prompt ID, workflow ID, terminal status and output descriptor count.
- Deliberately leaves duration, VRAM, effective seed and output-file SHA-256 as `null` because the existing history does not certify those measurements. This fingerprint is **not** the hash of model weights.
- Rejects running jobs, malformed graph/output JSON and unsupported record shapes.
- This is a **pure read-only adapter**, not a live ComfyUI queue attachment, API route, automatic job tracker or permission boundary. An eventual API caller must validate project ownership and authorized local access.
- Test with `python -m unittest discover -s tests -p "test_benchmark_generation_adapter.py" -v` on the alpha.1 feature branch. Results have **not yet been reported**.

## 2026-11-22 — B4 reported PASS; B5 implementation pending operator tests

**B4 — operator-reported Windows / Python 3.13:** `python -m unittest discover -s tests -p "test_benchmark_generation_import.py" -v` returned **3 tests, OK** (read-only lineage proposal, running job rejection, terminal failure mapping). This brings the operator-reported local checks to **12 total** (B1 + B2×4 + B3×4 + B4×3). No GPU benchmark has yet been run.

**B5 — atomic lineage implementation on this feature branch (not yet validated):**

- Existing SQLite store now creates `benchmark_generation_lineage` with each linked observation, storing the generation ID, graph fingerprint and factual source snapshot JSON.
- Observation and lineage are inserted in **one SQLite transaction**. Unique generation ID within each run prevents duplicate import; transaction rollback must leave no orphan observation.
- `persist_terminal_observation` requires an explicit `confirmed=True` and a matching `authorized_project_id`. The HTTP boundary must still independently enforce launcher-local and same-origin restrictions.
- Read-only `prepare_terminal_observation` remains available, and unknown seed/VRAM/duration/output hashes remain `null`.
- New `tests/test_benchmark_atomic_lineage.py` exercises restart/persistence, explicit approval/project scope, rollback, foreign-run prevention and terminal failure mapping. **Run locally before claiming B5 PASS.**
- A future queue adapter must use an explicitly associated, verified Generation History entry. This helper must not search or import other projects' history automatically.

**B5 test command:**
```powershell
git pull --ff-only
python -m unittest discover -s tests -p "test_benchmark_atomic_lineage.py" -v
```

## B5 import failure identified and corrected in source (operator retest pending)

The first B5 run on Windows/Python 3.13 failed during test module import, before any test cases ran. Source inspection identified **literal escaped `\\n` characters** in two Python source files introduced by the earlier edit and a missing definition of the lineage payload variables. The feature branch now corrects both syntax issues and restores the validated lineage payload initialization. No PASS is claimed for B5 until the operator reruns the tests.

Run `python -m py_compile scripts/benchmark_store.py scripts/benchmark_generation_import.py scripts/benchmark_generation_adapter.py` first, then `python -m unittest discover -s tests -p "test_benchmark_atomic_lineage.py" -v`, and finally all benchmark tests.

## B5 PASS and B6 read-only integration slice

**B5 operator acceptance (2026-11-22, Windows/Python 3.13):** `test_benchmark_atomic_lineage.py` returned **5/5 OK** in 0.146 seconds, followed by the entire `test_benchmark*.py` unit suite **16/16 OK** in 0.301 seconds. This is user-reported local testing; CI and real GPU acceptance remain pending.

**B6 first source increment (not validated yet):** `scripts/benchmark_history_bridge.py` reads a specifically requested generation from the pre-existing `GenerationHistory.get` and offers a read-only terminal observation proposal. It reuses the existing `settings/orkilab/generations.sqlite3` records and makes no queue, cancellation or HTTP calls. The caller must still establish local authorization, project ownership and explicit confirmation before any eventual write. It does **not** associate arbitrary history entries with project IDs automatically or claim measurement of VRAM or latency.

**B6 tests:** `python -m unittest discover -s tests -p "test_benchmark_history_bridge.py" -v`. Four cases check queued-entry rejection, read-only completed snapshot, absent ID and failure-status propagation. These tests have not yet been reported as passing on Windows.

**Still pending for full B6:** authenticated launcher-local API integration, scoped association of a generated job to a project and a benchmark variant, lifecycle tracking through the existing Generation Studio queue, cancellation behavior, and real ComfyUI testing.

## B6b — Explicit generation-to-project association (tests pending)

The operator reported B6 read-only bridge checks as OK and the full `test_benchmark*.py` set as OK (20 unit tests). This is local operator acceptance, not independent CI or GPU verification.

The new `attach_history_generation` helper in `scripts/benchmark_history_bridge.py` takes an **explicit generation ID** from existing Generation History and a **user-selected project/run/variant/repetition**. It requires `confirmed=True`, rejects missing/running generations, and uses the B5 atomic SQLite writer. **It does not claim to discover the owning project from ComfyUI:** current `GenerationHistory` entries do not carry an independently verified project identity. A future launcher-local API must enforce project authorization and origin protections before calling this helper. No queue or cancellation logic is touched.

Validate B6b with:
```powershell
git pull --ff-only
python -m unittest discover -s tests -p "test_benchmark_history_attachment.py" -v
python -m unittest discover -s tests -p "test_benchmark*.py" -v
```

Five new unit tests cover lineage persistence, project/confirmation rejection, queued-history rejection, exact identifier selection, and duplicate prevention. **B6b is unverified until these are executed.** Further work is required to prevent ambiguous association of a single generation across different benchmark runs, enforce API-side authentication and establish a durable binding at generation submission.

## Remaining 0.6 sequence

| Milestone | Concrete deliverable | Gate |
| --- | --- | --- |
| alpha.1 next | Explicit ComfyUI adapter, bounded queue integration, best-effort cancellation, safe preflight and project authorization | Mock queue tests + on-device smoke |
| alpha.2 | Multilingual Benchmark Studio, run creation, status and search | UI/browser + eight locales |
| alpha.3 | Stabilize LoRA Comparator and compare strengths, checkpoints and baseline | Real two-variant RTX 3090 workflow |
| beta.1 | Same-protocol model/checkpoint comparisons, incompatibility warnings | Controlled prompts/seeds + compatible family |
| beta.2 | Optional local evaluation, raw metrics, manual scoring, no universal quality claim | Held-out evaluation and reproducible report |
| beta.3 | Project/Multiview evaluation, provenance-aware grouping | No leakage across subjects; no fake pose claims |
| rc.1 | Reports, export, GPU/Windows/Linux and upgrade acceptance | Evidence on exact release SHA |
| stable | Changelog, supported matrix, signed-off release blockers, tag and GitHub release | No outstanding release blocker |

## Reproducibility contract

A record stores the values actually used, not just user-selected defaults. Later adapters must capture the final prepared API graph or its digest, checkpoint/LoRA identifiers and hashes where available, run-time seeds and output hashes. Use identical prompt/seed/resolution where meaningful; distinguish hardware/environment differences and separate wall-clock latency from ComfyUI processing time. Keep the held-out evaluation set isolated from training data and separate measured numeric metrics from vision-model opinions.

## Deferred

Full conversational Ollama Copilot belongs to 0.7; Hugging Face/Civitai Hub to 0.8; desktop packaging to 0.9. Advanced video and audio quality benchmarking is a separate later compatibility effort, not promised by 0.6 alpha.1.
