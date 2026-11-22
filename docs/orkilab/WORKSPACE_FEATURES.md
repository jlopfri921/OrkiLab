# OrkiLab Workspace — feature guide and implementation status

Last reviewed: 2026-11-20. **Development notes, not a stable release claim.** The version file is still `0.2.0-rc.1`. Features below are implemented on the repository's default branch; real ComfyUI Desktop integration, individual trainer regression and GPU smoke testing are still required.

## Navigation and usability

### Focused Workspace navigation (current development branch)

- The **Dashboard**, **Projects**, **Training engines** and **GPU Manager** links now open **separate views** within `/workspace`, rather than displaying unrelated sections together. Existing routes remain `/workspace#overview`, `#projects`, `#engines` and `#gpu-manager`.
- The active Workspace and ComfyUI section is highlighted. Every section displays its title and a collapsible **What can I do here?** explanation. Help is contextual to the selected section; it is not an automatic explanation of every trainer setting.
- The shared responsive page keeps one main content column beside the active navigation, with compact navigation on smaller screens and keyboard-visible focus indicators.
- Contextual help strings have translations in Spanish, French, German, Portuguese, Italian, Japanese and Korean alongside English. User-generated model and node names retain their original text.
- The project registry, existing trainer launchers and GPU monitoring continue to use their existing API endpoints. This iteration changes navigation and presentation, not training engine internals.
- **Pending:** real browser regression testing on mobile/tablet, testing all trainer pages, checking language switching across all controls and removing obsolete legacy views only after modern equivalents are validated.


- The modern Workspace at `/workspace` is the launcher hub, with project registry, training engines, queue, configuration and a dedicated **GPU Manager** (`/workspace#gpu-manager`).
- **ComfyUI Zone** lives at `/workspace/comfyui` and has a separate left-hand navigation and a return-to-Workspace link. Modules are connection, model inventory, node explorer, workflow library, generation studio, generation history and LoRA comparator.
- Workflow library can be collapsed, remembers its open/closed state in browser storage and scrolls internally when there are many entries. Import and folder synchronization panels are collapsible.
- Labels and contextual instructions are translated via `GUI/i18n.js` and `GUI/locales/*.json`; untranslated node titles and custom-node metadata can remain in their source language. Supported UI languages: English, Spanish, French, German, Portuguese, Italian, Japanese and Korean.
- New/updated interfaces generally expose the essential actions first and keep technical details in collapsible areas. The complete legacy trainer interface replacement has **not** been validated for every trainer.

## ComfyUI connection and library

1. Set `native`, `comfy` or `hybrid` mode in **ComfyUI Connect** and configure the ComfyUI URL. Connected mode is required for generation.
2. **Model library** displays read-only inventories and origin/category filters. Matching filenames do not prove byte-identical models.
3. **ComfyUI nodes** lists detected custom and built-in nodes, with capability filters. Metadata inspection is not a functionality guarantee.
4. **Workflow library** imports UI-format and API-format JSON or synchronizes a local folder recursively, without modifying original files. It offers search, categories, favourites and node inspection. Nodes named `LoraLoader` or `LoraLoaderModelOnly` are flagged as LoRA-compatible candidates; custom loaders and subgraphs may require verification.

## ComfyUI Bridge and generation

- The **OrkiLab Bridge** extension source lives in `integrations/orkilab_bridge/`. Install it through the Generation Studio panel into ComfyUI's `custom_nodes` folder, then **restart ComfyUI**. The bridge uses a dedicated ComfyUI browser tab to load a UI workflow and request ComfyUI's own API-graph conversion (including compatible subgraphs).
- Without Bridge, the local converter handles only a conservative subset of UI nodes. A workflow with unsupported subgraphs may fail preparation; use Bridge rather than modifying the original workflow.
- Generation Studio supports preparation, graph review and explicit submission. It exposes editable scalar/choice fields based on ComfyUI node schemas; linked inputs are not edited, and the saved workflow remains unchanged.
- Editor UI separates essential and advanced parameters, offers random seeds where an editable integer seed exists, and stores up to 30 browser-local presets **per workflow**. Presets are not yet shared across devices.
- Submitted generations are recorded in `settings/orkilab/generations.sqlite3`, with the graph, workflow reference, state and known output descriptors. Generated media **remains on ComfyUI**. Results may be previewed as images/audio/video and downloaded through a restricted local proxy. Mesh files can be downloaded; interactive 3D preview is not yet implemented.
- **Generation history** shows stored runs, API graph JSON and output references. The file remains accessible only while retained by ComfyUI.

