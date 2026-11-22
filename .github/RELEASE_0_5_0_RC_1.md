# OrkiLab v0.5.0-rc.1 — Multiview Studio (prerelease)

> **Release candidate.** This is an early-access source release for testing and feedback, **not** a stable 0.5.0 release or a guarantee that every GPU, model, trainer or third-party ComfyUI workflow is supported.

## Highlights

OrkiLab is a free, open-source and local-first workspace that brings together projects, data preparation, LoRA training, compatible ComfyUI generation, GPU monitoring and reusable exports.

- **Multiview Studio**: create persistent project-linked subjects and photo views, recover references from Dataset Studio, inspect 12-sector camera coverage, compare/review photos and preserve originals.
- **Local Ollama vision (optional)**: propose qualitative viewing direction, elevation and apparent distance, with explicit review and persistence. AI suggestions are **not numerical camera measurements**.
- **Generate missing viewpoint**: select real reference photographs; send copies to ComfyUI's real input directory (typed path or native folder picker) or via its API, map connected `LoadImage` nodes, preview/edit prompts, confirm generation and review/import synthetic output.
- **Official Multiview workflow library in the same interface**: three bundled core-only Img2Img API templates—**Core Preserve**, **Core Img2Img** and **Core Variation**—plus an offline ZIP download, local guided import with a checkpoint and likely-compatible workflow filtering.
- **Dataset ZIP export**: subject-grouped train/validation image sets, SHA-256 verification, reproducible manifests, optional inclusion of approved synthetic images; source image files stay untouched.
- **Eight-language help and navigation**: expanded Guide explains the entire app, its philosophy and goals, with consistent OrkiLab branding and responsive layouts.

## Get started

1. Back up `settings/orkilab/`, project images, training configurations and any ComfyUI workflows.
2. Update an existing Git clone using `git pull origin main` or download this release source. Do **not** delete existing images or `.safetensors` files.
3. Launch OrkiLab and open **Workspace → Multiview Studio**.
4. Choose an **Image** project, link your existing real images, optionally review Ollama orientation labels and open **Generate missing viewpoint**.
5. Select the configured ComfyUI `input` folder or API transfer method, copy a reference, import a supported graph if needed, prepare it and explicitly confirm any GPU generation.

## Requirements and limitations

- ComfyUI Desktop/Portable users must supply model weights and ensure nodes are installed. The starter templates use a standard image-to-image graph for **compatible SD-family checkpoints**, **not** FLUX or Qwen weights.
- These Img2Img graphs **do not guarantee correct new camera geometry** or preservation of hidden object details.
- **Qwen-Image 2.1 Edit, FLUX.3 Klein Image Edit, genuine 2–4-photo multi-reference conditioning and validated camera control** are planned for later updates. Their upstream examples are reference links, not directly supported OrkiLab templates.
- The ZIP is a general dataset archive, not necessarily the exact required layout for every trainer.
- Optional Ollama and ComfyUI are independent and not installed/downloaded automatically.
- Sensitive generation/exports are restricted to the launcher computer; browsing from a remote phone is not proof of remote execution permissions.
- Automated Windows/Linux tests do not validate full VRAM/GPU/model compatibility, Windows folder dialogs or workflow faithfulness.

## Documentation

- [Project README](README.md)
- [Multiview workflow library and compatibility](workflows/multiview/README.md)
- [0.5.0 candidate acceptance register](docs/orkilab/RC_0_5_0_READINESS.md)
- [Full changelog](CHANGELOG_ORKILAB.md)
- [Roadmap](docs/orkilab/ROADMAP.md)

## What happens next?

Test and fix RC.1 issues on a real supported setup, document results and rollback behavior, then publish **v0.5.0 stable** only after passing release acceptance. **0.6.0** development begins afterwards, initially with comparative benchmarks and reproducible evaluations.
