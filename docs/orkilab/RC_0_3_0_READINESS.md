# OrkiLab 0.3.0-rc.1 — release readiness and evidence register

**Date:** 2026-11-21  
**Status:** NOT READY TO TAG. This is a release-candidate readiness record, not release notes or a declaration of acceptance.  
**Version in published main at initial review:** `VERSION_ORKILAB = 0.2.0-rc.1`. **This release candidate branch proposes `0.3.0-rc.1`; it is not yet tagged or released.**  
**Baseline:** refreshed from `main` after CI PR #39 and acceptance documentation PR #41. Record the exact candidate SHA before tagging.

## Rules for recording evidence

- `PASS` requires an identifiable run, observed result and environment (commit SHA, Windows/Linux, GPU, ComfyUI Desktop version where relevant).
- `REPORTED` means the operator says they exercised a scenario, but no per-case pass/fail log is attached. It is **not** equivalent to `PASS`.
- `NOT VERIFIED` means no sufficient evidence has been recorded; it does not imply failure.
- `BLOCKED` means a failing critical release gate with reproducible evidence.
- `NOT APPLICABLE` requires a reason (e.g. multi-GPU on a single-GPU machine).

Do not convert reported successes into PASS by inference; do not fabricate screenshots, logs or test output.

## Candidate scope / freeze

Focus on stable ComfyUI connection, discovery, trusted workflow import/Bridge, explicit execution with cancellation/progress/history, optional resource release and diagnostics, read-only GPU Manager, and preserved trainer launching and queue. The existing LoRA Comparator remains available as an **experimental, not-yet-validated feature**; its GPU acceptance is deferred beyond rc.1. **Do not block this RC on the full rewrite of every trainer UI, Dataset Studio, multiview, Ollama, Hub or installer.** See [roadmap](ROADMAP.md).

## Gate checklist

| Gate | Status as of review | Proof needed | Blocking when failing? |
| --- | --- | --- | --- |
| Windows CI unit tests | PASS — PR #42 head (before latest docs edit) | RC run 44847212885 + foundation run 44847212900; rerun on final merged commit | Yes |
| Linux CI unit tests | PASS — PR #42 head (before latest docs edit) | RC run 44847212885 + foundation run 44847212900; rerun on final merged commit | Yes |
| Browser trainer smoke test | REPORTED PASS — full local suite | User confirms all trainers OK after 3/3 observed sample; exact count, log and SHA not attached | Yes for regression |
| Workspace/ComfyUI connection gate | REPORTED PASS — disconnect state | Operator confirms correct ComfyUI disconnected-state display; connect and broader routes not separately evidenced | Yes |
| API-format workflow prepare/execute | REPORTED | Trusted graph identifier, status and output | Yes |
| Bridge conversion of visual workflow | REPORTED | Graph, preparation stages, actual converted run | Yes |
| Progress and safe cancel | REPORTED PASS — generation cancellation, other work unaffected | Operator confirmation; pending vs active cases and logs not specified | Yes |
| History, result downloads, media previews | REPORTED PASS — generated image appears in history | Operator confirmation; refresh persistence, download and video/audio formats not yet verified | Yes for supported types |
| RAM/VRAM diagnostics and optional release | REPORTED PASS — RAM/VRAM before/after model release | Operator confirmation; numerical measurements and peak not attached | Yes for advertised scope |
| GPU Manager single-GPU RTX 3090 | REPORTED | Compare telemetry against `nvidia-smi` | Yes |
| Multi-GPU hardware | NOT VERIFIED | Two-adapter setup or explicit NOT APPLICABLE with reason | No if appropriately scoped |
| LoRA Comparator standard-loader path | DEFERRED — not verified in this RC | Do not claim comparator stability; run two-strength test before a later validated release | No — explicitly excluded from rc.1 acceptance |
| 8-language Workspace navigation | NOT VERIFIED | Browser screenshots/smoke, English fallback | Yes for UI regression |
| Trainer representative image/video/audio | NOT VERIFIED | Brief per-family tests, saved settings parity | Yes for regression |
| Failure handling / auth / invalid node | REPORTED PASS — invalid workflow, offline state | Operator tested an invalid workflow and earlier disconnected-state behavior; malformed-graph details, auth and hostile/unauthorized requests NOT VERIFIED | Yes — remaining critical cases |
| Preservation and safe update | REPORTED PASS — safe update | Operator confirms updating OrkiLab preserved projects, settings and workflows; exact SHA and data inventory not attached | Yes |
| Changelog, README, limitations | PARTIAL | Updated results and known limitations before tag | Yes |

Some user-reported hands-on runs are documented in project conversations; the evidence matrix [GPU_GENERATION_ACCEPTANCE.md](GPU_GENERATION_ACCEPTANCE.md) still shows `NOT TESTED` for the individual scenarios. Record observed outcomes there before setting this gate to PASS.

