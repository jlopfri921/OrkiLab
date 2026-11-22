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

## B6c — Bound generation identity (operator acceptance pending)

**B6b:** Operator reports both 5/5 new association checks and the cumulative 25/25 benchmark unit suite as OK in local Windows/Python 3.13. Full terminal output was not supplied; this is reported acceptance, not independently observed CI.

**B6c implementation:** `scripts/benchmark_job_binding.py` now provides a local, trusted-call binding API that reserves an exact, immutable generation token for one benchmark project/run/variant/repetition and expected workflow. The binding persists in `benchmark_generation_bindings` and enforces uniqueness of a generation across all benchmark runs. Result ingestion requires a matching prior binding, matching project/workflow and a terminal GenerationHistory record, then uses the tested atomic observation/lineage writer. It rejects a random historical generation with no binding and never sends ComfyUI requests.

**Important deployment boundary:** The feature is **not yet called by Generation Studio at submission**, and no Benchmark Studio UI/HTTP endpoint exists. Both systems have separate databases and ComfyUI is external; registering the binding does not create an atomic transaction with a ComfyUI submission. The future actual launcher integration must pass the token from the same authorized submission flow, reconcile a submitted-but-unbound job, and enforce local authorization. Do not claim safe live queue integration or automatic cancellation yet.

Test B6c on Windows:
```powershell
git pull --ff-only
python -m unittest discover -s tests -p "test_benchmark_job_binding.py" -v
python -m unittest discover -s tests -p "test_benchmark*.py" -v
```
Five new tests are included, with **30** total benchmark unit tests expected if all prior tests still pass. These results have **not yet been reported**.

## B6c operator PASS and B6d opt-in submission linkage (new, untested)

The operator confirms **B6c 5/5** and the cumulative benchmark suite **30/30** on local Windows/Python 3.13. This is operator-reported acceptance, not an independently verified CI result.

**B6d — behind explicit opt-in, source now updated:** the existing `POST /api/workspace/generation` retains its original request and behavior when no `benchmark` object is supplied. For an explicitly confirmed benchmark, it optionally accepts:

```json
{
  "confirm": true,
  "workflow_id": "existing-workflow-id",
  "token": "prepared-generation-token",
  "benchmark": {
    "project_id": "existing-active-project-id",
    "run_id": "existing-running-benchmark-id",
    "variant_id": "variant-in-the-same-run",
    "repetition": 0,
    "confirm": true
  }
}
```

Before calling ComfyUI, it checks project existence (nonarchived Workspace project), active benchmark run, matching project and variant, and uniqueness of the target repetition. After submission, it uses the **actual generation history token** to save an immutable binding. The response includes `benchmark_binding: "bound"` on success; if a job was successfully submitted but history or binding failed, it returns HTTP 201 with an explicit `benchmark_binding` warning, **never pretending the binding worked**.

This does not introduce a new queue or change existing cancellation. It does **not** yet automatically save a terminal benchmark observation when Generation Studio checks status, or offer a Benchmark Studio UI; the result still needs a controlled finalization step. The project ID comes from the locally selected Workspace project: application access is restricted to launcher-local callers, but **there is no independently verified user-project ownership model**. The caller must not describe this as multi-user authorization. Because ComfyUI, history and benchmarks use separate transactions, a submitted-but-unbound job is possible and must be surfaced/reconciled.

**Run the new B6d tests first:**
```powershell
git pull --ff-only
python -m py_compile scripts/generation_studio.py scripts/benchmark_job_binding.py
python -m unittest discover -s tests -p "test_benchmark_submission_preflight.py" -v
python -m unittest discover -s tests -p "test_benchmark*.py" -v
```

Four new preflight tests are included; **34 benchmark unit tests** are expected if there are no regressions. These offline tests do not execute the new HTTP submission route, so end-to-end ComfyUI acceptance and real GPU telemetry remain pending.

## B6d operator PASS and B6e terminal finalization (new, untested)

The operator confirms B6d compilation, four new preflight tests and the cumulative **34 benchmark unit tests** as passing locally (Windows/Python 3.13). This is operator-reported, not independent CI verification.

