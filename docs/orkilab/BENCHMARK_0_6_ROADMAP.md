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

## B8.1 read-only live probe — first real observation

The operator reported **66/66 benchmark tests PASS** and probed previously completed B7.4 generation `e754fd5eed294fbeb32b281b6db6d4c3` using the read-only historical timing probe. ComfyUI history returned valid paired events with `duration_ms=14` (`0.014 s`, no queue time). This is evidence of a **14 ms server event interval**, **NOT** proof of a full FLUX3 image inference benchmark; prompt caching or unchanged workflow inputs are plausible, but unconfirmed. The probe did not modify the benchmark database, and the existing B7.4 observation remains immutable.

To prevent accidental interpretation as full inference, the probe now reports `execution_cached_event_observed`, `cache_status` (either `cache_event_observed` or `undetermined`) and `full_inference_verified=false` alongside the factual event interval. Absence of a cached event does **not** prove there was no cache. One additional mocked regression test covers an observed cache event (67 tests expected after the new change). The next full-inference benchmark will need an explicit fresh, legitimately varied workload with verified node execution and a new run/variant; do not compare the 14 ms interval as model throughput.

## B8.1.2 — cache-safe persisted timing

Live operator evidence confirms `execution_cached` in the B7.4 ComfyUI history, while the exact event interval was 14 ms. New bound generations record the interval and `execution_cached_event_observed=true` in the immutable lineage snapshot but leave the **comparison column** `benchmark_observations.duration_ms=NULL` whenever matching-prompt ComfyUI history contains `execution_cached`. Lineage `execution_timing.comparability` is `cache_observed_not_comparable` (otherwise `full_inference_unverified`). Absence of `execution_cached` is **not** proof of full inference. Existing immutable B7.4 observation is not modified and previous 14ms read-only measurement remains only diagnostic, not comparable throughput.

One mocked Flask integration test added; expected **68 benchmark tests** following earlier operator-confirmed 67/67. No GPU work is needed to test this change. This is the prerequisite to building a stricter verified full-inference benchmark protocol and later GPU measurements.

## B8.1.3 — prompt-scoped cache evidence (pending operator verification)

After the operator reported the previous **68 benchmark tests PASS**, the cache detection was made prompt-specific: only `execution_cached` events whose `prompt_id` matches the exact ComfyUI job count as evidence. The read-only probe also returns the sorted, validated `cached_node_ids` from those events (diagnostic only). Unrelated prompt cache events are ignored, and missing cached events remain `undetermined`; neither case establishes full inference. This removes a possible false-positive cache warning in the previous probe. Two mocked tests added; **70 benchmark tests** expected. No ComfyUI submission and no modifications of previous observations.

## B8.1.4 real RTX 3090 sampler rerun — operator PASS

Operator manually copied the exact 10-node FLUX3 Klein API workflow and changed **only KSampler node 7 seed=42→43**, saved as workflow `c07586fe3219463d8cfe30842c1fbb33`. Real Generation Studio job `41b8689d219a4c10883533036ebd91c5`, ComfyUI prompt `63f447c1-9869-4c7d-8ecd-5c31fb4994dd`, run `5df86bc2-a31e-492a-afa2-4ffa5e83614b`, variant `6cba2ed2-a354-474f-b2bb-a148a2fde770`, repetition 0. Submission bound automatically, final job completed, output `OrkiLab_FLUX3_Klein_LoRA_00006_.png`, benchmark observation recorded. Live timing probe measured **13,622 ms**, excluding queue time. The cached-node list was `[1,2,3,4,5,6,8]`; sampler node **7 not cached**, nor nodes 9/10. Evidence is compatible with a *warm-model sampler rerun*, **not** full-cold inference verification. These are observational results, not CI.

## B8.1.5 sampler-aware comparability — implementation, pending operator tests

The prior rule excluded all durations if *any* `execution_cached` event was present. That penalized the legitimate warm-model case in B8.1.4. New rules inspect the **actual submitted API graph in GenerationHistory** (not user-entered claims), recognize only known `KSampler` and `KSamplerAdvanced` nodes, and compare those node IDs with the cached-node IDs from the **exact prompt**:

- `sampler_cached_not_comparable`: any identified sampler explicitly cached. Keep measured server interval in immutable lineage but leave comparison `duration_ms=NULL`.
- `sampler_cache_miss_partial_cache`: cache event exists for other nodes but no known sampler is in that list. Persist server event `duration_ms` for **warm-sampler** comparisons with category/provenance; **not** a full-cold inference measurement.
- `sampler_cache_unverified`: known sampler, no cache event; retain the server interval with explicitly unverified inference classification. No cache event does not prove a sampler executed.
- `unverified`: no supported sampler identifiable; when any cache event exists, comparison `duration_ms=NULL`, otherwise preserve previous B8.1 measured duration behavior with unknown sampler. Never infer arbitrary custom sampler semantics.

Read-only historical probe now also reports `sampler_node_ids`, `sampler_cached_node_ids`, `sampler_cache_status` and `comparability` alongside previously reported timing/cache facts. Existing observations remain immutable. **B8.1.4's previously recorded comparison duration stays NULL**; its historical read-only probe reveals the new interpretation without backfilling. 2 new parser tests + 2 Flask tests added; **74 benchmark tests** expected after previously operator-confirmed 70, pending execution on Windows. No GPU calls or new inference required.

Validation:
```powershell
git pull --ff-only
.\\venv\\Scripts\\python.exe -m unittest discover -s tests -p "test_benchmark_execution_timing.py" -v
.\\venv\\Scripts\\python.exe -m unittest discover -s tests -p "test_benchmark_http_flow.py" -v
.\\venv\\Scripts\\python.exe -m unittest discover -s tests -p "test_benchmark*.py" -v
.\\venv\\Scripts\\python.exe scripts/benchmark_live_timing_probe.py --generation-id 41b8689d219a4c10883533036ebd91c5
```

## B8.1.5 Windows operator acceptance

Operator confirmed the post-fix B8.1.5 suite was successful following the `f3634c7` test-assertion correction (**expected 74/74**; exact raw log not provided in this turn). Real B8.1.4 historical read-only classification remains `sampler_cache_miss_partial_cache` with a 13,622ms measured event interval; the already recorded immutable observation was not rewritten. No claim of fully cold inference is made.

