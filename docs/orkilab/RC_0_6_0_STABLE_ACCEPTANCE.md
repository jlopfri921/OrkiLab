# OrkiLab 0.6.0 — Stable acceptance and publication gates

**Status: SOURCE PREPARATION ONLY — NOT RELEASED OR TAGGED.** Candidate branch `release/0.6.0-stable-prep`. Stable predecessor [v0.5.0](https://github.com/jlopfri921/OrkiLab/releases/tag/v0.5.0). Tested prerelease [v0.6.0-rc1](https://github.com/jlopfri921/OrkiLab/releases/tag/v0.6.0-rc1).

## Operator acceptance on published v0.6.0-rc1 — 2026-11-23

Manual PASS results were communicated by the operator; no screen captures, raw GPU logs or Benchmark run IDs were attached. The tests were performed on the **published RC1**, not automatically on the stable candidate revision.

| Suite | Verified behaviour as reported | Result |
| --- | --- | --- |
| E1 (5) | Startup, version, main navigation, Projects/Dataset, ComfyUI/Benchmark | **PASS 5/5** |
| E2 (6) | Create project, list and select in Dataset/Benchmark, restart and recover details/images | **PASS 6/6** |
| E3 (6) | Real ComfyUI/RTX 3090 connection; preparation, human confirmation, generation result/history and RAM/VRAM contrast | **PASS 6/6** |
| E4 (6) | Benchmark preflight B10.2; prepare one variant/repetition; no auto-generation; RTX3090 job; persistent history | **PASS 6/6** |
| E5 (6) | Abandon preparation, project isolation, restart persistence, light/dark theme, responsive navigation, graceful errors | **PASS 6/6** |
| E6 (6) | Version/release, documentation, Apache/MIT license separation, backups, nonblocking regression checks, limitations | **PASS 6/6** |

**Total: 35/35 PASS communicated.** Historical operator acceptance is registered in comments on [PR #104](https://github.com/jlopfri921/OrkiLab/pull/104), which has already merged. E6 specifically indicated README/changelog were current, but subsequent direct repository inspection found **obsolete “RC1 not published” statements and a duplicated version-history section**; this stable-preparation branch corrects the discrepancy explicitly rather than treating E6 as repository proof.

## Stable release checks

- [x] Prior [RC1](https://github.com/jlopfri921/OrkiLab/releases/tag/v0.6.0-rc1) public prerelease and tag independently verified.
- [x] Operator E1–E6 accepted on RC1 (35/35 reported).
- [x] MIT core / original OrkiLab Apache-2.0 notices preserved as separate licensing domains.
- [x] Stable source version and launcher metadata staged consistently **on release branch only**.
- [x] Documentation and release notes prepared with known compatibility limitations; source-only delivery.
- [ ] PR from release branch reviewed; no unrelated changes or unexpected version drift.
- [ ] All CI on **exact final release-branch HEAD** green across Windows/Linux.
- [ ] After merging, both workflows green on **exact `main` stable candidate SHA**.
- [ ] Maintainer explicitly authorizes **publishing 0.6.0 stable**, separately from preparation.
- [ ] Publish workflow confirms exact approved SHA and creates a **new** immutable `v0.6.0` tag/GitHub Release; never overwrites an existing release.

## Known limitations

- ComfyUI API graphs with unsupported third-party nodes, dynamic custom schemas or unusual exports may be rejected; a successful FLUX.2 workflow is no universal compatibility promise.
- Benchmark median differences are descriptive only; not proof of better/faster model or scientific equivalence. No fully attested model weight bytes, cold-cache controls, complete input bytes or precise per-process VRAM attribution.
- Hardware evidence is primarily NVIDIA RTX 3090 (24 GB); results on other GPUs remain unverified.
- Light theme, mobile responsiveness and legacy trainer screens have operator-reported acceptance but no exhaustive cross-browser/device matrix.
- Backup/restore reports covered `settings` and an isolated file-copy/hash comparison. User subsequently reported copies sufficient; **full restored-app boot and backups of all external datasets and model files cannot be independently verified here**.

## Release prohibition until approval

**Preparing the stable version, merging its PR and publishing `v0.6.0` are separate operations.** This document explicitly **does not authorize** a GitHub tag, GitHub Release or automatic publication. The guarded workflow must require user-entered authorization and exact SHA, plus success of two independent workflows on main.

Stable v0.5.0 remains available as the documented rollback baseline. Keep backups of persistent projects, settings, datasets and models before updating.
