# OrkiLab 0.5.0 — Multiview Studio roadmap

**Status:** 0.5.0-alpha.1 implemented on a feature branch, pending final Windows/Linux CI and on-device browser acceptance; no 0.5 tag/release published. 
**Baseline:** 0.4.0-rc.1 is available in `main` (release metadata); publication of a GitHub Release/tag and the 0.4.0 stable acceptance must be verified separately.
**Owner workflow:** Projects → Dataset Studio → Multiview Studio → Training Engines / ComfyUI.

## Alpha.1 implementation (development)

- Project-linked subject cards and capture references, manually supplied azimuth/elevation/distance, explicit real/photo/frame/synthetic/unknown provenance, review fields and persisted SQLite metadata.
- Read-only local image previews with image validation, SHA-256 checks, size/pixel limits and symlink rejection. Removing a capture or subject removes references, never source files.
- Search/sort by name, angle and distance; local pagination. Separate on-device validation is needed for native Windows/mobile presentation and real image collections.
- Responsive mobile navigation is shared across Workspace, ComfyUI Zone, Dataset Studio, Queue and Multiview: four bottom tabs with an accessible **More** sheet; desktop retains the left sidebar.

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