## B8.2a — NVIDIA memory read-only inventory (pending operator validation)

`scripts/benchmark_gpu_memory_probe.py` runs a **single** bounded `nvidia-smi --query-gpu=index,uuid,name,memory.total,memory.used,memory.free --format=csv,noheader,nounits` diagnostic with 5-second timeout, parses up to 16 GPUs and reports device-wide used/free/total bytes. It does **not** call ComfyUI, send a workflow, change its queue, write any SQLite data, change GPU settings, or infer a per-job peak. On invalid/unsupported NVML results it fails closed. **`peak_vram_bytes` intentionally stays NULL** until a future explicit job-scoped, time-windowed and source-attributed sampler is implemented. The global used-memory value includes cached allocations and other applications, and must never be labelled benchmark peak. Multi-GPU index and GPU UUID are retained.

Four mocked unit tests cover CSV parsing on two GPUs, malformed/device mismatch, command failures, and non-attribution semantics. **78 benchmark tests** expected after the operator-confirmed 74 baseline, pending actual verification.

```powershell
git pull --ff-only
.\\venv\\Scripts\\python.exe -m unittest discover -s tests -p "test_benchmark_gpu_memory_probe.py" -v
.\\venv\\Scripts\\python.exe -m unittest discover -s tests -p "test_benchmark*.py" -v
.\\venv\\Scripts\\python.exe scripts/benchmark_gpu_memory_probe.py
```

Next B8.2b: explicit start/stop capture linked to a specific Generation Studio job, session-bound to device UUID and preferably ComfyUI PID/process memory rather than device global memory, with sampling interval, baseline, max sample, and flags for observed concurrent GPU jobs/processes and missed windows. No attribution without isolation evidence and no extrapolated true peak beyond observed samples.

## B8.2b — manual opt-in VRAM sample series (pending acceptance)

The standalone `scripts/benchmark_gpu_memory_series.py` obtains a bounded series of read-only device-level NVIDIA VRAM snapshots at an explicitly selected GPU UUID. Default 10 samples, interval 0.5 s; sample count must be 2–120 and interval 0.2–5 seconds. Captures monotonically timestamped samples and summarizes baseline VRAM, maximum **observed device-global usage**, and maximum observed increase over the starting baseline. The UUID must remain available, and reported device capacity must not change. Failure of an individual sample aborts the capture, without partial reported metrics.

These are **not per-generation or process measurements**. No PID/ComfyUI/Generation Studio attribution is possible from the data alone, so `peak_vram_bytes` stays NULL and `attributable_to_generation=false`. The observed increase is not ComfyUI's allocation: other GPU activity and persistent model caching can affect it. The sample maximum is not a continuous true peak. This phase does not update any database or attach results to a run; nor does it submit/cancel GPU jobs or alter GPU settings.

5 mocked tests added; expected **83 benchmark tests if previous B8.2a 78 tests pass**. B8.2a operator-run tests and real GPU inventory have not been seen in this conversation; do not state they are confirmed. Test using:
```powershell
git pull --ff-only
.\\venv\\Scripts\\python.exe -m unittest discover -s tests -p "test_benchmark_gpu_memory_series.py" -v
.\\venv\\Scripts\\python.exe -m unittest discover -s tests -p "test_benchmark*.py" -v
.\\venv\\Scripts\\python.exe scripts/benchmark_gpu_memory_probe.py
```
Select the actual `devices[0].uuid` from the last command; only then optionally run `python scripts/benchmark_gpu_memory_series.py --gpu-uuid <ACTUAL_GPU_UUID> --samples 5 --interval 0.5` with the genuine UUID. Never paste a placeholder as a literal argument. The follow-on phase needs a generation-bounded recorder with explicit process identity and concurrency checks before assigning a VRAM metric to a benchmark observation.

## B8.2a/b operator real RTX 3090 acceptance — 2026-11-22

Operator ran the **83-test benchmark suite, all PASS** in 2.374 seconds. First real read-only `nvidia-smi` inventory found one NVIDIA GeForce RTX 3090, UUID `GPU-149248bf-feeb-0a40-a155-c7e4ca072dbd`, 25,769,803,776 total bytes (24 GiB), 12,526,288,896 used, 12,982,419,456 free. The five-sample explicit global VRAM series was successful, spanning 2.209647 seconds; initial usage 12,529,434,624 bytes; maximum observed 12,529,434,624 bytes, maximum increase over baseline 0 bytes. Used-memory readings declined over the capture. **No claim of zero ComfyUI memory use**, process attribution or exact GPU peak. No benchmark database writes, no GPU inference submitted. Operator's trailing PowerShell `else` error resulted from running the `else` statement separately after the successful `if` block; no application fault.

## B8.2c — NVIDIA compute-process discovery (awaiting operator run)

Added `scripts/benchmark_gpu_process_probe.py` as a one-shot read-only `nvidia-smi --query-compute-apps=pid,process_name,gpu_uuid,used_gpu_memory --format=csv,noheader,nounits` diagnostic. Output lists reported compute processes with PID, process name, device UUID and memory bytes if supported. Importantly, **Windows WDDM may return N/A for process memory**, which maps to `null`, not zero. Unsupported query fails cleanly, and an empty compute process list does **not** establish GPU isolation or prove no other GPU programs are using the device. There is no ComfyUI PID verification or per-job attribution yet; `peak_vram_bytes` stays null. No change to GPU, queue, database, or model execution.

Four isolated mocked tests added; expected **87 benchmark tests** after the operator-confirmed 83. Operator validation:
```powershell
git pull --ff-only
.\\venv\\Scripts\\python.exe -m unittest discover -s tests -p "test_benchmark_gpu_process_probe.py" -v
.\\venv\\Scripts\\python.exe -m unittest discover -s tests -p "test_benchmark*.py" -v
.\\venv\\Scripts\\python.exe scripts/benchmark_gpu_process_probe.py
```
Future work must identify the actual ComfyUI PID (with locally checked trusted process ownership) and handle WDDM's possible refusal of per-process VRAM. A generation-scoped series and externally attributed peak are **not yet implemented**.