**B6e implementation:** Generation Studio now calls a best-effort finalizer after its existing history entry becomes `completed`, `error`, or `cancelled` (including safe pending cancellation and an already-terminal history entry). The helper reads only an **already-bound** generation token, checks the matching project/workflow, and writes an observation plus lineage atomically to the Benchmark SQLite store. It is idempotent after success and leaves other/unbound generations untouched. A failed optional benchmark finalization is logged and must not change the normal Generation Studio status or cancellation response. It does not submit additional ComfyUI jobs or change interruption policies. When no Benchmark database exists, normal generations do not create one on status checks.

**Known constraints:** Generation Studio currently updates its history on status polling; B6e finalization likewise occurs on status polling/cancellation, not from a background worker or push event. If nobody polls, a completed job may remain unfinalized until the next status read. Separate ComfyUI/GenerationHistory/Benchmark databases mean cross-system exactly-once processing is not guaranteed under concurrent processes; the binding table and uniqueness constraints prevent successful duplication, and failures must remain visible in logs. No actual per-job VRAM/duration metric is yet sourced. API-side local permissions and ComfyUI execution still require integration tests.

Validate B6e with:
```powershell
git pull --ff-only
python -m py_compile scripts/generation_studio.py scripts/benchmark_job_binding.py
python -m unittest discover -s tests -p "test_benchmark_terminal_finalizer.py" -v
python -m unittest discover -s tests -p "test_benchmark*.py" -v
```
Six new tests have been added; **40** benchmark unit tests are expected if all earlier 34 still pass. These are offline tests; real ComfyUI and RTX 3090 acceptance remain pending.

## B6e operator PASS; B6f local Flask HTTP integration tests (pending)

The operator reports **B6e PASS** with Python compilation, six new terminal-finalizer tests and the full benchmark unit suite **40/40** on Windows / Python 3.13. This is operator-reported, not verified CI.

**B6f** introduces `tests/test_benchmark_http_flow.py`, exercising the actual Flask `/api/workspace/generation/prepare`, `POST /api/workspace/generation`, and `GET /api/workspace/generation/<token>` routes with isolated temporary project/benchmark/history/workflow SQLite databases and a fully mocked ComfyUI queue, submission and history. The three cases check a successful opt-in benchmark binding and exactly-once observation on status polling, rejection of a nonexistent project before generation submission, and unaffected normal generation requests.

Run on the feature branch:
```powershell
git pull --ff-only
python -m unittest discover -s tests -p "test_benchmark_http_flow.py" -v
python -m unittest discover -s tests -p "test_benchmark*.py" -v
```

**Expected if no regressions:** three new cases and **43** total benchmark unit/integration tests. These have **not yet been operator-validated**. The fake ComfyUI runs no model and provides no GPU utilization, output digest or performance data. B6 still requires safe cancellation/error HTTP coverage, multi-process reconciliation and a real-world ComfyUI test before release acceptance.

## B6f Windows regression correction — retest required

The first real B6f execution with the project's `venv\\Scripts\\python.exe` and Flask 3.1.3 **failed during test setup**: the test tried to patch `generation_studio.submit`, but the actual `submit` function is local to `generation_studio.register()`. Two test helper SQLite connection lifetimes also triggered `WinError 32` during temporary file cleanup. The 40 pre-existing benchmark tests passed, but the three new HTTP tests **did not run successfully**. A previous recorded statement of 43/43 passing was incorrect and has been corrected in the PR discussion.

The test has now been changed to intercept the nested submission's `build_opener` with a strictly in-process fake `/prompt` response, and to close temporary SQLite connections explicitly. This source correction is **unverified** until retested on the Windows venv. Do not mark B6f PASS yet.

```powershell
git pull --ff-only
.\\venv\\Scripts\\python.exe -m unittest discover -s tests -p "test_benchmark_http_flow.py" -v
.\\venv\\Scripts\\python.exe -m unittest discover -s tests -p "test_benchmark*.py" -v
```

## B6f operator PASS; B6g HTTP error/cancellation regression (pending)

After the corrected Flask fixture and the venv retest, the operator reported B6f as OK: the 3 HTTP integration cases and cumulative 43 benchmark tests (Windows, Flask 3.1.3). The earlier broken fixture remains documented above for traceability. GitHub Actions and real ComfyUI remain unverified.

