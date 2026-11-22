# OrkiLab 0.4.0-rc.1 — prerelease

**Status:** release candidate / prerelease, **not stable OrkiLab 0.4.0**.

## Highlights

- Project-linked Dataset Studio: image indexing, duplicate/quality review, explicit manual captions, caption exports, optional local Ollama vision caption previews and non-destructive prepared image/caption folders.
- Project-to-training handoff for supported trainers using isolated draft settings; validates the selected prepared dataset.
- ComfyUI LoRA checkpoint management and comparison; persistent local paths; stars (1–5), Best/Final flags, a curated **Mis LoRA entrenados** library, reference pictures and training/test metadata.
- Collapsible generation history and LoRA cards; search, filtering and sorting across projects, history and curated models.
- Shared navigation and version beneath the left menu; direct official GitHub link in the footer; multilingual UI.

## Automated testing

- Windows/Linux foundation and RC validation: **238 unit/regression tests per platform**, zero reported failures in the Dataset Studio hardening PR #77.
- Fixture coverage includes source hash preservation, repeatable manifest export, rejection of changed/rejected images, path/symlink checks, and rejecting incomplete or tampered datasets at training handoff.

## Limitations and release scope

- CPU-only CI **does not verify real GPU pre-cache/training**, every LoRA trainer/dataset convention, or installed ComfyUI custom nodes.
- Real Windows GUI native folder-picker checks, Ollama inference/cancellation/VRAM behavior, and complete per-engine export compatibility need on-device acceptance.
- General per-engine dataset profiles and reproducible train/validation split are not yet certified. The 0.4.0 stable release remains gated.
- Original images, `.safetensors` and workflows are intended to remain untouched; prepare backups of `settings/orkilab/` and your datasets before upgrading.

See [0.4 release acceptance](https://github.com/jlopfri921/OrkiLab-LoRA-TrainerStudio/blob/main/docs/orkilab/RC_0_4_0_READINESS.md) and [0.5 Multiview Studio roadmap](https://github.com/jlopfri921/OrkiLab-LoRA-TrainerStudio/blob/main/docs/orkilab/MULTIVIEW_0_5_ROADMAP.md).

**Install/update:** `git switch main && git pull origin main` or use the prerelease tag. This is a source-code prerelease, not a packaged installer.
