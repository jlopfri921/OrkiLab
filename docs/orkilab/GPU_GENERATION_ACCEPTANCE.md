# OrkiLab — GPU Manager + ComfyUI Generation acceptance (2026-11-21)

**Scope:** combined behavior of merged PR #10 (Bridge preparation, execution progress, cancellation) and PR #9 (multi-GPU telemetry). This checklist is not evidence of successful hardware validation. Do not remove legacy trainer views or call the release stable until representative trainer jobs have passed.

## Baseline and evidence

- Record Git commit SHA (`git rev-parse HEAD`), OS, NVIDIA driver (`nvidia-smi`), ComfyUI Desktop version and OrkiLab URL (`http://127.0.0.1:4990`).
- Before updating, preserve user datasets, settings, workflows and outputs. Inspect `git status`, `git branch --show-current`, and `git remote -v`; do not discard local changes.
- With clean checkout: `git switch main` followed by `git pull --ff-only origin main`. If rejected, investigate rather than forcing.
- Run `python -m unittest discover -s tests -v`. Optional browser smoke test: `python tools/smoke_test_ui.py` in the appropriate environment.
- Open OrkiLab and reinstall the OrkiLab Bridge from the ComfyUI Zone, restart ComfyUI Desktop, then hard-reload the ComfyUI browser UI. An older installed Bridge lacks the latest stage messages.
- Use only trusted workflows/custom nodes; start with no unrelated active work in the shared ComfyUI queue.

## Acceptance matrix (fill in PASS / FAIL / NOT TESTED)

| ID | Scenario and expected evidence | Result | Notes |
| --- | --- | --- | --- |
| G01 | Workspace opens from both `/` and `/workspace`, and navigation to GPU Manager works with no blank content | NOT TESTED | |
| G02 | RTX 3090 is listed with reasonable VRAM total/free/used, GPU utilization and temperature compared with `nvidia-smi` | NOT TESTED | |
| G03 | Where supported, power draw/limit, fan %, clock speeds, driver and PCI bus appear; unavailable sensors are displayed as unavailable rather than zero | NOT TESTED | |
| G04 | With more than one NVIDIA adapter installed, each gets a separate card and totals refer to the correct devices (skip if only RTX 3090 present) | NOT TESTED | |
| G05 | GPU telemetry updates while generating, without restarting a trainer or interrupting the workflow | NOT TESTED | |
| B01 | Trusted visual workflow is prepared via installed Bridge; progress shows the conversion stages, not a fabricated precise workflow percentage | NOT TESTED | |
| B02 | Cancelling Bridge preparation closes the popup and does not queue generation | NOT TESTED | |
| B03 | API-format workflow prepares without Bridge; COMBO sampler scalar inputs accept valid choices, reject invalid choices with understandable errors | NOT TESTED | |
| E01 | Explicitly confirmed generation enters ComfyUI queue; execution view shows prompt/node/step progress when ComfyUI supplies them | NOT TESTED | |
| E02 | WebSocket updates are attributed only to the submitted prompt; HTTP status polling remains authoritative for completion | NOT TESTED | |
| E03 | Cancelling an OrkiLab-owned pending prompt removes only that prompt, preserving other queue entries | NOT TESTED | |
| E04 | Cancellation of active work is only attempted when safe; with unrelated ComfyUI jobs, OrkiLab refuses unsafe interruption | NOT TESTED | |
| E05 | After completion or cancellation, history accurately records terminal state; images/video/audio/mesh output links behave as applicable | NOT TESTED | |
| R01 | Dashboard, Projects, Engines, ComfyUI Zone and GPU Manager remain navigable after generation/cancellation | NOT TESTED | |
| R02 | Representative trainer from image, video and audio families opens and runs a *small authorized smoke job* without regression (record per-engine evidence) | NOT TESTED | |
| L01 | Progress, errors, cancellation and GPU labels translate appropriately in all supported locale options | NOT TESTED | |

## Operator-reported final checks (2026-11-21)

