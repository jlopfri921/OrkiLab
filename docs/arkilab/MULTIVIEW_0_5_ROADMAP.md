# OrkiLab 0.5.0 — Multiview Studio roadmap

**Status:** alpha.1 (PR #80), alpha.2 (PR #81) and beta.1 (PR #82) merged to `main`; beta.2 implementation under review, without a published 0.5 release/tag. 
**Baseline:** 0.4.0-rc.1 is available in `main` (release metadata); publication of a GitHub Release/tag and the 0.4.0 stable acceptance must be verified separately.
**Owner workflow:** Projects → Dataset Studio → Multiview Studio → Training Engines / ComfyUI.

## Alpha.1 implementation (development)

- Project-linked subject cards and capture references, manually supplied azimuth/elevation/distance, explicit real/photo/frame/synthetic/unknown provenance, review fields and persisted SQLite metadata.
- Read-only local image previews with image validation, SHA-256 checks, size/pixel limits and symlink rejection. Removing a capture or subject removes references, never source files.
- Search/sort by name, angle and distance; local pagination. Separate on-device validation is needed for native Windows/mobile presentation and real image collections.
- Responsive mobile navigation is shared across Workspace, ComfyUI Zone, Dataset Studio, Queue and Multiview: four bottom tabs with an accessible **More** sheet; desktop retains the left sidebar.

## Alpha.2 implementation (development)

- Read-only, project-scoped `GET .../subjects/<id>/coverage` returns a deterministic twelve-sector azimuth ring (30° sectors), provisional/approved counts, explicit missing sectors and unknown/rejected capture totals.
- Rejected images never count as valid angle coverage. Unknown azimuths remain unknown; estimated or manual angles must never be mistaken for measured 3D geometry.
- Image quality hints: short edge below 512 px, exact content-hash duplicates, and an optional conservative edge-contrast sharpness score computed from a bounded thumbnail when a new reference is added. Existing alpha.1 references show **not assessed** rather than fabricated sharpness; SQLite migration adds a nullable column without rewriting originals.
- Localized keyboard-focusable 360° interactive angle diagram, quality candidate review buttons, and a two-image comparison dialog with shared zoom slider. Retains the mobile bottom nav and eight languages.
- Comparer lists the first 5000 references (if more); sector totals and quality counters include every saved capture. No automatic rejection or generation.
- Real-image and mobile-browser acceptance must be completed before the 0.5.0 stable release.

## Beta.1 implementation (feature branch; operator acceptance pending)

- Only preinstalled **image** workflows from the saved OrkiLab workflow library are offered. Prepare/validate via the existing ComfyUI conversion and schema validators. Any text or seed edits use validated editable fields; no automatic prompt or hidden model download.
- Each generation requires explicit user confirmation, follows existing single-job/idle-queue safety, and uses OrkiLab's persisted generation history, status polling and targeted cancellation (never blindly clears the shared ComfyUI queue).
- Completed, saved output images (PNG/JPEG/WebP from the *currently configured* validated ComfyUI endpoint) may be **explicitly** imported into an image project subject. Import streams a bounded maximum of 20 MiB, validates the image, and creates a private project-scoped snapshot. It never moves/deletes original photos or ComfyUI files.
- Imported records are forced to `synthetic`, `provenance=workflow` and `review=unreviewed`. An auxiliary SQLite provenance table links the capture to the saved generation ID, ComfyUI prompt ID, workflow ID, graph hash, source filename, output index and integer seed values; the original graph remains in Generation History.
- Camera angles, elevations and distances are optional **manual** metadata, never guessed from generated pixels or prompts. The installed model/workflow must actually support source-image conditioning and view changes; this integration does not guarantee it.
- This phase uses the existing **launcher-local-only** generation endpoints. A phone browser on the LAN can open the shell, but generation/import actions cannot run from a remote IP. Expanding this safely is separately gated behind authenticated remote API review.
- Generation is not an automatically managed multiview batch, nor a claim of 3D reconstruction; multiple views can be run one-at-a-time and manually associated with the subject.
- Before a stable release, test with a real multiview-capable workflow installed on the user's GPU, a real subject collection, cancellation and import, and verify output quality on desktop and mobile.

## Beta.2 implementation (feature branch; operator acceptance pending)

- Project-wide, **explicit** preview/download workflow accessible inside Multiview Studio. Exports only **approved** captures; synthetic captures are excluded by default and can be included as an explicit opt-in.
- Builds a portable **ZIP** with `manifest.json`, `checksums.sha256`, and exact source image bytes under `images/train/<subject_id>/<capture_id>.<extension>` or the equivalent `validation` path. Source type, approved review, angles and optionally synthetic lineage are preserved in the manifest.
- Deterministic subject-level train/validation splits use SHA-256 of a fixed namespace, user seed and subject ID. **All views of a subject remain in one split**, including real and generated views. With few subjects, the actual fraction may differ from the selected validation percentage.
- Reproducibility: stable capture ordering, stable manifest serialization, fixed ZIP entry timestamps, and SHA-256 verification against indexed originals both before and during archive creation. A second export of unchanged records and settings yields identical ZIP bytes.
- Safety: access restricted to launcher-loopback, same-origin checks on both requests, project-scoped SQL, strict path/symlink validation, per-image hash verification and bounded export sizes (500 captures / 350 MiB uncompressed originals / 400 MiB final ZIP). A temporary archive exists only during download; never overwrites or deletes the source images.
- This is a **generic multiview manifest**, not a guaranteed direct training adapter for every LoRA engine. Automatic handoff and per-engine profile compatibility still require dedicated validation.
- No date-dependent field is embedded in the manifest; preview and download never start training or generate images.

## Product goal

Build an integrated **Multiview Studio** for organizing different photographs or video frames of the **same subject** at different angles, distances and elevations, with explicit provenance and controlled compatibility with training datasets. It should be useful for objects, products, sculptures, architectural objects and processional floats photographed from multiple positions. It must never claim that multiple 2D photos automatically constitute a faithful 3D model.

## Proposed interface

- New, translated **Multiview Studio** entry in Workspace, plus contextual access from Dataset Studio and a project-specific entry.
- A project contains one or more **subjects**. Each subject has named **captures** (individual images or extracted frames) and optional **view sets**.
- Grid of collapsible subject cards, lazy thumbnails, search, filters and sorting (date, coverage, angle, source, quality, distance, approved status).
- An interactive orientation coverage diagram with camera-position markers, with unknown angles clearly marked as unknown rather than inferred.
- Side-by-side comparison of two or more captures, including zoom, alignment/manual crop and an optional reference view.
- Field help and accessibility in all eight existing languages, keyboard navigation, clear empty states and per-project persistence.

## Data model and provenance

All records remain project-scoped in SQLite, with migrations and versioned metadata. Original image/video files remain **immutable references**.

Capture fields:
- `subject_id`, `capture_id`, `project_id`, `source_path`, content hash/bytes, captured timestamp (if available), source type (`real_photo`, `video_frame`, `synthetic`, `unknown`).
- Explicit optional `azimuth_deg` (0–359.99), `elevation_deg` (−90…90), `distance_m`, focal length or FOV, rotation/orientation, camera ID and viewpoint name.
- Metadata provenance: `manual`, `embedded_exif`, `workflow` or `estimated`, with estimation confidence and editable validation status. EXIF generally cannot prove azimuth/elevation or distance.
- Caption linkage, source dataset image ID, group and duplicate relation, quality flags, notes, manual approval and revision timestamp.
- Synthetic-image lineage: workflow ID/hash, prompt, seed, base model, LoRA(s), generation time and source references. Synthetic views never silently masquerade as real references.

## Milestones and acceptance

| Stage | Deliverable | Acceptance gate |
| --- | --- | --- |
| **0.5.0-alpha.1 — Capture library** | Subject/view-set creation, image references, manual angle/elevation/distance metadata, provenance, search, preview and grouped cards | Import mixed-angle fixtures; project isolation; invalid angles/paths rejected; zero changes to original files |
| **0.5.0-alpha.2 — Coverage and validation** | Orientation/coverage diagram, overlap/duplicate hints, missing-angle warning, quality assessment and explicit approve/reject | Deterministic coverage from known metadata; unknown positions not invented; camera labels and keyboard navigation verified |
| **0.5.0-beta.1 — Assisted multiview** | Optional ComfyUI multi-reference/view generation via validated installed workflows; manual assignment of generated outputs; source/derived lineage | One explicit job at a time; no hidden model download or generation; prompt/seed/workflow recorded; cancellation/retry and output validation |
| **0.5.0-beta.2 — Dataset preparation** | Project-specific multiview manifest, view grouping, optional holdout grouping and non-destructive export profiles for supported trainer classes | Repeatable export/checksum manifest and group-aware split without leakage across views of the same subject; originals immutable |
| **0.5.0-rc.1 — Integrated testing** | End-to-end UI and API integration, translations, persistence after restart, Windows/Linux CI, realistic capture sets | One real multi-angle dataset including partial/unknown metadata, one supported training handoff, one ComfyUI inference workflow verified on-device |
| **0.5.0 — Stable** | Stabilization, documentation, supported feature/model matrix and upgrade/rollback acceptance | No critical security/data-loss regressions; real Windows/GPU acceptance plus release evidence and resolved blocking bugs |

Each stage should be a separate PR with acceptance fixtures and no silent change to saved training projects.

## Example: an ornate procession float or sculpture

1. Create subject **Procession float A** with real photographs from front, left/right profiles, rear, high oblique and varying distances.
2. Preserve source image files and original EXIF, even if focal length and angle are missing.
3. Manually tag angle/distance and mark uncertain values; compare overlapping views.
4. Use the coverage diagram to identify genuinely missing perspectives and flag camera position uncertainty.
5. Optionally generate *synthetic candidate* views from an installed ComfyUI workflow. Save them separately with model/workflow/seed provenance and require manual confirmation.
6. Export an approved multiview dataset with real and synthetic captures distinguished. If train/validation splitting is requested, group views of the same subject to avoid leakage.
7. When a 3D reconstruction workflow is explicitly installed, track its mesh outputs as derivatives; do not present 2D view management itself as guaranteed geometry or measured CAD.

## Safety and constraints

- **Privacy:** local-only by default; any future remote model/API integration requires explicit opt-in, disclosed transfers and secret handling.
- **Integrity:** immutable originals; reject symlink traversal/out-of-root paths, malformed media and unsafe output destinations; do not overwrite existing exports.
- **Scale:** bounded preview decoding, cancellable scans, pagination/virtualized grids and database migration tests. Distinct error states for missing, corrupted and oversized media.
- **Provenance:** real / extracted / generated and confirmed / estimated must remain distinguishable in the UI, exports and any training job.
- **Model compatibility:** do not assume all LoRA trainers support multi-view conditioning. Advertise only tested export adapters and combinations.
- **Hardware:** do not promise multi-view generation, 3D reconstruction or mesh quality without a validated installed ComfyUI workflow and real GPU test.
- **Avoid mixing milestones:** unfinished 0.4 stable blockers (per-engine dataset profiles, reproducible train/validation split, Windows/Ollama acceptance) must be closed or explicitly carried as blockers, not silently reclassified as 0.5 features.

## Definition of done

A stable 0.5.0 release requires a saved/reloaded capture library, real/synthetic distinctions, optional unambiguous angle metadata, visual coverage with honest unknowns, controlled generated-view lineage, non-destructive and repeatable export, documented supported engines/workflows, tests on Windows and Linux, real local-machine acceptance, and a published changelog with known limitations.

## Out of scope for 0.5.0

General-purpose guaranteed 3D reconstruction from arbitrary images; true multi-view training for every engine; live camera calibration/photogrammetry precision guarantees; bulk cloud GPU farms; automatic publication to model hubs; CAD/STEP/B-rep reverse engineering.
