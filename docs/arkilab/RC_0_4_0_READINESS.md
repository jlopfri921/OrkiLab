# OrkiLab 0.4.0-rc.1 — release acceptance register

**Prepared:** 2026-11-21
**Version target:** `0.4.0-rc.1`
**Release state:** NOT TAGGED / NOT PUBLISHED
**Source:** `release/0.4.0-rc.1` (PR to `main`)
**Previous published prerelease:** `v0.3.0-rc.1`
**Automated validation:** foundation run `44917024684` — SUCCESS; RC validation run `44917024693` — SUCCESS on candidate commit `45a10106be00492ab16a106503ab3b48b601ff22` (before updating this evidence register). Both include Windows and Ubuntu. The RC run completed **231 tests per platform, zero failures**, and checked version metadata. This evidence-update commit requires a fresh final CI pass before merge/tag.

This register distinguishes automated evidence, user-reported tests, and hardware checks not yet confirmed. Do **not** describe `0.4.0` as stable simply because `0.4.0-rc.1` has passed CI.

## Acceptance criteria

| Area | Gate | Status at preparation | Evidence/next action |
|---|---|---|---|
| Version consistency | `VERSION_ARKILAB`, `GUI/launcher.json`, README badge | PASS CI | Version consistency passed on candidate commit; repeat on final evidence commit |
| Import safety | Original image/caption/LoRA and unrelated model files untouched | PASS CI | Run fixture tests, then Windows test with backup |
| Core regression | Full Python test suite, JS syntax, release metadata | PASS CI | GitHub Actions (Windows + Ubuntu, Python 3.13) |
| Project & curated LoRA | Checkpoint ratings, Best/Final, persistence and image reference | REPORTED | Operator reported OrkiLab functioning; repeat the relevant cases on candidate |
| ComfyUI comparison | Project checkpoint 100 vs later steps, fixed seed/workflow, installed paths | REPORTED | Project 'Prueba' comparison was exercised earlier; record candidate evidence separately |
| Generation history | Collapsible records and server search/filter/sort, page boundaries | PASS CI | Unit tests and local UI smoke |
| Dataset Studio | Image import, duplicate analysis, captions, prepared folder, no source mutation | NOT VERIFIED END TO END | Real Windows images and dataset preparation |
| Project → training | Prepared image dataset in isolated trainer settings, successful real GPU pre-cache/train | NOT VERIFIED END TO END | At least one supported image trainer |
| Local Ollama | Caption preview/batch, cancellation and VRAM/resource behavior | NOT VERIFIED END TO END | Real installed vision-capable Ollama model |
| Navigation/version/footer | Version below sidebar, GitHub footer, i18n | PASS CI; VISUAL PENDING | Browser view on Windows |
| Desktop packaging | Standalone portable/installer and rollback | OUT OF RC SCOPE | Tracked for later release; no package promised |
| 0.4.0 stable prerequisites | Per-engine export profiles, train/validation split, reproducible round trip and supported hardware matrix | NOT COMPLETE | Do not label this candidate stable |

## Test plan before a tag or release

1. GitHub Actions: ensure **both** OrkiLab foundation checks and OrkiLab RC validation complete successfully on the *exact* candidate SHA for both Windows and Ubuntu. Check the number of tests and list any skips.
2. On Windows, start from `main` or a safe candidate checkout after backing up `settings/orkilab/`, datasets and ComfyUI project/LoRA folders. Confirm version, sidebar, footer, language switching and navigation.
3. In Projects, select an existing test project without modifying its source files. In Dataset Studio, index a small disposable image set, review duplicates, save captions and generate the prepared training folder. Compare source checksums before/after.
4. Launch the matching trainer through the project and verify isolated draft dataset path; run representative pre-cache/training on the real GPU when the environment supports it. Mark untested engines as unsupported/unverified, never as passed.
5. Connect to ComfyUI, run a representative prepared workflow and verify cancellation/history. Compare project checkpoints using identical prompt/seed, score models and mark a Final; upload/view reference image in the curated library. Restart and verify all metadata persists.
6. Perform upgrade/restart and rollback from backup, checking that old SQLite data, generated `.safetensors`, workflow JSON and dataset originals remain intact.
7. Record actual evidence (commit hash, commands, screenshots or logs, hardware and versions), outstanding issues, and accept/reject the candidate. Only then create the exact `v0.4.0-rc.1` tag and a GitHub prerelease; `v0.4.0` stable requires the separate stable gates.

## Explicit limitations

- CI does not download model weights or exercise GPU training.
- Supported ComfyUI custom nodes and LoRA model/loader compatibility depend on the installed ComfyUI server.
- OrkiLab can store user-entered training-time and hardware metrics but cannot reconstruct historical measurements that were never recorded.
- Manually selected reference images are stored separately from immutable original LoRA weights.
- Prepared training datasets are separate copies; original image files remain intact. Exact trainer-specific formats and valid train/validation split have not been certified across all engines.
- The GitHub connector used for PR and code operations does not, by itself, establish that a release/tag exists. Do not claim publication without verifying it.
