# Foundation release candidate acceptance

Version 0.1.0-rc.2. Scope: documentation, branding, safe fork update and non-GPU tests; no changes to trainer engines or external ComfyUI.

## Automated gates
Run `python -m unittest discover -s tests -v` with standard Python and Git. CI runs on Windows and Ubuntu. Tests check SVG parsing, launcher links, version consistency, license attribution, update script guards, and actual local fast-forward/rejection behavior using disposable repositories. No network or model downloads in tests.

## Local acceptance (pending until executed)
1. Stop running training jobs. Back up settings and inspect git status and git remote -v.
2. Clone or switch to Foundation branch. Run Start_LoRAlab-TrainerStudio.bat, open http://127.0.0.1:4990. Verify logo, favicon, version, About, trainer cards, queue and language settings.
3. Run tools/smoke_test_ui.py using project venv (Chrome/Edge required); record exit status.
4. Open FLUX.3 Klein trainer. Use authorized small dataset, pre-cache, train a small sample and inspect checkpoint/preview. Stop/resume and export safetensors into a test folder. Verify LoRA loads in ComfyUI with compatible base. Record driver, CUDA, torch, VRAM peak and time; do not claim results without measurements.
5. Test updater in disposable clone, with clean/dirty/diverged/detached branch. Verify origin unchanged and dirty work remains. Source update by default; --deps only intentionally within local venv.

## Release gate
Merge only after reviewing diff and CI status; stable 0.1.0 requires local checks. Record failures and open issues. Roll back by reverting the merge commit (do not reset user work). Do not remove models, settings or outputs. External deployment security and full trainer validation remain outside Foundation.

## Branding follow-up

All 20 trainer HTML interfaces (21 launcher engine entries) now use OrkiLab vector assets in model-local asset directories. The original image files remain available for backward compatibility and historical documentation. The selected PNG has not yet been imported. Test the live trainer and Dataset Forge asset routing on the installed environment. Automated checks do not establish GPU readiness.