## LoRA Comparator — current capabilities and limits

1. Open `/workspace/comfyui#compare` and select a workflow in the comparator itself. The list prioritizes detected standard LoRA loader nodes, followed by entries needing investigation.
2. Click **Prepare selected workflow** (or **Prepare with ComfyUI Bridge** for UI graphs). This shares the same preparation pipeline as Generation Studio and does not execute generation.
3. Select a recognized standard LoRA loader, enter 2–6 distinct strengths between -2 and 2 (decimal points), and explicitly confirm the comparison.
4. Runs are submitted one at a time; outputs are displayed together. **Stop after current** prevents additional submissions but does not cancel a running ComfyUI job.
5. The prepared graph retains the same prompt and seed. On standard `LoraLoader`, model and text-encoder strengths are adjusted together. Weight zero disables only the *selected* LoRA; any other LoRAs in the graph remain active.

Current support: `LoraLoader` and `LoraLoaderModelOnly` with editable `strength_model` (and `strength_clip` for the former). Custom LoRA loader nodes, a cross-LoRA file picker, checkpoint comparison, automatic seed selection, simultaneous inference and results benchmarking **are not available**.

## GPU Manager — no ComfyUI restart required

- Open `/workspace#gpu-manager` or use its Workspace navigation link.
- The read-only endpoint `GET /api/workspace/gpu/monitor` calls the local `nvidia-smi` executable with a fixed GPU query, no shell, a 5-second timeout and a short cache. It shows detected NVIDIA GPUs, VRAM total/used/available, GPU utilization and temperature where supported by the driver.
- The panel refreshes every five seconds **only when visible**; manual refresh and an auto-refresh toggle are provided. It warns on high VRAM occupancy or an active OrkiLab training task.
- No GPU process is terminated, unloaded, reconfigured, queued or assigned automatically; the manager is an *observer*, not a scheduler. VRAM figures cover other applications too. If NVIDIA tools or supported metrics are unavailable, the UI displays a fallback message.
- The monitoring endpoint is limited to requests from the launcher PC's loopback interface.

## Tests and outstanding validation

- JavaScript parsing and isolated code-level checks are not substitutes for browser or real-GPU testing. **The browser flows, ComfyUI Bridge, conversion of nested subgraphs, playback/range proxy, LoRA comparisons and GPU metrics on actual hardware remain unverified.**
- Validate imports in the launcher environment, inspect browser console, confirm local route permissions, run a known simple API workflow, then a real visual workflow with Bridge.
- Validate ComfyUI Desktop Bridge after restarting ComfyUI; ensure the extension is loaded and the prepared graph corresponds to the original nodes.
- Verify output media, history persistence after restart, sequential comparison and how the app behaves when ComfyUI is unavailable.
- Verify GPU telemetry with NVIDIA drivers, multi-GPU cases and unavailable metrics; confirm that a running training job does not allow conflicting generation submissions.

## Code map

| Component | Implementation |
|---|---|
| Workspace interface | `GUI/workspace.html` |
| Workspace routes | `scripts/workspace_routes.py` |
| GPU sampling | `scripts/gpu_monitor.py` |
| ComfyUI connection | `scripts/comfyui_connect.py` |
| Workflow library | `scripts/workflow_library.py` |
| Generation endpoints | `scripts/generation_studio.py` |
| Graph conversion | `scripts/workflow_conversion.py` |
| Parameter validation | `scripts/generation_parameters.py` |
| Generation history | `scripts/generation_history.py` |
| Bridge frontend | `integrations/orkilab_bridge/js/bridge.js` |
| Localization | `GUI/locales/` |

See also [roadmap](ROADMAP.md), [changelog](../../CHANGELOG_ORKILAB.md) and [repository README](../../README.md).
