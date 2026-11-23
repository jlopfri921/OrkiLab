# OrkiLab v0.6.0-rc1 — Benchmark Studio (prerelease)

> **Release candidate, not stable OrkiLab 0.6.0.** This source prerelease is for testing and feedback. Keep a backup before updating an existing installation.

## What's new

- **Benchmark Studio B1–B10.5:** local, project-scoped SQLite records for comparison runs, variants and observations; provenance and history inspection; reproducibility declarations and explicit compatibility preflight for supported checkpoint/LoRA API workflows.
- **Controlled ComfyUI execution:** prepare exactly one candidate variant and repetition, review it, then authorize one GPU generation separately. No automatic multi-run batch and no silent generation.
- **Read-only reports:** factual timing summaries and pairwise median differences. The values are descriptive and do **not** prove that one model is objectively faster or better.
- **Light mode:** persistent light/dark theme for the web workspace, Benchmark, Dataset, Queue and shared navigation, with improved RAM/VRAM diagnostic contrast.
- **Workflow compatibility improvements:** validation and safer handling of some ComfyUI V3 dynamic dropdown and zero-minimum autogrow inputs, and explicit API error diagnostics.
- **Open-source attribution:** original OrkiLab additions Apache-2.0; inherited Academia SD core MIT; third-party components follow their own licenses.

## Acceptance evidence

- Final PR #104 head `a5f84e873bed48ba4a117f1b14e52f8d3ef260d4` passed GitHub Actions **RC Validation** and **Foundation checks** on Windows and Ubuntu. This release publisher additionally requires successful **main-branch** checks for its exact SHA.
- Operator reported successful local RTX 3090 24 GB execution in **Nueva generación** (compatible FLUX.2 visual workflow; generation `f69ac654-d111-4c96-ad71-506329085771`).
- Operator separately confirmed a successful **Benchmark Studio** generation recorded in its project, but no Benchmark-specific run ID or console transcript was attached.
- Operator reported successful backup of the `settings` directory, SQLite read-only checks and SHA-256 comparison after copying to an isolated restore directory. Full restored-app startup and external-model/dataset backups were **not** evidenced.
- Readiness and historical test evidence: [RC1 acceptance register](https://github.com/jlopfri921/OrkiLab/blob/main/docs/orkilab/RC_0_6_0_READINESS.md).

## Known limitations

- **Partial ComfyUI workflow compatibility.** Some custom-node graphs, unusual UI exports or conflicting node schemas may be rejected. A workflow working directly in ComfyUI is not necessarily usable by OrkiLab's API-graph preparation. Unsupported graphs should fail safely, without silent edits or unintended submissions.
- Model weights, input-file bytes and dynamic prompt polarity are not fully attested by Benchmark records. No scientific speed-ranking or model quality claim is supported.
- GPU monitor values may be **global** and sampling **partial**; they cannot reliably attribute all VRAM to one workflow or demonstrate a memory leak.
- Light/dark and language coverage may differ in legacy trainer pages. GPU/ComfyUI functionality depends on locally installed nodes, drivers and model weights; no universal hardware compatibility is implied.
- This release includes **source code**, not a GPU-ready installer or prebundled model weights.

## Update / rollback

1. Back up `settings/orkilab`, SQLite databases, datasets, workflow references, generated results and model weights **wherever stored**. Stop OrkiLab before copying its SQLite files.
2. Use a separate checkout of this prerelease tag, or update a backed-up Git installation deliberately. Do not delete existing user data.
3. Configure and verify your local ComfyUI connection, import a compatible workflow, and test a single confirmed generation.
4. To roll back, use the previous stable `v0.5.0` source and restore compatible saved settings from your backup as needed.

[README](https://github.com/jlopfri921/OrkiLab/blob/main/README.md) · [Changelog](https://github.com/jlopfri921/OrkiLab/blob/main/CHANGELOG_ORKILAB.md) · [License policy](https://github.com/jlopfri921/OrkiLab/blob/main/LICENSING.md) · [PR #104](https://github.com/jlopfri921/OrkiLab/pull/104)
