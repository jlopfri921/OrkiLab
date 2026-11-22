# OrkiLab v0.3.0-rc.1 — published prerelease notes

> **Published 2026-11-21 as a GitHub prerelease**, not a stable version. [Official GitHub release](https://github.com/jlopfri921/OrkiLab-LoRA-TrainerStudio/releases/tag/v0.3.0-rc.1). The annotated tag resolves to `3d7dde0ce19d1937320cd2517523a5b36860b098`.

## Summary

The 0.3 release candidate focuses on the modern Workspace, the ComfyUI Zone and more controlled real-world generation workflows. The supported path is **local and operator-confirmed**; not every ComfyUI custom node, trainer or LoRA model is guaranteed to work.

## What is included

- Guided ComfyUI connection/onboarding, workflow exploration and inspection, and optional OrkiLab Bridge preparation for trusted visual graphs.
- Generation Studio: explicit submission, progress where supplied by ComfyUI, cancellation isolation, result preview/history and safe paths for supported outputs.
- Read-only GPU telemetry with RAM/VRAM monitoring and optional release of ComfyUI model/cache resources.
- Modern trainer navigation, contextual assistance and compact configuration panels; existing training engines are retained.
- English and other locales in the new Workspace; locale completeness and fallback across all legacy trainer inputs are not independently certified.
- The existing LoRA Comparator **remains experimental and unverified**, with no compatibility guarantee or required acceptance for this RC.

## Acceptance evidence and limitations

- **GitHub Actions:** Python 3.13 GPU-free RC validation and foundation checks completed successfully on **Windows and Ubuntu** at the tagged main commit `3d7dde0ce19d1937320cd2517523a5b36860b098`: [RC validation](https://github.com/jlopfri921/OrkiLab-LoRA-TrainerStudio/actions/runs/44847967490) and [foundation checks](https://github.com/jlopfri921/OrkiLab-LoRA-TrainerStudio/actions/runs/44847967279).
- **Windows local UI:** operator supplied a screenshot-free console transcript `3/3 OK` for `sdxl`, `wan22`, `yue2` using the project virtualenv, and reported that the full trainer UI smoke suite and unit tests passed. Browser smoke tests simulate training actions rather than performing GPU training.
- **ComfyUI real-world operator reports:** generated image found in history; cancellation did not affect other jobs; RAM/VRAM checked before/after releasing models; correct disconnected state; invalid workflow handled; safe update retained data. These are operator **reported successes** and not complete per-case instrumented verification.
- **Not independently covered by the above:** full hostile-access/security assessment (although automated local-only endpoint checks passed), every invalid custom-node scenario, all audio/video/mesh previews and persistence cases, every GPU telemetry sensor, multi-GPU physical validation, the two-strength LoRA Comparator, end-to-end training on every engine, and a cross-platform installer/rollback run.
- Exact workflow percentage and immediate interruption are dependent on ComfyUI's reported progress and queue status.
- Local-first behavior and model compatibility depend on ComfyUI Desktop, optional custom nodes and the installed model set. Only import workflows and install dependencies from trusted sources.

Detailed acceptance: [0.3 readiness register](RC_0_3_0_READINESS.md) and [GPU/Generation matrix](GPU_GENERATION_ACCEPTANCE.md).

## Install or update (Windows; non-destructive)

1. Before updating, back up datasets, user settings, workflows, projects and generated outputs. Do not delete or reset them.
2. From the repository directory, inspect `git status --short`, `git branch --show-current` and `git remote -v`. If local changes are present, preserve them and resolve safely instead of forcing a reset or cleaning ignored data.
3. Use the published tag `v0.3.0-rc.1` source or the official repository instructions. Do not confuse later unreleased development branches with this tagged prerelease.
4. Use the existing project's virtualenv for checks: `.\venv\Scripts\python.exe -m unittest discover -s tests -v` and `.\venv\Scripts\python.exe tools\smoke_test_ui.py --only sdxl,wan22,yue2`.
5. If needed, reinstall the OrkiLab Bridge from ComfyUI Zone and restart ComfyUI Desktop. Verify connection before running a trusted workflow.
6. If a regression appears, stop unsafe jobs, preserve logs and user data, then return the code to the previously working tagged version; avoid resetting or overwriting settings, datasets, projects or outputs.

## Publication checklist for maintainers

- [ ] Complete the remaining mandatory security and integrity checks, and record honest limitations.
- [ ] Verify Windows and Ubuntu Actions checks on the **current PR head SHA** and **merged main SHA**.
- [ ] Verify `VERSION_ORKILAB`, `GUI/launcher.json`, README badge and changelog consistently show `0.3.0-rc.1`.
- [ ] Merge release candidate PR after acceptance.
- [ ] Create annotated tag `v0.3.0-rc.1` **on the verified merge SHA**, push the tag without rewriting history.
- [ ] Publish GitHub **Pre-release** (not Latest/stable), link these notes and acceptance docs; verify displayed tag and SHA.
- [ ] Keep the prior release available for rollback.