**CI observation:** both GitHub Actions workflows completed successfully on the PR #39 branch (Windows and Linux), as detailed below. **Exact-final-release-commit** verification remains necessary.

## Recorded Windows smoke-test evidence (user-reported, 2026-11-21)

The user ran from `D:\\orkilab\\orkilab-lora-trainerstudio` with the project's virtual-environment Python:

```powershell
.\venv\Scripts\python.exe tools\smoke_test_ui.py --only sdxl,wan22,yue2 --keep
```

**Observed console result:** `OK sdxl`, `OK wan22`, `OK yue2`, **`3/3 OK`**. Preserved logs for `server_sdxl`, `server_wan22` and `server_yue2` each contained `Serving Flask app` and `Debug mode: off`, with no reported startup exception. The earlier run via plain `python` yielded `0/3 OK` (servers did not start), suggesting an interpreter/environment mismatch; the exact earlier traceback was not preserved.

This is **user-supplied evidence for the headless UI smoke test**, not an independent CI pass or proof of full GPU training. The script intercepts process starts and checks UI-triggered actions without running actual GPU jobs. The exact tested Git SHA was not supplied, and only three trainers were covered. A full smoke run and precise candidate-SHA verification remain necessary. The separately reported successful ComfyUI image generation is real-workflow evidence but does not turn these mocked trainer runs into GPU validation.

## Additional operator test report (2026-11-21)

After the observed `3/3 OK` representative UI test, the operator was asked to run:

```powershell
.\venv\Scripts\python.exe -m unittest discover -s tests -v
.\venv\Scripts\python.exe tools\smoke_test_ui.py --keep
```

The operator replied **"todo ok"**, which is recorded as **reported success for both the local Python unit-test suite and the full headless trainer UI smoke suite**. The exact totals, execution transcript, commit SHA and GitHub Actions job URLs were **not supplied**; the result is therefore a reported local pass, not independently confirmed CI on Windows and Linux. The smoke tool simulates training actions rather than running GPU training.

Remaining independent gates include release-commit CI on Windows/Linux, complete ComfyUI cancellation/foreign-queue safety, persistent history/media and resource-release checks, negative tests, language/upgrade validation and final versioned release notes.

## ComfyUI final-check operator report (2026-11-21)

The operator submitted five manual-check outcomes for the local OrkiLab–ComfyUI setup. These are **user-reported PASS results**, not independently collected logs or screenshots; no test commit SHA, ComfyUI version, before/after memory values or workflow identifier was supplied.

| Manual check | Operator result | What this supports / limitations |
| --- | --- | --- |
| Generate one image and verify its appearance in generation history | **REPORTED PASS** | Image-generation/history pathway; does not establish persistence after restart or audio/video outputs |
| Cancel a generation without disturbing other jobs | **REPORTED PASS** | General cancellation isolation; pending and active cancellation subcases not individually recorded |
| Check RAM and VRAM before/after releasing ComfyUI models | **REPORTED PASS** | Model-release flow and memory readings; no measured values or peak attribution recorded |
| Disconnect ComfyUI and confirm OrkiLab displays disconnected state correctly | **REPORTED PASS** | UI disconnected-state handling; invalid input/auth failure not inferred |
| Run a comparison of two LoRA strengths | **DEFERRED / NOT TESTED** | Existing interface remains experimental; no assertion that comparisons or particular LoRAs work in rc.1 |

**Do not misinterpret** reported image-history success as verified outputs for all media, or the broad cancel success as proof of the exact E03/E04 adversarial queue scenarios. Preserve those detailed cases as `NOT TESTED` in the separate GPU acceptance matrix until scenario-specific evidence exists. Windows/Linux GitHub CI on release commit, negative security/invalid-node checks, navigation/i18n and update-safety review remain to be closed before tagging. Comparator acceptance is deferred and must not be presented as complete.

## Verified CI results for PR #39 (2026-11-21)

GitHub Actions returned **completed / success** for the following workflow runs associated with commit `1ce30c6182e486160c17e59e2842db27b99e4f05`:

- **OrkiLab RC validation**, run ID `44846938042`: `Python unit tests (windows-latest, Python 3.13)` **success**, `Python unit tests (ubuntu-latest, Python 3.13)` **success**.
- **OrkiLab foundation checks**, run ID `44846938103`: `tests (windows-latest)` **success**, `tests (ubuntu-latest)` **success**.

PR #39 was merged into `main` with squash commit `289e6859843c1bf6c93591a84023eaca943ac4f2`.

**Scope note:** CI on the PR branch is confirmed. The combined-status and PR-workflow-only queries have **not** yet established successful runs on the eventual final `v0.3.0-rc.1` commit. Repeat or verify both platform checks for the exact release SHA before tagging. These are GPU-free tests; they complement, rather than replace, real on-device ComfyUI acceptance.


