# OrkiLab 0.4.0 — Dataset Studio: initial scope and acceptance

**Status:** Dataset Studio was included in published GitHub prerelease [`v0.4.0-rc.1`](https://github.com/jlopfri921/OrkiLab-LoRA-TrainerStudio/releases/tag/v0.4.0-rc.1); subsequent hardening in PR #77 was merged to `main` after the release-candidate preparation. This is **not** certified stable `0.4.0`. Local Windows/Ollama/GPU and complete per-trainer dataset acceptance are not certified by CPU-only CI. PR #77 added seven safety/manifest/handoff regression checks, passing 238 tests on both Windows and Linux with no failures. The original alpha.1 closeout is retained as historical evidence ([alpha.1 register](DATASET_STUDIO_0_4_ALPHA1_CLOSEOUT.md)); the current gate is [RC 0.4.0 readiness](RC_0_4_0_READINESS.md). The published 0.3.0-rc.1 tag remains immutable.

## Goal and workflow

**Projects → Dataset Studio → Training Engines → ComfyUI**.

Prepare, inspect and export **image** datasets for LoRA training in one local-first workspace. Video/audio dataset support is a future extension, not part of the first 0.4 acceptance gate.

## Delivery stages

| Stage | Scope | Must pass |
| --- | --- | --- |
| 0.4.0-alpha.1 | Project-linked image library: import by reference, thumbnails, filter/sort, metadata, review and selection | Original files unchanged; empty/broken directories handled, no remote upload |
| 0.4.0-alpha.2 | Duplicates (exact SHA-256 and optional perceptual near-duplicates), dimension/ratio/blur warnings and bounded scan progress | Deterministic results on fixtures, cancellable scans and no hidden deletion |
| 0.4.0-beta.1 | Manual captions, batch edit preview, optional explicit locally executed captioner adapter; non-destructive resize/crop export | Reversible edit history, sidecar validation, consent before model use |
| 0.4.0-rc.1 | Per-trainer export profiles, reproducible dataset manifest, train/validation split and UI integration | Manifest round trip, reproducible split/seed and trainer launch compatibility |
| 0.4.0 | Docs, accessibility/i18n, Windows/Linux CI, real local Windows smoke and no-data-loss update | Release evidence recorded, known limits documented |

## Product requirements

1. **Non-destructive by default.** Import references existing paths, never moves, renames or rewrites source images/captions. Dataset removal removes only library references. Derived versions and exports live in a separate managed destination. A destructive filesystem operation, if ever added, needs a separate design/review.
2. **Local-first and private.** No automatic upload or public sharing; no Hugging Face or Civitai integration as part of this milestone. Future cloud captioning requires an explicit opt-in and clear data transfer disclosure.
3. **Per-project ownership.** Persist image references, sources, collection labels and edit decisions in SQLite under `settings/orkilab`; use migrations, bounded queries and safe path checks.
4. **Useful failure states.** Handle missing/renamed files, unreadable directories, unsupported formats, huge images, truncated content, low disk space and processing cancellation.
5. **Explicit decisions.** Duplicates, quality flags and AI captions are suggestions, not silent edits. Human review precedes any batch application.
6. **Compatibility.** Train/export adapters must describe each engine's folder, resolution/caption conventions; avoid pretending all engines accept the same schema.
7. **Access and safety.** Mutation endpoints are local-only, validate paths and request sizes and reject symlink traversal outside approved roots. No processing at import time until explicitly started.
8. **Languages/accessibility.** New interface strings in all eight supported locales with English fallback; labels, keyboard navigation and no unnecessary long vertical scroll.

## Implemented in alpha.1 (PRs #46 and #47)

- Dedicated `/workspace/datasets` entry from the main Workspace, with a clear introduction and empty state.
- SQLite-backed collection index scoped to a project, import-by-reference and image-only extension/filter metadata.
- Local-only preview service for indexed files, with file-size limits and symlink checks. This is an image preview endpoint, not a transcoded thumbnail cache.
- Search/sort/filter, bounded best-effort image dimensions, multi-selection and explicit batch review/rollback of metadata and removal of index references, without touching image source files.
- Synthetic-fixture tests pass on Windows and Ubuntu for non-destructive imports, batch actions, validation and local access. Full browser/security assessment is not yet demonstrated.

**Out of scope for alpha.1:** AI captioning, image generation, automatic training, caption rewrites, cloud sync, multiview, audio/video, marketplace integration and any direct write to the user's dataset folders.

## 0.3.0 stable prerequisite

Before calling 0.3.0 stable, review outstanding ComfyUI custom-node/Bridge failures, browser regressions, history/media persistence, unsupported media types and on-device security; label anything unverified. Boogu's compact-layout change is a post-0.3.0-rc.1 development improvement and is not backdated into that tag.

## 0.4.0-beta.1 manual-caption slice — development status (2026-11-21)

**Code available in development `main` after PR #56, not a released beta tag.** Per-image manual captions are stored in local SQLite and can be retrieved, edited and cleared via a modal. Updates require the latest revision number (stale writes return HTTP 409), with 25 saved revisions available to load and save as new revisions. Captions are limited to 2,000 characters. No automatic AI inference, internet request, original image modification or sidecar overwrite occurs.

**Remaining beta.1 scope:** batch caption editing and preview; optional explicitly configured local captioner; standalone sidecar export/validation; reversible non-destructive resize/crop export; real Windows browser exercise with user datasets. Do not certify the full 0.4.0-beta.1 milestone until these acceptance gates are met.

### Sidecar ZIP export — separate beta.1 slice

Users can select up to 200 image references, preview saved non-empty captions and explicitly confirm downloading a UTF-8 ZIP containing `captions/*.txt` plus `captions-manifest.json`. Uncaptioned selections are reported and excluded. Unique filenames match their source image basename; collisions use stable IDs. The source folders, existing sidecars and image bytes are never changed, and the generated archive contains no source images. Access requires the local launcher and same-origin request; the download is not an automatic sidecar write.

**Remaining:** image-plus-caption derived export, optional non-destructive resize/crop outputs, bulk caption edit preview, opt-in local captioner, per-trainer profiles, Windows real-dataset validation and full 0.4 beta milestone acceptance.

### Optional local vision caption suggestions (beta.1 development slice)


The next slice provides installed vision-model detection with bounded local `/api/tags` → `/api/show` lookups (up to 40 models, no pull/installation), a dropdown with manual fallback, and per-request cancellation using a random one-use token. The backend interrupts the active Ollama HTTP stream; the stop of GPU inference is **best effort** and subject to Ollama behavior. The UI never saves suggestions implicitly. Real Windows/Ollama smoke tests must verify cancellation, no unwanted continued GPU use and model-memory cleanup.
An optional per-image Ollama adapter can be invoked **only by explicit user action** from Caption Studio. Ollama must be already installed and running locally with an image-capable model; neither installations nor downloads occur automatically. Requests are loopback-only (port 11434), prevent redirects/proxy forwarding, are single-flight, are limited to 12 MiB source images, and time out after 120 seconds. A generated caption is initially a **read-only suggestion**. Applying it to the editor and saving with the normal versioned API are two separate deliberate actions; source files and sidecars are never written.

**Acceptance remains pending:** real Windows Ollama+RTX 3090 workflow, supported vision-model inventory/compatibility, UI cancellation, GPU contention tests, opt-in model management, and full integration with the existing Qwen3-VL shared captioner. Unit tests mock the local backend and do not certify actual GPU inference.

## Acceptance model

`PASS`: test command/result, commit and environment recorded. `REPORTED PASS`: operator result without retained detailed log. `NOT VERIFIED`: no sufficient evidence; not equal to failure. CI without a GPU **cannot** certify actual end-to-end training. Maintain a separate acceptance record for each 0.4 milestone.

## Project-to-training handoff development slice (PR #61, not released)

- Projects API now reports indexed image counts and links each image project to its own Dataset Studio library.
- Dataset Studio supports explicit preview and download of a **generic** ZIP containing matched `dataset/<image>` + `dataset/<stem>.txt` pairs and a `manifest.json`; incomplete/rejected/stale entries are skipped with reasons. Originals are not changed.
- The paired export requires an existing saved caption and explicit download confirmation. Supported file types: JPEG, PNG, WebP and BMP. Maximum 200 selected entries, 40 MiB per file and 256 MiB total indexed image bytes per export.
- **Important:** This ZIP is **not** an engine-specific export adapter, does not set the trainer's dataset path, and does not itself trigger training. A user must extract the ZIP and select a compatible dataset directory in the target trainer.
- Future work: true per-trainer profile, safe managed output directory, project dataset path persistence/hand-off, train/validation split and real Windows + GPU acceptance.

### Native dataset folder browser (PR #61 development)

The Image folder field continues to accept a pasted or typed absolute path. The new **Browse…** button asks the **launcher computer's** Windows/Linux desktop session for a native folder using a local-only, same-origin API. Cancelling does not erase the text field. Linux headless servers without a GUI session show an error and retain manual-path input. Browser-only file input is intentionally not used because browsers do not reliably expose the local absolute path of a directory. No files are imported by selecting a folder; the user must explicitly click **Import images**. Real Windows and Linux GUI acceptance is still pending.

### Prepare local image/caption dataset (PR #61 development)

Dataset Studio now offers **Prepare local training folder** for selected, fully captioned images. This is an explicit, confirmed local operation that copies images and creates corresponding UTF-8 captions in a fresh, uniquely named directory at `Datasets/OrkiLab/<project-id>/<preparation-id>/` relative to the OrkiLab installation, plus a reproducibility manifest. Existing prepared folders are never overwritten; original files and captions remain untouched. A preview enumerates incomplete/rejected entries and prevents an incomplete local preparation. The resulting absolute path is displayed and best-effort copied to the clipboard to paste into a compatible trainer. **No training run is started and no trainer's settings are modified automatically.** True per-engine handoff, collision/race security hardening, disk-space behavior and on-device Windows verification remain acceptance work.

### Selected-engine project handoff (development, unverified on GPU)

Launching from a **project** now sends its project ID as well as its configured trainer ID. The launcher verifies that the two match and selects that project's most recently prepared image+caption copy. It creates a separate draft instance and supplies `dataset_path` in that trainer's **pre-cache and training settings**, leaving shared settings and active trainers unchanged. The project-specific draft also has a unique project name for cache/output isolation. The image dataset adapter covers image-only trainer families with the current flat image/caption convention; formats such as editing pairs or video inputs may need further adaptation. For video/audio projects whose dataset path was explicitly entered in Projects, their selected trainer gets that path in isolated settings, subject to trainer-specific validation. When there is no prepared or explicitly configured dataset, the launch fails with actionable feedback rather than silently using an unrelated one. Launching from the general Training Engines screen is unchanged.

**Not certified yet:** end-to-end GPU pre-cache/training with every trainer, automatic modality-specific validation, and multi-project real-world browser acceptance.

### Project overview visibility (linked data, not a manual path)

The project metadata's optional `dataset` text field is **not** automatically populated when Dataset Studio indexes images. Those references are stored independently in `datasets.sqlite3` and are associated with the project by ID. Projects now display **Indexed source folders**, indexed/captioned counts, and the **latest locally prepared dataset folder** when present, even if the project's manually entered path is empty. Source folders are labeled separately from the prepared training copy, so their presence cannot be mistaken for a validated trainer-ready export. The underlying manual project path is preserved and never rewritten merely because image references were indexed.

### Batch captions via local Ollama (development)

Dataset Studio has a **Generate AI captions** action for selected images. The dialog discovers installed **local vision-capable** Ollama models, preferring `gemma4:26b` when present, then generates suggestions **sequentially** using the already supported local vision endpoint. A live counter/progress bar, per-image results, editable previews and per-image approval checkboxes are shown. Existing saved captions are skipped and never overwritten by batch generation; errors on one image do not discard successful proposals. Users must explicitly click **Save approved captions**, which uses revision-checked updates. Original image files and existing sidecar files remain untouched. Generation can be cancelled, including the active server request. This feature is opt-in, not a background job, and requires Ollama running on the launcher PC. The generation itself is GPU-dependent and needs manual acceptance with actual local models before release.

## Acceptance update — PR #77 (2026-11-21)

**PASS (automated Windows and Linux):** 238 tests per platform (231 previous + seven new); source checksums unchanged after repeated preparation, manifest contents and paired images/captions consistent, changed or rejected images excluded, managed destination symlink rejected, tampered manifest paths/missing captions/symlinked files rejected before launch, and previous project-launch behaviour preserved.

**Still NOT VERIFIED on real hardware:** Windows native folder-picker end-to-end, real photos including corrupted/special-format media, large-library/performance/low-disk behaviour, real GPU pre-cache/train for each supported engine, Ollama vision inference/cancellation/VRAM, and reproducible train/validation split with validated per-engine profiles. These cannot be marked PASS from mocked CPU tests; they remain blockers for declaring **stable** 0.4.0.
