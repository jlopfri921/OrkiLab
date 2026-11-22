# ComfyUI integration — proposed contract

Existing export: Send to Models copies LoRA to selected models/loras folder; export path shared across trainers, metadata embedded. Preserve it. New adapter must run in OrkiLab environment, not install into ComfyUI.

Config: default http://127.0.0.1:8188; explicit opt-in for LAN URL. Read-only health/inventory candidates: GET /system_stats, /object_info, /queue, /history/{prompt_id}. Validate exact node class and model names before generating API-format workflow. Submit only on explicit user action via POST /prompt; track prompt_id, use /ws or polling; retrieve output only through supported endpoints. Confirm against actual ComfyUI version before implementation. No arbitrary URL fetching from untrusted workflows.

Define registry: architecture, variant, loader class, compatible LoRA format, model/text encoder/VAE requirements. Distinguish GGUF and native loaders, do not guess compatibility from file extensions. Initial target FLUX.3 and Qwen 2.1 with native models. Store templates per architecture and test with mocked object_info. Keep file copy atomic and reject collisions by default. Prefer separate GPU scheduling or user confirmation when training is active.

Acceptance: mock tests for missing model/node, unreachable endpoint, invalid workflow, failed job, duplicate filenames, cancellation handling; live smoke run on local machine. Never expose unauthenticated ComfyUI publicly.

## Bridge browser message cloning (ComfyUI Desktop)

If the browser reports `Failed to execute 'postMessage' on 'Window': [object Object] could not be cloned`, the bridge may be attempting to send live ComfyUI editor data containing non-cloneable objects across the tab boundary. The patched `integrations/orkilab_bridge/js/bridge.js` converts the output of `app.graphToPrompt()` to JSON-only data before sending it. Values that cannot be represented as JSON cause a displayed conversion error rather than silently accepting an invalid prompt.

**Apply in a local OrkiLab installation after merging/updating:** restart the OrkiLab launcher if needed, use **Install Bridge** again (pointing to the actual ComfyUI `custom_nodes` folder; this overwrites the bridge JS), fully restart ComfyUI Desktop, and hard-refresh the ComfyUI browser tab (Ctrl+F5). Then use a saved *visual-format* workflow in Generation Studio and click **Convert using Bridge**. Review the resulting API prompt before submitting any generation job.

This is not evidence of an end-to-end ComfyUI runtime test. Custom-node serialization can still fail and should display a specific error identifying the problem. Test also on the installed ComfyUI Desktop version, since browser caching or third-party extension scripts can generate similar `postMessage` errors.

## Persistent postMessage cloning error — isolate source

The v1 JSON serialization patch did not resolve every observed installation error. An upstream ComfyUI frontend / custom-node issue can happen during `app.loadGraphData()` or `app.graphToPrompt()` itself, before OrkiLab sends a prompt. This diagnostic patch labels the failing stage and adds a guard to the OrkiLab-to-ComfyUI send direction. It does not claim to fix an upstream ComfyUI bug.

After applying this branch locally, **reinstall/update the Bridge** to copy its changed JavaScript into ComfyUI's `custom_nodes/orkilab_bridge/js/bridge.js`, fully restart ComfyUI Desktop and hard-refresh ComfyUI's browser tab. Retry the same workflow, then capture the **exact text in Generation Studio** and the browser console stack from the ComfyUI popup (F12 → Console, preserving logs). A message beginning `Bridge failed at loadGraphData` means the failure occurred while ComfyUI loaded the visual workflow; `Bridge failed at graphToPrompt` means conversion failed before the outgoing reply. A message beginning `Bridge failed sending workflow to ComfyUI` identifies the other direction.

To isolate upstream incompatibilities, try the same visual workflow directly in ComfyUI Desktop (open it and use its normal conversion/export functions); then repeat using a minimal workflow without custom nodes. If ComfyUI itself fails, inspect the installed frontend version and extensions rather than repeatedly reinstalling OrkiLab.