## B8.2c operator acceptance / B8.2d Windows PID-to-port correlation

Operator supplied the complete Windows log: **87/87 tests PASS** and real `scripts/benchmark_gpu_process_probe.py` returned **27 NVIDIA-listed processes**, all with `used_gpu_memory_bytes=null`, consistent with Windows WDDM's lack of per-process GPU memory in this query. The list included candidate ComfyUI Python **PID 32808** (`D:\\Comfy-Desktop\\ComfyUI-Installs\\ComfyUI\\standalone-env\\python.exe`), Comfy Desktop **PID 21428**, another Python **PID 26860**, Blender **PID 22336**, and numerous other GPU users. This supports process discovery only, **not** verified ComfyUI ownership, process isolation, or per-job peak VRAM. No benchmark observations were changed.

Added `scripts/benchmark_comfyui_port_probe.py` (Windows only) to correlate read-only `Get-NetTCPConnection -LocalPort 8188 -State Listen` owners with NVIDIA's process PIDs and GPU UUIDs; uses a fixed, non-interactive PowerShell command (no user-supplied script), retrieves executable name/path but deliberately **not command line**. Port 8188 may belong to a proxy/bridge rather than the ComfyUI Python worker, so `comfyui_process_verified=false` and `process_isolation_verified=false` remain hard false. It does NOT terminate processes, query secrets, submit ComfyUI work, modify GPU settings or benchmark DB, nor report a job peak. Four isolated mock tests added; expected **91 benchmark tests**, pending operator verification. Run:
```powershell
git pull --ff-only
.\\venv\\Scripts\\python.exe -m unittest discover -s tests -p "test_benchmark_comfyui_port_probe.py" -v
.\\venv\\Scripts\\python.exe -m unittest discover -s tests -p "test_benchmark*.py" -v
.\\venv\\Scripts\\python.exe scripts/benchmark_comfyui_port_probe.py
```
The pending future milestone is an explicit **per-generation, process-scoped** memory recording mechanism with Windows WDDM fallback; **not** to fill benchmark `peak_vram_bytes` from global memory maxima.

## B8.2d real Windows acceptance / B8.2e read-only HTTP identity

Operator reported **91/91 benchmark tests PASS** (2.345 seconds). Real `benchmark_comfyui_port_probe.py` found a single TCP port **8188** listener, **PID 32808**, executable `D:\\Comfy-Desktop\\ComfyUI-Installs\\ComfyUI\\standalone-env\\python.exe`, listening on **0.0.0.0** and listed in NVIDIA compute processes on GPU UUID `GPU-149248bf-feeb-0a40-a155-c7e4ca072dbd`. Separate operator `GET http://127.0.0.1:8188/system_stats` returned `comfyui_version=0.46.2`, `python_version=3.13.12`, `pytorch_version=2.12.1+cu130`, `deploy_environment=local-desktop2-standalone`. This confirms a valid ComfyUI HTTP response on that port and gives strong cross-source process correlation. However, **no GPU process isolation or per-process VRAM** is available in this WDDM environment. External LAN exposure may exist because listener is 0.0.0.0; operators should restrict access using firewall or bind to loopback where appropriate.

**B8.2e** adds `scripts/benchmark_comfyui_identity_probe.py`. This *read-only* diagnostic checks the configured exact `http://127.0.0.1:8188` endpoint via GET `/system_stats`, then independently correlates the Windows listening port/PID and NVIDIA compute process on the same host. It reports protocol-level `http_comfyui_confirmed` and `http_tcp_gpu_correlated`, but retains `comfyui_process_verified=false`, `process_isolation_verified=false`, `peak_vram_bytes=null`, and `attributable_to_generation=false`. It neither submits generation nor modifies GPU/queue/SQLite. The check fails closed on missing HTTP identity, ambiguous listeners, no NVIDIA PID intersection, or wrong endpoint. Four mocked unit tests added. **95 benchmark tests** expected after previous confirmed 91; operator validation pending.

```powershell
git pull --ff-only
.\\venv\\Scripts\\python.exe -m unittest discover -s tests -p "test_benchmark_comfyui_identity_probe.py" -v
.\\venv\\Scripts\\python.exe -m unittest discover -s tests -p "test_benchmark*.py" -v
.\\venv\\Scripts\\python.exe scripts/benchmark_comfyui_identity_probe.py
```

Next: design a generation-window sampling protocol with reliable start/end and concurrency flags. Any global GPU memory remains expressly diagnostic and must not fill an attributed benchmark `peak_vram_bytes` field.

## B8.2e operator confirmation and B8.2f temporal window logic

Operator responded `todo ok` to B8.2e acceptance (expected **95** benchmark tests and an HTTP/GPU cross-source diagnostic); this is **operator-reported**, not an independently observed raw test transcript in this turn.

B8.2f adds the pure, I/O-free module `scripts/benchmark_gpu_generation_window.py` to align GPU device-global samples carrying **UNIX epoch milliseconds** with exact ComfyUI `execution_start`/`execution_success` timestamps for one prompt. The pre-existing `benchmark_gpu_memory_series.py` supplies **monotonic timestamps**, so its outputs must **not** be passed directly as wall-clock timestamps or converted without obtaining a shared valid timebase. The new analyzer is not yet wired to live capture or Generation Studio.

The analysis reports the maximum *observed global device usage* and its observed increase relative to the first in-window sample. It flags missing server events, no samples in the generation window, and incomplete cadence/endpoint coverage, never inventing samples. A concurrency flag (`true/false/null`) is annotation only and does not prove isolation. **The analyzer never fills `peak_vram_bytes`**, always declares `attributable_to_generation=false`, does not write SQLite and cannot infer ComfyUI-process usage under Windows WDDM. It also cannot prove true instantaneous peaks even when sampling cadence is within the configured maximum gap.

Six isolated synthetic tests added; **101 benchmark tests expected** after previously operator-reported 95. Validation:
```powershell
git pull --ff-only
.\\venv\\Scripts\\python.exe -m unittest discover -s tests -p "test_benchmark_gpu_generation_window.py" -v
.\\venv\\Scripts\\python.exe -m unittest discover -s tests -p "test_benchmark*.py" -v
```
The next slice should safely collect epoch-based snapshots during a specifically tracked Generation Studio job (with explicit opt-in, bounded duration, adequate event coverage and process/queue concurrency flags), but this implementation alone neither starts a sampler nor performs a GPU job.

