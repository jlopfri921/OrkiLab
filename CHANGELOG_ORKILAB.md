# OrkiLab changelog

## 0.5.0-rc.1 — published GitHub prerelease (2026-11-22; not stable)

**Status:** [v0.5.0-rc.1](https://github.com/jlopfri921/OrkiLab-LoRA-TrainerStudio/releases/tag/v0.5.0-rc.1) is published as a **GitHub prerelease**, commit `b4bc236bd61db2888aa035986b6dca84126dd83b`, after Windows/Linux CI. There is no stable `v0.5.0` yet; stable release depends on additional real-device acceptance.

### Multiview from alpha to RC.1
- **Alpha.1:** subject/capture records scoped to Image projects in local SQLite, metadata, real/synthetic source distinctions, original-file protection and mobile navigation.
- **Alpha.2:** 12-sector angle/coverage chart, missing views, quality/duplicate hints, review, filtering and two-photo comparator.
- **Beta.1:** optional explicit ComfyUI generation from compatible workflows, reviewed synthetic registration and source lineage.
- **Beta.2:** SHA-256-checked, reproducible, non-destructive ZIP export with subject-grouped train/validation separation and opt-in approved synthetic images.
- **RC.1:** active project discovery, recovery and linking of existing Dataset Studio photographs, confirmed saved orientation/metadata and persistence.
- **Guided missing-view workflow:** 1–4 references; stage image copies by typed ComfyUI `input` folder or native desktop folder picker, or upload via ComfyUI API; show target filenames; inspect connected `LoadImage` nodes, automatically suggest or manually select mapping; select qualitative camera direction; prepare and explicitly confirm generation; review/cancel/register output as synthetic and unreviewed.
- **Built-in official Multiview starter library:** three core-only single-photo SD-family Img2Img API graphs (Preserve, Core, Variation), downloadable as ZIP or directly importable inside view creation with an installed checkpoint. Filter likely-compatible workflows; offer a direct download/import path when none appear.
- **Future model integrations:** Qwen-Image 2.1, FLUX.3 Klein, true multi-reference and validated camera control are **planned**, not supported built-in workflows for this candidate.

### App-wide usability and documentation
- Multilingual Multiview, embedded generator/AI and complete Guide in Spanish, English, Portuguese, French, German, Italian, Japanese and Korean.
- Expanded guide describing OrkiLab philosophy, objectives, all major modules and roadmap. Detailed [Multiview workflow README](workflows/multiview/README.md) and this consolidated top-level README.
- Standalone/ComfyUI-connected/hybrid modes, contextual help, clean mode-aware navigation, version below all sidebar actions and mobile layout refinements.
- Consolidated OrkiLab product identity across active source, documentation and assets, with regression checks against obsolete naming.
- Preserve backward-compatible source files, user projects and model weights; workflows are never executed merely by importing them.

**Evidence and limitations:** a local Windows/RTX 3090 user-reported subset of workflows and data handling has been exercised, but the latest official workflow library, local folder copy, full cancellation flow and Desktop vs Portable compatibility matrix still require direct final-version acceptance. Automated Windows/Linux CI does not validate GPU models. See [0.5 candidate acceptance register](docs/orkilab/RC_0_5_0_READINESS.md).

## 0.4.0-rc.1 — published GitHub prerelease (2026-11-21)

- Published source prerelease [`v0.4.0-rc.1`](https://github.com/jlopfri921/OrkiLab-LoRA-TrainerStudio/releases/tag/v0.4.0-rc.1). Windows/Linux automated gates passed; remaining real-device and stable-release limitations are documented separately.

- Expand Dataset Studio: project-linked image inventory, duplicate/quality diagnostics, manual captions with revision history, export of captions in ZIP format, optional opt-in local Ollama vision previews and batch caption review.
- Prepare separate image-and-caption training folders without modifying original sources, and connect project-specific prepared datasets to isolated trainer drafts where supported. Engine-specific dataset formats still require verification.
- Improve ComfyUI checkpoint comparison: identify project checkpoints by steps, persist the chosen ComfyUI LoRA folder, safely manage named checkpoint copies, and preserve original `.safetensors`.
- Add human checkpoint ratings (1–5 stars), Best and one Final designation per project, and a SQLite library for shortlisted LoRAs with optional reference image and training/test/hardware metadata.
- Make trained LoRA records and generation history collapsible. Add searches, filters and sorting for the LoRA library, Projects and generation history.
- Align shared header and left navigation across Workspace, Queue and Dataset Studio; move the live app version below the active left menu and add the official GitHub repository to the common footer.
- Provide seven translated locales in addition to English, accessibility and layout refinements, and Windows/Linux CI with Python 3.13 and syntax checks.
- **Release gate:** full Windows/Linux CI and genuine on-device testing before tagging. CPU-only CI cannot certify GPU model compatibility, every trainer, Windows GUI integration, Ollama cancellation/memory behavior or a reproducible end-to-end trainer-ready dataset with validation split.
- **Not yet completed for 0.4 stable:** documented per-engine export profiles, guaranteed reproducible train/validation split, hardware compatibility matrix, complete integration tests on supported local GPU machines, and final stability acceptance.

The release metadata is updated on the release-preparation branch; the GitHub tag/release must be created only after its exact merged SHA is verified. See [readiness register](docs/orkilab/RC_0_4_0_READINESS.md).


## 0.3.0-rc.1 — published GitHub prerelease (2026-11-21)

- Add a welcome/introduction screen and verified-connection navigation gate for ComfyUI Zone.
- Explain Projects and Training Engines with guided introductions, contextual actions and localized empty states.
- Extend GPU Manager with bounded, session-only system RAM and GPU telemetry graphs.
- Add per-generation RAM/VRAM snapshots (before, sampled peak, after completion and optionally after model/cache release). These are system-wide readings, not proof of memory leaks or per-process attribution.
- Define the planned **0.3.0-rc.1** feature freeze and acceptance tests in [the roadmap](docs/orkilab/ROADMAP.md). Real-device verification has been reported by the user; specific pass/fail evidence remains to be filed.
- Released at [v0.3.0-rc.1](https://github.com/jlopfri921/OrkiLab-LoRA-TrainerStudio/releases/tag/v0.3.0-rc.1), commit `3d7dde0ce19d1937320cd2517523a5b36860b098`, with successful Windows/Linux foundation and RC CI. Model compatibility, unsupported ComfyUI custom nodes, complete trainer modern-view migration and final installer testing remain outside this candidate's guaranteed scope.

## Unreleased — Workspace and ComfyUI development (2026-11-20)

### Usability review: focused Workspace and contextual help

- Split the original Workspace overview into separate Dashboard, Projects, Training engines and GPU Manager views using existing hash navigation.
- Add a reusable, collapsible contextual explanation for each Workspace and ComfyUI module, with eight-language coverage including English.
- Highlight selected navigation sections, improve keyboard focus outlines and keep the main layout responsive.
- Preserve project records, trainers and generation backend behaviour; **browser/mobile regression tests remain pending**.


- Introduce a separate, multilingual ComfyUI Zone with its own navigation and a return-to-Workspace action.
- Add ComfyUI connection modes, read-only model and node inventories, and a searchable/favouritable workflow library with folder synchronization and collapsible tools.
- Add OrkiLab Bridge frontend integration for UI-workflow conversion through ComfyUI; requires a ComfyUI restart and real workflow testing.
- Add Generation Studio graph review, editable parameters, random seed control and browser-local presets.
- Add persistent generation history, safe media descriptors, image/audio/video previews and output downloads; mesh downloads do not yet have an interactive viewer.
- Add sequential LoRA strength comparison for standard loader nodes and an integrated workflow picker with compatibility hints.
- Add read-only GPU Manager using NVIDIA telemetry, automatic visible-page refresh, VRAM warnings and training-activity hints.
- Extend interface translations to the new modules. Full translations of custom-node inputs are not guaranteed.
- Document feature workflows, code map and validation limitations in [Workspace feature guide](docs/orkilab/WORKSPACE_FEATURES.md).

**Historical development note:** the previous candidate was `0.2.0-rc.1`. The 0.3.0-rc.1 prerelease is published but is not a production-stable or universally compatible release.

## 0.2.0-rc.1 — Workspace closeout candidate

- Make the modern Workspace the sole launcher entry point, including old `/legacy` bookmarks.
- Remove the preview label and update the documented launch flow.
- Preserve trainer engines and shared compatibility assets.
- User smoke testing reported successful trainer navigation; comprehensive regression and GPU validation remain pending.

## 0.2.0-dev.1 — Workspace preview

- Add opt-in dashboard, engine filters, hardware summary and local SQLite project metadata.
- Create, archive and restore projects without modifying training files.
- Preserve classic launcher and all existing trainers. Foundation runtime validation remains pending.

## 0.1.0-rc.2 — Foundation identity and validation candidate

- Original OrkiLab engine covers and README banner.
- English public README and personal maintainer attribution.
- Remove promotional links from launcher; retain original credits and model identifiers.

## 0.1.0-rc.1 — Foundation release candidate

- Add dependency-free regression tests for branding, version, updater guards and safe Git updates (temporary local repositories).
- Add Windows/Linux CI with no model downloads or GPU dependencies.
- Make package updates explicit with --deps; refuse external Python environments.
- Align launcher version, queue branding and start-script titles.
- Add acceptance checklist and local hardware test procedure.

Release candidate: CI and local hardware validation still required before stable designation.

## 0.1.0-dev — Foundation (2026-11-20)

- Introduce independent OrkiLab SVG branding, launcher title, palette, favicon and About panel.
- Preserve upstream documentation and MIT copyright.
- Document architecture, audit, roadmap, integration contracts, dataset plan, security and development rules.
- Replace destructive updater synchronization with fast-forward-only updates of the current origin branch; ZIP installations require a clone. Dependency updates retain upstream behavior.
- Extend ignore rules for private data and model weights.

Status: development snapshot; runtime validation pending. No training engine changes.

### Interface branding follow-up

- Unify the launcher, queue and all 21 launcher covers with the orbital O vector identity.
- Preserve legacy asset paths as compatibility aliases; use OrkiLab paths for new UI links.

- Rebrand all trainer interfaces and Dataset Forge; remove inherited promotional social links from trainer pages.
- Add regression checks for model-local branding assets and engine covers.

## Community links

- Disable inherited social links in documentation; reserve unlinked placeholders for future OrkiLab channels.
