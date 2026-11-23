# OrkiLab v0.6.0-rc1 — draft release notes

**DRAFT ONLY — not published, no tag or release created.** This document prepares a future GitHub prerelease and does not authorize creation of one. Review [RC acceptance](../docs/orkilab/RC_0_6_0_READINESS.md) before publishing.

OrkiLab v0.6.0-rc1 introduces **Benchmark Studio**, a local-first set of tools for declaring, preparing, running and inspecting checkpoint/LoRA comparison sessions through supported ComfyUI API workflows. It also introduces an optional **light mode** alongside the original dark web interface.

## Included

- Local, project-scoped SQLite benchmark runs, variant declarations, terminal observation snapshots and persistent generation lineage.
- Explicit `orkilab-repro-v1` protocol declarations and read-only checks for supported literal checkpoint/LoRA model loaders.
- Guided, individually confirmed ComfyUI submission: activate a draft, prepare one variant and repetition, then separately authorize a **single** generation. No silent or batch submission.
- Read-only observation summaries, audit of historical local data and descriptive pairwise median differences in milliseconds.
- A visible, conservative B10 release-readiness checklist that never authorizes tagging or claiming scientific model superiority.
- Persistent user-selected **light/dark** palette in main web tools, integrated Benchmark UI and shared-shell screens, with eight language button labels and contrast-specific logos.
- Retention of independent Open Source license notices: OrkiLab original contributions Apache-2.0; original Academia SD fork core MIT; third-party assets and weights remain under their own licenses.

## Critical limitations

**Do not interpret a negative median difference as proof one model is faster.** The feature does not attest model weight bytes, complete inference execution, file bytes, physical GPU equality, seed equivalence, dynamic prompt polarity, warm/cold cache policy, or visual model quality. Historical records and declared choices are not substitutes for controlled experiments. Unsupported API/custom loaders remain blocked conservatively.

The explicit submission path can consume GPU time and write ComfyUI output files. User consent, ComfyUI idle state and supported node validation are required; no background comparison batch is automatically scheduled.

The light theme is a visual enhancement. All trainer pages, mobile layouts, embedded panels, color contrast and keyboard focus require final visual acceptance on supported devices.

## Known workflow compatibility constraints (release candidate)

ComfyUI workflow compatibility is **partial, not universal**. OrkiLab may reject or fail to prepare workflows with unsupported custom nodes, unusual API exports or dynamically linked sampler/model choices. Earlier user-reported cases include `KSamplerSelect` with mismatched `COMBO`/`SAMPLER` node schemas. A successful workflow in the ComfyUI UI does **not** automatically imply it is compatible with Benchmark Studio's API-graph preflight.

- The app must fail closed with a useful, actionable error and must not silently rewrite an unsupported graph into a different generation.
- Unsupported workflows do not establish a general Benchmark or release failure, **provided** at least one supported representative API workflow is demonstrated end-to-end on a real NVIDIA RTX 3090 (24 GB) and failures stay non-destructive.
- No claim of full compatibility with all custom-node packs, automatic adapter coverage or cross-workflow scientific comparability is made.
- Broader import/adaptation support and a compatibility catalogue can be addressed in later updates. Confirming the real GPU run and safe failure handling remains a release acceptance gate.

## Provenance and evidence

- Milestones B1–B10.5 implemented in the open [PR #104](https://github.com/jlopfri921/OrkiLab/pull/104).
- **283 Benchmark unit checks operator-reported PASS**, via user acceptance; complete independent Windows/Linux CI and full-app test logs for the exact candidate SHA are still required.
- Source metadata staged at `0.6.0-rc1` **only** on the development branch. Main retains stable 0.5.0 metadata; branch reconciliation and release approval are outstanding.
- [Acceptance checklist](../docs/orkilab/RC_0_6_0_READINESS.md) specifies backup, regression, ComfyUI/RTX GPU verification and approval gates.

## Upgrade caution

Back up the `settings/orkilab` directory, project SQLite files, user datasets, workflow references and LoRA outputs **before** testing any candidate upgrade. Do not delete model weights, modify production settings or rewrite historical Git commits during candidate validation.

**Release command/tag intentionally not provided.** No tag or GitHub Release is authorized until the release checklist passes and the maintainer explicitly approves publication.