## B8.2f operator PASS / B8.2g live opt-in read-only capture — pending tests

Operator reported **101/101 benchmark tests PASS** for B8.2f (no raw test log attached in that turn). New `scripts/benchmark_gpu_live_capture.py` is an **operator-started, read-only passive capture** that requires an existing Generation Studio record in `queued` or `running` state and the exact configured localhost ComfyUI URL. The script cannot submit or cancel a job: it queries ComfyUI GET `/history/<prompt_id>` and GET `/queue` and samples a specific NVIDIA GPU UUID through `nvidia-smi`, with explicit 2–120 sample and 0.2–5 second interval bounds. Time stamps are UNIX epoch milliseconds taken at the midpoint of an individual subprocess measurement, so on the same local machine they can be compared with ComfyUI's history event times. Once completed history arrives it stops sampling; on an error or max-sample limit, it fails conservatively or indicates incomplete observation. The implementation does **not** call the launcher terminal status endpoint and therefore does not finalize or alter benchmark observations.

The existing pure B8.2f analyzer labels maximum observed **device-global** usage and window coverage only. It cannot prove process memory or job isolation, especially on Windows WDDM. `peak_vram_bytes` stays NULL, `attributable_to_generation=false`, and `benchmark_database_modified=false`. An observed running queue entry is diagnostic only. This is **not** an automatic background monitor, nor a benchmark peak metric. Launch the monitor manually only after submitting a **new** job; it cannot retroactively monitor an already completed generation. Users must keep the launcher terminal GET/status workflow separate to finalize observations. No new inference should be initiated solely to test the fake unit cases.

Five mocked tests added; **106 benchmark tests expected** from the operator-reported 101 baseline. Run:
```powershell
git pull --ff-only
.\\venv\\Scripts\\python.exe -m unittest discover -s tests -p "test_benchmark_gpu_live_capture.py" -v
.\\venv\\Scripts\\python.exe -m unittest discover -s tests -p "test_benchmark*.py" -v
```
No live GPU job is required for this acceptance gate. Future work: safe opt-in integration into the Generation Studio submission lifecycle, queue concurrency assessment, and more reliable per-process attribution where NVIDIA drivers provide that data. Only then consider adding dedicated memory columns or storing diagnostic series with explicit source and limitations.

## B8.2g Windows regression: SQLite fixture handle fix (2026-11-22)

Operator ran the **101-test B8.2f baseline PASS** and then updated to B8.2g. The 5 new tests raised `PermissionError [WinError 32]` in `LiveCaptureTests.tearDown` while deleting the temporary `generations.sqlite3` file; 106-test suite reported 5 errors. Both B8.2g fixture connections were created using `with sqlite3.connect(...) as con:` which manages transactions but does **not** close the SQLite connection on context exit. Windows file locking exposes this. Fixed both fixture contexts with `contextlib.closing(sqlite3.connect(...))` and an inner transaction manager (`with closing(...) as con, con:`) so transactions commit and handles close deterministically. The production capture's `_target` already uses `closing`, so **no production SQLite, GPU, ComfyUI, queue, or database changes were required**. Retest expected 5/5 B8.2g and 106/106 benchmark suite; **operator verification pending**.

```powershell
git pull --ff-only
.\\venv\\Scripts\\python.exe -m unittest discover -s tests -p "test_benchmark_gpu_live_capture.py" -v
.\\venv\\Scripts\\python.exe -m unittest discover -s tests -p "test_benchmark*.py" -v
```

## B8.2g operator confirmation / B8.2h experimental opt-in Generation Studio bridge

Operator confirmed **106/106 B8.2g benchmark tests PASS** after the Windows fixture SQLite connection fix (confirmation in chat; new raw logs not attached in that turn).

B8.2h implements the first **explicitly optional** monitoring path on the existing `POST /api/workspace/generation` endpoint, alongside the current benchmark linkage. With **no** `gpu_monitor` field, existing generations remain unchanged. An experimental monitoring request must contain exactly:
```json
{"gpu_monitor":{"confirm":true,"gpu_uuid":"GPU-<REAL_DEVICE_UUID>","samples":40,"interval":0.3}}
```
The GPU UUID must be taken from the real local inventory (the literal placeholder above is NOT a usable UUID). Valid sample counts are 2–120 and intervals 0.2–5 seconds. A request without affirmative consent or invalid bounds is **rejected before any ComfyUI generation is submitted**. Experimental monitoring is available only when ComfyUI is configured on `http://127.0.0.1:8188`. The capability route advertises `experimental_gpu_monitor=true` and the field `gpu_monitor`.

When a user **explicitly** includes the option and Generation Studio successfully persists the new generation record, the server schedules a **daemon** thread to run the existing passive `benchmark_gpu_live_capture.observe` with the just-submitted generation ID. That monitor is fail-open relative to generation submission: if it cannot start or fails, the already-submitted generation remains valid. The monitoring report is **ephemeral in process memory** (at most 100 entries, no restart persistence), retrievable via local-launcher-only GET `/api/workspace/generation/<generation_id>/gpu-monitor`. Possible states: `scheduled`, `running`, `completed`, `failed`. A monitor report cannot be treated as the completion status of the generation itself. This feature does **not** add or automatically activate any UI checkbox yet; it is an internal API/contract integration for testing. It is NOT enabled by default.

No monitoring report writes SQLite or populates benchmark observations; every receipt declares `peak_vram_bytes=null` and `attributable_to_generation=false`. The only ComfyUI writes are those already caused by the user's explicit normal generation submission; the optional telemetry makes only read-only ComfyUI GET and `nvidia-smi` calls. Time-window analysis continues to report *observed device-global VRAM*, not WDDM-hidden per-process memory or exclusive job usage. Monitoring is best-effort and can miss short workflows; a 120-sample cap is intentional.

