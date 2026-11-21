# Managed checkpoint installation in ComfyUI (draft PR #74)

OrkiLab can copy selected training checkpoints into a local ComfyUI installation for comparisons. This is **opt-in** and never changes or deletes training outputs.

## Naming

A project checkpoint named `Flux3Klein_LoRA_step_300.safetensors` is copied to:

`ComfyUI/models/loras/OrkiLab_Prueba_Flux3Klein_LoRA_step_300.safetensors`

The readable project name is normalized for safe filenames (for example, accents are removed and spaces become underscores). If two projects would produce the same target filename, the manager refuses to overwrite a copy owned by another project. Project ownership is still tracked internally by ID. The comparison endpoint maps the project checkpoint to this managed name when ComfyUI reports it in the node's LoRA choices. Legacy/manual names remain supported.

## Usage

1. Open ComfyUI Zone → LoRA Comparator → Project checkpoints.
2. Select a project and the desired steps (2–6 for a comparison).
3. Enter the **existing folder path on the launcher PC** ending in `ComfyUI/models/loras`. The folder is remembered in the host's ComfyUI connection settings after a successful Install, Uninstall or Check, and restored when OrkiLab is reopened. A network or remote-only ComfyUI server cannot use this local file management endpoint.
4. Choose **Install selected**. A destination that exists but is not an unchanged, already registered OrkiLab copy will never be overwritten.
5. Refresh the models in ComfyUI (or restart ComfyUI), **then prepare the workflow again** so its `lora_name` choices are current. Confirm and run the comparison.
6. To free disk space, select the checkpoints and choose **Uninstall selected**. Confirm removal. This only removes tracked copies whose file hashes still match their installation records; never the training Outputs source.

**Important:** The local manager checks the supplied path and files on disk. It does not control model folders on a remote ComfyUI host, and does not itself reload ComfyUI's in-memory model options. It uses a local manifest in `settings/orkilab/managed_checkpoints.json`.

## Validation still required

Windows and Linux automated tests, plus manual end-to-end testing on ComfyUI Desktop. Keep the PR in draft until validated. Never merge based on code-only inspection.

## Review checkpoints and curate the trained-LoRA library

In **ComfyUI Zone → LoRA Comparator → Project checkpoints**, rate each checkpoint from 1 to 5. Select **Best** for shortlisted variants or **Final model** for the chosen release candidate. Only these manually curated checkpoints appear in the **Trained LoRA library** on the **Projects** page. A project may have multiple Best models but only one Final model at a time.

Each catalog card includes:
- Project, training engine, final checkpoint step and file paths (automatically sourced from OrkiLab).
- Rating (1–5), observations and Best/Final status (user selection).
- Base model identifier (editable, as the trainer-engine ID alone does not prove the precise base-model weights).
- Workflow used for comparison (recorded from the selected saved comparator workflow when explicitly requested, not guessed).
- Training duration in minutes, GPU name, GPU VRAM capacity, peak VRAM and peak system RAM. These are optional manually supplied values with provenance **Manual**; blank unknowns show **Not recorded**. No invented historical telemetry.
- The review date via the metadata `updated_at` field.

Catalog records use the local `settings/orkilab/checkpoint_reviews.sqlite3` database. The database stores metadata only; original .safetensors remain in the trainer Outputs directory. Unmarking Best/Final removes the entry from the curated library but retains its review and original file. Changing Final automatically clears the old Final designation within the same project, without removing a separate Best selection.

The catalog currently covers the image-project checkpoint inventory available to the comparator. A future extension can ingest measured hardware/runtime telemetry directly from training history when available, including provenance; the current implementation does not promise historical automatic measurements.
