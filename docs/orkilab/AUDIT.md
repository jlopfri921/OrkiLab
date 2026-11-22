# Initial audit — 2026-11-20

Scope: repository tree, README, launcher HTML/JSON and Python, two representative trainer servers, project_layout, remote_access, file_transfer, requirements, LICENSE, ignore rules and both updater scripts. This is a static targeted review, not an exhaustive line-by-line or hardware audit.

| Finding | Evidence | Priority | Disposition |
|---|---|---|---|
| Updaters overwrite origin and hard-reset | Update_LoRAlab-TrainerStudio.bat/.sh | Critical for fork | Replace with guarded fetch + ff-only merge |
| Repeated trainer endpoints/helpers | server_flux3klein.py and server_qwenimage21.py, e.g. settings/export/run/stop | High | Introduce shared contracts; audit semantic differences first |
| Runtime package installs | ensure_package in representative servers | High | Inventory and move to explicit diagnostics/installation in later PR |
| Remote access is HTTP Basic; local bypass | remote_access.py | High | LAN only; review loopback proxy trust, CSRF and routes before external deployment |
| File access and credentials are sensitive | trainer browse/export/hf-token endpoints; file_transfer.py | High | Threat model, path and authorization tests required |
| Dependency drift | requirements.txt: several unpinned packages, Diffusers pinned commit | Medium | Record tested environment matrix, lock per platform later |
| Model storage migrations already exist | project_layout.py | Medium | Reuse dry-run/migration support; do not duplicate |
| UI smoke harness exists | tools/smoke_test_ui.py | Medium | Run on Windows/Linux; add focused tests over time |

Existing features: dataset forge, captions, queue, preview scoring, export path, HF upload, GPU selector, block swap, DoRA/LoKr/rsLoRA. Avoid duplicates.

Acceptance: unchanged trainer scripts, original UI behavior retained, all branding served from existing assets route, no destructive Git commands in updated scripts, no data uploads, original LICENSE unchanged. Pending: actual launcher smoke test, Windows batch behavior, representative GPU training, comprehensive route/security review.

## Foundation RC follow-up

Reviewed Windows/Linux installer and launcher scripts, queue and Dataset Forge pages, launcher configuration and existing smoke harness. Installers do not show origin-reset commands in the reviewed matches. Added explicit dependency-update opt-in and local Git regression tests. Trainer-specific branding remains intact to avoid changing model-specific asset routing. Static review does not certify security, performance or all trainer behaviors.