**B6g adds three more Flask integration cases** to the same in-process, mocked ComfyUI harness: a terminal ComfyUI error becomes a single `failed` benchmark observation, a running job produces no premature observation, and a previously acknowledged cancellation becomes one `cancelled` observation after the prompt disappears from ComfyUI's queue. Tests exercise status polling and history persistence but **do not** send a real `/interrupt` request or perform real inference.

Run in the OrkiLab Windows virtual environment:
```powershell
git pull --ff-only
.\\venv\\Scripts\\python.exe -m unittest discover -s tests -p "test_benchmark_http_flow.py" -v
.\\venv\\Scripts\\python.exe -m unittest discover -s tests -p "test_benchmark*.py" -v
```
Expected after validation: six HTTP cases and 46 total benchmark tests. **B6g remains pending local operator acceptance**. Live ComfyUI cancellation, output integrity, timings, VRAM, and CI still need independent verification.

## B6g operator PASS; B7 read-only live preflight (not yet run)

The operator reports **B6g PASS**, with six HTTP lifecycle tests and the cumulative suite **46/46** passing in the project virtual environment on Windows. This is user-reported acceptance; full successful output and CI have not been independently inspected.

**B7 phase 1 — safe, read-only ComfyUI readiness probe:** `scripts/benchmark_comfyui_preflight.py` reads the existing local ComfyUI connection configuration and checks whether OrkiLab training is active. If training is inactive, it sends only **GET** requests to the configured private ComfyUI `/system_stats` and `/queue` endpoints, validating the returned device inventory and that both queue lists are empty. It fails closed for missing configuration, disabled ComfyUI mode, unreachable server, malformed data or occupied queue. It does not submit or cancel tasks, alter models, run inference, allocate VRAM for generation, create databases or claim a valid benchmark measurement.

**B7 test and live probe commands (Windows repository root):**
```powershell
git pull --ff-only
.\\venv\\Scripts\\python.exe -m unittest discover -s tests -p "test_benchmark_comfyui_preflight.py" -v
.\\venv\\Scripts\\python.exe -m unittest discover -s tests -p "test_benchmark*.py" -v
.\\venv\\Scripts\\python.exe scripts/benchmark_comfyui_preflight.py
```
Five new offline preflight tests have been added (**51** cumulative benchmark tests expected). The last command contacts the **real configured ComfyUI** read-only and returns `ready: true` only when the safety checks pass. A nonzero exit code with `ready: false` is a protective refusal, not necessarily an application fault. This probe is **not** a substitute for actual inference or RTX 3090 benchmark acceptance.

## B7 supervised single-generation pilot (read-only audit available)

Real ComfyUI preflight produced `ready:true`, version `0.46.2`, device `cuda:0 NVIDIA GeForce RTX 3090 : cudaMallocAsync`, running queue 0 and pending queue 0. This shows readiness at the time of the check, **not a completed generation**. The operator has not yet provided the result of the five B7 unit tests or the 51-test suite.

The first GPU pilot is **one explicitly confirmed Generation Studio generation** with a previously validated, lightweight saved workflow. From launcher-local Workspace / ComfyUI / Generation Studio, select that saved workflow, prepare it and check the settings, then press the normal Generate control once. Wait for terminal status in Generation Studio. Do not run another job concurrently or start a trainer. Existing queue and safe cancellation rules remain in effect.

After the generation, a **new read-only command** inspects the latest persisted history result and (if any) its benchmark linkage, without submitting or contacting ComfyUI:
```powershell
git pull --ff-only
.\\venv\\Scripts\\python.exe scripts/benchmark_comfyui_preflight.py
# Then run ONE generation through the existing Generation Studio UI.
.\\venv\\Scripts\\python.exe scripts/benchmark_live_audit.py
# To inspect a particular job:
.\\venv\\Scripts\\python.exe scripts/benchmark_live_audit.py --generation-id YOUR_ID
```

The audit reports `state`, `output_count`, actual `generation_id`/`prompt_id` and optionally `benchmark_binding`/`benchmark_observation`. **A plain Generation Studio run is not automatically a Benchmark run**; without the opt-in benchmark payload, binding should correctly be `none`. Do not describe the pilot as a measured or bound benchmark unless an actual binding exists. No per-job runtime, output digest or peak VRAM is inferred from history. A separate opt-in benchmark run / UI integration is required before true B7 performance comparison.