Five pure validation tests and four mocked Flask integration tests added; **115 benchmark tests expected** after the confirmed 106 baseline, pending operator Windows execution. Test:
```powershell
git pull --ff-only
.\\venv\\Scripts\\python.exe -m unittest discover -s tests -p "test_benchmark_gpu_monitor_contract.py" -v
.\\venv\\Scripts\\python.exe -m unittest discover -s tests -p "test_benchmark_http_flow.py" -v
.\\venv\\Scripts\\python.exe -m unittest discover -s tests -p "test_benchmark*.py" -v
```
No live ComfyUI inference is required for these tests. Future work: expose the experimental option clearly in the Generation Studio UI, show real-time progress/status with explicit device-global labels, introduce cancellation for monitoring alone, and make results restart-safe if the user opts into persistence—without compromising immutable benchmark observations.

## B8.2h operator acceptance / B8.2i Generation Studio opt-in UI (pending validation)

Operator reported that all **115 B8.2h benchmark tests passed** (confirmation in chat; full execution log not attached). B8.2i adds the **default-off** experimental NVIDIA device-global VRAM checkbox to `GUI/workspace.html`, a GPU selection drop-down populated by a local-only, one-shot `GET /api/workspace/generation/gpu-monitor/devices` read-only NVIDIA inventory endpoint, and a diagnostic monitor status readout while a generation is running. The selected UUID is provided using the previously validated explicit `gpu_monitor` consent contract, with a 120-sample limit and 0.3s nominal interval. The existing submitted workflow, seed, checkpoint and scheduler are untouched by enabling monitoring. The new HTML has Spanish/English explanatory copy and labels. Controls are disabled while the generation is active.

When a generation was submitted with monitoring enabled, its session-only results are queried through local-only `GET /api/workspace/generation/<generation_id>/gpu-monitor`. Values, if present, are explicitly labelled **maximum observed global GPU VRAM**, **not** job- or process-attributed VRAM; WDDM's per-process memory remains unavailable. There is NO data insertion into benchmark observations, and `peak_vram_bytes` stays NULL. This is not a reliable continuous VRAM peak capture; very short workflows may complete before sampling. Monitoring errors must not invalidate a submitted generation. Without the user's checkbox selection, the existing generation path stays unchanged. Read-only UUID endpoint reports only index/name/UUID (not memory or any process secrets) and rejects remote clients.

Two mocked Flask tests added for GPU UUID inventory endpoint/local-only access/unsupported inventory. **117 benchmark tests expected**, pending Windows operator verification. In addition, verify the UI manually by opening Generation Studio, confirm the experimental checkbox is initially unchecked, check GPU selection, uncheck it again, and run no workflow. Confirm labels and selection in Spanish and English without running inference. The scope of this round is UI and endpoint readiness, **not** an acceptance claim about a real monitored inference.

```powershell
git pull --ff-only
.\\venv\\Scripts\\python.exe -m unittest discover -s tests -p "test_benchmark_http_flow.py" -v
.\\venv\\Scripts\\python.exe -m unittest discover -s tests -p "test_benchmark*.py" -v
```
After refreshing the actual Python launcher process, inspect `http://127.0.0.1:4990/workspace/comfyui#generation` and ensure ComfyUI connection is configured. Do not merge PR #104 or claim 0.6.0 stable from these tests alone.

## B8.2i acceptance / B8.2j terminal capture safeguards (awaiting operator validation)

Operator answered `todo ok` after the B8.2i checklist, recorded as **operator-reported 117/117 benchmark tests and local UI acceptance** (raw console output not attached in this turn). No claim of having run a real monitored workflow or real background process monitoring has been made.

B8.2j fixes a lifecycle ambiguity: **a bounded GPU monitor that runs out of samples without seeing the generation's completed ComfyUI history is now labelled `partial`, not `completed`**. Only reports explicitly ending with `termination=completed_history` are marked monitor-completed. A passive device-global monitor cannot establish true peak or attributable per-job VRAM even when it did observe the full time window, and terminal states are for the *monitor*, not the ComfyUI workflow. The contract now supports `scheduled | running | completed | partial | failed`; `peak_vram_bytes` remains NULL, no benchmark database writes. Generation Studio now attempts a final local read-only monitor report query on completed/error/cancelled generation, without waiting for capture to finish, rather than displaying a potentially stale state from the preceding poll. Ephemeral monitor report may still be running after a very fast workflow and may later complete; this is a documented limitation.

Two new mocked Flask integration tests explicitly execute the real monitor-thread callback **synchronously with a fake thread and fake `observe`** to check success, truncated capture, no attributed VRAM, no benchmark writes and existing generation behavior. This addresses the previous gap where tests only checked that a thread was scheduled, not that its callback correctly transitioned states. **119 benchmark tests expected**, operator verification pending.

```powershell
git pull --ff-only
.\\venv\\Scripts\\python.exe -m unittest discover -s tests -p "test_benchmark_http_flow.py" -v
.\\venv\\Scripts\\python.exe -m unittest discover -s tests -p "test_benchmark_gpu_monitor_contract.py" -v
.\\venv\\Scripts\\python.exe -m unittest discover -s tests -p "test_benchmark*.py" -v
```
No new GPU generation required for these tests. After acceptance, perform *one consciously initiated small workflow* with the experimental monitor checked and inspect the result. Do not merge PR #104 before the live evidence is evaluated and critical regressions are resolved.

## B8.2k real-device smoke test and deferred workflow compatibility register

The operator reported that a **real opt-in NVIDIA GPU monitor generation completed successfully** in Generation Studio. This establishes an operator-reported functional smoke test, but no raw device-global sample report, actual peak number, trace ID or sampling coverage was supplied; **per-job VRAM attribution remains unverified and is not claimed**. They also reported some (not all) imported workflows show error messages; per-workflow troubleshooting is **explicitly deferred by operator request**. Create the workflow-error catalogue only when the operator resumes it, recording exact workflow/version, ComfyUI/nodes, message, cause, correction and verification; do not invent defects or alter workflows during Benchmark closeout.

## B9.1 — read-only descriptive benchmark reporting (operator tests pending)

