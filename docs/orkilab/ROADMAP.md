# Roadmap

## Current work: OrkiLab 0.6.0 B10.5 — release readiness (not published)

The 0.6 Benchmark Studio development remains on **[PR #104](https://github.com/jlopfri921/OrkiLab/pull/104)**. B10.1–B10.4 have been accepted by the local operator, with **267 benchmark checks operator-reported PASS**. B10.5 adds a conservative RC publication checklist, optional **light/dark UI mode** across Workspace/Benchmark/Queue/Dataset and shared shell screens, and 16 new tests. **283 benchmark checks expected**, not yet verified by the operator on Windows. Acceptance is documented in [RC_0_6_0_READINESS.md](RC_0_6_0_READINESS.md); detailed evidence history in [BENCHMARK_0_6_ROADMAP.md](BENCHMARK_0_6_ROADMAP.md).

**B10 phase status:** B10.1 protocol declarations — accepted; B10.2 model-choice checks — accepted; B10.3 guided one-job submission — accepted by mocked tests/UI, real GPU still to certify; B10.4 descriptive pairwise results — accepted; **B10.5 final regression, web theme and RC acceptance — in development/pending tests**.

Do **not** interpret a passed local Benchmark test suite as verified scientifically comparable inference or release authorization. Complete Windows/Linux CI at the final commit, real ComfyUI/GPU acceptance with explicit consent, full app regression, mobile/light-theme visual review, data safety, documentation and author signoff **before** tagging `v0.6.0-rc1`. The older 0.5.0 prerelease notes below are historical, not this branch's current release decision. No 0.6.0 release tag has been created here.


| Release | Scope | Acceptance gate |
|---|---|---|
| 0.1 Foundation | branding, docs, safe update | review diff; launch existing UI; update tests |
| 0.2 Workspace | SQLite library, project registry, read-only inventory | index synthetic data; no destructive writes |
| 0.3 Connect | ComfyUI API adapter, workflow validation, explicit submission | mock API tests; real local inference |
| 0.4 Dataset | quality checks, dedup, captions, split; [Dataset Studio delivery scope](DATASET_STUDIO_0_4_SCOPE.md) | reproducible manifest and non-destructive edits |
| 0.5 Multiview | subject/view library, camera coverage, reference/synthetic provenance, optional ComfyUI generation and grouped export; [full 0.5 roadmap](MULTIVIEW_0_5_ROADMAP.md) | measured/unknown viewpoints clear, immutable originals, supported workflows and real GPU acceptance |
| 0.6 Benchmark | paired prompts/seeds, comparable performance | reproducible report and held-out evaluation |
| 0.7 Copilot | Ollama suggestions, logs | user confirmation for mutations |
| 0.8 Hub | HF/Civitai integration | license/token checks and explicit downloads/uploads |
| 0.9 Desktop | portable application/installer | clean Windows/Linux install and rollback |
| 1.0 Stable | documented supported matrix | regression and hardware validation |

## Current milestone: 0.5.0-rc.1 — Multiview prerelease published; stable acceptance pending

[v0.5.0-rc.1](https://github.com/jlopfri921/OrkiLab-LoRA-TrainerStudio/releases/tag/v0.5.0-rc.1) was published as a **prerelease on 2026-11-22**, commit `b4bc236bd61db2888aa035986b6dca84126dd83b`, with Windows/Linux CI passed. This release includes Multiview development through PR #99 and comprehensive 0.5.0 documentation through PR #100. Operator-reported Windows/RTX 3090 acceptance covers earlier configurations, not all later workflows. There is **no stable v0.5.0 yet**. See [the 0.5 acceptance register](RC_0_5_0_READINESS.md) for final hardware, safety, compatibility and rollback gates. Proceed to **0.6.0** only after stable 0.5.0 acceptance. Earlier 0.4.0 stable blockers remain explicit.

## Previous milestone: 0.4.0-rc.1 — integrated dataset and curated LoRA candidate

**Status:** [`v0.4.0-rc.1`](https://github.com/jlopfri921/OrkiLab-LoRA-TrainerStudio/releases/tag/v0.4.0-rc.1) is a published GitHub prerelease based on the candidate merged through PR #76. Subsequent Dataset Studio safety changes (PR #77) are in `main` and may be newer than the immutable release tag. This is not 0.4.0 stable. The Dataset Studio hardening checks (PR #77) were also merged after Windows/Linux CI. The last published prerelease remains `v0.3.0-rc.1` until GitHub Releases confirms otherwise.

**In candidate:** project-linked Dataset Studio, captions, non-destructive derived export, optional local Ollama preview, project-specific trainer draft handoff, named ComfyUI checkpoint management and comparison, human LoRA ratings and a searchable curated library, collapsible and searchable generation history, common footer and sidebar version.

**Release candidate gate:** Windows/Linux unit tests and frontend syntax; launch the Windows app and verify existing data/weights, one representative project dataset/caption/train handoff, one ComfyUI comparison workflow, persistence and reference images. Document skipped/on-device-only checks explicitly in [the acceptance register](RC_0_4_0_READINESS.md).

**Stable 0.4.0 gate (not yet met):** complete documented supported-engine export profiles, train/validation reproducibility and round-trip manifests, GPU/Windows acceptance across a supported matrix, rollback/no-data-loss update and addressed release blockers. These remain planned, not hidden by a version number.

## 0.5.0 stable milestone — Multiview Studio (pending)

See [the detailed 0.5.0 delivery and acceptance plan](MULTIVIEW_0_5_ROADMAP.md). It covers subjects/captures/view metadata, source provenance, visual coverage, optional controlled ComfyUI view generation, group-aware exports, multilingual UI, and Windows/Linux plus GPU acceptance. The 0.5 milestone does not waive unfinished 0.4 stable release gates.

## Immediate milestone: 0.3.0-rc.1 — ComfyUI integration candidate

**Status:** **published as a prerelease on 2026-11-21** (tag `v0.3.0-rc.1`, commit `3d7dde0ce19d1937320cd2517523a5b36860b098`). The release is not designated stable; further acceptance and follow-up fixes are tracked separately.

**Release evidence register:** [0.3.0-rc.1 readiness and test evidence](RC_0_3_0_READINESS.md). Use it to distinguish observed passes, reported runs and unverified gates before tagging.

**Included in the 0.3 RC (features to stabilize, not a promise every workflow will work):**

- Modern Workspace entry points and the ComfyUI Zone introduction/connection gate, with eight interface languages.
- Local/private ComfyUI connection validation; read-only node and model discovery.
- Workflow library: importing trusted UI/API JSON, indexing local folders, search, favorites, and non-destructive inspection.
- OrkiLab Bridge visual-to-API graph preparation; validation of representative installed-node workflows.
- Generation Studio: explicit review/confirmation, supported parameter editing, job status, best-effort per-node progress, safe cancellation, history and output access.
- Optional, queue-safe ComfyUI model/cache release and per-generation system RAM/VRAM diagnostic snapshots. GPU Manager read-only multi-adapter telemetry and bounded charts.
- Existing standard-LoRA-loader comparison UI remains accessible **as experimental / unverified**, excluded from the rc.1 stability promise. GPU validation of the comparator is deferred to a subsequent release.
- Preserved existing trainer launching and queue; no claim of full trainer-interface modernization in 0.3.

**Original release acceptance criteria (historical):**

1. CI passes on Windows and Linux; unit tests include connection/navigation, Bridge parsing, execution safety, RAM/VRAM diagnostics and existing trainer launch routes.
2. Record **actual** Windows + RTX 3090 + ComfyUI Desktop smoke-test evidence: connected/disconnected state, one known-good API graph, one visual graph via Bridge, execution progress, cancellation, history/output links and memory release without interrupting unrelated queue jobs.
3. Check failure states: ComfyUI absent, invalid workflow/sampler, missing custom nodes, unsupported output, failed generation and unauthorized remote access. Imported workflows must never run automatically.
4. Test language switching and page navigation (including Projects and Training Engines) in a real browser, verify no dataset/workflow files are rewritten, and review multi-GPU readings when hardware is available. Single-GPU validation must not be represented as multi-GPU validation.
5. Update README, changelog and acceptance notes with results and known limitations; verify a safe update from the previous release candidate.

**Trainer UX modernization (ongoing):** Optional, non-destructive quick navigation is being rolled out by engine family. The FLUX.1/SDXL pilot and FLUX.3/Qwen-Image 2.1/Krea 2/LTX 2.3 expansion are already merged; this third wave adds LTX 2.5, MiniMax-H3, Wan 2.2, Fibo 2.0 and YuE2-3B. This only improves navigation around the existing trainer panels; it is **not** a full modern interface replacement or evidence of real training compatibility. Browser acceptance and parameter-by-parameter trainer review are still required before deleting legacy views.

**Fourth-wave trainer UX progress:** Shared, optional quick navigation now also covers Qwen-Image 2512, Boogu Image Edit, Z-Image, Ming-Image, Anima, FLUX.2 Klein 9B, ERNIE-Image, MOSS-Image and Ideogram 4 (subject to CI/merge and browser acceptance). Together with earlier waves this reaches 20 catalogued trainers. **MiniMax-H3 Image shares `GUI/trainer_ui_minimaxh3.html` with MiniMax-H3 (video/audio)**. Its launcher supplies `h3_model_forced: image` to the settings endpoint, and the shared UI pins image mode. The existing quick navigation therefore covers all **21 catalogue entries across 20 distinct HTML trainer interfaces**; mode-specific, server-confirmed navigation help distinguishes the Image entry. Automated tests check the mapping and safe UI behaviour, but complete trainer redesign, real browser acceptance and hardware validation remain outstanding.\n\n**Reported progress (2026-11-21):** user reports that the previously planned real-world ComfyUI/GPU tests have been carried out. Detailed per-scenario PASS/FAIL evidence still needs to be recorded before claiming full certification. Engine-by-engine modernization remains ongoing. Documentation/version planning is being updated here. Packaging and RC tagging follow the exit checks.

**Deferred beyond 0.3 RC:** Dataset Studio (0.4), multiview validation (0.5), broader benchmarking (0.6), Ollama assistant (0.7), Hugging Face/Civitai Hub integration (0.8), production desktop installer (0.9), full trainer modern-view replacement when independently verified, and scheduling or an interactive mesh viewer unless separately accepted.

### 0.3 implementation checkpoints (development, not released)

| Area | Implemented in code | Acceptance still required |
|---|---|---|
| ComfyUI Zone | Separate navigation; read-only model/node inventory and workflow library | Local browser UX and translations |
| Bridge | Installable frontend extension and safe preparation path | ComfyUI Desktop restart and subgraph conversion tests |
| Generation | Graph review, editable inputs, browser presets, explicit execution | Real ComfyUI inference and error-state tests |
| Results | SQLite history, media proxy, images/audio/video playback and downloads | Large-file playback, restarts and 3D viewer |
| LoRA Comparator (experimental) | Direct workflow discovery, standard-loader weight variants, sequential execution code exists | Two-strength GPU test and cancel/error handling deferred beyond rc.1; **not a release gate or validated capability** |
| GPU Manager | Read-only local NVIDIA polling and utilization/VRAM alerts | NVIDIA hardware tests, multi-GPU validation, scheduling separately |
| UX/i18n | Modern Workspace/ComfyUI routing and translations | Audit each trainer interface and contextual guidance |

Detailed status: [Workspace feature guide](WORKSPACE_FEATURES.md). Keep the version file unchanged until the corresponding acceptance gates pass.

Dependencies: Foundation -> Workspace -> Connect and Dataset -> Multiview/Benchmark -> Copilot/Hub -> Desktop -> Stable. Prioritize read-only adapters, then writes. No release dates promised. GPU scheduling, plugins, offline mode and migration backups require separate design reviews.