## B7.3 — Confirm the *running* launcher's benchmark capability

The operator successfully generated a real image, then explicitly recovered and attached it to the original B7.2 run/variant. The read-only audit confirms `benchmark_binding=bound`, `benchmark_observation=recorded`, `binding_workflow_matches=true`. **This is recovery, not proof of automatic submission binding.** The initial HTTP submission response lacked the `benchmark_binding` property, so the active launcher may have been started before the latest feature branch was pulled.

A new **read-only, launcher-local** GET endpoint now exposes the actual loaded route capability: `/api/workspace/generation/capabilities`. Unlike reading the checked-out Python file, probing this endpoint distinguishes an old running Flask process from the new code without initiating inference or writing a DB. An old process should return 404 (or an old route's not-found response) rather than `benchmark_submit: true`.

1. Run tests first (two new capability tests; **expected 57 total** benchmark tests only if the prior 51-test B7 gate and four recovery tests also pass):
```powershell
git pull --ff-only
.\\venv\\Scripts\\python.exe -m unittest discover -s tests -p "test_benchmark_http_flow.py" -v
.\\venv\\Scripts\\python.exe -m unittest discover -s tests -p "test_benchmark*.py" -v
```
2. Query the currently serving launcher **before restarting**:
```powershell
Invoke-RestMethod "http://127.0.0.1:4990/api/workspace/generation/capabilities" | Format-List
```
3. If old/404, verify no active ComfyUI work, then restart **only OrkiLab launcher**. Keep ComfyUI running; query endpoint again. Expected marker: `generation_studio: benchmark-submission-v1`, `benchmark_submit: True`, `benchmark_terminal_finalization: True`.
4. If endpoint already shows marker, investigate why POST response lacked benchmark binding before launching more GPU work; do not infer from code or retry the completed run/repetition.

No new generation is required by this diagnostic.

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

## B7.4 live evidence (2026-11-22)

**PASS:** operator confirmed a real RTX 3090/ComfyUI job was automatically bound at submission, completed and finalized without recovery. Generation `e754fd5eed294fbeb32b281b6db6d4c3`, prompt `3324fc23-0062-4ff6-b50c-fc3a3489a9c0`, run `30229702-26b7-41d5-821b-8a02088f21b6`, variant `d4f65507-69ed-4c6a-9533-ea7486b6414c`, repetition 0. Final read-only audit: `completed`, one output, `benchmark_binding=bound`, `benchmark_observation=recorded`, `binding_workflow_matches=true`. Earlier 57/57 automated tests passed. These are real operator-provided results, not CI results.

## B8.1 measured execution duration — feature branch, pending operator tests

ComfyUI `/history/<prompt_id>` may return `status.messages` containing paired `execution_start` and `execution_success` events with millisecond timestamps and exact `prompt_id`. B8.1 parses these server-issued events **only for a successfully completed matching prompt**, subtracts `start` from `success`, excludes queue wait, rejects duplicates, reversed or malformed timestamps, and stores `duration_ms` plus `generation_lineage.execution_timing` provenance in the existing atomic observation record. These are ComfyUI server event measurements, **not** local poll intervals or GPU kernel-only timing. If valid events do not exist, `duration_ms` stays `null`, with no fallback estimate. Existing B7 observations remain unchanged (immutable).

For this first iteration, capture occurs on the terminal HTTP poll while ComfyUI history is available. If an already-terminal generation is loaded from local history without an active ComfyUI entry, its duration remains unknown. B8.2 will address separate hardware monitoring and B8.3 output hashes; neither is claimed here.

Validation without GPU:
```powershell
git pull --ff-only
.\\venv\\Scripts\\python.exe -m unittest discover -s tests -p "test_benchmark_execution_timing.py" -v
.\\venv\\Scripts\\python.exe -m unittest discover -s tests -p "test_benchmark_http_flow.py" -v
.\\venv\\Scripts\\python.exe -m unittest discover -s tests -p "test_benchmark*.py" -v
```

Expected test counts: 4 timing, 10 mocked HTTP, **63 benchmark tests total** if no other changes have been made. A future new benchmark run+variant/repetition and a new ComfyUI generation are needed before claiming **live B8.1 duration measurement**, but not for the code/tests stage. Do not rerun B7.4's completed binding.