A pure, non-I/O module `scripts/benchmark_report_summary.py` now accepts the exact existing `BenchmarkStore.report()` shape, validates project-run/variant/observation lineage and duplicate repetition keys, and returns *factual counts* per variant (completed/failed/cancelled, valid duration measurements, missing duration, present/missing per-job VRAM measurements). It computes descriptive duration min/median/max **only** from existing recorded durations for completed observations. This is **not** a performance ranking and never implies that measurements are comparable across configurations, caches or model families. A field in the report database marked `peak_vram_bytes = null` stays unknown; sampling of device-global VRAM is NEVER substituted for a per-job measurement. The original database and report are unmodified. No new visible benchmark UI or HTTP endpoint in B9.1.

Eight synthetic read-only unit tests added. Following the operator-reported previous 119 benchmark tests, **127 benchmark tests are expected** once B9.1 tests are included (not yet confirmed on Windows).

```powershell
git pull --ff-only
.\\venv\\Scripts\\python.exe -m unittest discover -s tests -p "test_benchmark_report_summary.py" -v
.\\venv\\Scripts\\python.exe -m unittest discover -s tests -p "test_benchmark*.py" -v
```

**Remaining to call OrkiLab 0.6.0 ready for RC:** user-facing Benchmark Studio run/variant comparison/report UI, approval and source/quality evidence on real comparisons, test coverage for Windows/Linux launchers and CI, migration/backwards compatibility and end-to-end update review. The benchmark source is still on the separate feature branch and PR #104; no merge, stable tag or release is authorized at this point.

## B9.1 operator acceptance / B9.2 read-only Benchmark Studio report UI (pending tests)

Operator confirmed the previous **127/127 benchmark tests** via `todo ok` in chat after the B9.1 commands (operator-reported; no new raw log). B9.2 adds actual **project- and run-scoped read-only report views**.

- New `scripts/benchmark_reporting_routes.py` registers local-launcher-only GET `/api/workspace/benchmark/reports?project_id=...` and `/api/workspace/benchmark/reports/<run_id>?project_id=...`. Invalid IDs fail closed; a requested run must explicitly belong to the selected project. Connections use SQLite URI `mode=ro` and close deterministically. If the benchmark DB does not exist, listing is empty and DOES NOT create a database.
- Summary endpoint validates the original report semantics via `benchmark_report_summary.summarize_benchmark_report`: completed/failed/cancelled, duration sample count/min/median/max and missing measures, null per-job VRAM, no automatic model ranking. Does not reveal graph JSON, model input prompts, stored error text, output filenames or source media. No mutation routes.
- New responsive `GUI/benchmark_reports.html` opens as `/workspace/benchmark` and can be reached from the **Projects** workspace. The report page has Spanish/English switch, project and run selectors, status and summary table; it does not itself generate or import anything. UI uses `textContent`, not arbitrary HTML from the database.
- `scripts/workspace_routes.py` mounts the read-only endpoints and local-only reports HTML. **No existing generation, training, dataset or ComfyUI route behavior changes**. There are no writes to Benchmark database.

Seven new isolated, mocked/fixture Flask route tests cover missing DB, per-project index/counts, existing metrics, cross-project denial, remote access, invalid IDs and malformed database. Following the operator-reported 127 tests, **134 benchmark tests expected**. User acceptance pending; no new GPU generation required.

```powershell
git pull --ff-only
.\\venv\\Scripts\\python.exe -m unittest discover -s tests -p "test_benchmark_reporting_routes.py" -v
.\\venv\\Scripts\\python.exe -m unittest discover -s tests -p "test_benchmark*.py" -v
```
Restart OrkiLab launcher to load the new route, then navigate via **Workspace → Projects → Benchmark Studio** or directly to `http://127.0.0.1:4990/workspace/benchmark`. If no saved benchmark runs exist, an empty-state message is correct; never fabricate runs. The feature branch and draft PR #104 remain open. Next gates: clearer comparison protocol and comparability markers, controlled real execution evidence, tests/CI and RC review. The requested per-workflow error catalogue remains deferred.

## B9.2 operator acceptance / B9.3 conservative comparability evidence (operator tests pending)

The operator confirmed `todo ok` following B9.2 testing and UI walkthrough, recorded as **134/134 benchmark tests and first reports UI operator-reported PASS** (raw console output not attached in this turn). The next slice establishes a cautious, *explainable non-ranking* diagnostic, not a benchmark speed winner.

B9.3 adds `scripts/benchmark_comparability.py` and integrates `assess_duration_comparability` into the existing local-only GET report. The endpoint now reads **only lineage for observations of the exact requested run** through SQLite `mode=ro`, filtering to a minimal internal set of workflow ID, submitted graph SHA-256 and ComfyUI execution-timing provenance. The public report exposes only per-variant status, measured/completed sample counts and coded reasons (no full prompts, graph, source images or raw lineage). The UI displays a new bilingual comparability table. A sampler **explicitly recorded as cached** or multiple differing workflow IDs *inside the same variant* trigger `blocked`; absent proof of hardware, seed, cache warmth and full inference remains `not_established` even when all observed times exist. A changed graph SHA within a variant is flagged as requiring review (may be a legitimate deliberate variable), never automatically called an error. **No variant is marked verified comparable, ranked or winner.** This is intentionally conservative until a future measurement protocol captures independently verified equivalence. Raw observation durations remain unchanged; global NVIDIA VRAM samples do not become job-level VRAM peaks.

Eight new pure synthetic evidence tests and one Flask report integration test added; **143 total benchmark tests expected** after the operator-reported 134 baseline. No ComfyUI run is necessary for these tests.

```powershell
git pull --ff-only
.\\venv\\Scripts\\python.exe -m unittest discover -s tests -p "test_benchmark_comparability.py" -v
.\\venv\\Scripts\\python.exe -m unittest discover -s tests -p "test_benchmark_reporting_routes.py" -v
.\\venv\\Scripts\\python.exe -m unittest discover -s tests -p "test_benchmark*.py" -v
```

Restart the OrkiLab launcher and open `http://127.0.0.1:4990/workspace/benchmark`. A new **Comparabilidad de resultados** section should appear for a selected stored run, with `No acreditada` or `Bloqueada` and specific reason codes. If no run is saved, there is correctly nothing to compare. Do not merge PR #104 or release 0.6.0 from B9.3 alone; pending: richer benchmarking protocol, explicit evidence approval, complete UI flow, CI/regression reviews and user acceptance. The workflow error catalog remains deferred by operator request.

## B9.3 operator acceptance / B9.4 versioned reproducibility declarations

