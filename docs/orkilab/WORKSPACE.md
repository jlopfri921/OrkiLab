# Workspace development preview

Version 0.2.0-dev.1. Opt-in route `/workspace`; classic launcher remains the default. Projects are metadata only, stored in `settings/orkilab/projects.sqlite3`, excluded by Git. Create/list/archive/restore supported. No data deletion, model downloads, training orchestration, project import, ComfyUI integration or live telemetry beyond existing launcher endpoints yet. Existing remote-access middleware applies when launched normally. Back up the SQLite database with the launcher stopped. Run `python -m unittest discover -s tests -v` and validate the UI locally. Foundation GPU acceptance remains open.

## Default entry point and direct launching

Workspace is served at `/` and `/workspace`. `/legacy` is a temporary settings fallback. All configured engines can be launched directly using the existing `/api/launch` endpoint. When another engine is open, Workspace offers parallel launch, close and replace, or cancel. Replacement requires explicit selection and remains subject to the backend's training protection. Active training disables replacement; parallel launch and cancellation remain available. It waits for readiness using `/api/status` and navigates to the returned trainer URL. Projects open the associated engine only; they do not inject metadata into training settings. Runtime validation remains pending.
