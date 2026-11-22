# OrkiLab 0.5.0 — stable publication acceptance

**Status: release gate OPEN — operator completed H1–H7; individual PASS/FAIL results not yet confirmed.** RC.1 has been [published](https://github.com/jlopfri921/OrkiLab-LoRA-TrainerStudio/releases/tag/v0.5.0-rc.1). The original 7/7 on-device report covered Multiview PRs #80–#85, but later changes #86–#99 were not all independently validated. This checklist is the release blocker record, not a claim that items have passed.

## Supported scope for the first stable release

- Windows local OrkiLab launcher, local ComfyUI, and one documented supported SD-compatible img2img workflow/model. Other ComfyUI/Custom Node combinations remain best-effort.
- Project-linked Multiview subject/gallery; non-destructive references, review, qualitative viewpoint suggestions, explicitly generated synthetic image review, deterministic grouped dataset ZIP, contextual help and optional GPU tools.
- The three included core Img2Img starter graphs **do not guarantee camera pose or geometric fidelity**. Qwen Image Edit, FLUX/Klein camera control and true multi-reference editing remain **future features**.
- Do not imply each trainer, ComfyUI Desktop and Portable, or GPU is validated merely because one setup works.

## Manual hardware checks — user reports all seven performed (2026-11-22)

**Operator report:** On 2026-11-22, the user selected H1, H2, H3, H4, H5, H6 and H7 in the validation checklist and submitted: *"He completado estas pruebas de OrkiLab 0.5.0: H1, H2, H3, H4, H5, H6, H7."* This is evidence of **completion**, not an explicit declaration that all seven passed without incidents. Exact checkpoint/workflow, ComfyUI variant/version, SHA-256 comparison and restoration observations have not been supplied. These details remain open; they must not be invented or silently inferred.

## Manual test records — status awaiting result confirmation

| ID | Required real-device check | Pass criteria | Evidence/status |
| --- | --- | --- | --- |
| H1 | Upgrade existing RC.1 on Windows with backup | Saved projects, datasets, captions and settings persist; no original images/weights deleted | **PENDING RESULT** (performed per operator; PASS/FAIL not specified) |
| H2 | Test one *named* compatible workflow on RTX 3090 | Record model/checkpoint, ComfyUI version and Desktop/Portable type; create output from connected reference image | **PENDING RESULT** (performed per operator; PASS/FAIL not specified) |
| H3 | In-app reference staging and bundled template import | Select **real** ComfyUI input folder (or API), copy source, confirm file hash/filename, choose installed checkpoint, prepare, generate | **PENDING RESULT** (performed per operator; PASS/FAIL not specified) |
| H4 | Cancellation and resource safety | Stop only targeted OrkiLab generation; other ComfyUI jobs remain intact; no silent data deletion | **PENDING RESULT** (performed per operator; PASS/FAIL not specified) |
| H5 | Synthetic provenance and repeatable ZIP | Reopen project, inspect synthetic/unreviewed status and lineage; approve/export same inputs twice and compare SHA-256 | **PENDING RESULT** (performed per operator; PASS/FAIL not specified) |
| H6 | Negative cases, mode boundaries, basic mobile UI | Missing ComfyUI/model/input, no compatible workflow, stand-alone mode, language navigation and mobile rendering fail safely | **PENDING RESULT** (performed per operator; PASS/FAIL not specified) |
| H7 | Rollback and restore | Confirm settings/data backup can be restored and older source can launch without destructive migration | **PENDING RESULT** (performed per operator; PASS/FAIL not specified) |

Attach test outputs in this document or a linked GitHub issue before checking off any pending row; record the tested Windows and ComfyUI versions, sample workflow/model and limitations. An operator confirmation can satisfy the manual stage if it identifies the test and pass/fail outcome; do not invent evidence.

## Automated release gates

1. Final commit on `main` has all **foundation** and **RC validation** checks passing on Windows and Linux.
2. `VERSION_ORKILAB`, `GUI/launcher.json`, README badge, changelog and release notes all identify **0.5.0**, not RC.1, while preserving historical RC.1 links.
3. Explicit stable-release workflow uses `workflow_dispatch` only with a deliberate approval phrase; it verifies the exact current `main` SHA and successful **push** CI for that SHA, refuses an existing tag/release, and publishes without rewriting history.
4. Only after the H1–H7 evidence is attached and blocking failures resolved, merge the stable-version change and manually publish `v0.5.0`.
5. Create the `0.6.0` development branch only after `v0.5.0` is published and verified.

**This file records that H1–H7 were performed, but deliberately does not mark them PASS or authorize stable publication until the user confirms the results and blocking incidents.**
