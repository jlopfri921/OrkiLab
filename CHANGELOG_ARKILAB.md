# OrkiLab changelog

## 0.5.0-rc.1 — release candidate in preparation (unpublished)

- Multiview Studio 0.5 alpha.1: SQLite project-scoped subject/view records, manually provided camera metadata, provenance and mobile bottom navigation.
- Alpha.2: twelve-sector angular coverage, missing-angle diagnostics, image quality hints, review controls and photo comparator.
- Beta.1: opt-in ComfyUI generation from installed validated workflows, explicit capture registration and synthetic lineage tracking.
- Beta.2: reproducible, non-destructive ZIP exports with SHA-256 manifest and subject-level train/validation grouping; excludes synthetic images unless approved and opted in.
- RC.1: existing Workspace Image project discovery, Dataset Studio photo recovery/linking, project persistence and safety regression tests.
- On-device operator reports 7/7 functional checks passed on Windows with RTX 3090; these reports do not establish a complete training pass, broad workflow compatibility, final release CI or rollback acceptance. See [RC.1 readiness](docs/arkilab/RC_0_5_0_READINESS.md).
- **Not yet released:** stable v0.5.0 remains gated on final SHA CI, named tested configuration, release review and documented limitations. 0.4 stable scope gaps are not silently considered completed.


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

The release metadata is updated on the release-preparation branch; the GitHub tag/release must be created only after its exact merged SHA is verified. See [readiness register](docs/arkilab/RC_0_4_0_READINESS.md).


## 0.3.0-rc.1 — published GitHub prerelease (2026-11-21)

- Add a welcome/introduction screen and verified-connection navigation gate for ComfyUI Zone.
- Explain Projects and Training Engines with guided introductions, contextual actions and localized empty states.
- Extend GPU Manager with bounded, session-only system RAM and GPU telemetry graphs.
- Add per-generation RAM/VRAM snapshots (before, sampled peak, after completion and optionally after model/cache release). These are system-wide readings, not proof of memory leaks or per-process attribution.
- Define the planned **0.3.0-rc.1** feature freeze and acceptance tests in [the roadmap](docs/arkilab/ROADMAP.md). Real-device verification has been reported by the user; specific pass/fail evidence remains to be filed.
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
- Document feature workflows, code map and validation limitations in [Workspace feature guide](docs/arkilab/WORKSPACE_FEATURES.md).

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
