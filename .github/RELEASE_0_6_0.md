# OrkiLab v0.6.0 — Benchmark Studio (stable)

**STATUS: NOTES PREPARED — RELEASE NOT YET PUBLISHED.** These notes are source-staged for a future stable GitHub Release. [v0.6.0-rc1](https://github.com/jlopfri921/OrkiLab/releases/tag/v0.6.0-rc1) was publicly released and accepted in E1–E6 testing; stable publication requires a separate explicit approval.

## Highlights

- **Benchmark Studio B1–B10.5**: project-scoped comparison runs, variant specifications, persisted observations, provenance and history, conservative read-only reporting, versioned reproducibility declarations.
- **Consent-led generation:** validate supported checkpoint/LoRA API workflows, prepare one selected variant and repetition, then explicitly confirm one GPU submission. No implicit batch generations.
- **Local workflows and projects:** integrated ComfyUI generation, Dataset Studio and project histories; persistent records and safe error handling.
- **Persistent light/dark web themes**, shared navigation and RAM/VRAM diagnostic contrast improvements.
- **Compatibility fixes** for some ComfyUI V3 dynamic controls and optional image input declarations.
- **Licensing:** original OrkiLab contributions Apache-2.0; inherited Academia SD core MIT, with third-party license notices preserved.

## Validation

Operator reported **35/35 PASS** in the published RC1's E1–E6 acceptance: startup/navigation, project persistence, real FLUX.2 9B generation using a local RTX 3090, Benchmark Studio generation and history, cancellation/isolation, visual/mobile checks, backups, licensing and documentation. No operator console or ComfyUI GPU logs were attached to these reports. See [stable acceptance record](https://github.com/jlopfri921/OrkiLab/blob/main/docs/orkilab/RC_0_6_0_STABLE_ACCEPTANCE.md). The stable publishing workflow independently requires Windows/Linux tests from **both** CI workflows on the exact main SHA.

## Compatibility limitations

- Partial ComfyUI workflow compatibility; third-party/custom-node graph schemas can fail validation, even when direct ComfyUI generation works.
- Descriptive pairwise medians **do not prove a model is faster, better or scientifically comparable**; not all model/input bytes, environment factors or cold/warm cache are attested.
- GPU RAM/VRAM monitoring can be global/partial; per-generation attribution and memory leak proof are not provided.
- No weights, models, CUDA bundles or one-click GPU-ready installer are shipped in GitHub's source archive.
- Local tests primarily cover RTX 3090; other GPUs and specialized trainer combinations require independent testing.

## Installation / rollback

1. Stop OrkiLab and back up `settings`, SQLite data, user datasets, workflows, trained LoRA outputs and model weights **at their actual storage paths**.
2. Download the stable source archive or deliberately update a Git checkout after publication. Keep the previous validated `v0.5.0` source/tag and backup for recovery.
3. Start the web workspace with `Iniciar-OrkiLab-Web.bat` on Windows (requires Python environment installed); configure ComfyUI locally where relevant.
4. Test a single compatible workflow with explicit consent; never assume every custom workflow works unchanged.

[README](https://github.com/jlopfri921/OrkiLab/blob/main/README.md) · [Changelog](https://github.com/jlopfri921/OrkiLab/blob/main/CHANGELOG_ORKILAB.md) · [Licensing](https://github.com/jlopfri921/OrkiLab/blob/main/LICENSING.md) · [Stable acceptance](https://github.com/jlopfri921/OrkiLab/blob/main/docs/orkilab/RC_0_6_0_STABLE_ACCEPTANCE.md)