## Candidate branch preparation (2026-11-21)

The proposed version bump, README badge and changelog from draft PR #40 have been reapplied onto current `main` on branch `release/0.3.0-rc.1-final-checks`, which includes the merged Windows/Linux CI workflow. **The branch is a candidate, not a publication.** Both CI platforms must pass on this branch and on the final merged/tagged release commit. The user reported successful local tests and core ComfyUI scenarios, but missing failure/upgrade screenshots or logs remain unverified and must not be inferred as passed.

## Final operator acceptance: invalid workflow and upgrade (2026-11-21)

The operator explicitly reported:

| Scenario | Operator result | Recorded limitation |
| --- | --- | --- |
| Invalid workflow | **REPORTED PASS** | The specific error type, before/after queue state and failure message were not supplied; do not extrapolate to unauthorized connections, custom-node failures or other malformed inputs |
| Safe OrkiLab update | **REPORTED PASS** | Exact before/after SHA and backed-up data inventory were not supplied; does not prove clean-install portability or rollback |

**Four CI jobs verified on PR #42 head commit `52b4a98f3089c26ce8201cf37d0f25dd1f7a55a4`:** run `44847212885` (`OrkiLab RC validation`) passed Python 3.13 on Windows and Ubuntu; run `44847212900` (`OrkiLab foundation checks`) passed on Windows and Ubuntu. These results are independently verified GitHub Actions outcomes for the candidate prior to this documentation edit, **not** proof of the final merge commit.

### Still to resolve before tagging

- Unauthorized remote access and sensitive-data safety have not been explicitly exercised as acceptance cases. Do not claim security validation based on the invalid-workflow test.
- Multi-language navigation/fallback, exact GPU sensor parity and every media-preview format have not been separately verified. Document these as RC limitations or run the missing cases.
- Confirm the final PR SHA checks and the eventual `main` release SHA are green. The detailed scenario-specific GPU matrix still has unchecked entries; the operator-level checklist must not be misrepresented as equivalent evidence.
- No tag or GitHub prerelease should be called published without a successful GitHub action creating them.

## Suggested safe operator command sequence

Run in the local Windows installation with ComfyUI Desktop; stop on errors rather than resetting uncommitted work:

```powershell
git status --short
git branch --show-current
git switch main
git pull --ff-only origin main
git rev-parse HEAD
python -m unittest discover -s tests -v
python tools/smoke_test_ui.py --only sdxl,wan22,yue2
nvidia-smi
```

The browser smoke test needs a supported Chrome/Edge/Chromium and uses an isolated temporary worktree, so inspect its tool documentation if dependencies or git state are unusual. The selected three trainers are **representative**, not proof that every engine is verified.

Then follow the step-by-step [GPU/Generation acceptance matrix](GPU_GENERATION_ACCEPTANCE.md), including Bridge installation and restart, safe cancellation of only OrkiLab-owned jobs, valid/invalid sampler input, media results, RAM/VRAM and GPU sensor sampling. Keep custom workflow files, tokens and private paths out of public attachments.

## Blockers and safe scope decisions

- **Mandatory:** no critical data loss; no unwanted queue manipulation; no execution on import; canceled runs do not terminate unrelated jobs; offline/disconnected state remains usable; supported workflows complete with accurate status; tests pass.
- **Permissible with clear release notes:** unsupported third-party nodes, exact overall percentage unavailable, multi-GPU not physically tested where only one adapter exists, downloadable mesh without interactive 3D, incomplete legacy trainer translations and incomplete full trainer UI migration.
- Do not widen the feature freeze or claim every custom workflow is compatible.

## Release procedure — only after PASS evidence

1. Ensure no unresolved critical blocker; review `git status` on the candidate and confirm passing Windows/Linux CI, browser and on-device tests.
2. Update `VERSION_ORKILAB`, `GUI/launcher.json`, the README version badge and any other canonical version references **in one release PR**, avoiding inconsistent version strings.
3. Update `CHANGELOG_ORKILAB.md`, README's development/test caveats and `GPU_GENERATION_ACCEPTANCE.md` to reflect actual evidence; document limitations explicitly.
4. Merge reviewed release PR into `main`, confirm checks on exact release commit, and create Git tag `v0.3.0-rc.1` **pointing to that commit**.
5. Publish a GitHub prerelease with installation/update and rollback instructions, supported workflow examples, known issues and links to the evidence.
6. Retain prior candidate as rollback option; do not force-reset or overwrite datasets, workflows, settings or outputs.

**Next decision:** PR #42 is the candidate. Confirm remaining security/error cases and exact-release-commit CI, then publish if no critical risk is outstanding. The experimental LoRA Comparator is not a release gate.