The operator introduced **`tok` = `todo OK`** and explicitly confirmed B9.3 after the Windows test checklist. This is treated as **operator-reported 143/143 tests PASS** (raw command output not included in this turn). Future short `tok` messages mean the operator confirms the immediately requested tests/verification as successful; do not mistake them for a recorded CI run.

B9.4 adds a **pure, opt-in declaration contract** in `scripts/benchmark_repro_protocol.py` under `schema: "orkilab-repro-v1"`. The run-level declaration specifies the *single variable allowed to change* (`checkpoint` or `lora`), workflow ID, SHA-256 digests of positive prompt, negative prompt and input image/content, NVIDIA GPU UUID, cache policy (`cold` or `warm_sampler`), seed policy (`fixed` or `enumerated`), 1–100 planned repetitions and resolution width/height. Each variant must declare its distinct `controlled_value`. A graph override or variant variable mismatch requires independent review; missing fixed-field declarations or fewer than two variants are flagged. This is not an attempt to validate the actual ComfyUI graph, model hashes or hardware. A declaration could be inaccurate: the module explicitly marks a complete declaration **`declared_unverified`**, not fully comparable, never a ranked/winning model. Existing legacy run protocols (arbitrary stored JSON) remain **`legacy_unverified`** and continue to work without database migration.

The existing project-scoped, launcher-local **read-only** report detail endpoint now adds a `reproducibility_protocol` diagnostics object with status and coded reasons, but no raw prompt, source hash, model path, secret or full protocol payload. The bilingual report UI displays a new **Protocolo reproducible** section clearly distinguishing declarations from evidence. All operations remain read-only and no generation or GPU sampling is triggered. This module **does not add an editing/creation UI** or mark pre-existing benchmark runs invalid. A future separate workflow will collect/confirm these declarations with clear user consent.

Ten new pure tests and one Flask integration test: **154 benchmark tests expected** after the operator-reported 143 baseline; pending Windows operator verification.

```powershell
git pull --ff-only
.\\venv\\Scripts\\python.exe -m unittest discover -s tests -p "test_benchmark_repro_protocol.py" -v
.\\venv\\Scripts\\python.exe -m unittest discover -s tests -p "test_benchmark_reporting_routes.py" -v
.\\venv\\Scripts\\python.exe -m unittest discover -s tests -p "test_benchmark*.py" -v
```
Restart the OrkiLab launcher and inspect `http://127.0.0.1:4990/workspace/benchmark` with a saved run: legacy runs should explicitly say **Sin protocolo versionado; evidencia no acreditada**, rather than generating a guessed protocol or ranking. Feature PR #104 stays draft/open and must NOT merge or claim 0.6.0 release from this slice. The operator explicitly deferred the per-workflow error catalogue.

## B9.4 operator acceptance / B9.5 guided and explicitly confirmed inactive protocol drafts

Operator replied **`tok`**, explicitly defined by the operator as **`todo OK`**, after the B9.4 test checklist. Record **154/154 as operator-reported**, without raw test logs or CI claims.

B9.5 introduces `scripts/benchmark_draft_creation.py`, an explicit-confirmation validator and an atomic SQL transaction that creates **only** a new `draft` benchmark run and its 2–20 uniquely named variants. The input contains a versioned `orkilab-repro-v1` protocol declaring workflow ID, fixed prompt/input SHA-256 fingerprints, an NVIDIA GPU UUID, seed/cache policies, resolution, repetitions and *one* varied checkpoint or LoRA field. The creation contract checks `declared_protocol_readiness` before writing; unknown or incomplete declarations are rejected. A new launcher-local JSON POST `/api/workspace/benchmark/drafts` validates the selected project is active using read-only access to the existing projects database. An archived/nonexistent project, remote caller, incomplete JSON, missing explicit confirmation, duplicate variant label or duplicate controlled value is rejected. Saving a draft **does not execute a workflow, transition the run to running or create observations**. No existing runs or observations are modified. The new responsive bilingual reports page contains a collapsible protocol-draft form that appears separately from the read-only reports. Users must manually supply SHA-256 fingerprints corresponding to the real inputs; these declarations are **not** verification of runtime equivalence and they do not automatically rank variants.

Seven pure draft-creation tests (validation, no writes on rejection, project mismatch, duplicate values, atomic draft persistence) and two HTTP tests (successful draft with 2 variants/zero observations, remote/archived/invalid denied) added; **163 benchmark tests expected** after the operator-reported 154 baseline. These tests use isolated SQLite fixtures, **no actual ComfyUI generation or GPU sampling**. The normal report reads remain read-only. As the UI now explicitly supports draft creation, the top report remains read-only but the separate opt-in creation control is intentionally a write operation.

```powershell
git pull --ff-only
.\\venv\\Scripts\\python.exe -m unittest discover -s tests -p "test_benchmark_draft_creation.py" -v
.\\venv\\Scripts\\python.exe -m unittest discover -s tests -p "test_benchmark_reporting_routes.py" -v
.\\venv\\Scripts\\python.exe -m unittest discover -s tests -p "test_benchmark*.py" -v
```

After restarting the OrkiLab launcher, `http://127.0.0.1:4990/workspace/benchmark` displays a new **Crear protocolo de Benchmark (borrador)** section. It should not submit any inference on its own. A real draft should only be created when the operator has their own actual hashes, model/variant identifiers and deliberately opts in; no fake hashes should be used for a real report. The feature PR #104 stays open. Defer the requested per-workflow error catalogue.

## UX correction following operator feedback — Benchmark shell integration and Spanish accents

The operator reported that the B9.5 Benchmark Studio interface was **visually inconsistent with OrkiLab, isolated from the app's sections, and displayed unsatisfactory Spanish accents/copy**. This is **not** acceptance of B9.5's tests: previous **154 benchmark tests** remain the last operator-reported validated baseline; 163 B9.5 tests had been requested but not yet confirmed.