These results were provided by the operator through the release-readiness checklist. `REPORTED PASS` means the operator confirmed the scenario; no screenshots, logs, GPU readings, test commit SHA or workflow JSON are attached. This register does not convert narrower tests in the technical matrix above into PASS where their full expectations were not explicitly checked.

| Scenario | Result | Important qualification |
| --- | --- | --- |
| Generate image and find it in OrkiLab history | **REPORTED PASS** | Image path only; output persistence across refresh/restart and other media types not yet recorded |
| Cancel generation without affecting other jobs | **REPORTED PASS** | Active/pending distinctions and queue state logs not recorded |
| Observe RAM/VRAM before and after releasing ComfyUI models | **REPORTED PASS** | Numerical measurements, peak and process attribution not recorded |
| Disconnect ComfyUI; OrkiLab reflects disconnected state | **REPORTED PASS** | Does not cover all authentication, malformed workflow or offline cases |
| Compare two LoRA strengths | **DEFERRED — NOT TESTED** | UI remains experimental; comparator is outside the 0.3.0-rc.1 acceptance gate and is not certified |

See [the 0.3.0-rc.1 release readiness register](RC_0_3_0_READINESS.md) for publication gates. Windows/Linux CI evidence, detailed queue-safety cases, failures/recovery, multi-format media, i18n and upgrade checks remain open.

## Additional operator acceptance results (2026-11-21)

After the earlier four reported successful ComfyUI checks, the operator confirmed:

| Scenario | Result | Limits of evidence |
| --- | --- | --- |
| Reject / handle an invalid workflow | **REPORTED PASS** | Exact invalid graph, error message, authorization outcome and queue changes were not provided. Does not cover all B03 or security cases |
| Update OrkiLab without losing projects, settings or workflows | **REPORTED PASS** | Exact source/target SHA, backup details and data directory diff were not provided. No evidence of installer/rollback validation |

The two outcomes above are user-reported application-level checks. They **do not retroactively mark G01–L01 individual matrix rows as PASS** when those rows demand additional evidence. CI Windows/Linux on the PR #42 candidate commit passed both foundation and RC validation suites (run IDs `44847212900` and `44847212885`); final merge commit still needs verification.

## Manual test procedure

1. Capture idle `nvidia-smi` before opening GPU Manager; compare available sensor fields without treating missing telemetry as a fatal error.
2. Import a known-good API workflow and the previously successful visual workflow. Prepare visual via Bridge and document each stage.
3. For the API workflow, test editable sampler option and a deliberately invalid option. Do **not** assume fixing a COMBO error validates every remaining node.
4. Submit a small workflow explicitly. Observe node updates and progress while viewing GPU Manager in another tab; capture GPU/VRAM/temp before/during/after.
5. Repeat with a longer but safe workflow to test cancellation. First cancel when pending, then (if queue is otherwise empty) attempt an active job cancellation.
6. Create a separate unrelated ComfyUI queue entry and confirm OrkiLab does not clear or interrupt it. Do not test active cancellation with irreplaceable user work.
7. Open the generation history, download/preview available output types and confirm terminal status is preserved across refresh.
8. Perform navigation/translation checks and small representative image/video/audio trainer smoke tests; preserve logs of any failure.

## Expected limitations (not failures by themselves)

- Whole-workflow percentage cannot be exact unless ComfyUI supplies a meaningful denominator; sampler step percent is local to that sampler.
- Cancellation cannot guarantee instantaneous GPU interruption.
- The manager monitors NVIDIA sensors read-only: it does not allocate GPUs or unload models.
- Real multi-GPU testing requires multiple devices and must not be marked PASS on a single-GPU PC.

## Failure report template

- Test ID, result, commit SHA, locale and OS:
- ComfyUI Desktop / NVIDIA driver version:
- What was clicked and the exact error message:
- Expected vs. observed:
- Queue state before and after:
- Relevant browser Console / OrkiLab terminal log (redact secrets and local private paths):
- Reproducible workflow JSON without private data:

**Release gate:** when any E/B/G critical result fails, create an issue referencing this checklist; keep stable release blocked. Never force-reset user work. Prefer reverting a regression commit in a dedicated PR after identifying the cause.
