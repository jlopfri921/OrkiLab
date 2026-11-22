# OrkiLab contributor instructions

- Preserve upstream license, credits, existing trainers, model-specific behavior and public formats.
- Read docs/orkilab/ARCHITECTURE.md, AUDIT.md and SECURITY.md before changes.
- Use small branches and PRs; never force-push or reset user work. Keep origin as the fork and upstream as AcademiaSD.
- Use standalone modules under orkilab/ for new features. Prefer adapters to rewriting training scripts.
- Do not install packages into ComfyUI or download models during unit tests. Never commit datasets, secrets, weights or caches.
- Test new logic with synthetic fixtures. Run existing tools/smoke_test_ui.py in the project environment before merging UI changes; hardware tests require explicit local validation.
- Clearly distinguish planned, implemented and measured features. Update CHANGELOG_ORKILAB.md and VERSION_ORKILAB with releases.

- Use English for new documentation. Keep upstream attribution and technical publisher IDs intact. Use OrkiLab for all visible branding.
