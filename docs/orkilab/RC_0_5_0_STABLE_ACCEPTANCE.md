# OrkiLab 0.5.0 — stable publication acceptance

**Status: release gate OPEN.** RC.1 has been [published](https://github.com/jlopfri921/OrkiLab-LoRA-TrainerStudio/releases/tag/v0.5.0-rc.1). The original 7/7 on-device report covered Multiview PRs #80–#85, but later changes #86–#99 were not all independently validated. This checklist is the release blocker record, not a claim that items have passed.

## Supported scope for the first stable release

- Windows local OrkiLab launcher, local ComfyUI, and one documented supported SD-compatible img2img workflow/model. Other ComfyUI/Custom Node combinations remain best-effort.
- Project-linked Multiview subject/gallery; non-destructive references, review, qualitative viewpoint suggestions, explicitly generated synthetic image review, deterministic grouped dataset ZIP, contextual help and optional GPU tools.
- The three included core Img2Img starter graphs **do not guarantee camera pose or geometric fidelity**. Qwen Image Edit, FLUX/Klein camera control and true multi-reference editing remain **future features**.
- Do not imply each trainer, ComfyUI Desktop and Portable, or GPU is validated merely because one setup works.

## Manual hardware checks — evidence required before stable

| ID | Required real-device check | Pass criteria | Evidence/status |
| --- | --- | --- | --- |
| H1 | Upgrade existing RC.1 on Windows with backup | Saved projects, datasets, captions and settings persist; no original images/weights deleted | **PENDING** |
| H2 | Test one *named* compatible workflow on RTX 3090 | Record model/checkpoint, ComfyUI version and Desktop/Portable type; create output from connected reference image | **PENDING** |
| H3 | In-app reference staging and bundled template import | Select **real** ComfyUI input folder (or API), copy source, confirm file hash/filename, choose installed checkpoint, prepare, generate | **PENDING** |
| H4 | Cancellation and resource safety | Stop only targeted OrkiLab generation; other ComfyUI jobs remain intact; no silent data deletion | **PENDING** |
| H5 | Synthetic provenance and repeatable ZIP | Reopen project, inspect synthetic/unreviewed status and lineage; approve/export same inputs twice and compare SHA-256 | **PENDING** |
| H6 | Negative cases, mode boundaries, basic mobile UI | Missing ComfyUI/model/input, no compatible workflow, stand-alone mode, language navigation and mobile rendering fail safely | **PENDING** |
| H7 | Rollback and restore | Confirm settings/data backup can be restored and older source can launch without destructive migration | **PENDING** |

Attach test outputs in this document or a linked GitHub issue before checking off any pending row; record the tested Windows and ComfyUI versions, sample workflow/model and limitations. An operator confirmation can satisfy the manual stage if it identifies the test and pass/fail outcome; do not invent evidence.

## Automated release gates

1. Final commit on `main` has all **foundation** and **RC validation** checks passing on Windows and Linux.
2. `VERSION_ORKILAB`, `GUI/launcher.json`, README badge, changelog and release notes all identify **0.5.0**, not RC.1, while preserving historical RC.1 links.
3. Explicit stable-release workflow uses `workflow_dispatch` only with a deliberate approval phrase; it verifies the exact current `main` SHA and successful **push** CI for that SHA, refuses an existing tag/release, and publishes without rewriting history.
4. Only after the H1–H7 evidence is attached and blocking failures resolved, merge the stable-version change and manually publish `v0.5.0`.
5. Create the `0.6.0` development branch only after `v0.5.0` is published and verified.

**This file deliberately does not mark the release as accepted.**
