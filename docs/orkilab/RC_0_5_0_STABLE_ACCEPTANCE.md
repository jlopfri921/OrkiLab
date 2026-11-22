# OrkiLab 0.5.0 — stable publication acceptance

**Status: manual H1–H7 acceptance SIGNED OFF by operator on 2026-11-22; final CI and publication checks remain pending.** RC.1 has been [published](https://github.com/jlopfri921/OrkiLab-LoRA-TrainerStudio/releases/tag/v0.5.0-rc.1). The original 7/7 on-device report covered Multiview PRs #80–#85, but later changes #86–#99 were not all independently validated. This checklist records the operator's affirmative PASS confirmation, not independently captured logs or universal compatibility.

## Supported scope for the first stable release

- Windows local OrkiLab launcher, local ComfyUI, and one documented supported SD-compatible img2img workflow/model. Other ComfyUI/Custom Node combinations remain best-effort.
- Project-linked Multiview subject/gallery; non-destructive references, review, qualitative viewpoint suggestions, explicitly generated synthetic image review, deterministic grouped dataset ZIP, contextual help and optional GPU tools.
- The three included core Img2Img starter graphs **do not guarantee camera pose or geometric fidelity**. Qwen Image Edit, FLUX/Klein camera control and true multi-reference editing remain **future features**.
- Do not imply each trainer, ComfyUI Desktop and Portable, or GPU is validated merely because one setup works.

## Manual hardware checks — user reports all seven performed (2026-11-22)

**Operator report:** On 2026-11-22, the user selected H1, H2, H3, H4, H5, H6 and H7 in the validation checklist and submitted: *"He completado estas pruebas de OrkiLab 0.5.0: H1, H2, H3, H4, H5, H6, H7."* The operator additionally confirmed on 2026-11-22: **"Confirmo que las siete pruebas H1–H7 de OrkiLab 0.5.0 fueron satisfactorias, sin errores bloqueantes."** Each check is therefore recorded **PASS (operator-confirmed)**. This is not independently verified test evidence. Exact checkpoint/workflow, ComfyUI variant/version, SHA-256 comparison and restoration observations have not been supplied. These details remain open; they must not be invented or silently inferred.

## Manual test records — operator-confirmed PASS (2026-11-22)

| ID | Required real-device check | Pass criteria | Evidence/status |
| --- | --- | --- | --- |
| H1 | Upgrade existing RC.1 on Windows with backup | Saved projects, datasets, captions and settings persist; no original images/weights deleted | **PASS** (operator-confirmed; artifacts/details not supplied) |
| H2 | Test one *named* compatible workflow on RTX 3090 | Record model/checkpoint, ComfyUI version and Desktop/Portable type; create output from connected reference image | **PASS** (operator-confirmed; artifacts/details not supplied) |
| H3 | In-app reference staging and bundled template import | Select **real** ComfyUI input folder (or API), copy source, confirm file hash/filename, choose installed checkpoint, prepare, generate | **PASS** (operator-confirmed; artifacts/details not supplied) |
| H4 | Cancellation and resource safety | Stop only targeted OrkiLab generation; other ComfyUI jobs remain intact; no silent data deletion | **PASS** (operator-confirmed; artifacts/details not supplied) |
| H5 | Synthetic provenance and repeatable ZIP | Reopen project, inspect synthetic/unreviewed status and lineage; approve/export same inputs twice and compare SHA-256 | **PASS** (operator-confirmed; artifacts/details not supplied) |
| H6 | Negative cases, mode boundaries, basic mobile UI | Missing ComfyUI/model/input, no compatible workflow, stand-alone mode, language navigation and mobile rendering fail safely | **PASS** (operator-confirmed; artifacts/details not supplied) |
| H7 | Rollback and restore | Confirm settings/data backup can be restored and older source can launch without destructive migration | **PASS** (operator-confirmed; artifacts/details not supplied) |

Operator signoff is sufficient to record the manual outcomes as reported, but no independent artifacts were supplied. The exact Windows and ComfyUI versions, Desktop/Portable variant, sample workflow/checkpoint, SHA-256 values, and restore logs remain **not recorded**. Do not invent details, certify a broader compatibility matrix, or describe these outcomes as independently reproduced. Obtain supporting details before making specific model/workflow compatibility claims. No blocking issue was reported.

## Automated release gates

1. Final commit on `main` has all **foundation** and **RC validation** checks passing on Windows and Linux.
2. `VERSION_ORKILAB`, `GUI/launcher.json`, README badge, changelog and release notes all identify **0.5.0**, not RC.1, while preserving historical RC.1 links.
3. Explicit stable-release workflow uses `workflow_dispatch` only with a deliberate approval phrase; it verifies the exact current `main` SHA and successful **push** CI for that SHA, refuses an existing tag/release, and publishes without rewriting history.
4. With explicit operator PASS recorded for H1–H7 and no blocking issues reported, review PR, verify exact-SHA CI and metadata, and manually publish `v0.5.0` only after all automated publication checks succeed.
5. Create the `0.6.0` development branch only after `v0.5.0` is published and verified.

**Manual acceptance signoff (2026-11-22): H1–H7 PASS, no blocking issues — explicitly confirmed by the operator in ChatGPT.** Stable publication remains **not yet authorized as complete** until PR review, exact-main-SHA Windows/Linux CI, and guarded publication workflow succeed. Specific hardware evidence and compatibility details are not available.
