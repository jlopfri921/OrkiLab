# OrkiLab v0.5.0 — Multiview Studio (stable release)

The first 0.5 stable version consolidates the open-source OrkiLab local-first workspace around **Multiview Studio**, dataset preparation, optional ComfyUI workflows and human-reviewed results. This release is based on successful automated Linux/Windows checks plus an explicit, documented on-device acceptance record. See the [stable acceptance checklist](docs/orkilab/RC_0_5_0_STABLE_ACCEPTANCE.md) for the tested configurations and scope.

## Included

- **Project-scoped Multiview:** organize subjects and original images, compare photos, keep their source provenance, review capture quality and display a twelve-sector 360° coverage diagram.
- **Recovery and persistence:** link photographs already indexed in Dataset Studio, retain source files and restore project links after restart.
- **Optional Ollama vision:** suggest directions for photos locally, require user confirmation and distinguish qualitative orientation from measured geometry.
- **Optional missing-view generation:** explicitly copy selected references into the correct ComfyUI input folder, or use its API; map connected LoadImage inputs, prepare and confirm a workflow, inspect outputs and import generated images as synthetic/unreviewed.
- **Bundled starter workflows:** Core Preserve, Core Img2Img and Core Variation (one source image, SD-family compatible checkpoint required), downloadable in an offline ZIP and importable from the generation screen.
- **Dataset export:** approved, project-grouped ZIP with provenance, SHA-256 integrity checks and deterministic train/validation partitioning.
- **Accessible UI:** eight-language help, mobile navigation, dedicated ComfyUI area, standalone/hybrid operating modes, refreshed OrkiLab branding and GPU/queue controls.

## Honest compatibility limits

- The **three starter workflows are not geometric camera-control models** and do not reliably infer occluded surfaces. Real multi-reference conditioning, Qwen Image 2.1 and FLUX/Klein editing workflows remain future improvements.
- No model weights are downloaded or bundled. Individual trainers and custom ComfyUI nodes are not universally validated.
- Tested hardware and supported configurations are explicitly recorded in the [stable acceptance checklist](docs/orkilab/RC_0_5_0_STABLE_ACCEPTANCE.md). Workflows outside those configurations remain best-effort.
- Keep backups of your existing `settings/orkilab`, datasets, presets, workflows and model weights before updating. No installer or universal zero-risk rollback is guaranteed.

## Upgrade

On a Git checkout of a previously validated installation, back up persistent data, stop OrkiLab, then run `git pull origin main` and restart. For a reproducible pinned installation, use the immutable GitHub Release source tagged `v0.5.0` after publication.

## Next milestone: 0.6.0

Once stable 0.5.0 is published and verified, development can proceed toward **reproducible benchmarks** and richer, clearly validated model-specific workflows.

[README](README.md) · [Changelog](CHANGELOG_ORKILAB.md) · [Workflow library](workflows/multiview/README.md) · [Stable acceptance](docs/orkilab/RC_0_5_0_STABLE_ACCEPTANCE.md)
