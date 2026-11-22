# Architecture — Foundation

Baseline: upstream-derived main commit 8386cbd1b10e29530e9db8c20d43d14d1a0eb4a6. Evidence: GUI/launcher.html, GUI/launcher.json, scripts/launcher.py, scripts/server_flux3klein.py, scripts/server_qwenimage21.py, scripts/project_layout.py and README.md.

## Current system
Launcher Flask server serves HTML/JS and assets, GPU/network settings, queue and trainer launch API. Each trainer has separate Flask server/UI and subprocess entry points 0_caption, 1_pre_cache, 2_train_lora. Shared job_queue, queue_link, trainer_stream, gpu_stats, lora_options, settings_limits, project_layout, file_transfer, face_match and dataset_forge modules already exist. Models/, Cache_Data/, Outputs/ and settings/ are runtime state. Windows and Linux scripts create an isolated environment; requirements use CUDA 13 and pinned Diffusers source. Model-specific processing remains in existing scripts.

Data flow: image + caption -> pre-cache text embeddings/latents -> trainer -> checkpoint/preview -> export safetensors. Launcher queues jobs; trainer ports start at 5000 and can increase.

## Target
Add orkilab/core, integrations, datasets, library and benchmark as independent Python modules behind adapters. First introduce a read-only project/model catalog and registry. Define typed versioned contracts before any unified UI. SQLite for index only; paths and model files remain source of truth. Separate API, services, storage, GPU coordination and frontend. No new framework in Foundation.

## Boundaries
Never invoke GPU jobs through import side effects; use existing queue contract. Avoid shared Python environment with ComfyUI. Preserve existing filenames, settings and LoRA exports. Multi-GPU scheduling is future work. See roadmap for acceptance gates.