Corrections on feature branch:
- Benchmark Studio now has an **explicit navigation entry inside Workspace → Zona ComfyUI**, with its own `#benchmark` module panel, normal OrkiLab header, sidebar navigation, contextual help, and scroll-to-top behavior. The module remains accessible **without a live ComfyUI connection**, since reading reports and preparing draft protocols are offline activities; it does not unlock model-dependent tools when ComfyUI is disconnected.
- The existing `/workspace/benchmark` URL redirects to `/workspace/comfyui#benchmark` to eliminate a confusing second top-level destination. The embedded report surface uses `/workspace/benchmark?embed=1` within the normal shell; origin-validated messaging synchronizes Spanish/English and adjusts iframe height without including a second navbar/header. No extra iframe origins are allowed; all API restrictions remain launcher-local.
- The report surface now adopts the OrkiLab core palette (**#0b1221 background, #152238 panels, #3cdbd0 accent**), matching font scale, form controls and responsive layout; favicon updated. Large forms use a responsive grid.
- Spanish labels and accents were reviewed, including readable Spanish translations of evidence codes instead of raw English snake_case descriptions, and controls for cache/seed policy. The source declares UTF-8 and writes text with `textContent`.
- Navigation from main Workspace Projects now targets the embedded module. No benchmark database or run observation migrations or execution behavior changed.

**Four new regression tests** in `tests/test_benchmark_workspace_integration.py` check nav, module, theme, redirects, UTF-8 Spanish and translated reasons. **167 benchmark tests expected** when B9.5 and integration tests are included (last user-confirmed baseline 154; neither 163 nor 167 are yet operator-verified). These are static checks, not a pixel-level browser screenshot; manual Windows visual inspection and Spanish/English text review remain required.

```powershell
git pull --ff-only
.\\venv\\Scripts\\python.exe -m unittest discover -s tests -p "test_benchmark_workspace_integration.py" -v
.\\venv\\Scripts\\python.exe -m unittest discover -s tests -p "test_benchmark*.py" -v
```

Restart OrkiLab's Python launcher, open `http://127.0.0.1:4990/workspace/comfyui#benchmark`. Verify active left-hand **Benchmark Studio** navigation, only one OrkiLab header, cohesive page colors and mobile width, expected Spanish tildes (e.g. **Ejecución, Política, Resolución, generación, caché**), in-page bilingual switch behavior, no generation submission on viewing/switching sections. Route `/workspace/benchmark` should redirect to the same module. Preserve the operator-requested deferred per-workflow error catalogue.

## Critical B9 navigation regression — corrected after operator report

The operator reported that clicking the Benchmark link opened the main page and that the Workspace language selector stopped responding. Investigating the **actual shipped inline Workspace JavaScript** identified a fatal syntax error in the new Benchmark language-change listener: the source contained a malformed regex literal `/\\\\/$/` rather than the proper trailing-slash regex `/\\/$/`, so the browser could not parse the entire inline Workspace script. This caused **all its event handlers not to initialize**, not only Benchmark navigation. Corrected in commit `6be17c3`. The Workspace and standalone embedded benchmark inline JavaScript blocks were both syntactically compiled (without execution) via a JS parser check following this correction. Added a specific static regression test guarding the route normalization literal to `tests/test_benchmark_workspace_integration.py`. The rest of the application and database are unchanged.

After `git pull --ff-only` on the `feat/0.6-benchmark-core` branch and launcher restart, force reload with Ctrl+F5 and verify: Spanish/English switch responds, main dashboard/Projects navigation responds, ComfyUI Zone sidebar lists Benchmark Studio and clicking it renders the panel at `/workspace/comfyui#benchmark`. As no operator validation has yet followed these fixes, do NOT mark the UX issue accepted. **168 total benchmark tests expected** (previous 167 expected plus 1 regression; baseline 154 confirmed, remainder pending). Reproducible check: parse every inline `<script>` from `GUI/workspace.html` and `GUI/benchmark_reports.html`, not merely string-search for nav labels.

## B9 Spanish accent issue in “Selecciona ejecución” dropdown — display-only remediation

Operator reported that some Spanish accent characters in the **run-selection dropdown options** appear malformed after the JS navigation fix. Source review confirmed the static UTF-8 placeholder `Selecciona una ejecución` and Spanish translated states already contain correctly accented Unicode characters in `GUI/benchmark_reports.html`, while option labels also interpolate **run names from the existing SQLite database**, which can have legacy mis-decoded character sequences. Without the exact example/raw DB, this is a plausible source rather than a proven root cause.

The report UI now applies `readableName()` to the **displayed** project name, run name in dropdown options and report heading. Only text matching common UTF-8 → Western-byte mis-decoding markers is considered for a **strict, fatal UTF-8 re-decoding**; on any exception, malformed bytes or nonmatching Unicode, it leaves the input unchanged. No names/IDs in SQLite are rewritten, no data migrations, and no HTTP query parameter changes. The known Spanish placeholder and statuses remain translated using ordinary UTF-8. Added two static regression checks in `tests/test_benchmark_workspace_integration.py`. These protect against reintroduction but **cannot establish whether the operator observed an underlying mis-encoded persisted run name or an incorrect HTTP charset header**, nor replace a real browser check.

After updating the feature branch, restarting the Python launcher and Ctrl+F5 refresh, inspect the dropdown in `/workspace/comfyui#benchmark`. If still wrong, capture a **literal example of the broken text** and note whether the placeholder or a named run is affected; investigate actual response bytes/headers before changing stored data. Expected total benchmark test count after this change: **170** (previous 168 + 2), still pending operator verification. Do not confuse this fix with the separately deferred workflow-compatibility error register.

## Confirmed run title with irrecoverable question marks

The operator supplied the exact malformed text **`vinculaci?n autom?tica`** in the context of the Benchmark Studio run selector. This is materially different from recoverable UTF-8 mojibake (`vinculaciÃ³n`); the original characters have already become literal question marks, so a general Unicode decoder cannot restore them. A bounded **display-only** exact Spanish phrase substitution in `GUI/benchmark_reports.html` shows `vinculación automática` (respecting initial capitalization). It does not change persisted SQLite data, run IDs, report semantics or unrelated question marks. The original unknown upstream encoding/serialization boundary still needs a sample of a new run or raw DB content to diagnose and repair universally; do not claim general resolution for other lost characters. A regression check was added to `tests/test_benchmark_workspace_integration.py`. Operator acceptance remains pending. Total expected benchmark tests: **171** (previous 170 expected + 1).
