<p align="center"><img src="assets/orkilab/orkilab-hero-v3.svg" alt="OrkiLab — LoRA Trainer Studio" width="100%"></p>

<p align="center"><strong>Train. Adapt. Create.</strong><br>Local-first LoRA training for image, video and audio.</p>

<p align="center">
  <a href="VERSION_ORKILAB"><img alt="Version 0.5.0-rc.1" src="https://img.shields.io/badge/version-0.5.0--rc.1-087F91"></a>
  <a href="LICENSING.md"><img alt="Apache-2.0 and upstream MIT" src="https://img.shields.io/badge/license-Apache--2.0%20%2B%20MIT-315DB3"></a>
  <img alt="Windows and Linux" src="https://img.shields.io/badge/platform-Windows%20%7C%20Linux-293C60">
  <a href="https://ko-fi.com/jorgelf"><img alt="Support OrkiLab on Ko-fi" src="https://img.shields.io/badge/Ko--fi-Support%20OrkiLab-FF5E5B?logo=kofi&logoColor=white"></a>
</p>

<p align="center"><a href="#orkilab-050-rc1--current-release-candidate">What’s new (0.5.0)</a> · <a href="#quick-start">Quick start</a> · <a href="#training-engines">Training engines</a> · <a href="docs/orkilab/ROADMAP.md">Roadmap</a> · <a href="CHANGELOG_ORKILAB.md">Changelog</a> · <a href="#credits">Credits</a></p>

# OrkiLab — LoRA Trainer Studio

Maintained by [jlopfri921](https://github.com/jlopfri921). OrkiLab is an independent, open-source and local-first workspace for adapting generative models with LoRA and connecting training, datasets and optional ComfyUI image-generation workflows. Workspace is the default interface. **Version v0.5.0-rc.1 is published as a GitHub prerelease; stable v0.5.0 remains pending final acceptance.** The preceding public prereleases are [v0.4.0-rc.1](https://github.com/jlopfri921/OrkiLab/releases/tag/v0.4.0-rc.1) and [v0.3.0-rc.1](https://github.com/jlopfri921/OrkiLab/releases/tag/v0.3.0-rc.1).

## OrkiLab 0.5.0-rc.1 — current release candidate

**Current source version: `0.5.0-rc.1`.** [**GitHub prerelease `v0.5.0-rc.1` is published**](https://github.com/jlopfri921/OrkiLab/releases/tag/v0.5.0-rc.1), from validated commit `b4bc236bd61db2888aa035986b6dca84126dd83b` (2026-11-22). This is **not** stable `v0.5.0`. The preceding prerelease is [v0.4.0-rc.1](https://github.com/jlopfri921/OrkiLab/releases/tag/v0.4.0-rc.1).

**Why OrkiLab exists.** OrkiLab aims to be an independent, open-source, local-first workbench that connects projects, data preparation, LoRA training, compatible ComfyUI generation, model/GPU inspection and export. It coordinates tools and models installed by the user rather than being a model itself. The [eight-language in-app guide](http://127.0.0.1:4990/workspace/guide) now explains the overall philosophy, practical use, individual modules, limitations and future direction.

### What's included in 0.5.0-rc.1

| Area | Implemented functionality | Important limitation |
| --- | --- | --- |
| **Multiview subjects and captures** | Persistent project-scoped subjects, photo/video/synthetic provenance, names, annotations, search/sort, optional manually entered camera angles and review metadata | Images remain at their original paths; unknown numerical camera angles stay unknown |
| **Viewpoint coverage and comparison** | Twelve-sector 360° azimuth coverage display, missing-angle diagnostics, quality/duplicate hints, approval/rejection, two-image comparison with zoom | Estimated directions are not calibrated camera positions |
| **Projects and Dataset Studio integration** | Discover active Image projects, recover already indexed photos, link selected images to subjects without moving or duplicating originals, persist relationships after restart | A dataset handoff is not a validated full trainer run |
| **Optional Ollama vision** | Discover locally installed vision models, suggest qualitative orientation/height/apparent distance for individual photos, human confirmation and persisted metadata | No automatic Ollama/model installation or invented azimuth/elevation degrees |
| **Generate missing viewpoint** | Select 1–4 real references; stage copies by choosing a ComfyUI `input` folder (manual path or native Browse) **or** via the API; inspect/reference-map connected `LoadImage` nodes manually or automatically, choose a prompt and explicitly submit a job | Requires an actually compatible image-conditioned workflow; does not reconstruct unseen geometry |
| **Review and record synthetic results** | Generation history/lineage, source reference IDs, requested-view labels, targeted cancellation and explicit import as `synthetic` and `unreviewed` | Generated perspectives and labels are never treated as measured angles |
| **Multiview ZIP export** | Preview and explicitly export approved, grouped subject datasets, SHA-256 source checks, deterministic manifest/archive, train/validation grouping, optional inclusion of approved synthetic photos | The generic ZIP is not a universally supported trainer input |
| **Workflow compatibility and official library** | Prefer likely compatible reference workflows, allow reviewing all; download offline ZIP and import **three** OrkiLab core-only single-photo img2img templates with a selected installed checkpoint in the same Multiview screen | Starter graphs need compatible SD-family checkpoints; they do not guarantee camera rotation or support FLUX/Qwen models directly |
| **Multilingual UI and navigation** | Eight UI languages in Multiview/AI helpers, guide translated in eight languages, responsive mobile bottom menu, clearer ComfyUI-only navigation, context help and version at the bottom of the left menu | Legacy trainer/custom-node wording may still require checking |
| **Operating modes and identity** | Standalone (without ComfyUI tools), connected/hybrid, optional independent Ollama, consistent OrkiLab source/asset/documentation naming and branding regression checks | The UI hiding a module is not permission to use its API remotely |

**Official workflows today:** [Core Preserve](workflows/multiview/orkilab-multiview-core-preserve-api.json), [Core Img2Img](workflows/multiview/orkilab-multiview-core-img2img-api.json), [Core Variation](workflows/multiview/orkilab-multiview-core-variation-api.json). Their defaults are denoise 0.30, 0.55 and 0.72 respectively, with one reference photograph per template. Full [Multiview workflow README](workflows/multiview/README.md), including dependencies and Desktop/Portable caveats.

**Future improvements (not included, not prevalidated):** dedicated **Qwen-Image 2.1 Edit**, **FLUX.3 Klein Image Edit**, true **2–4-image multi-reference conditioning**, and validated **camera control**. The app may link to upstream ComfyUI examples; these are external references, not official ready-to-run OrkiLab templates.

### Multiview workflow: from real photographs to a reviewed result

1. Create or open a **Project** with category `Image`. Open **Multiview Studio**, create a subject and link real photographs from Dataset Studio.
2. Optionally use **Ollama** to suggest qualitative orientation. Check, correct and explicitly save the suggestions; leave unknown numeric angles empty.
3. In **Generate missing viewpoint**, select photos. For the three bundled core templates, use **one** image. Specify the actual ComfyUI **input** folder or **Browse**, or choose API upload.
4. **Copy selected photographs**, preserving originals. Choose a suitable workflow; if none is detected, the embedded **Official OrkiLab workflow library** offers a ZIP download, GitHub links and guided import.
5. Select a checkpoint actually installed in the running ComfyUI, import the starter template, **Prepare workflow**, inspect connected `LoadImage` inputs and map each reference manually or automatically.
6. Review the requested direction/prompt and explicitly confirm generation. Inspect the output, then choose whether to import it as **synthetic/unreviewed**.
7. Approve only reviewed captures and export the grouped ZIP with its manifest and hashes. No automatic photo-to-3D or geometric truth is claimed.

### Evolution of the 0.5.0 candidate

| Delivery | Key milestone |
| --- | --- |
| **Alpha.1 · PR #80** | Subject/capture library, source provenance, desktop/mobile navigation |
| **Alpha.2 · PR #81** | Coverage sectors, quality hints, review and comparator |
| **Beta.1 · PR #82** | Opt-in ComfyUI generation and synthetic provenance |
| **Beta.2 · PR #83** | Safe reproducible dataset ZIP |
| **RC.1 · PRs #84–#85** | Recover existing projects/photos, persist linkage |
| **RC.1 follow-ups · PRs #86–#97** | Guidance, optional Ollama orientation, translated Multiview, input-folder copies, workflow compatibility filtering and bundled official workflow library |
| **RC.1 documentation/brand · PRs #98–#99** | Uniform OrkiLab branding and multilingual product vision/help with Qwen/FLUX explicitly deferred |

Further details: [Multiview implementation roadmap](docs/orkilab/MULTIVIEW_0_5_ROADMAP.md), [0.5 acceptance register](docs/orkilab/RC_0_5_0_READINESS.md), [changelog](CHANGELOG_ORKILAB.md) and [open-source roadmap](docs/orkilab/ROADMAP.md).

### Publication status and remaining checks

Reported Windows/RTX 3090 acceptance includes saved projects/photos, persistence, representative ComfyUI generation, dataset ZIP and browser layout. The **newer** copy-to-input, guided official workflow import and full Multiview flow still need appropriately scoped evidence against the final installed code. A user-reported success does not automatically validate all Desktop/Portable versions, model families, complete training runs, custom nodes, remote-access safety or upgrade/rollback.

**Published RC evidence:** Windows/Linux CI passed on commit `b4bc236`, and the [v0.5.0-rc.1 GitHub prerelease](https://github.com/jlopfri921/OrkiLab/releases/tag/v0.5.0-rc.1) is available. Stable `v0.5.0` is separately gated on actual device/workflow compatibility, non-destructive upgrade and rollback testing, safety and regression acceptance. The next milestone after stable is **0.6.0**.

## OrkiLab 0.4.0-rc.1 — published GitHub prerelease

**Candidate scope:** a searchable and multilingual training Workspace, Dataset Studio (image library, quality/duplicate review, manually approved captions and optional local vision suggestions), project-aware prepared dataset handoff, managed ComfyUI checkpoints, and a curated **My trained LoRAs / Mis LoRA entrenados** catalog. The catalog supports 1–5 star ratings, Best/Final flags, optional reference images, collapsed model cards, and local SQLite metadata. ComfyUI Generation history also offers collapsed, searchable and sortable jobs.

The main application's version is read from `VERSION_ORKILAB` and shown beneath the active left navigation. The shared footer links to the [OrkiLab GitHub project](https://github.com/jlopfri921/OrkiLab). Current integration is local-first: original training weights and imported datasets are preserved, and saved library records refer to local files.

**Important scope limits:** the prepared image/caption workflow does not establish that every trainer can successfully pre-cache/train from its generated dataset. Per-engine export profiles, a formal train/validation split, reproducibility acceptance across engines, full trainer/GPU validation, and real Windows image/Ollama smoke tests remain separate gates for the eventual **0.4.0 stable** milestone. The candidate's CI uses CPU-only dependencies and synthetic fixtures; it does not run a real GPU training pass. See [candidate readiness](docs/orkilab/RC_0_4_0_READINESS.md), [Dataset Studio scope](docs/orkilab/DATASET_STUDIO_0_4_SCOPE.md), and [managed checkpoints](docs/orkilab/MANAGED_COMFYUI_CHECKPOINTS.md).

**Updating from an earlier installation:** back up `settings/orkilab/`, your project datasets, trainer configurations and ComfyUI workflows before updating. Use the tagged prerelease or the current `main` branch; always back up existing state first. Existing `.safetensors` and original image folders must not be deleted by the update.

## Dataset Studio 0.4 — manual Caption Studio (candidate scope; see limits above)

Current 0.4 candidate development, following the published 0.3.0-rc.1 prerelease, includes a project-linked Dataset Studio under **Workspace → Dataset Studio**. Import references to local image files, review them, scan for exact/possible visual duplicates and blur, and compare pairs. Images remain at their original locations.

The first **0.4 beta.1 development slice** adds a per-image **Edit caption** dialog with manual text, a bounded history of the 25 latest saved revisions and a way to load an older version before saving it as a new revision. Captions are kept in OrkiLab's local SQLite metadata, with concurrent-edit conflict detection; they **do not yet create or modify `.txt` sidecars**. This is **not an AI caption generator**, a resize/crop exporter or a completed 0.4 beta.1 release; these are separate acceptance steps.

The next beta.1 development slice adds **Export selected captions (.txt ZIP)** with a preview of which selected images have saved text, a separate confirmation checkbox and a browser download. The ZIP contains UTF-8 `.txt` sidecars (matching the image stem when unique, with stable suffixes when names collide) and `captions-manifest.json`. It **does not copy source images, write alongside originals or overwrite sidecars**. Captions must be saved first, and the download is limited to 200 selected image references per request. A derived image/sidecar pair export for trainer-ready datasets remains a future step.

The same development work also synchronizes the Workspace/Queue/Dataset header markup, removes the duplicate ComfyUI return button and resets scrolling to the top after selecting menu sections. Browser appearance and real-dataset acceptance must be verified on the user's Windows installation separately from CI. See [Dataset Studio scope and milestones](docs/orkilab/DATASET_STUDIO_0_4_SCOPE.md).

### Dataset Studio: optional local Ollama caption previews (0.4 development)


A newer development slice detects **installed image-capable Ollama models** using Ollama's local `/api/tags` and `/api/show` APIs. Open the Caption Studio editor and choose a model from the dropdown; if discovery fails, manual entry is still available. Only models reporting the `vision` capability are listed, so unknown-capability models are not assumed image-compatible. The lookup does not pull models.

When a generated caption is in progress, the **Cancel generation** button sends a separate local cancellation request and interrupts the streaming HTTP connection to Ollama. This is a best-effort cancellation of inference, **not a guarantee of immediate VRAM release or preemption of another application**; a real Ollama/GPU smoke test is still required. Cancelling never changes saved captions or original files. The local server enforces one simultaneous caption generation request.
In **Dataset Studio → Edit caption → Local AI suggestion**, you may choose a **previously installed image-capable Ollama model** and explicitly click **Generate preview locally**. Ollama must already be running on this computer at `127.0.0.1:11434`; OrkiLab does **not** install Ollama, download or select a model for you, or enable cloud inference. The model name is entered manually (for example, `qwen3-vl:8b` if you have actually installed it). The selected source image is sent only to the local loopback Ollama endpoint. The request is capped at 12 MB and 120 seconds, performs no redirects and asks Ollama to unload the model afterward with `keep_alive: 0` (subject to Ollama's behavior).

The suggestion appears in a separate **read-only preview**. Only **Use suggestion in editor** copies it into the editable text box; only the existing **Save caption** action writes the reviewed text to OrkiLab's local SQLite metadata. No original images, sidecars or caption history are changed just by generating a preview. Generating uses GPU memory and can contend with ComfyUI or training; run it only when resources are available. One preview is processed at a time. This is an **experimental development integration**, not a verified 0.4 release or a substitute for the training captioner already used by individual trainers. The official image-captioning acceptance still requires a real Windows/GPU test.

## Ecosystem spotlight — owner-managed announcement

The Dashboard includes a small, dismissible **OrkiLab ecosystem** announcement currently restricted to OrkiLab and OrkiCAD AI. It is a first-party editorial promotion, never an advertising network. One announcement is shown at a time, rotated daily, with a session-level dismiss control.

**To change it remotely for installations:** edit `GUI/promotions.json` on the repository's **main** branch. A local OrkiLab installation fetches the fixed HTTPS file through its own backend and caches a validated result for six hours; it does **not** need a software update for future copy changes. A brand-new announcement becomes visible after the next successful refresh. While offline, the last successful announcement is retained for the running server process; otherwise the slot stays hidden. Pull requests and changes on other branches have no impact until merged into `main`.

The manifest uses `{"version":1,"items":[...]}`. Items support `id`, `enabled`, multilingual `title` and `description` objects (`es`, `en`, etc.) and an HTTPS `url`. Links are limited to the project's approved domains in `scripts/promotions_feed.py`; updating that allowlist requires shipping a code change. The UI uses text only (no HTML, third-party JavaScript, embedded images, cookies or tracking). Remote requests are made by the local server to the fixed file, not directly from visitors' browsers; no visitor identifiers are sent.

## OrkiLab 0.3.0-rc.1 — published prerelease (2026-11-21)

This prerelease focuses on a **locally exercised ComfyUI integration** rather than expanding all trainers at once. The expected scope is ComfyUI Zone onboarding and connection verification; read-only models/nodes; trusted workflow import, inspection and Bridge preparation; explicit Generation Studio submission with progress, safe cancellation, results and history; GPU monitoring; optional model/cache release; system-wide RAM/VRAM readings per generation; and the existing, **experimental and not yet GPU-validated** LoRA strength-comparison UI (not part of the rc.1 stability promise).

**Not included as complete 0.3 commitments:** full per-trainer interface replacement, Dataset Studio, multiview tools, Ollama Copilot, Hub integrations, a packaged desktop installer, or support for every third-party ComfyUI node/workflow. Existing trainers remain accessible. Windows/Linux GitHub Actions passed on the exact tagged commit; on-device operator checks are recorded separately and do not guarantee all engine/model combinations.

**Project status (November 21, 2026):** the user reports completion of the hands-on ComfyUI/GPU tests; detailed outcomes, supported workflow samples and hardware evidence still need recording in the [acceptance checklist](docs/orkilab/GPU_GENERATION_ACCEPTANCE.md). Trainer modernization is underway. See the [0.3 RC scope and release gates](docs/orkilab/ROADMAP.md#immediate-milestone-030-rc1--comfyui-integration-candidate).

## What's new in OrkiLab — modern Workspace and ComfyUI integration

> **Prerelease status (2026-11-21).** The 0.3.0-rc.1 tag and GitHub prerelease are published. Windows/Linux CI passed on the tagged commit, and an operator reported successful image generation and selected ComfyUI flows. Not all trainer/GPU workflows have undergone full end-to-end acceptance; keep backups of important workflows and datasets.

OrkiLab is growing beyond a collection of LoRA trainers into a unified **local-first training, generation and model-management workspace**, while keeping the existing training engines. The newer interfaces prioritize focused screens, contextual help, collapsible advanced options, and internationalization.

### Open the new interfaces

| Screen | Address on the launcher PC | What you can do |
| --- | --- | --- |
| **Workspace** | [`/workspace`](http://127.0.0.1:4990/workspace) | Dashboard, projects, trainer engines, queue, settings |
| **GPU Manager** | [`/workspace#gpu-manager`](http://127.0.0.1:4990/workspace#gpu-manager) | Inspect NVIDIA GPU activity, VRAM, temperature and training warnings |
| **ComfyUI Zone** | [`/workspace/comfyui`](http://127.0.0.1:4990/workspace/comfyui) | Manage ComfyUI through a dedicated area with its own navigation |
| ComfyUI connection | [`#comfyui`](http://127.0.0.1:4990/workspace/comfyui#comfyui) | Configure local/private ComfyUI connection and engine mode |
| Model library | [`#models`](http://127.0.0.1:4990/workspace/comfyui#models) | Search read-only inventories of installed and shared models |
| Node explorer | [`#nodes`](http://127.0.0.1:4990/workspace/comfyui#nodes) | Inspect available built-in/custom ComfyUI nodes |
| Workflow library | [`#workflows`](http://127.0.0.1:4990/workspace/comfyui#workflows) | Import, synchronize, search, inspect and favorite workflows |
| Generation Studio | [`#generation`](http://127.0.0.1:4990/workspace/comfyui#generation) | Prepare and review workflows, edit parameters and generate |
| Generation history | [`#history`](http://127.0.0.1:4990/workspace/comfyui#history) | Review past jobs, output files and exact submitted API graphs |
| LoRA Comparator | [`#compare`](http://127.0.0.1:4990/workspace/comfyui#compare) | Compare LoRA strengths in controlled, sequential generations |

**Navigation update:** Dashboard, Projects, Training engines and GPU Manager each open in a **focused Workspace view**. The selected navigation item is highlighted. Each Workspace and ComfyUI screen has a collapsible **What can I do here?** explanation, available in all eight interface languages. Keyboard focus is more visible, and navigation adapts to narrower screens. This is an incremental UX improvement: individual trainer settings and legacy views still require separate review.

**Navigation:** the Workspace has a single **ComfyUI Zone** entry. The Zone has its own sidebar; choosing an item shows only that module. Use **Back to Workspace** to return to training and projects. The workflow library is collapsible, its list has its own scroll area, and import/synchronization tools can be expanded only when needed.

### New and improved features

| Module | Implemented capabilities | Current limits |
| --- | --- | --- |
| **Modern Workspace** | Central dashboard, existing trainer shortcuts, project metadata in SQLite, queue and configuration access, separate ComfyUI area | Some specialized trainers still need individual UX/regression review |
| **Multilingual UI** | English, Spanish, French, German, Portuguese, Italian, Japanese and Korean; additional navigation labels, contextual explanations and controls | Custom-node labels, model names and all legacy trainer text may not have translations |
| **ComfyUI Connect** | Native, connected and hybrid modes; connection testing and private-network URL configuration | Does not automatically configure or restart ComfyUI |
| **Model library** | Read-only model inventory by source/category, searching and filtering | Name matching is not a hash-based compatibility check |
| **ComfyUI nodes** | Explore installed built-in/custom nodes, origin and capabilities | Metadata discovery does not guarantee successful execution |
| **Workflow library** | Import API/UI JSON, synchronize folders without editing originals, categories, favorites, search, node inspection, LoRA detection hints | Custom nodes and nested subgraphs can require Bridge and runtime validation |
| **OrkiLab Bridge** | Installable ComfyUI frontend extension, converts visual workflows via ComfyUI's own graph machinery | Requires restarting ComfyUI after installation; conversion of real nested subgraphs not yet validated |
| **Generation Studio** | Explicit prepare/review/confirm flow, dynamic parameter editor, essential/advanced grouping, random seed for supported integer seed inputs, per-workflow presets | Presets are browser-local; linked node inputs cannot be changed here; not all workflows convert |
| **Media results and history** | SQLite job history; image/video/audio preview and download; export submitted API JSON; mesh-file downloads | Generated media stays in ComfyUI; interactive 3D rendering and large-media verification remain outstanding |
| **LoRA Comparator (experimental)** | Direct workflow selector with compatibility hints, standard LoRA-loader selection, 2–6 strengths, fixed other parameters, sequential jobs and result grid | **Not GPU-validated for 0.3.0-rc.1; not a supported/stable RC guarantee.** Standard `LoraLoader` / `LoraLoaderModelOnly` only; no arbitrary-LoRA/checkpoint comparison yet |
| **GPU Manager** | Read-only `nvidia-smi` telemetry, VRAM used/free, GPU load and temperature, visible-page auto-refresh and warnings for active OrkiLab training | Observes only; does **not** manage processes, free memory, or schedule jobs |

### Using ComfyUI generation: step by step

1. In **ComfyUI Zone → ComfyUI Connect**, choose **ComfyUI connected** or **Hybrid** and save/test your local ComfyUI URL (for example `http://127.0.0.1:8188`).
2. Open **Workflow library**. Import a saved ComfyUI JSON workflow, or synchronize your local workflows directory. You can inspect required node types without running anything.
3. Open **Generation Studio**, choose a workflow and click **Prepare workflow** for API JSON. Visual workflows with unsupported nodes or subgraphs may need **Prepare with Bridge**.
4. If using Bridge for the first time, expand **OrkiLab Bridge**, install the extension into ComfyUI's `custom_nodes` folder, then **restart ComfyUI**. Bridge opens a dedicated browser tab for conversion; it does not run the workflow automatically.
5. Review the prepared API graph. Set available prompt, seed, sampler and other scalar parameters; apply changes, then explicitly check the confirmation before clicking **Generate with ComfyUI**.
6. Once completed, review media previews and downloads in the Generation Studio result area or **Generation history**. The history records the submitted graph; the generated files remain on the ComfyUI server.

**Safety:** OrkiLab does not silently execute imported workflows. Running an untrusted ComfyUI workflow can execute installed custom-node code on the ComfyUI host. Use trusted workflows and nodes. Generation actions remain local-only on the launcher PC, and the application checks active training and ComfyUI queue state before submission.

### Comparing a LoRA without manually inspecting node code

1. Open **ComfyUI Zone → LoRA Comparator**.
2. Search/select a workflow. The selector prioritizes **LoRA detected**, then **LoRA needs checking**, then **No standard LoRA detected**. These are **hints**, not guaranteed compatibility.
3. Click **Prepare selected workflow** (or **Prepare with ComfyUI Bridge** if it is visual JSON). If a standard LoRA loader is available after validation, select it by name.
4. Enter two to six strengths such as `0, 0.5, 0.8, 1.0`, confirm and run. OrkiLab submits one generation at a time with the same prepared prompt/seed/model settings and displays the results together.

A zero strength removes the effect of **the selected LoRA only**, not every other LoRA that may be in the workflow. **Stop after current** prevents additional submissions; it does not cancel a ComfyUI job already running. Compatibility for custom LoRA loaders is planned, not implemented.

### GPU Manager: what it does and doesn't do

Open **Workspace → GPU Manager** to see video memory totals and free/used VRAM, processing utilization and temperature where the NVIDIA driver provides them. The monitor refreshes roughly every five seconds while the page is visible and auto-refresh is enabled. It also indicates when OrkiLab detects active training. It works independently of ComfyUI, so **you can test it without restarting ComfyUI**.

The monitor executes a fixed, read-only `nvidia-smi` query; it does **not** close GPU processes, unload models, force memory reclamation or automatically decide whether a generation will fit. GPU memory may be used by other applications. A missing NVIDIA tool or unsupported sensor should show an unavailable state.

### Storage, source code and known validation gaps

| Data | Location | Notes |
| --- | --- | --- |
| Workspace project metadata | `settings/orkilab/projects.sqlite3` | Local metadata only |
| Imported workflows | `settings/orkilab/workflows.sqlite3` | Original source JSON files are not overwritten |
| Generation history | `settings/orkilab/generations.sqlite3` | Run records, API parameters and output descriptors, **not duplicated media** |
| ComfyUI connection settings | `settings/orkilab/comfyui.json` | Locally validated connection configuration |
| Generation presets | Browser local storage | Device/browser-specific, not yet in SQLite |
| GPU telemetry | `scripts/gpu_monitor.py` | Local read-only NVIDIA query |
| Browser interface | `GUI/workspace.html`, `GUI/locales/` | Shared page and translated UI |
| Bridge extension | `integrations/orkilab_bridge/` | Installed separately into ComfyUI's `custom_nodes` |

**Still requiring acceptance tests for the RC:** ComfyUI Desktop Bridge after restart, real custom-node/subgraph conversion, image/video/audio playback, GPU Manager on actual hardware, multi-GPU handling and trainer UI regressions. **Deferred beyond rc.1:** LoRA Comparator sequential runs and stop behavior; the visible tool is experimental and unverified. An interactive 3D viewer, central/server-side presets, cross-LoRA/checkpoint comparisons and GPU scheduling are future work—not completed features.

For deeper architecture, endpoint/security notes, a feature-by-feature checklist and tests, see **[the Workspace feature guide](docs/orkilab/WORKSPACE_FEATURES.md)**, **[development roadmap](docs/orkilab/ROADMAP.md)** and **[full changelog](CHANGELOG_ORKILAB.md)**.

## Workspace at a glance

Open **Workspace** at `/` or `/workspace` on the launcher host. Create and archive project metadata in local SQLite storage and launch the existing training engines from the modern interface.

| Dataset | Training | Export |
| :--- | :--- | :--- |
| Dataset manager, captions and Dataset Forge | Model-specific trainers, job queue, live previews and checkpoint resume | LoRA weights for compatible ComfyUI workflows |

## Quick start

```bash
git clone https://github.com/jlopfri921/OrkiLab.git
cd OrkiLab-LoRA-TrainerStudio
```

On Windows, run `Install_LoRAlab-TrainerStudio.bat`, then `Start_LoRAlab-TrainerStudio.bat`. Linux instructions are in [the Linux guide](docs/Linux.md). Use the dedicated virtual environment; see the full installation and requirements sections below. The launcher opens at http://127.0.0.1:4990.

## Engine gallery

Original OrkiLab vector artwork for each trainer; illustrations are not generated training samples or screenshots.

| Image & video | Generative models | Creative engines |
| :---: | :---: | :---: |
| ![LTX 2.3](assets/ltx23/orkilab-cover.svg) | ![LTX 2.5](assets/ltx25/orkilab-cover.svg) | ![Krea 2](assets/krea2/orkilab-cover.svg) |
| ![MiniMax-H3](assets/minimaxh3/orkilab-cover.svg) | ![MiniMax-H3 Image](assets/minimaxh3image/orkilab-cover.svg) | ![Wan 2.2 (T2V-A14B)](assets/wan22/orkilab-cover.svg) |
| ![Qwen-Image 2.1](assets/qwenimage21/orkilab-cover.svg) | ![Fibo 2.0](assets/fibo2/orkilab-cover.svg) | ![Qwen-Image 2512](assets/qwenimage2512/orkilab-cover.svg) |
| ![Boogu Image Edit](assets/boogu/orkilab-cover.svg) | ![Z-Image](assets/zimage/orkilab-cover.svg) | ![Ming-Image](assets/mingimage/orkilab-cover.svg) |
| ![Anima](assets/anima/orkilab-cover.svg) | ![YuE2-3B](assets/yue2/orkilab-cover.svg) | ![FLUX.1 Dev](assets/flux1/orkilab-cover.svg) |
| ![FLUX.2 Klein 9B](assets/klein9b/orkilab-cover.svg) | ![FLUX.3 Image Klein](assets/flux3klein/orkilab-cover.svg) | ![ERNIE-Image](assets/ernie/orkilab-cover.svg) |
| ![MOSS-Image](assets/mossimage/orkilab-cover.svg) | ![Ideogram 4](assets/ideogram4/orkilab-cover.svg) | ![SDXL](assets/sdxl/orkilab-cover.svg) |

## Training engines

The following compatibility details and VRAM measurements are inherited from upstream; they have not all been independently reproduced by OrkiLab. Quantization and actual memory use depend on the model and settings.

| Trainer | Trains | Minimum VRAM |
| :--- | :--- | :--- |
| **Fibo 2.0** *(experimental)* | Image LoRAs (characters, objects, styles) **and edit LoRAs** (before → after) on BRIA Fibo 2.0 Dev | **8 GB** with block swap (5.3 GB peak with image LoRAs at 768², measured) |
| **Qwen-Image 2.1** | Image LoRAs (characters, objects, styles) **and edit LoRAs** (before → after) | 8 GB |
| **Qwen-Image 2512 / Edit 2511** | Image LoRAs on Qwen-Image-2512 **and edit LoRAs** on Qwen-Image-Edit-2511 (before → after); 20B in NF4 with block swap | **~4 GB** (512², measured) / 8 GB (edit at 1024²) |
| **Krea 2** | Image LoRAs (characters, objects, styles) for Krea 2 Raw and Turbo | 8 GB |
| **Boogu Image Edit 0.1** | Edit LoRAs (before → after) and image LoRAs on Boogu-Image-0.1-Edit | **8 GB** with block swap (5.5 GB peak with edit LoRAs at 512², measured) |
| **Z-Image** | Image LoRAs (characters, objects, styles) for Z-Image and Z-Image-Turbo | 8 GB |
| **Ming-Image** *(experimental)* | Image LoRAs for transparent designs and edit LoRAs (before → after) on inclusionAI's Ming-Image 0.1 Design | **8 GB** with block swap (5.8 GB peak at 1024², measured) |
| **Anima** | Anime and illustration LoRAs (characters, styles) | **4 GB** (NF4) / 6 GB (BF16) |
| **ERNIE-Image** | Image LoRAs (characters, objects, styles); supports rsLoRA, LoRA+ and LoKr | **Under 8 GB** (NF4; verified during training) |
| **FLUX.1 Dev** | Image LoRAs (characters, objects, styles) | **8 GB** with block swap (5.0 GB peak at 512², measured) |
| **FLUX.2 Klein 9B** | Image LoRAs (characters, objects, styles) **and edit LoRAs** (before → after) | **8 GB** with block swap (6.0 GB peak at 768², 5.8 GB with edit LoRAs at 1024², measured) |
| **FLUX.3 Image Klein** | Image LoRAs (characters, objects, styles) **and edit LoRAs** (before → after) | 8 GB |
| **MOSS-Image** | Image LoRAs (characters, objects, styles) on MOSS-Image Base or SFT **and edit LoRAs** (before → after, on top of armV5, armV4 or Moss-Image-Edit); supports rsLoRA, LoRA+ and LoKr | **6 GB** (512²) / 8 GB |
| **Ideogram 4** | Image LoRAs (characters, objects, styles), with JSON captions | **8 GB** with block swap (6.4 GB peak at 1024² with CFG previews, measured) |
| **SDXL** | Image LoRAs for SDXL Base, Pony, Illustrious, NoobAI, Juggernaut, RealVis or your own SDXL checkpoint | **4 GB** (NF4) / 12 GB (BF16) |
| **LTX 2.5** | Image LoRAs, video LoRAs from clips, **video + audio** LoRAs and **edit IC-LoRAs** (before → after), on LTX-2.5; block swap | **8 GB** |
| **LTX-2.3** | Character and style LoRAs for LTX-2.3, trained from images (they usually load in LTX-2.5 too) | **8 GB** with block swap (5.2 GB peak at 768², measured) |
| **MiniMax-H3** | Video LoRAs from images, clips and audio, plus training-free **RefMods** | 8 GB |
| **MiniMax-H3 Image** *(experimental)* | Image LoRAs (characters, objects, styles) **and edit LoRAs** (before → after) on the 6-step distilled MiniMax-H3-Image, trained with a de-distillation adapter; 33B in NF4 with block swap | 8 GB (image LoRAs) / 10 GB (edit LoRAs), estimated from the VRAM plan with Resident Blocks on 0 |
| **Wan 2.2 (T2V-A14B)** | Video and image LoRAs from images and clips, for the **high noise** and/or **low noise** expert | **8 GB** with block swap (5.2 GB peak with images or 17-frame clips at 480p, both experts; 5.7 GB with a video preview, measured) |
| **YuE2-3B** *(experimental / beta)* | Song LoRAs: the AR clones the singer's voice, the NAR learns lyrics and phrasing | ~8 GB (NF4, measured on NAR) |

---

## 📉 Smaller downloads

Each trainer downloads **only what it uses**, already quantized. The table compares the official full-precision model, what the previous standalone LoRAlab downloaded, and what Trainer Studio downloads now (sizes from the Hugging Face repositories, in GB):

| Trainer | Official model | LoRAlab before | **Trainer Studio now** | What changed |
| :--- | ---: | ---: | ---: | :--- |
| **Krea 2** | 62.0 | 43.2 | **17.0** | The BF16 transformer (26.3 GB) is no longer downloaded or used: the model is built directly from its NF4 weights. |
| **LTX 2.5** | ~70 | — | **26.3** | New trainer: the full transformer (9.6 GB NF4 + 0.85 GB BF16), the Gemma 4 12B text encoder in NF4 (7.2 GB), connectors, VAEs and vocoder, from `AcademiaSD/LTX25-NF4-for-LoRA-Training`. The official Diffusers repo is gated; this one is not. |
| **LTX-2.3** | 101.3 | 111.1 | **32.2** | The BF16 transformer (38.0 GB) and the FP32 Gemma 3 text encoder (48.8 GB) are replaced by NF4 versions (9.8 GB + 7.8 GB). |
| **Qwen-Image 2.1** | ~32 (BF16) | 21.9 | **21.9 / 14.4 / 11.0** | Only the text encoder you pick is downloaded: BF16 (exact, default) / INT8 / NF4. |
| **MiniMax-H3** | 498.5 | 41.4 | **41.4** | The 33B model ships in NF4 from the start. |
| **MiniMax-H3 Image** | 204.0 | — | **38.4** | New trainer: the 33B transformer in NF4 (17.2 GB), its VAE (2.3 GB) and the de-distillation adapter (0.5 GB) from `AcademiaSD/MiniMax-H3-Image-NF4-for-LoRA-Training`, plus the Qwen3-VL text encoder in NF4 (18.4 GB) from the MiniMax-H3 NF4 repo. If MiniMax-H3 is already installed, the text encoder is not downloaded again (~20 GB). |
| **Z-Image** | 20.5 | — | **5.9** | New trainer: the 6B transformer (12.3 GB) and the Qwen3-4B text encoder (8.0 GB) in NF4 (3.4 GB + 2.7 GB). |
| **Anima** | 5.6 | — | **5.6** | New trainer: the official diffusers version of Anima-Base. The 2B model trains in BF16, or in NF4 quantized when loading (nothing extra to download). |
| **SDXL** | ~7 per model | — | **~7 per model** | New trainer: only the preset you pick is downloaded (one `.safetensors` file); your own checkpoint downloads nothing. |
| **Ideogram 4** | 16.1 (NF4) | — | **16.1** | New trainer: the official NF4 release, which includes the unconditional transformer used only by the previews. It is downloaded from Unsloth's ungated mirror (same weights, no license gate or token needed); the Ideogram license still applies. |
| **FLUX.1 Dev** | 33.7 | — | **13.5** | New trainer: the 12B transformer (23.8 GB) and the T5-XXL text encoder (9.5 GB) in NF4 (6.7 GB + 6.3 GB), from `diffusers/FLUX.1-dev-bnb-4bit`. |
| **FLUX.2 Klein 9B** | 34.7 | — | **8.8** | New trainer: the 9B transformer (18.2 GB) and the Qwen3-8B text encoder (16.4 GB) in NF4 (4.9 GB + 3.8 GB; only the 28 text encoder layers Klein reads). |
| **Qwen-Image 2512 / Edit 2511** | 57.8 each | — | **26.8 / 18.6 / 15.7** | New trainer: the 20B transformer of 2512 or Edit-2511 in NF4 (9.9 GB each; only the one you train on is downloaded) and the Qwen2.5-VL-7B text encoder you pick: BF16 (exact, default) / INT8 / NF4. The optional Lightning turbo LoRA adds 0.85 GB. |
| **MOSS-Image** | 27.2 | — | **20.2 / 13.2 / 9.9** | New trainer: the 5B transformer of Base or SFT in NF4 (3.1 GB each; only the one you train on is downloaded) and the Qwen3.5-9B text encoder you pick: BF16 (exact, default) / INT8 / NF4. The optional turbo preview adapter adds 1.2 GB. |
| **Wan 2.2 T2V-A14B** | 126.2 | — | **~19.5 / ~27** | New trainer: one expert / both, downloaded already in NF4 (~7.6 GB each) from `AcademiaSD/Wan22-T2V-A14B-NF4-for-LoRA-Training`. An expert that repo does not have yet is downloaded from the original shard by shard (57.2 GB in FP32: 69.0 / 126.2 GB in total) and converted to NF4 on your PC, deleting each shard as it goes. On disk it takes **~19.5 GB** with one expert and **~27 GB** with both (UMT5-XXL text encoder and VAE: 11.9 GB). |
| **ERNIE-Image** | 31.6 | — | **~6.7** | New trainer: downloads the prepared NF4 transformer and Ministral 3B text encoder from `AcademiaSD/Ernie-NF4-for-LoRA-Training`. The optional prompt enhancer is not needed for training. |

The automatic captioner adds, only the first time you use it: **nothing** for Krea 2 (it uses Krea 2's own text encoder), **5.5 GB** for Qwen-Image 2.1 when its text encoder is not already the NF4 one and for LTX-2.3, Z-Image, Anima, FLUX.2 Klein 9B and Ideogram 4 (Qwen3-VL-8B NF4, shared by all of them), and **8.9 GB** for MiniMax-H3 (Qwen3-VL-4B).

> **Upgrading from an old standalone LoRAlab?** Copy its model folder into `Models/` instead of downloading it again. Legacy model, cache and output folders in the project root are moved automatically on first start. Then you can delete what is no longer used: `Models/Krea-2-NF4/transformer` (~26 GB) and, in `Models/LTX23-NF4`, the `transformer` (~38 GB) and `text_encoder` (~49 GB) folders.

---

## 🖥️ Requirements

| | Minimum | Recommended |
| :--- | :--- | :--- |
| **OS** | Windows 10 / 11, or 64-bit Linux ([docs/Linux.md](docs/Linux.md)) | Windows 11 |
| **GPU** | NVIDIA **RTX 20xx / GTX 16xx or newer** (compute capability 7.5+) with **8 GB VRAM** (4 GB for Anima and SDXL in NF4, 10 GB for MiniMax-H3 Image edit LoRAs, 12 GB for SDXL in BF16) | 12–24 GB VRAM |
| **AMD GPU** *(experimental)* | Radeon **RX 7000 / RX 9000** or Ryzen AI Max (Strix Halo) with 16 GB of VRAM, using the AMD installer (see *Installation*). Confirmed on an RX 7800 XT 16 GB under Windows with MiniMax-H3 | — |
| **Driver** | NVIDIA **580 or newer** (CUDA 13). AMD: a recent Adrenalin driver on Windows, or `amdgpu` on Linux | Latest |
| **RAM** | 16 GB | 32 GB |
| **Disk** | The model of each trainer you use (table above) plus your datasets and caches | SSD |
| **Other** | Internet the first time each model is used. MiniMax-H3, Wan 2.2 and LTX 2.5 clips and audio files need **`ffmpeg`** in the `PATH`. | |

Python, Git and every library are installed by the installer. GTX 10xx and older cards are **not** supported: PyTorch for CUDA 13 starts at the RTX 20xx generation.

---

## 📦 Installation

**Option A — Git (recommended, makes updating easy).** Open the folder where you want to install it, type `cmd` in the address bar of the Windows Explorer, press Enter and run:

```bash
git clone https://github.com/jlopfri921/OrkiLab.git
```

**Option B — ZIP.** Press the green **Code** button → **Download ZIP** and unzip it where you want to install it (the folder is called `OrkiLab-LoRA-TrainerStudio-main`).

Then, inside the folder:

1. Double-click **`Install_LoRAlab-TrainerStudio.bat`**. It installs Git if it is missing (Windows asks for permission), Python 3.13.1 if it is missing, and one `venv` shared by every trainer: PyTorch 2.14 (CUDA 13.0), Diffusers from GitHub, Transformers, PEFT, bitsandbytes, Flask and the rest. It takes a while; at the end it shows the detected GPU and versions.
2. *(Optional)* Double-click **`Install_Triton_SageAtten220.bat`** for Triton and SageAttention 2.2.

Pick a disk with plenty of free space: every model is downloaded into this folder.

**AMD GPUs (experimental).** Use **`Install_LoRAlab-TrainerStudio_AMD.bat`** (Windows) or **`Install_LoRAlab-TrainerStudio_AMD.sh`** (Linux) instead of the normal installer. It asks for your GPU family (RX 7000, RX 9000 or Ryzen AI Max / Strix Halo) and installs PyTorch ROCm from AMD's TheRock nightly builds. It is based on [a user's guide](https://civitai.com/articles/36293/training-krea-2minimax-h3etc-lora-on-low-vram-low-ram-amd-gpu-windows), and the same user [confirmed the installer](../../issues/8) on an **RX 7800 XT 16 GB under Windows**: a full MiniMax-H3 training at about 7 s/step, with no errors. The other trainers are not confirmed yet on AMD; results are welcome in that issue. Attention runs on PyTorch's native kernels (SageAttention is NVIDIA only). Do not run `Install_Triton&SageAtten220`, it is NVIDIA only. On Linux you need the `amdgpu` driver and your user in the `render` and `video` groups.

The **VRAM panel** of the trainers reads the real usage of the whole AMD GPU: on Windows through AMD's [ADLX](https://gpuopen.com/adlx/), which comes with the Adrenalin driver (the AMD installer and the updater install its Python package, `amd-adlx`; older installs with `tools/all-smi/` keep working); on Linux straight from the `amdgpu` driver, with nothing to install. The trainers that fit part of a model in the free VRAM also ask ADLX on Windows, because PyTorch for ROCm there only counts its own process, not the desktop or other programs. With two or more AMD GPUs, the launcher's GPU selector lists them too.

**Linux.** Every `.bat` has a `.sh` equivalent with the same name (`Install_LoRAlab-TrainerStudio.sh`, `Start_LoRAlab-TrainerStudio.sh`, `code/Run_LoRAlab-<Model>.sh`…) and the launcher picks the right one. Install and usage steps are in [docs/Linux.md](docs/Linux.md).

## Updating

Stop training and back up settings. Run the updater for a safe fast-forward update of the current branch. By default it updates code only; pass `--deps` to update the local virtual environment. External Python environments must be maintained manually.

## 🚀 Using it

**`Start_LoRAlab-TrainerStudio.bat`** opens the launcher in your browser (`http://127.0.0.1:4990`). Click a trainer: its console window and its web interface (`http://127.0.0.1:5000`) open on their own. The trainer opened from a card uses port 5000. While one is training, clicking another card opens it on the next free port (5001, 5002…) so you can prepare a job for the [job queue](#-job-queue) without stopping the one that trains. Each trainer can also be started directly with its `code\Run_LoRAlab-<Model>.bat`.

Every trainer follows the same five steps:

1. **Project and dataset.** Type a project name, an optional trigger word, and pick the dataset folder with **Browse**. Each image needs a `.txt` caption with the same name. From another device, **⬆ Upload** in the Dataset Manager (or dragging files or a `.zip` onto it) copies them into that folder.
2. **Captions** *(optional)*. **Create Captions** writes a caption for every image with a vision-language model, trigger word first. The prompt is editable and **Overwrite** off only fills the missing ones. Review them in the **Dataset Manager**: click an image to edit its caption, use **Append / Replace / Remove** to change a common text in every caption, delete images, clear all captions, or empty the whole dataset folder with **Clear Dataset** (it asks you to type the number of files; subfolders are kept).
3. **Pre-Cache.** Choose the resolution and press **Start Pre-Cache**. The text encoder and the VAE run once and their output is stored on disk; the first time, the model is downloaded. Running it again skips the images that did not change.
4. **Train.** Set steps, learning rate, rank and alpha, and press **Start / Resume**. Watch the progress, VRAM, RAM and GPU temperature, and the previews (each trainer has its own previews panel). **Stop Training** saves the exact step: press **Start / Resume** again — even days later — to continue without losing a step. To train longer, raise the steps and press it again.
5. **Export.** Type the final name, pick your ComfyUI / Forge / A1111 `models/loras` folder and press **Save Path** — the folder is remembered for **every** trainer — then **🚀 Send to Models**. **⬇ Download LoRA** lists the final LoRA and the step checkpoints and saves the one you pick on the device you are browsing from.

Also in every trainer:

- **Live settings:** while training, change steps, save/preview frequency, preview settings or learning rate and press **Save JSON**; the change applies on the next step.
- **Delete Pre-Cache / Delete Training** empty the current project's folders (the dataset is never touched).
- Exported LoRAs carry kohya-style metadata (trigger word, rank, steps, resolution) that CivitAI and LoRA managers read.
- **Several NVIDIA GPUs?** Pick the one to train with in **🎮 GPU**, next to the language at the bottom of the launcher, and press **💾 Save settings**. It applies to the trainers opened from then on, and the VRAM panel shows that card. *Automatic* keeps CUDA's choice, which puts the card it considers fastest first, not always the one with more VRAM. The selector only appears with two or more NVIDIA cards.
- Optional **Hugging Face token** for faster downloads. Your settings and token are stored in `settings\`, which is never uploaded.
- Models live under `Models/`. Each project uses `Cache_Data/cached_data_<model>_<project>` for the pre-cache and `Outputs/<model>_lora_output_<project>` for checkpoints, previews and LoRAs. Legacy root folders are moved automatically on first start. Migration is skipped while a training or captioning process is running.

---

## 🧾 Job queue

Queue trainings and pre-caches, from one trainer or several, and they run one after another on the GPU.

- **Adding jobs.** While something is training, **Start / Resume** or **Start Pre-Cache** in any trainer asks *Add to queue?* instead of starting. The job keeps a copy of the settings saved at that moment, so you can go on changing that trainer for the next one. With the GPU free, a training starts at once as before, and it shows in the queue too.
- **Missing or outdated pre-cache.** **Start / Resume** checks the project's pre-cache against its dataset. With no pre-cache, or with images or captions added, edited, removed or renamed after it, it lists what changed and offers **Pre-cache, then train**: the pre-cache starts and the training waits in the queue until it finishes well (if it fails, the training keeps waiting until you retry it). **Train with the old cache** trains anyway. Without the launcher the page itself waits for the pre-cache, so keep it open.
- **Training after its pre-cache.** While a trainer runs its pre-cache, its **Start / Resume** stays available: the training goes to the queue and starts as soon as the pre-cache finishes.
- **Editing a waiting job.** **✎** on a job of the queue opens its trainer with that job's settings, and its start button becomes **💾 Save changes to the queue**. The job does not start while you edit it; **Cancel** leaves it as it was.
- **Another trainer while one trains.** Click its card in the launcher: it opens on another port without closing the one that trains.
- **Another training of the same model.** While a trainer trains, **➕ New training for the queue** appears under Start / Stop. It opens a draft of that trainer on another port, starting from the current settings but saving to its own copy: change the project, dataset or anything else without touching the training in progress, and its Start adds it to the queue. Give the draft its own project name, so it does not overwrite the project folder of the one training.
- **The queue page.** The **Queue** button, in the launcher and in every trainer, opens it in the same tab: the job training now, with its progress, time left and loss curve; the jobs waiting, which you drag to change their order, pause, resume or remove; and the history. **Go to the training** opens that job's trainer, with its console, chart and previews, also in the same tab. In the history, **⧉** uses a finished job as a template: it opens its trainer with the settings of that job, in a copy of their own, to change what you want and train again. Give it another Project Name: with the same name, Start / Resume continues the finished training instead of starting a new one.
- **Pause and resume.** Pausing a job, the one training or one waiting, keeps it in the queue as paused: the one training saves a checkpoint and stops, and the next one starts. Resuming it continues from that step. This also works for a training started directly from its trainer. **Pause the queue** lets the current job finish and starts nothing new; **Stop if a job fails** pauses the queue when a job fails.
- **When a job fails** it stays in the list, in red, saying why in plain words (the pre-cache or the dataset was not found, not enough VRAM…) with the console line below. The next job starts meanwhile. Fix the cause and press **↻** to queue it again (at the end, so a Pre-Cache added for it runs first), or add the job again and it replaces the failed one. A job that hangs and does not answer **Remove** or **Pause** is closed after 30 s (3 min when pausing); pressing **Remove** again closes it at once.
- **Each job runs in its own trainer,** opened without a window on a free port (5001, 5002…). What you save in that trainer applies only to that job, never to your trainer settings. If the launcher is closed while a job trains, the job shows as paused (interrupted) and can be resumed.
- **⏻ Pause all and exit,** at the bottom of the launcher, pauses the job training (with its checkpoint), closes every trainer and job and then the launcher itself, all from the browser. Next time you open the launcher, the queue continues on its own where it was, starting with that training from its checkpoint. On RunPod and other clouds, or when used remotely, the launcher stays open so the page keeps working, with the queue paused: turn off **Pause the queue** to carry on.
- Behind a reverse proxy or on RunPod only ports 4990 and 5000 are published: the queue works, but **Go to the training** needs the job's port to be reachable.

---

## 🎯 Custom prompts in the previews

In **2b. Training Previews** of every trainer, **Custom Prompts (0-4)** sets how many prompts of your own the previews use.

- **0** — the previews use the dataset captions, as chosen in **Caption Mode** (First, Random, Rotate 4).
- **1 to 4** — a box appears for each prompt, and each preview round makes one image per prompt: `preview_step_N.png`, `preview_step_N_2.png`… In the gallery they show as *Step N*, *Step N · #2*… Caption Mode is not used meanwhile.
- **One random prompt per preview** — each round makes a single image, with one of your prompts chosen at random. Previews then take as long as with one prompt.
- The trigger word is added in front of each prompt, as in the captions. A settings file from before, with Caption Mode = Custom prompt, opens as 1 prompt.
- **Each preview keeps its prompt.** Click a preview: under its name you see the prompt it was made with, your own or the dataset caption. It is stored inside the PNG (and in a `.txt` next to video and audio previews), so it travels with the file.

**When they are encoded.** Pre-Cache encodes the prompts on the GPU with the rest of the texts. If you change them with **Save JSON**, only the prompts that changed are encoded, in one process: on the GPU when nothing is running, on the CPU while training (it does not touch the training's VRAM; about a minute). The trainer switches to each prompt when it is ready; until then the previews use the ones that are, or the dataset captions. The console lists the prompts and marks with `...` the ones not encoded yet. YuE 2 takes your prompts as lyrics: nothing is encoded, the trainer reads them directly.

**LTX 2.3, LTX 2.5, MiniMax-H3 and MiniMax-H3 Image** encode them in Pre-Cache only: their text encoders (Gemma, MiniMax) are too large to load on the CPU next to a training. After changing a prompt, run Pre-Cache again (it skips the images already cached). If a training is running, the console says which prompts are not encoded and the previews go on with the others. MiniMax-H3 Image uses your prompts for image LoRAs; for edit LoRAs its previews keep using the dataset pairs.

**Edit trainers.** The prompts are the instructions, applied to the preview's reference image(s) (**Edit Preview Image** or **Edit Preview Reference Images**; empty = the "before" of the first pair). Changing the images re-encodes them and every prompt, because Qwen-Image and MOSS-Image show them to the text encoder too.

- In the trainers with a list of reference images (Qwen-Image 2.1, Qwen-Image 2512 / Edit 2511, FLUX.2 Klein 9B, FLUX.3 Image Klein, MOSS-Image), by default all the images are `<image1>`, `<image2>`… of the same edit, for every prompt: the output follows image 1, and image 2 only matters if the prompt names it (*put the jacket of `<image2>` on the person of `<image1>`*).
- **One image per prompt** makes each prompt edit its own image instead: prompt 1 → image 1, prompt 2 → image 2… (with fewer images than prompts they start over). Each image is used at full preview size. Use it to see the effect on several photos in one round, ideally photos that are not in the dataset.

---

## 🎛️ LoRA options: rsLoRA, LoRA+, DoRA and LoKr

Under **LoRA Rank / Alpha**, the trainers have extra checkboxes. They change **how** the LoRA learns, so they are fixed for the whole training (to change them, *Delete Training* and start again; the pre-cache is reused).

| Option | What it does | Trainers |
| :--- | :--- | :--- |
| **rsLoRA** | Scales the LoRA by `alpha/√rank` instead of `alpha/rank`, so high ranks keep learning. Ticking it lowers alpha to keep the same strength. | Z-Image, FLUX.2 Klein 9B, Qwen-Image 2.1, Qwen-Image 2512, Krea 2, Anima, Ideogram 4, ERNIE-Image, MOSS-Image, SDXL, LTX-2.3, MiniMax-H3 |
| **LoRA+** | The `B` matrix of every layer learns 16× faster than `A`: usually the same quality in fewer steps. Lower the LR if it burns early. | same as rsLoRA |
| **DoRA** | Each layer also learns the size (magnitude) of every output row, apart from its direction, which is the usual LoRA. It often follows the dataset more closely at the same rank. Every step is slower and uses some more VRAM, because the 4-bit weight of each layer is unpacked to measure it. Works with rsLoRA and LoRA+. | Z-Image, FLUX.1 Dev, FLUX.2 Klein 9B, FLUX.3 Image Klein, Krea 2, Qwen-Image 2.1, Qwen-Image 2512, Ming-Image, MOSS-Image, Anima, Wan 2.2, ERNIE-Image, Fibo 2.0, Ideogram 4, SDXL, LTX 2.3, LTX 2.5, Boogu |
| **NormFix** (with DoRA, on by default) | Saves the `dora_scale` with the row sizes of the original model instead of those of the 4-bit copy it trains on. ComfyUI measures them on the model it loads, and the 4-bit copy is off by more than what DoRA learns: without NormFix a DoRA can lose the likeness in ComfyUI even when the previews look right. Only the saved file changes, not the training. The sizes come from `dora_norms.safetensors` in the NF4 model folder, downloaded before training when it is missing (SDXL and Anima take them from the original weights when loading). | every DoRA trainer |
| **LoKr** + **Factor** | Replaces LoRA with a Kronecker product (LyCORIS). Much smaller files (~3 MB instead of ~40 MB at rank 8), good for characters with small datasets, more sensitive to the LR. rsLoRA, LoRA+ and DoRA turn off. | Z-Image, FLUX.2 Klein 9B, Qwen-Image 2.1, Krea 2, Anima, ERNIE-Image, MOSS-Image |

- The exported file is a **standard LoRA / LyCORIS file** that ComfyUI and Forge load as usual (with rsLoRA, the alpha is converted so it acts exactly as trained; with DoRA, every layer carries a `dora_scale`, stored the way ComfyUI applies it).
- **Send to Models** and **⬇ Download LoRA** add **`_rs`**, **`_plus`**, **`_dora`** or **`_lokr`** to the name, taken from the file's own metadata, so you always know how it was trained. The *Final LoRA Filename* field shows the suffix as you tick the boxes.
- No extra VRAM with rsLoRA, LoRA+ or LoKr: LoKr never builds the full weight matrix, and the other two only change the scaling and the optimizer. DoRA is the exception: slower steps and some more VRAM.
- **Testing a DoRA in ComfyUI:** use a full caption like the ones in your dataset. A very short prompt with a high CFG and a long negative loses the likeness with a DoRA and with a plain LoRA alike.

**Which one to use.** All of them are optional: with no box ticked the trainer works exactly as before. Train the same dataset with the same steps, seed and LR to compare them; the pre-cache is shared, so only *Delete Training* is needed between runs.

| Mode | Boxes | When it helps | Starting point | Name suffix |
| :--- | :--- | :--- | :--- | :--- |
| **LoRA** (default) | none | Everything: the safe choice | The trainer's defaults | — |
| **rsLoRA** | rsLoRA | Higher ranks (32-64) for styles or many concepts: with plain LoRA, raising the rank adds little | Rank 32; the alpha it sets for you (≈ alpha/√rank) | `_rs` |
| **LoRA+** | LoRA+ | Reaching the same result in fewer steps | Same LR; check the intermediate checkpoints, and lower the LR if it burns early | `_plus` |
| **rsLoRA + LoRA+** | both | The two together: stable high ranks that also learn faster. They do not conflict: one changes the scaling, the other the optimizer | Rank 32, the alpha rsLoRA sets, and an LR about 2× lower than usual, because both make the training stronger | `_rs_plus` |
| **DoRA** | DoRA | Likeness that a plain LoRA does not reach at the same rank, when slower steps are acceptable. Can be combined with rsLoRA and LoRA+ | The trainer's defaults: same rank, alpha and LR as LoRA | `_dora` |
| **LoKr** | LoKr (+ Factor) | Characters and objects with small datasets, or when file size matters | Rank 8, alpha 8, factor 16, same LR as LoRA; factor 8 or a higher LR if it learns too little | `_lokr` |

### LR scheduler

Every trainer has an **LR Scheduler** selector under the learning rate, with **Warmup Steps** (and **Cycles** for restarts). The default keeps each trainer's previous behaviour: `cosine` everywhere, `constant_with_warmup` on MiniMax H3.

| Scheduler | What it does |
| :--- | :--- |
| `cosine` | Rises during the warmup, then eases down to 10% of the LR |
| `constant` | The same LR from the first step to the last (no warmup), like the Civitai trainer |
| `constant_with_warmup` | Rises during the warmup, then stays at the LR |
| `linear` | Rises during the warmup, then goes down in a straight line to 10% |
| `cosine_with_restarts` | Like `cosine`, but climbs back up and repeats the curve *Cycles* times; for long trainings |

With `constant` every checkpoint is trained equally hard, so stopping early gives the same result as a shorter training; the decaying ones usually leave cleaner final checkpoints.

The chosen scheduler is shown in the console summary when training starts and saved in the LoRA metadata (`ss_lr_scheduler`). It is read again on every start, so a resumed training continues with whatever is selected.

---

## 🌍 Languages

The launcher, every trainer interface and the console messages are available in **English, Español, Deutsch, Français, Português, Italiano, 日本語 and 한국어**. English is the default.

1. At the bottom of the launcher, pick a language in **🌍 Language**: the launcher switches at once, as a preview.
2. Press **💾 Save settings**. The choice is stored in `settings/ui.json` and applies to every trainer.
3. A trainer page that is already open changes after reloading it; the scripts (captioner, pre-cache, training) use the new language on their next run.

What stays in English on purpose:

- **Caption prompts and the captions themselves**, because that is the language the models were trained on.
- Technical names and log tags: settings such as `vram_budget_gb` or `max_seq_len`, markers such as `[NF4-TE]` or `[BACKFILL]`, model names and paths.
- The `.bat` and `.sh` windows of the installer, the updater and the launchers.

**Improving a translation.** Each language is one file, `GUI/locales/<code>.json` (`es`, `de`, `fr`, `pt`, `it`, `ja`, `ko`). The key is the English text and the value is its translation:

```json
{
  "Start Pre-Cache": "Iniciar Pre-Caché",
  "{n} images inside": "{n} imágenes dentro"
}
```

Keep every `{marker}` of the English text, in the same order when it has no name (`{}`). A text with no translation is shown in English, so nothing breaks while a translation is incomplete; edit the file, reload the page, and the change is there. The German, French, Portuguese, Italian, Japanese and Korean translations are first versions: if a term sounds wrong in your language, open an [issue](../../issues) or a pull request with the fix.

---

## 🖼️ Sharp previews in ComfyUI

Some of these models are slow to generate, so it pays to see where an image is going early on, while it is still sampling, and cancel it if it is not working. That needs a good preview, and ComfyUI's default one for Qwen-Image 2.1, Krea 2 and FLUX.2 is Latent2RGB, a blurry, blocky color projection.

**Optional third-party preview resources (not developed or hosted by OrkiLab):** [KJNodes by kijai](https://github.com/kijai/ComfyUI-KJNodes) together with the tiny decoders (TAE) published by **AcademiaSD**. The original Hugging Face links and filenames are retained to credit their publisher and point to the actual download sources. OrkiLab does not claim ownership of these weights. They can provide sharper previews at sampling steps without loading the full VAE:

| Model | TAE | File |
| :--- | :--- | :--- |
| Qwen-Image 2.1 | [AcademiaSD/TAE-Qwen-Image-2.1](https://huggingface.co/AcademiaSD/TAE-Qwen-Image-2.1) | `TAEQwenImage21_AcademiaSD.safetensors` |
| Krea 2 | [AcademiaSD/TAE-Krea-2](https://huggingface.co/AcademiaSD/TAE-Krea-2) | `TAE_Krea2_AcademiaSD.safetensors` |
| FLUX.2 and Ideogram4 | [AcademiaSD/TAE_Flux2_AcademiaSD](https://huggingface.co/AcademiaSD/TAE_Flux2_AcademiaSD) | `TAE_Flux2_AcademiaSD.safetensors` |

> **Attribution:** These are external AcademiaSD assets. Linking to their Hugging Face pages does not mean OrkiLab is an AcademiaSD service or that these files have been rebranded. Check each model repository for its own licensing terms before redistribution.

1. Download the file to `ComfyUI/models/vae_approx/`.
2. Install [ComfyUI-KJNodes](https://github.com/kijai/ComfyUI-KJNodes) by kijai.
3. Add the **Model Preview Override** node between the model (with your LoRA) and the sampler, and pick the TAE in its `tiny_vae` input.

ComfyUI's built-in TAESD preview method does not load these files: use the KJNodes node. They are for previews only; the final image is still decoded with the real VAE.

## 👤 Face likeness in the previews



For character LoRAs: each preview gets a badge with how much its face looks like the person in the dataset, so you can see from which step the LoRA has learned the face and whether later steps keep it. The same % appears above each preview circle on the training chart, in 2D and 3D.

- **Off by default, nothing is downloaded.** Click **👤 Face likeness → Enable...** above the previews. A popup explains the terms and has two checkboxes: *I accept that I download and use these models under my own responsibility* and *I will not use them for commercial purposes*. **Download** is enabled only with both checked.
- It downloads InsightFace's `buffalo_l` (the SCRFD face detector and the ArcFace recognizer, ~280 MB, only those two files are kept) to `Models/FaceMatch-InsightFace/`, and installs `onnxruntime`. **The InsightFace pretrained models are licensed for non-commercial research purposes only**; the acceptance is saved in `settings/face_match.json`.
- It runs on the CPU of the machine with the trainer, so it uses no VRAM and works the same on Windows, Linux, macOS and RunPod, from any browser or phone.
- **Reference:** the largest face in each dataset image, averaged. **Likeness:** ArcFace cosine similarity of the preview's closest face to that reference, ×100. Real photos of the same person usually score above 50%; a different one, under 20-30%. Generated faces score lower: in the previews of a LoRA, 45% or more is a strong likeness. Green from 45%, amber from 30%, red below; *no face* when none is detected. Video previews are scored on their first frame.
- **Show %** hides or shows the badges in the gallery and the chart. Video previews (Wan 2.2, LTX-2.3) are not scored; YuE2 (audio) does not have it.

## 🧬 Dataset Forge

A character dataset from a few images, even just one: new outfits, places and framings that keep the face. Open it with **🧬 Dataset Forge** in the Dataset Manager toolbar of any image or video trainer; it opens in its own tab.

1. **Source and references:** a folder with a few photos of one adult person (it does not touch it). Click the ones to use as reference: up to 4 go into the model, the rest only help the likeness check.
2. **Analyze:** the shared Qwen3-VL-8B captioner writes the captions the references lack and a character sheet: woman / man and the features that do not change (age, hair, eyes, visible marks). Edit it if needed.
3. **Plan:** one line per image combining framing (half close-ups, 30% waist-up, 20% full body: the LoRA learns the face from close-ups), outfit, place (half indoors, half outdoors), light, angle and expression, without repeating outfits or places until they run out. Edit, add or delete lines; **🎲 New plan** makes another one.
4. **Generate:** the model gets the references and each line, with a new pose and expression for every image:
   - **FLUX.3 Klein** (default, NF4). The most natural images: clean anatomy, new poses and the framing of the plan. **Fast** quality (default): NoiseToNova's turbo LoRA (PDD), 4 or 8 steps (about 12 or 25 s per image), with higher likeness but a more made-up, contrasted look. **Best**: 12 to 50 steps with CFG 3.5 (16 steps about 85 s, 28 about 2.5 min), softer and more natural. **Steps** picks the count. **FLUX Kommunity License:** non-commercial use; commercial use of the images only for Qualifying Users (see the license).
   - **Fibo 2.0 Dev** (NF4, 30 steps, CFG 5, about 5 min per image). The highest likeness and clean anatomy, with a slightly more retouched look. **CC BY-NC 4.0: non-commercial use only.**
   - **Qwen-Image 2.1** (NF4, no CFG). High likeness, but bodies can be out of proportion and it tends to copy the pose of the reference. **Best** quality: 20 steps of the base model, clean anatomy, about 40-70 s per image. **Fast**: Viggle's turbo LoRA, 4 steps, about 20-30 s, but more deformed bodies. **Qwen Research License: non-commercial use only.**
   - **FLUX.2 Klein 9B** (NF4 with kalle07's turbo LoRA, 4 steps). Natural anatomy, but the face drifts more and it does not always follow the framing. **FLUX Non-Commercial License.**
   - **Qwen-Image-Edit-2511** (NF4 with lightx2v's Lightning LoRA, 4 steps, Apache 2.0). The only one for commercial use, but it drifts most from the face: expect a lower minimum likeness.

   With two references of the same woman (65% minimum), averages in our test: Fibo 2.0 71%, Qwen-Image 2.1 Best 68%, Fast 64%, FLUX.3 Klein Fast 67% (4 steps) / 64% (8), Best 58-60% (16-28 steps), FLUX.2 Klein 55%, Edit-2511 about 50%. The likeness score is not everything: FLUX.3 Klein's images looked the most natural and were judged closest by eye. For reference, real photos of her scored 61-78% against one reference.

   Every image is checked with the [face likeness](#-face-likeness-in-the-previews): under the minimum (60% by default) it is tried again with another seed, and if it still does not reach it, it goes to `_rejected`. It needs a checkbox confirming you have the right or the person's permission to use their images.
5. **📂 Use in Dataset Manager** sets the new folder as the trainer's dataset: references and generated images, each with its `.txt`.

- **Captions:** the trigger plus the line of the plan (*close-up portrait of a woman, head and shoulders, wearing a black leather jacket, in a coffee shop...*). The fixed features go into the instruction for the model but not into the caption, so the trigger learns the identity.
- **Output:** a new folder (by default `<source>_forge`), never the source. GPU job: it does not start while a training, pre-cache or caption job is running, and they see it as busy.
- **Models:** the same folders as their trainers, downloaded the first time if the trainer has not done it: `Models/FLUX.3-Image-Klein_NF4` (~12 GB, plus the PDD turbo LoRA in `LoRAs`, ~1.2 GB), `Models/Fibo2_Dev-NF4` (`transformer`, `text_encoder_BF16`; ~13 GB), `Models/Qwen-Image21-NF4` (`transformer`, `text_encoder_BF16`, the Viggle turbo LoRA; ~22 GB), `Models/FLUX.2-Klein-9B_NF4` (~9 GB) or `Models/Qwen-Image-2512-NF4` (`transformer_edit`, `text_encoder_BF16`, the Edit-2511 Lightning LoRA; ~27 GB). The BF16 text encoders are split between GPU and RAM; the transformers of FLUX.3 Klein (5.5B), Fibo 2.0, 2.1 (7B) and Klein (9B) fit in the GPU and the 20B of 2511 uses BlockSwap.
- **Two references are better than one:** the likeness check averages them, and the model sees more of the face.
- Without face likeness installed, the images are kept without checking the likeness.

## 🧪 The trainers

> ⚠️ **About the default settings:** the tests were made to check that every training works, not to find the best performance or quality. Run your own tests with different settings (steps, learning rate, rank, resolution, captions) to improve the quality of your LoRAs.

All times were measured on an RTX 5080 16 GB.

### Fibo 2.0 — image and edit LoRAs (BRIA)

> **New and experimental:** full runs (pre-cache, training, previews, edit mode, resume) verified on Fibo 2.0 Dev. It works, but it is young: the defaults will move as more people test it.

- **Normal LoRAs** (characters, objects, styles): one image + one caption each.
- **Edit LoRAs**: pairs named `name_before.png` / `name_after.png` plus the instruction in `name.txt` (for example `replace the jacket with a red leather one`). Choose **LoRA Type → Edit**. The before image goes through the text encoder with the instruction and, as a clean latent, conditions the generation as context tokens; the loss is computed only on the "after".
- **The model:** `briaai/Fibo-2.0-dev`, the full non-distilled base (8.1 B, flow matching on the FLUX.2 VAE, Qwen3-VL-4B as text encoder). Its licence is **CC BY-NC 4.0**: non-commercial use only. The NF4 build is downloaded from `AcademiaSD/Fibo-2.0-NF4-for-LoRA-Training` the first time (the transformer in NF4 and the text encoder in BF16, INT8 or NF4); to build it yourself from the diffusers folder, run `tools/fibo2/5_conversor_Fibo2_NF4.py` once with the folder as `Fibo2_Dev-Raw/`. The conversion needs diffusers with `BriaFibo2Pipeline` (merged upstream): run `Update_LoRAlab-TrainerStudio.bat` first.
- **NF4:** the attention, MLP and cross-attention of the 44 blocks are quantized (342 layers); the perceptor that turns the caption into gist tokens, the modulation of every block and the input/output layers stay in BF16 (73 layers), because quantizing them puts noise in the text path. The transformer is 5.2 GB in VRAM instead of 16 GB.
- **Text encoder for the pre-cache:** Qwen3-VL-4B, the model's own — **NF4 (~2.7 GB, default)**, INT8, BF16 (9 GB+ VRAM) or BF16 with CPU offload (exact, any GPU). The pre-cache runs it once; the training never loads it.
- **Captions:** Fibo 2.0 was trained on structured JSON captions (VGL). A plain `.txt` also works (the pipeline reads it as a short description); for the best results drop a `<name>.json` next to the image with the structured caption — the pre-cache prefers the `.json` over the `.txt`, and the Dataset Manager shows and edits whichever one is there. A `text_render` entry is drawn and shown to the model exactly as in training, so the text of the image comes out right; above the noise level 0.9 the caption goes in without those drawings, as in the official recipe.
- **Recipe:** the one BRIA publishes in `fine_tuning/train_lora.py`: logit-normal noise with 10 % uniform, 10 % text dropout, 20 % context dropout in edit mode, AdamW (weight decay 0.01), gradient clip 1.0.
- **LoRA Targets:** *All* (default) trains all 415 linear layers, exactly the recipe BRIA used; *Blocks* trains only the attention and MLP of the 44 blocks.
- **Previews:** 30 steps / CFG 5, the model's own defaults, and a **Preview Size** (Training / 768 / 1024) to see the result at the size you will use in ComfyUI even if you train at 512. **Fast Previews** cuts the steps and the guidance: Fibo 2.0 Dev has no distilled LoRA (the "Edit Turbo" is another checkpoint), so the preview is about twice as fast but rougher.
- **The LoRA is exported for ComfyUI**, in the format its loader takes (`diffusion_model.<capa>.lora_A/lora_B` + `alpha`). ComfyUI runs its own repack of Fibo 2.0, where the attention, the MLP and the cross-attention are single fused matrices, so the layers that fuse are re-written as one LoRA of several times the rank: the applied change is exactly the same as in diffusers, but the file is about half again as big.
- **To convert a LoRA trained before this change** (with the `transformer.*` keys), without retraining: `python tools/fibo2/7_conversor_lora_comfyui.py <lora.safetensors>`. It rewrites the keys in place and keeps the metadata.
- **Technical notes:** [docs/README_Fibo2.md](docs/README_Fibo2.md).

- **From 8 GB of VRAM:** **VRAM Profile**, **Resident Blocks**, **Block Swap Storage** and **RAM Limit**, as in [FLUX.2 Klein 9B](#flux2-klein-9b--image-and-edit-loras): the blocks that do not fit wait in RAM or on disk and come to the GPU just in time. Measured with the 8 GB profile (rank 16, image LoRAs at 768²): 3.5 s/step and 5.3 GB of peak VRAM, against 3.2 s/step with everything in VRAM; DoRA fits too (5.9 s/step).

| Measured on an RTX 5080 16 GB, **Auto** profile (rank 8, LoRA Targets: all) | s/step | Peak VRAM |
| :--- | :--- | :--- |
| Image 512² | 2.0 | 8.7 GB |
| Image 1024² | 6.2 | 11.2 GB |
| Edit 512² | 3.1 | 9.9 GB |
| Edit 1024² | 14.9 | 15.9 GB |

The edit mode adds the tokens of the before image to the sequence, so edit LoRAs at 1024² need much more memory: on small cards train them at 512².

### Qwen-Image 2.1 — image and edit LoRAs

- **Normal LoRAs** (characters, objects, styles): one image + one caption each.
- **Edit LoRAs**: pairs named `name_before.png` / `name_after.png` plus the instruction in `name.txt` (for example `make it TOSTIOK style`). Choose **LoRA Type → Edit**. The "before" image goes through the text encoder with the instruction, like the ComfyUI `TextEncodeQwenImage21` node, and the loss is computed only on the "after".
- **Captioner:** Qwen3-VL-8B, the model's own text encoder in NF4 (~6 GB VRAM, ~11 s per image), with **Normal** and **Edit** modes. For a style or effect, one common instruction in every pair usually works better than one per pair.
- **Text encoder for the pre-cache:** BF16 with CPU offload (exact, any GPU, default), BF16 (16 GB+ VRAM), INT8 (~9 % error, 10 GB+) or NF4 (~24 % error, 6 GB+). With 8 GB of VRAM and 16 GB of RAM, choose NF4.
- **Previews:** 30 steps / CFG 3, or **Turbo** (Viggle Turbo LoRA, 4 steps / CFG 1: ~5 s instead of ~34 s). For edit LoRAs, pick a **before** image that is **not** in the dataset: it is the only way to see whether the effect generalizes.
- **LoRA Targets:** *Blocks* (attention + MLP of the 32 blocks, default) combines cleanly with the Turbo LoRA; *All* also trains the shared modulation and input/output layers.

| Verified starting point | Characters | Edits |
| :--- | :--- | :--- |
| Resolution | 512×512 | 512×512 |
| Rank / Alpha | 8 / 8 | 8 / 8 |
| Learning rate | 4e-4 | 4e-4 |
| Steps | 500 (~9 min 20 s) | 300 with 30 pairs (~9 min) |

8 GB cards train at 512² and 768² (previews switch to a tiled VAE decode at 768²). 768²: ~2.2 s/step, ~8.4 GB VRAM; 1024²: ~4.3 s/step.

### Qwen-Image 2512 / Edit 2511 — image and edit LoRAs

> **New:** full runs (pre-cache, training, previews, resume) verified on Qwen-Image-2512 and on Qwen-Image-Edit-2511 with an edit LoRA.

- One trainer, two models, chosen with **Base Model**: **Qwen-Image-2512** (`Qwen/Qwen-Image-2512`, text to image) and **Qwen-Image-Edit-2511** (`Qwen/Qwen-Image-Edit-2511`, editing). An edit LoRA (`name_before` / `name_after` pairs + instruction) always uses Edit-2511. Both are Apache 2.0, share the text encoder and the VAE, and only the transformer you train on is downloaded. They are separate fine-tunes of Qwen-Image (18-23 % apart in the weights), so a LoRA trained on one is not guaranteed to work on the other.
- The 20B transformer is **NF4** (9.9 GB instead of 40.9 GB), except the modulation of the first block, which stays in BF16: in 4 bits it leaves grain all over the image. **Blocks on GPU** keeps that many of the 60 blocks in VRAM and copies the rest from RAM one by one as they are used, while the next one is already being copied; `-1` picks the number from the free VRAM, the resolution and the rank. Each resident block costs ~0.17 GB and saves its copy time.
- The LoRA trains attention and MLP of the 60 blocks and is exported as `transformer.transformer_blocks.N.*` with `alpha`, which ComfyUI loads with the standard LoRA loader.
- **Edit:** the before image goes to the text encoder (~384², as in the official pipeline) and, as a clean latent at the size of the after image, behind the target in the image sequence; Edit-2511 gives those tokens timestep 0.
- **Text encoder (pre-cache only):** Qwen2.5-VL-7B in **BF16 CPU Offload** (default; exact), **BF16** (18+ GB), **INT8** (10+ GB) or **NF4** (6+ GB). The prompt is encoded with the official templates; in edit mode the before image gets its 3D MRoPE positions, as in ComfyUI.
- **Captioner** (Qwen3-VL-8B NF4, shared): descriptions in normal mode, imperative instructions in edit mode.
- **Previews:** 30 steps / CFG 4 with the official norm rescaling. Edit previews always use the preview reference image, with a negative that also sees it, as in the official pipeline. **Turbo LoRA (Fast Previews)** uses lightx2v's [Lightning 4-step LoRAs](https://huggingface.co/lightx2v/Qwen-Image-2512-Lightning) (2512 and [Edit-2511](https://huggingface.co/lightx2v/Qwen-Image-Edit-2511-Lightning)), with their shift 3 and no CFG.
- Default settings: 500 steps, LR 0.0002, cosine with 100 warmup steps, rank 16 / alpha 16.

| Measured on an RTX 5080, PCIe 3.0 x16 (rank 16, every block from RAM) | Peak VRAM | s/step |
| :--- | :--- | :--- |
| Image 512² | 3.0 GB | 2.2 |
| Image 1024² | 4.9 GB | 5.7 |
| Edit 512² | 3.6 GB | 2.9 |
| Edit 1024² | 7.6 GB | 14.1 |
| Image 512², all 60 blocks on GPU | 13 GB | 1.8 |

Copying the blocks from RAM costs little on a x16 slot (2.2 against 1.8 s/step at 512²); on a x4 slot or a riser it is several times slower.

### Boogu Image Edit 0.1 — edit LoRAs

> **New:** full runs (pre-cache, training, previews, stop and resume) verified with an edit dataset and with normal images.

- Trains on **Boogu-Image-0.1-Edit** (`Boogu/Boogu-Image-0.1-Edit`, Apache 2.0) with the training code of [DiffSynth-Studio](https://github.com/modelscope/DiffSynth-Studio), which is part of the Studio's regular dependencies. The first Pre-Cache downloads the NF4 model once (~11 GB, [AcademiaSD/Boogu-Image-Edit-NF4-for-LoRA-Training](https://huggingface.co/AcademiaSD/Boogu-Image-Edit-NF4-for-LoRA-Training)): transformer and Qwen3-VL-8B text encoder in NF4, ~5 GB each.
- **Edit LoRAs:** each sample is `name_before.ext`, `name_after.ext` and `name.txt` (the instruction). The before image goes to the text encoder (~384²) and, as a clean latent at the same scale as the target, next to it in the image sequence, as ComfyUI's `TextEncodeBooguEdit` does. **Normal LoRAs** (one image + caption) also work.
- The LoRA trains the attention layers and is exported as `diffusion_model.*`, which ComfyUI's native Boogu support loads with the standard LoRA loader. rsLoRA, LoRA+ and LoKr are available.
- **Previews:** 30 steps / CFG 4 on the preview reference image; the negative is empty and does not see the image, as in ComfyUI.
- Default settings: 500 steps, LR 0.0002, cosine, rank 16 / alpha 16.
- **From 8 GB of VRAM:** **VRAM Profile**, **Resident Blocks**, **Block Swap Storage** and **RAM Limit**, as in [FLUX.2 Klein 9B](#flux2-klein-9b--image-and-edit-loras): the blocks that do not fit wait in RAM or on disk and come to the GPU just in time. DiffSynth loads the whole transformer first (~5 GB) and then parks what does not fit.

| Measured on an RTX 5080 (rank 16, edit, 512²) | |
| :--- | :--- |
| Training, **Auto** profile | ~2.1 s/step, ~7.8 GB (8.3 GB with previews) |
| Training, **8 GB** profile | ~2.8 s/step, 5.5 GB of peak VRAM, previews included |

### Krea 2 — image LoRAs for Krea 2 Raw and Turbo

- The 12B transformer is built directly from its **NF4** weights (no BF16 copy is ever downloaded or loaded): ~7.5 GB of VRAM while training.
- **Captioner:** Qwen3-VL-4B, Krea 2's own text encoder (NF4, ~3.5 GB VRAM, no extra download).
- **Previews** with the Krea 2 Turbo LoRA (8 steps). A new custom preview prompt is encoded on the CPU without stopping the training.
- 8-bit AdamW, gradient checkpointing, Krea 2's own noise-shift schedule.
- The exported LoRA works with Krea 2 Raw and Krea 2 Turbo and carries its alpha, so ComfyUI applies it at the same strength as the previews.

| Starting point | |
| :--- | :--- |
| Resolution | 512×512 (768×768 / 1024×1024 need more steps and VRAM) |
| Rank / Alpha | 16 / 32 |
| Learning rate | 3e-4 |
| Steps | 500–1000 at 512² (~1,500 at 768², ~2,000 at 1024²) |
| Time | 500 steps, 14 images, 512²: ~15 min (RTX 3060 12 GB: ~1 h 30 min) |

### Z-Image — image LoRAs for Z-Image and Z-Image-Turbo

- Trains on **Z-Image** (the undistilled base model, the one meant for fine-tuning). The LoRA has the same layers as **Z-Image-Turbo** and also loads there.
- The 6B transformer is built directly from its **NF4** weights, and the Qwen3-4B text encoder of the pre-cache is NF4 too: ~5.5 GB of VRAM while training at 512².
- **Captioner:** Qwen3-VL-8B NF4, shared with LTX-2.3 (~5.5 GB VRAM, ~10 s per image).
- **Previews:** 28 steps / CFG 5 (CFG as in ComfyUI: 1 = off), or **Turbo** with Alibaba PAI's **Z-Image-Fun-Lora-Distill** (made for Z-Image base, 4 steps / CFG 1, about 10 times faster; downloaded the first time, ~570 MB). **Preview Size** renders them at the training size or at 768 / 1024 with the same proportions, to see what you will get in ComfyUI even when training at 512 (1024 with Turbo: ~5 s, ~6.4 GB of VRAM).
- **LoRA Targets:** *Blocks* (attention + MLP of the 30 blocks and the 4 refiners, default) or *All*. ComfyUI loads the exported LoRA directly.
- **Steps count micro-steps:** with Grad Accum 4 the LoRA is updated once every 4 steps, so 1,500 steps are 375 updates. The likeness shows in the previews much earlier, but a 900-step LoRA still needed a strength of ~2.6 in ComfyUI.

| Verified starting point | |
| :--- | :--- |
| Resolution | 512×512 |
| Rank / Alpha | 8 / 8 |
| Learning rate | 4e-4 |
| Steps | 1,500 (14 images) |
| Time | ~0.9 s/step at 512²: ~23 min plus previews |
| LoRA strength in ComfyUI | **Z-Image: 1.0–1.5** · **Z-Image-Turbo: 1.5–2.5** |

### Ming-Image — image and edit LoRAs for transparent designs

> **New and experimental:** full runs (pre-cache, training, previews, edit mode, resume) verified on Ming-Image 0.1 Design. It works, but it is young: the defaults will move as more people test it.

- **Normal LoRAs**: one image + one caption each, in Ming-Image's own **Figma-style JSON** format. The captioner writes it for you.
- **Edit LoRAs**: pairs named `name_before.png` / `name_after.png` plus one instruction in `name.txt`. The model sees the before image and learns to produce the after.
- **The model:** `inclusionAI/Ming-Image-0.1-Design`, the Design variant, which generates the **alpha channel**: that is what makes the transparent designs. The NF4 build is published as `AcademiaSD/Ming-Image-NF4-for-LoRA-Training` (16.2 GB instead of ~49 GB).
- **The "text encoder" is a full MLLM**: BailingMoE-V2 (a Mixture-of-Transformers) plus a ViT, 10.3 B parameters, in NF4. It is asked for the conditioning with `image_gen_only_extract_hidden_states` and returns two tensors: the 256 scale tokens the DiT sees, and the direct LLM states.
- **VAE with alpha**: the VAE is RGBA, so the images are trained **with** their alpha channel; the opaque ones enter with alpha = 1.
- **Captioner:** the shared Qwen3-VL-8B-Instruct NF4, with **Normal** (the JSON caption) and **Edit** (one instruction per pair) modes. When the image really has an alpha channel it is told so, so it does not invent a background behind a transparent design.
- **Previews:** 12 steps / CFG 1.0, the official pipeline's `pos + cfg·(pos−neg)`, and up to **4 reference images** for the edit preview (`<image1>`, `<image2>`, …).
- **Live settings:** the changes saved with *Save JSON* while the training runs are applied on the next step, and the console says what changed.

- **From 8 GB of VRAM:** **VRAM Profile**, **Resident Blocks**, **Block Swap Storage** and **RAM Limit**, as in [FLUX.2 Klein 9B](#flux2-klein-9b--image-and-edit-loras): the blocks that do not fit wait in RAM or on disk and come to the GPU just in time. Measured with the 8 GB profile at 1024² (rank 16): 5.2 s/step and 5.8 GB of peak VRAM, previews included, against 4.9 s/step with everything in VRAM.

Measured on an RTX 5080 16 GB with the **Auto** profile (rank 8, batch 1): **1024² → 12 s/step and 13.2 GB of peak VRAM**; **512² → 2.4 s/step and 7 GB of peak VRAM** (a real run of 960 steps at 512² averaged 1.3 s/step). The pre-cache proposes 768² by default.

The official image-edit task works at 1024: 512 and 768 are out of its distribution, so train edit LoRAs at 1024 if your card allows it.

### Anima — anime and illustration LoRAs

- **Anima** is a 2B anime / illustration model by CircleStone Labs and Comfy Org, built on NVIDIA Cosmos-Predict2. The trainer uses **Anima-Base**, the version its author recommends for LoRAs, downloaded from the official diffusers repository.
- **Model Precision:** *BF16* (full quality, ~5.6 GB of VRAM while training at 512²) or *NF4* (attention and MLP quantized when loading, ~3.1 GB at 512²: it fits **4 GB** cards). Images from the NF4 transformer look like the BF16 ones.
- The text goes through Qwen3-0.6B and Anima's **LLM adapter** in the pre-cache. The adapter is **never trained**, as the author advises: it holds a lot of the model's knowledge and degrades easily.
- **Captioner:** Qwen3-VL-8B NF4, shared with LTX-2.3 and Z-Image, with two styles: **natural language** or **Danbooru tags** (lowercase, spaces instead of underscores). Anima was trained on both.
- **Previews:** 30 steps / CFG 4 with the author's recommended negative prompt, and **Preview Size** as in Z-Image.
- The LoRA is exported with Anima's own layer names (`diffusion_model.blocks.N.self_attn.q_proj`…), which ComfyUI loads directly.

| Starting point (author's recommendation) | |
| :--- | :--- |
| Resolution | 768×768 (Anima works from 512² to 1536²) |
| Rank / Alpha | 32 / 32 |
| Learning rate | 2e-5 |
| Speed | ~0.65 s/step at 512² in BF16, ~0.8 s/step in NF4 (under 4 GB of VRAM); ~1.6 s/step at 1024² in BF16 |

### FLUX.1 Dev — image LoRAs

- Trains on **FLUX.1 [dev]** (11.9B) in **NF4**. The first run downloads `diffusers/FLUX.1-dev-bnb-4bit`, which is not gated and needs no token; the FLUX.1 [dev] license still applies.
- **Pre-cache:** the same caption goes to T5-XXL (NF4, the 512-token sequence) and to CLIP-L (the pooled vector). Training does not load either of them.
- **Train Guidance:** FLUX.1 dev takes guidance as an input. Training uses 1 by default; the setting is read when training starts.
- **Timesteps:** the resolution-dependent shift of the official pipeline.
- **Previews:** 28 steps / **Preview Guidance** 3.5 (the same input as ComfyUI's FluxGuidance node, with no negative pass). There is no turbo option.
- **Captioner:** Qwen3-VL-8B NF4, shared with Z-Image and FLUX.2 Klein 9B.
- **Defaults:** 512², 800 steps, rank / alpha 8 / 8, previews off (**Preview Every** 0).
- **Speed and VRAM** (RTX 5080, with previews, **Auto** profile): ~1.2 s/step and ~10 GB at 512², ~2.6 s/step and ~11 GB at 768² · pre-cache ~5 GB.
- **From 8 GB of VRAM:** **VRAM Profile**, **Resident Blocks**, **Block Swap Storage** and **RAM Limit**, as in [FLUX.2 Klein 9B](#flux2-klein-9b--image-and-edit-loras): the blocks that do not fit wait in RAM or on disk and come to the GPU just in time. Measured with the 8 GB profile at 512² (rank 16): 2.0 s/step and 5.0 GB of peak VRAM, against 1.55 s/step with everything in VRAM; DoRA fits too (3.8 s/step).
- **LoRA Targets:** *Blocks* (attention + MLP of the 19 double and 38 single blocks, default) or *All*. The LoRA is exported in diffusers format, which ComfyUI maps to FLUX.1's layers.
- `tools/flux1/5_conversor_Flux1_NF4.py` is optional: it builds your own NF4 cache from the gated official repo (accept the license on Hugging Face first).

### FLUX.2 Klein 9B — image and edit LoRAs

- Trains on **FLUX.2 [klein] Base 9B** (the undistilled model, the one meant for fine-tuning). The LoRA also loads on the distilled **FLUX.2 [klein] 9B**; it is not compatible with the 4B models.
- The 9B transformer and the Qwen3-8B text encoder of the pre-cache are **NF4**: 8.8 GB to download instead of 34.7 GB.
- **Normal LoRAs** (characters, objects, styles) and **Edit LoRAs** with the same `name_before.png` / `name_after.png` pairs as Qwen-Image 2.1. Klein's text encoder only reads the instruction: the "before" goes to the transformer as a clean reference image, as in the official pipeline, and the loss is computed only on the "after".
- **Captioner:** Qwen3-VL-8B NF4, shared with LTX-2.3, Z-Image and Anima, with **Normal** and **Edit** modes.
- **Previews:** 28 steps / CFG 4, or **Turbo** with kalle07's Klein 9B turbo LoRA (4 steps / CFG 1; downloaded the first time, ~350 MB), and **Preview Size** as in Z-Image.
- **LoRA Targets:** *Blocks* (attention + MLP of the 8 double and 24 single blocks, default) or *All*. ComfyUI loads the exported LoRA directly.
- **From 8 GB of VRAM:** **VRAM Profile** (Auto / 8 / 10 / 12 / 16 / 24 / 32 GB) simulates a smaller card with a hard cap, and the blocks that do not fit wait in RAM or on disk (**Block Swap Storage**, with **RAM Limit**, as in LTX 2.5 and MiniMax-H3) and come to the GPU just in time. **Resident Blocks** -1 lets the plan decide. With DoRA at 1024² use the 10 GB profile or more; the console warns when a run does not fit. If a step still runs out of VRAM (many bucket sizes fragment it), 2 more blocks go to RAM and the step is repeated, as in MiniMax-H3.

| Verified starting point | |
| :--- | :--- |
| Resolution | 768×768 |
| Rank / Alpha | 16 / 16 |
| Learning rate | 3e-4 |
| Steps | 1,000 (14 images): the likeness shows from ~500, but in ComfyUI the 1,000-step LoRA looks better than the 600 and 700 ones |
| LoRA strength in ComfyUI | 1.0 for characters (1,000 steps) · 1.0–1.5 for edit LoRAs |
| Speed and VRAM, **Auto** profile (everything in VRAM) | 512²: ~1.5 s/step, ~8 GB · 768²: ~2.6 s/step, ~10 GB · edit at 512²: ~2.3 s/step, ~8 GB · edit at 768²: ~5.7 s/step, ~11 GB |
| 8 GB profile (RTX 5080, rank 16) | 768²: 2.2 s/step (2.0 with everything in VRAM), 6.5 GB peak · 1024²: 3.1 s/step (2.8), 5.8 GB · edit at 1024²: 10.7 s/step (10.0), 5.8 GB instead of 11.5 GB · DoRA at 768²: 3.6 s/step, 5.9 GB. Same losses as with everything in VRAM. Measured with 7 GiB for PyTorch; the profile also leaves out what your other apps use (with 1.3 GB open, 6.4 GiB: a 14-image dataset at 768² ran at 3.0 s/step, 6.0 GB peak) |

### FLUX.3 Image Klein — image and edit LoRAs

- Trains on **FLUX.3 Image Klein Base** (`black-forest-labs/flux-3-image-klein-base`, the undistilled model meant for fine-tuning). The LoRA also loads on the distilled Klein.
- The 5.5B transformer is **NF4** (3.1 GB instead of 11 GB); the Qwen3-VL-4B text encoder of the pre-cache stays in BF16 and, on small GPUs, the layers that do not fit run from RAM, as in Krea 2.
- **Normal LoRAs** and **Edit LoRAs** with `name_before` / `name_after` pairs: the "before" goes in through FLUX.3's own reference-image stream, clean, as in the official pipeline.
- Same recipe as the official diffusers Klein trainer: fixed timestep shift 6.93, velocity target, LoRA on attention + MLP of the image, text and single blocks (plus the reference blocks for edit LoRAs). The LoRA is exported with BFL's original layer names, which ComfyUI loads directly.
- **Captioner** (Qwen3-VL-8B NF4, shared) in **FLUX.3's own caption formats**, adapted from BFL's prompt-upsampler instructions: *Normal* (a detailed prose caption: medium, scene, lighting, frame-relative layout, subjects), *Normal + boxes* (the caption cites each element as `<person_1>` and ends with a JSON table `[{"id", "bbox", "desc"}]`), *Edit* (a detailed instruction that closes with everything else staying identical) and *Edit + boxes* (the instruction cites `<ref_image_0>` and each item, plus `[{"id", "from", "src_bbox", "tgt_bbox", "desc"}]`, the annotation format BFL trained editing on). Boxes are `[y_min, x_min, y_max, x_max]` on a 0-1000 grid; colors go in words (FLUX.3 has no hex palette, unlike Ideogram 4). For edit pairs the captioner sees the before **and** the after and is told which region changed, computed from the pixels.
- **Previews:** 28 steps / CFG 3.5 (there is no turbo LoRA for FLUX.3 yet).
- Needs diffusers with FLUX.3 support: `requirements.txt` pins it, so **Update_LoRAlab-TrainerStudio** installs it.

| Measured on an RTX 5080 | |
| :--- | :--- |
| Training | 512²: ~0.7 s/step, ~4.2 GB · 768²: ~2.1 s/step · 1024²: ~3.9 s/step, ~5.7 GB · edit at 768²: ~6 s/step (rank 16) |
| Previews | 1024², 28 steps with CFG: ~35 s, ~3.7 GB |
| Text encoder (pre-cache only) | ~8.3 GB in BF16; the part that does not fit in VRAM runs from RAM |

### MOSS-Image — image and edit LoRAs for MOSS-Image Base and SFT

- Trains on **MOSS-Image Base** (`OpenMOSS-Team/MOSS-Image-Base`, the model OpenMOSS publishes for LoRA training) or **MOSS-Image SFT** (`OpenMOSS-Team/MOSS-Image-SFT`, Base fine-tuned for quality), chosen with **Base Model**. Both share the text encoder and the VAE, so the same pre-cache works for either.
- The 5B single-stream transformer is **NF4** (3.1 GB instead of 10.2 GB). The LoRA trains attention (q, k, v, o) and MLP of the 42 blocks and is exported with the original layer names (`diffusion_model.layers.N.proj.*`), which ComfyUI (nightly, with native MOSS-Image support) loads with the standard LoRA loader.
- **Text encoder (pre-cache only):** Qwen3.5-9B, the same modes as Qwen-Image 2.1: **BF16 CPU Offload** (default; exact, the part that does not fit in VRAM runs from RAM), **BF16** (24+ GB), **INT8** (~7-14 % error, 14+ GB) or **NF4** (~20-30 % error, 8+ GB). Error = relative difference of the embeddings against BF16, measured. Only the version you pick is downloaded.
- Training recipe from OpenMOSS's technical report: velocity target, logit-normal noise sampling of their last pretraining stage (μ −1.09, s 0.95, cut at σ 0.95, 1 % uniform). The text encoder stays frozen, as they recommend.
- **Captioner** (Qwen3-VL-8B NF4, shared): detailed prose following OpenMOSS's own recaptioning guide, with any visible text copied exactly, in double quotes, and its layout described.
- **Previews:** 28 steps / CFG 3 with block 22 skipped in the negative branch, like the official pipeline. **Turbo LoRA (Fast Previews)** uses [darask0's 4-step adapter](https://huggingface.co/darask0/MOSS-Image_4-step_adapter_lora) (no CFG, ~1.2 GB, downloaded on first use). It is not a regular LoRA: it is added unmerged in FP32, with its own time embedding and its own "data-space" sampler, so it does not touch the LoRA being trained. It was distilled from SFT and also works on Base.
- Default settings: 500 steps, LR 0.0004, cosine with 100 warmup steps, rank 8 / alpha 8.
- **Edit LoRAs:** MOSS-Image cannot edit on its own; an edit LoRA teaches it, and yours trains on top of it, frozen. Choose **LoRA Type → Edit** and use `name_before.png` / `name_after.png` pairs with the instruction in `name.txt` (the captioner has an **Edit** mode). **Edit Base** picks the edit LoRA, downloaded on first use:
  - **armV5** (default): [akhaliq's MOSS-Image-Edit-HQ](https://huggingface.co/akhaliq/MOSS-Image-Edit-HQ) (~495 MB), trained on SFT with masks that keep the unedited parts of the image and with full scene captions. It follows ai-toolkit's layout: the "before" goes in as a clean reference up to 0.5 MP, and the text encoder also sees it (at 384×384, after "Picture 1:", as ComfyUI feeds it).
  - **armV4**: the previous version of MOSS-Image-Edit-HQ, used the same way.
  - **chinoll**: [chinoll's Moss-Image-Edit](https://huggingface.co/chinoll/Moss-Image-Edit) (~300 MB), the first one; the reference long side is scaled to 512 px and the instruction is encoded as plain text.

  Either way the reference goes in at timestep 0 with attention that only looks at the references. Changing the base needs Pre-Cache again. Previews edit the "before" of a pair or up to 4 reference images of your own. Train on **SFT**: both bases were trained on it.
- **Using an edit LoRA in ComfyUI** needs ComfyUI's own MOSS-Image edit support (recent ComfyUI): a LoRA loader and **Text Encode MOSS-Image Edit** (positive and negative, with the VAE and the image), with `edit_format` **ai-toolkit** for armV5 and armV4 or **Moss-Image-Edit** for chinoll. **Edit LoRA Export** gives you two choices. **Separate** (default) exports your LoRA alone: load it next to the edit base LoRA (at 1.0). **Fused** merges both into one LoRA (name ending in `_FUSED`) that you load alone; the merge concatenates the matrices, so it is exact. A LoKr can only be exported separately. **Recommended strength for your LoRA: 0.5 to 1.0**; lower it if the effect is too strong (in the fused file it also lowers the edit base).

| Measured on an RTX 5080 | |
| :--- | :--- |
| Training | 512², rank 8: ~1.0 s/step, under 6 GB · edit at 512²: ~1.8 s/step |
| Previews | 1024²: 28 steps with CFG ~43 s · Turbo, 4 steps ~4 s |
| Text encoder (pre-cache only) | BF16 ~17 GB (the part that does not fit in VRAM runs from RAM) · INT8 ~10 GB · NF4 ~6.5 GB |

### Ideogram 4 — image LoRAs

- Trains on the official **Ideogram 4 NF4** release (9.3B, diffusers). It is a single-stream transformer: text and image tokens share one sequence.
- **Captioner:** Qwen3-VL-8B NF4 (the same model as Ideogram's text encoder) writes Ideogram's native JSON caption with a **bounding box for every subject, object and piece of text** — the format Ideogram 4.5 and FLUX.3 Image will also use. A second **OCR pass** reads every sign with its box (in one pass the model misses many texts in busy scenes). **JSON detailed** also boxes each part of every person or animal (face, nose, ears, hands, legs...), each garment and accessory, for edit LoRAs. Captions are saved in the official format (key order, `[y1, x1, y2, x2]` boxes in 0–1000, no repeated elements) with the trigger word at the start of the description. **Natural language** is also available.
- **Use JSON for captions and preview prompts.** Ideogram 4 depends on its JSON format: in our tests a short plain prompt ("a woman with blonde hair in a green sweater reading in a library") gave odd crops or was blocked, while the same scene written as a JSON caption came out right. For the custom preview prompt, copy a caption from the dataset and edit it.
- **Previews:** 28 steps / CFG 7 with the last 3 steps at CFG 3, as in the official pipeline. Ideogram's guidance uses a second, **unconditional transformer** (4.3 GB): it is loaded only for the previews and moved to the GPU while each one runs, so with the **Auto** profile previews with CFG need ~15 GB at 1024². With a smaller **VRAM Profile** its blocks come to the GPU one by one too, and the training's blocks wait in RAM during the preview. **Preview Size** as in Z-Image.
- **Built-in safety filter:** Ideogram 4 was trained to output a grey "Image blocked by safety filter" image for some prompts (for example a woman at the beach). It is the model itself, not the trainer, and its license forbids circumventing it: change the preview prompt if it happens.
- **LoRA Targets:** *Blocks* (attention + MLP of the 34 blocks, default) or *All*. The LoRA is exported with ComfyUI's own layer names (q, k and v merged into `attention.qkv`), so ComfyUI loads it directly.
- **From 8 GB of VRAM:** **VRAM Profile**, **Resident Blocks**, **Block Swap Storage** and **RAM Limit**, as in [FLUX.2 Klein 9B](#flux2-klein-9b--image-and-edit-loras): the blocks that do not fit wait in RAM or on disk and come to the GPU just in time. Measured with the 8 GB profile at 1024² (rank 16): 7.5 s/step and 6.4 GB of peak VRAM with a CFG preview, against 6.5 s/step with everything in VRAM.

| Tested starting point | |
| :--- | :--- |
| Captions | Ideogram JSON |
| Resolution | 1024×1024 |
| Rank / Alpha | 16 / 16 |
| Learning rate | 3e-4 |
| Steps | 1,000 (14 images): the likeness shows from ~500 |
| LoRA strength in ComfyUI | 1.0 |
| Speed and VRAM, **Auto** profile | ~5.7 s/step (~1 h 35 min for 1,000 steps plus previews) and ~10 GB at 1024²; ~15 GB during previews with CFG |

### SDXL — Base, Pony, Illustrious, NoobAI, Juggernaut, RealVis or your own checkpoint

- **Base Model** picks what the LoRA is trained on. Each preset is downloaded the first time (~7 GB) into `Models/SDXL-Models/`:

  | Preset | Best for | Captions | Quality prefix (optional) · Preview CFG |
  | :--- | :--- | :--- | :--- |
  | SDXL Base 1.0 | general, realistic | natural | CFG 6 |
  | Juggernaut XI v11 | photorealistic | natural | CFG 5 |
  | RealVisXL V5.0 | photorealistic | natural | CFG 5 |
  | Pony Diffusion V6 XL | anime, cartoon, furry | tags | `score_9, score_8_up, score_7_up` · CFG 7 |
  | Illustrious XL v0.1 | anime | Danbooru tags | `masterpiece, best quality` · CFG 6 |
  | NoobAI-XL 1.1 | anime | Danbooru tags | `masterpiece, best quality, newest` · CFG 5 |
  | Custom checkpoint | any SDXL `.safetensors` (Juggernaut Ragnarok, WAI...) | either | CFG 6 |

  A LoRA works best on the model it was trained on and on models derived from it: train on Illustrious v0.1 for Illustrious-based checkpoints such as WAI or NoobAI.
- **Captioner:** Qwen3-VL-8B NF4 (shared), with **natural language** or **Danbooru tags**. Long captions are encoded in blocks of 75 tokens (up to 225), as kohya does.
- **Model Precision:** *BF16* or *NF4*, which quantizes the transformer blocks to 4 bits when loading and fits in a **4 GB GPU**. The first training run on a model saves its converted UNet in `Models/SDXL-Models/unet_cache/` (~5 GB on disk); from then on it loads with ~5.5 GB of RAM instead of ~14 GB.
- **Training:** the UNet with gradient checkpointing, noise prediction with Min-SNR weighting (γ = 5). **LoRA Targets:** *Blocks* (attention, MLP and projections of the transformer blocks, kohya's default) or *All* (+ the resnet convolutions, LoCon).
- **Quality prefix in captions** (Pony, Illustrious, NoobAI; off by default): puts the preset's prefix (`score_9, score_8_up, score_7_up` for Pony) before every caption and the preview prompt. Off, the previews show the LoRA alone; on, use the LoRA with that prefix in ComfyUI.
- **Previews:** Euler, 28 steps, with the preset's negative prompt. **Preview CFG 0** uses the preset's recommended value.
- The LoRA is exported in **kohya format** (`lora_unet_…`), which ComfyUI, Forge, A1111 and CivitAI load.
- **Grad Accum** multiplies the steps: with Grad Accum 4, 800 steps are only 200 LoRA updates. Style LoRAs on SDXL usually need around 1,000–3,000 updates.

| Tested on Pony (Greg Rutkowski style, 153 images) | BF16 | NF4 (low VRAM) |
| :--- | :--- | :--- |
| Resolution | 1024×1024 | 512×512 |
| Rank / Alpha | 16 / 16 | 8 / 8 |
| Steps / Grad Accum / LR | 1000 / 1 / 1e-4 | same (quality not yet compared) |
| Speed | ~1.1 s/step | ~1.5 s/step |
| VRAM | ~10.8 GB with the previews | ~3.5 GB, previews at 768² included |
| RAM | ~5.5 GB | ~5.5 GB |

The LoRA works at strength 0.8–1.2; at 2.0 it breaks anatomy.

### Wan 2.2 (T2V-A14B) — video and image LoRAs (high / low noise)

Wan 2.2 A14B splits the denoising steps between two 14B experts: **high noise** (the first steps, σ ≥ 0.875: layout and motion) and **low noise** (the rest: detail, faces, style). *Train Expert* picks which one learns:

- **Low noise**: enough for characters, objects and styles.
- **High noise**: for new motions, choreographies or camera moves.
- **Both** (default): one LoRA for each in the same run; the waiting expert stays in RAM and they swap on the GPU.

Each expert exports its own LoRA, named `_high_noise` / `_low_noise`. In ComfyUI each one goes on its own model.

- **Datasets:** images, video clips (`.mp4`, `.mov`, `.mkv`, `.webm`, `.avi`) or a mix, each with its `.txt`. Clips are read at **16 fps** from their start, up to *Max Frames* (4k+1: 17, 33, 49, 81…); a shorter clip uses all it has.
- **Model:** the first run downloads each expert it needs already in NF4 (~7.6 GB) from `AcademiaSD/Wan22-T2V-A14B-NF4-for-LoRA-Training`. If that repo does not have it, it downloads the original **one shard at a time** (57 GB in FP32), converts it to NF4 and deletes the shard; if it stops, it continues from the next shard. The other expert is only downloaded when you train it.
- **Captioner:** Qwen3-VL-8B NF4 (shared with the other trainers), with one prompt for images and another for clips. Of each clip it sees only the part that is trained.
- **Activation Offload** (on by default) keeps the activations in RAM, and the checkpoint works in half blocks.
- **From 8 GB of VRAM:** **VRAM Profile**, **Resident Blocks**, **Block Swap Storage** and **RAM Limit**, as in [FLUX.2 Klein 9B](#flux2-klein-9b--image-and-edit-loras): the blocks that do not fit wait in RAM or on disk and come to the GPU just in time. Each expert has its own blocks in RAM or on disk: switching experts no longer moves a whole 14B model, so with both experts it is also faster than before (rank 16, images at 512², 8 GB profile: 3.0 s/step and 5.2 GB, against 7.0 s/step and 10.4 GB before).
- **Previews:** an image (1 frame) or an `.mp4`, generated with both experts like ComfyUI when the other one is converted. *Turbo LoRA* (on by default) uses Kijai's lightx2v distill LoRA: 12 steps at CFG 1, high noise for the first 4 and low noise for the rest, about 2 minutes for a 17-frame clip instead of 9. Previews are off until you set *Preview Every*.

| Default starting point | |
| :--- | :--- |
| Resolution | 832×480 (480p) |
| Max frames per clip | 17 (1 s at 16 fps) |
| Rank / Alpha | 8 / 8 |
| Learning rate | 1e-4 |
| Steps | 1000 |

| Measured on an RTX 5080 16 GB (low noise, rank 16, 480p) | s/step | Peak VRAM |
| :--- | ---: | ---: |
| Image, before block swap | ~3 | 10.0 GB |
| Clip, 17 frames, before block swap | ~18.5 | 12.0 GB |
| Clip, 33 frames, before block swap | ~43 | 14.3 GB |
| Clip, 17 frames, **8 GB** profile | ~22 | 5.2 GB (a 17-frame video preview: 5.7 GB) |

On Windows a sample that does not fit in VRAM is left out with a message instead of letting the driver spill into system RAM, where a step takes 30 times longer. More in [docs/README_Wan22.md](docs/README_Wan22.md).

### LTX 2.5 — image, video, video + audio and edit LoRAs

LTX-2.5 is LTX-2.3 with a retrained transformer and a new text encoder (Gemma 4); its VAEs and vocoder are the same. One trainer covers four kinds of LoRA, chosen in the Pre-Cache panel and in the dataset itself:

- **Image LoRAs** (characters, styles): images with their `.txt`.
- **Video LoRAs** (motion, effects, camera moves): clips (`.mp4`, `.mov`, `.mkv`, `.webm`) with their `.txt`, next to images if you want. Press **Prepare clips** first: every clip ends at 24 fps with an 8n+1 frame count (9, 17 … 121), stretching time slightly instead of cutting the end, where the payoff of an effect is. **Max Frames** (49 by default, ~2 s; 121 = 5 s) and **Video Area** (384 × 384 by default) set what is trained.
- **Video + audio LoRAs**: tick **Train Audio**. Clips with a track also train the sound (audio attention and audio↔video cross attention); mute clips train only the picture. Audio files (`.wav`, `.mp3`, `.flac`, `.m4a`, `.ogg`) can also go in the dataset, but training audio on its own is **experimental**. The captioner cannot hear: write the sound in the caption.
- **Edit IC-LoRAs**: **LoRA Type → Edit**, pairs `name_before` / `name_after` (images or clips) with the instruction in `name.txt`; Create Captions writes the instructions. The before goes to the model as a clean reference and only the after is learned, as Lightricks' IC-LoRAs. **Reference Downscale ×2** halves the reference side to save VRAM.
- **8 GB of VRAM**: the transformer blocks that do not fit stay in RAM and are brought in just in time (block swap). **VRAM Profile** plans for your card or simulates a smaller one with a hard cap. Measured on the 8 GB profile: pre-cache 6.0 GB, images 6.65 GB (~6.8 s/it), 49-frame clips with audio 6.75 GB (~7.2 s/it).
- **Previews**: images as `.png`; clips (or **Preview Frames**) as `.mp4` at 24 fps with the generated sound, never larger than the training clips.
- **Captioner:** Qwen3-VL-8B NF4, with separate prompts for images, clips and edit pairs.
- Downloads `AcademiaSD/LTX25-NF4-for-LoRA-Training` (26.3 GB) the first time. LoRAs use the official key names and load in ComfyUI.

| Default starting point | Images | Clips |
| :--- | :--- | :--- |
| Resolution | 768×768 | 384×384, 49–121 frames |
| Rank / Alpha | 32 / 32 | 32 / 32 |
| Learning rate | 1e-4 | 1e-4 |
| Steps | 800 | 1500 |

More in [docs/README_LTX25.md](docs/README_LTX25.md).

### LTX-2.3 — character and style LoRAs for the LTX video model

- Trains **LTX-2.3**. Its LoRAs usually load in LTX-2.5 too, since both models have the same layers and LoRA key names, but it does not train LTX-2.5: 2.5 retrains the transformer and uses another text encoder (Gemma 4 instead of Gemma 3).
- Trains from **images** (single frames) to teach a character or a style to the video model.
- The 22B transformer and the Gemma 3 text encoder come pre-quantized in NF4; the BF16 / FP32 originals are never downloaded (see the table above).
- **Captioner:** Qwen3-VL-8B NF4 (~5.5 GB VRAM, ~13 s per image).
- Paged 8-bit AdamW and gradient checkpointing.
- **From 8 GB of VRAM:** **VRAM Profile**, **Resident Blocks**, **Block Swap Storage** and **RAM Limit**, as in [FLUX.2 Klein 9B](#flux2-klein-9b--image-and-edit-loras): the blocks that do not fit wait in RAM or on disk and come to the GPU just in time. Measured with the 8 GB profile at 768² (rank 16): 5.0 s/step and 5.2 GB of peak VRAM, the same speed as with everything in VRAM (11.1 GB).

| Default starting point | |
| :--- | :--- |
| Resolution | 768×768 |
| Rank / Alpha | 32 / 32 |
| Learning rate | 1e-4 |
| Steps | 800 |

### MiniMax-H3 — video, audio and RefMods

MiniMax-H3 is a 33B model that generates **video and audio together**. The official checkpoint is 498.5 GB; this trainer uses a 41 GB NF4 version and fits in 8 GB of VRAM with **block swap**.

- **Datasets:** images, video clips (`.mp4`, `.mov`, `.mkv`, `.webm`), audio (`.wav`, `.mp3`, `.flac`, `.m4a`) or a mix, each with its `.txt`. Images teach appearance; clips teach how something **changes over time**.
- **Prepare clips:** one button leaves every clip at **24 fps** with a valid **17n+5** frame count, stretching time slightly instead of cutting the end. Originals are kept in `_originals\`.
- **Captioner:** Qwen3-VL-4B (4-bit, ~4.2 GB VRAM, ~6 s per image), with one prompt per content type (image, video, audio).
- **VRAM profiles** for 32 / 24 / 16 / 12 / 10 / 8 GB cards size the block swap to your resolution and captions; choosing a smaller card than yours simulates it. Parked blocks can live in RAM, on disk (for 16 GB of RAM) or switch automatically.
- **RefMod:** encodes a few reference stills or clips into a file that ComfyUI's `MiniMaxH3ReferenceToVideo` node uses as a native reference. No training: seconds instead of hours.
- **Audio** as part of video clips trains well. **Audio-only training is still experimental:** past a point it degrades the video branch.
- fp32 LoRA and optimizer (8-bit optimizers lose the fine facial detail on this model), deterministic sampling across resumes, and a full log in `train_log.txt`.

| Verified starting point | Images | Video clips |
| :--- | :--- | :--- |
| Resolution | 576×576 | 192×192, 124 frames |
| Rank / Alpha | 16 / 16 | 8 / 8 |
| Learning rate | 2e-4 | 2e-4 |
| Steps | 600 (~37 min on 16 GB) | 600 (~1 h 10 min on 16 GB) |

Rank 16 matters for characters: with rank 8 the likeness is just as good, but the model starts ignoring the prompt (ask for a beach, get a bedroom). On an 8 GB card the same image run takes ~80 minutes instead of 37.

### MiniMax-H3 Image — image and edit LoRAs · ⚠ Experimental

> **New and experimental:** pre-cache, training, previews, edit mode and resume verified. The defaults come from the first run with good likeness and will move as more people test it.

MiniMax-H3-Image is the image model of the MiniMax-H3 family, **distilled to 6 steps** with one output head per step and no CFG. The trainer uses its NF4 build, downloaded the first time from `AcademiaSD/MiniMax-H3-Image-NF4-for-LoRA-Training` (~19 GB), plus the text encoder alone from the MiniMax-H3 NF4 repo (~18 GB).

- **Why an adapter:** plain flow matching on a distilled model turns the high-noise heads into the dataset's average (blotches). So the LoRA trains on MiniMax-H3-Image itself, one distilled step and its head at a time, with a frozen **de-distillation adapter** on top (`adapter/` in the NF4 repo, 489 MB, downloaded by itself). The adapter absorbs what training does to the distilled heads, so the LoRA learns only your subject. It is **not used when generating**: previews and ComfyUI run without it. **Adapter Strength** (default x1.5) sets how hard it pushes while training.
- **Normal LoRAs** (characters, objects, styles): one image + one caption each.
- **Edit LoRAs:** pairs `name_before.png` / `name_after.png` with the instruction in `name.txt`. Choose **LoRA Type → Edit** in the Pre-Cache panel. MiniMax-H3-Image edits on its own, and the pairs are packed the way its official pipeline does it:
  - the text encoder sees the before image as `Picture 1: ` plus a vision block (short edge 1024 px), followed by the instruction;
  - the DiT gets its latent as reference rows held at t = 0.999, and the loss is computed only on the after image.

  Write the instruction the way you will prompt it, for example `Edit <Picture 1>. Make it TOSTIOK style.` A trigger word is optional: an edit LoRA only acts when it is loaded. **Reference Size** sets how big the DiT sees the before image:
  - **Match** (default): the area of the after image, at the before image's own aspect;
  - **Native**: the official short edge of 1024 to 2048 px, closer to how the model was trained, but the reference can cost more tokens than the image itself.
- **Edit pre-cache on 16 GB:** the text encoder is 14.9 GB in NF4. The vision tower runs first, with the 50 language layers parked in RAM; then the language model runs with those features, with the token embedding table in RAM. About 0.7 s per pair instead of 30-46 s spilling into shared memory.
- **Previews:** always 6 steps at CFG 1, the distilled schedule, rendered by MiniMax-H3-Image with the LoRA being trained attached. **Preview Size** goes from 1024² (1 MP, fast) to 4096² (16.8 MP, native, very slow). **Preview LoRA Strength** works like the LoRA strength in ComfyUI and can be changed while training: the saved LoRAs do not change. Edit previews are saved as `before | after`.
- **VRAM:** the NF4 blocks live in RAM and are uploaded one by one. **Resident Blocks** keeps some of them on the GPU for speed; 0 picks them from your card, the resolution and the longest sequence. If a step comes close to the card's limit, training moves blocks back to RAM instead of spilling into shared memory. After 20 steps the log says how many more blocks would fit.
- **Face likeness:** the face match score of the previews is the quickest way to follow a character run (see [Face likeness in the previews](#-face-likeness-in-the-previews)). Previews use the dataset captions, so try new prompts in ComfyUI before judging a run.
- **The LoRA is exported for ComfyUI** (`diffusion_model.*`, with `qkv_proj` as [q; k; v], the layout ComfyUI loads). Load it with the standard LoRA loader on the MiniMax-H3-Image checkpoint.
- Default settings: 1500 steps, LR 4e-4, constant with 50 warmup steps, rank 16 / alpha 32, adapter x1.5, previews every 40 steps at 1024².

| Face dataset, 14 images at 768² (face match of the previews, average) | Steps 800-1200 | Steps 1200-1500 | Best |
| :--- | :--- | :--- | :--- |
| Rank 16 / alpha 16, LR 2e-4 | 33.9 % | 37.3 % | 46.5 % |
| Rank 16 / alpha 32, LR 4e-4 (**defaults**) | 35.0 % | 44.9 % | 53.6 % |
| Rank 8 / alpha 8, LR 4e-4, cosine, adapter x1.0 | — | — | 25.1 % |

With the defaults the likeness was still rising at step 1500 and the loss still falling: a longer run (1800-2000 steps) may give more.

Image and edit LoRAs do not cost the same: an edit sample also carries the before image, so each step takes about twice as long.

| Measured on an RTX 5080 16 GB, 768², rank 16 | Image LoRA (character, style, object) | Edit LoRA (before / after pairs) |
| :--- | :--- | :--- |
| Sequence | image only | ~2,200 tokens: vision block of the before image in the text + its reference latent + the after image |
| Resident blocks (auto) | 28 | 19 |
| Training | ~4.3 s/step | ~8.2 s/step |
| Preview at 1024² | ~17 s | ~24 s (`before \| after`) |
| 1500 steps + 37 previews | ~2 h | ~3 h 40 min |
| Pre-cache | text encoder NF4 14.9 GB | + ~2.4 s per pair for the vision tower and ~0.7 s per pair for the text |

The edit column comes from a 30-pair style run stopped at step 629 (1 h 32 min, already working) and is extrapolated to 1500 steps. The edit sequence is longer because the vision block of the reference rides in the text (~1,000-1,800 rows) and its latent adds as many rows as the image itself; 768² fits on 16 GB with Resident Blocks on 0.

---

### YuE2-3B — song LoRAs (voice AR + phrasing NAR) · ⚠ Experimental / Beta

> [!WARNING]
> **This trainer is experimental and in beta.** The settings below — defaults, "verified starting point", steps, rank and learning rates — are **not final** and should not be taken too seriously: they come from a handful of runs on one dataset. **Check every result by ear and keep adjusting it**; expect the recipe to change.

> [!IMPORTANT]
> **Real tests: the AR LoRA clones the singer's voice; the NAR LoRA does not.** To get an artist's voice, train the **`ar`** stage (or `both`) and load the AR LoRA in ComfyUI. A NAR LoRA alone changes how the codes are rendered, but the voice stays the base model's.

YuE2-3B (m-a-p) is a **Mixture-of-Transformers**: every one of its 28 blocks carries two complete routes — an **AR** causal route that generates the semantic codec tokens, and a **NAR** route that does flow matching on the 64-dim audio latent. This trainer keeps them apart: choose **`ar` (default), `nar`, or `both`** in Training Settings. Each stage exports its own LoRA and only touches its own branch; `both` runs NAR first, reloads the base model from disk, then runs AR.

- **Datasets:** songs (`.wav`, `.mp3`, `.flac`, …) with their lyrics in a `.txt` of the same name. The prepare pass re-encodes to **48 kHz stereo** and slices by silence into ≤30 s clips (`__cNN.wav`); a global `Style prompt` (and the optional `[Tags]`/`[Lyrics]` protocol) shapes every request.
- **Real-audio codes:** m-a-p has not released YuE2's audio-to-code tokenizer, so Pre-Cache uses the community one: MERT-v2-FullSong layer 20 → Mothersuperior's tokenizer head (`v5_30k`) → one semantic code per 40 ms latent frame (`<cache>/_realcodes_<clip>.pt`, ~2.8 GB VRAM, ~1.4 GB downloaded once). It gets about 1 code in 5 exactly right, but rendering those codes with the base NAR keeps the song's voice timbre, harmony and structure.
- **Stage = `nar`** — lyrics and phrasing: it renders the codes into audio. **In real tests it does not clone the voice**: the voice comes from the codes, which the AR writes. It learns the VAE-latent velocity seeing the text prefix **plus the clip's real codes**, the same context ComfyUI gives it, so the LoRA acts where ComfyUI generates. It is exported in ComfyUI's native layout (`diffusion_model.model.layers.N.self_attn.qkv_proj`, `mlp.gate_up_proj`…, q/k/v and gate/up fused losslessly): load it with **Load LoRA (model only)**.
- **Stage = `ar`** (default) — voice identity, vocal timbre, instruments and the sound of the artist. **This is the stage that clones the voice in real tests**: the AR writes the semantic codes, and the voice lives in those codes (cross-entropy on the clips' real codes). This is the stage of the community's artist LoRAs, mixed 50 % with the minted regularizer pack so a small dataset cannot collapse YuE2's token grammar. It memorizes the training songs past ~1500 steps.
- **Stage = `both`** — NAR first, then a fresh base model from disk for AR: two exports, `YuE2_FINAL_NAR_LoRA.safetensors` (ComfyUI layout) + `YuE2_FINAL_AR_LoRA.safetensors` (ComfyUI layout for the CLIP side, `text_encoders.model.layers.N.self_attn.qkv_proj`…). In ComfyUI, load the NAR LoRA on the model and the AR LoRA with **Load LoRA** (clip strength). There is no `_BOTH` file: the two stages load in different places, so they are always two LoRAs.
- **File names:** every LoRA carries its stage. In the output folder: `YuE2_AR_LoRA_step_N` / `YuE2_FINAL_AR_LoRA` and `YuE2_NAR_LoRA_step_N` / `YuE2_FINAL_NAR_LoRA` (older runs named the NAR `YuE2_LoRA_step_N` / `YuE2_FINAL_LoRA`; they are still recognised). **Send to Models** and **Download LoRA** add `_AR` or `_NAR` to your *Final LoRA Filename* (`yue2_lora_<project>_AR.safetensors`), read from the LoRA's own metadata; Send to Models exports the stage selected in *Training Stage*, and with `both` it exports the two files.
- **Previews** render short songs (codes → 32-step midpoint ODE → VAE decoder) as 48 kHz WAVs during training.
- **NF4:** a pre-quantized backbone (`YuE2-3B_NF4`, built with `tools/yue2/5_conversor_YuE2_NF4.py`) loads in ~5 s at 3.1 GB; only the attention+MLP of both branches are quantized — the latent bridges (`llm2vae`/`vae2llm`/`time_embedder`), layernorms, embeddings and heads stay BF16. Without the cache the trainer quantizes the raw model on the fly.

| Starting point (not final) | NAR (lyrics & phrasing) | AR (voice, timbre & sound) |
| :--- | :--- | :--- |
| Rank / Alpha | 16 / 16 | 8 / 8 |
| Learning rate | 3e-4 | 2e-4 |
| Steps | 1200 | 600 |
| VRAM (NF4, 30-32 s clips) | ~8 GB steady, peaks 8.7 GB | pending |

Measured on an RTX 5080 with the Agila dataset (91 clips, rank 16/16, lr 3e-4): the NF4 backbone loads in 3.1 GB and the run holds **~8 GB of VRAM with brief peaks to ~8.7 GB** (preview ODE + VAE decode and checkpoint saves) — everything fits comfortably under 9 GB on a 16 GB card. Loss went 1.18 → 1.08 in 300 steps and → 1.056 by step 1200, dropping slowly and cleanly; exact-step resume reproduced the schedule mid-run (step 301 continues the same warmup/cosine curve).

The NAR loss depends on the clips' latent amplitude (the latent is not normalized, std ≈ 1.07): ~2.3 at the start on short synthetic test clips, ~1.15 on real music (91 clips of a full album, 30–32 s). It falls slowly and cleanly: 1.18 → 1.08 in 300 steps and → 1.056 at 1200 (rank 16/16, lr 3e-4). Training holds **~8 GB of VRAM on a 16 GB card with the NF4 backbone** (brief peaks ~8.7 GB at preview decode and checkpoint save) and runs at ~0.4 s/step with 30 s clips; the BF16 backbone takes ~7.3 GB more of headroom (~1 s/step with 12 s clips). The initial AR CE is well below `ln(32768)` and drops steadily.

---

## ☁️ RunPod

The following upstream cloud template is provided for historical compatibility; it is not an OrkiLab cloud release:

<a href="https://console.runpod.io/deploy?template=lfxvtg5rrb&ref=jbvdshm0"><img src="https://img.shields.io/badge/Deploy%20on-RunPod-673ab7.svg?style=for-the-badge" alt="Deploy on RunPod"></a>

1. Pick a GPU (the template only allows machines with **CUDA 13**). 24 GB or more is comfortable; SDXL and Anima also train on 16 GB. Cheap cards cost around $0.25–0.50 per hour.
2. Keep the 100 GB volume: models, datasets and LoRAs are stored in `/workspace`.
3. Open **Logs → Container** and wait for `Open / Abre: https://<pod>-4990.proxy.runpod.net` (the first start takes a few minutes). Log in with user `loralab` and the password printed just above it, or set `LORALAB_PASSWORD` when deploying to choose your own.
4. Pick a trainer, upload your dataset with **⬆ Upload** (images and captions, or a `.zip`), pre-cache, train and save the result with **⬇ Download LoRA**.
5. **When you finish, Stop and then Terminate the pod.** Closing the browser does not stop billing, and a stopped pod still pays for its volume.

This inherited deployment uses the upstream container and source repository, not the OrkiLab fork. A dedicated OrkiLab cloud deployment is not yet published.

## 🌐 Remote access

The launcher and the trainers are web pages, so you can train from a laptop, a tablet or a phone while the GPU works on another PC. By default they only answer this PC (`127.0.0.1`).

1. On the training PC, click **🌐 Remote access** at the bottom of the launcher.
2. Tick **Allow other devices on the network**, set a **user and password** and, if you need them, other ports (4990 for the launcher, 5000 for the trainers).
3. Restart the launcher. The panel shows the address to open from the other device, e.g. `http://192.168.1.20:4990`.

- The training PC never asks for the password; other devices always do. Without a password, network access is refused.
- **Behind a reverse proxy** that already asks for a login (Authelia, Authentik, Cloudflare Access...), tick **I use my own authentication** to drop the built-in login, and set **Trainer public URL** (e.g. `https://trainer.example.com`) so the launcher links there instead of `host:5000`. Without a proxy with authentication in front, that option leaves the PC open to anyone on the network.
- On Windows, allow Python through the firewall the first time it asks (private networks).
- **Browse** buttons open a dialog on the training PC's screen, so from another device the folder ones switch to the web folder browser, and for files you type the path.
- **⬆ Upload** in the Dataset Manager (or dragging files onto it) sends images, captions or a whole `.zip` from your device to the dataset folder, and **⬇ Download LoRA** under *Send to Models* saves the trained LoRA on your device.
- The settings can only be changed from the training PC and are saved in `settings/network.json` (the password as a hash).
- It is plain HTTP, meant for your home network. **Do not open these ports to the Internet**: to connect from outside, use [Tailscale](https://tailscale.com) or an SSH tunnel (`ssh -L 4990:localhost:4990 -L 5000:localhost:5000 user@training-pc`).

## 🐍 Using your own Python environment

The installers create `venv\` and install everything there. To use your own environment instead (conda, uv...), install `requirements.txt` in it and set **`LORALAB_PYTHON`** to its python before starting; every launcher uses it instead of `venv\`:

```bat
set LORALAB_PYTHON=C:\Users\you\miniconda3\envs\loralab\python.exe
Start_LoRAlab-TrainerStudio.bat
```

```bash
LORALAB_PYTHON=~/miniconda3/envs/loralab/bin/python ./Start_LoRAlab-TrainerStudio.sh
```

It needs Python 3.13, the CUDA 13.0 build of PyTorch (`requirements.txt` takes it from the PyTorch index), diffusers from its main branch and, for MiniMax-H3 clips, ffmpeg on the PATH.

## 📚 Technical notes

Detailed measurements and the reasoning behind each design decision are in `docs\`: [Qwen-Image 2.1](docs/README_QwenImage21.md) · [Krea 2](docs/README_Krea2.md) · [LTX-2.3](docs/README_LTX23.md) · [LTX 2.5](docs/README_LTX25.md) · [MiniMax-H3](docs/README_MiniMaxH3.md) · [Wan 2.2](docs/README_Wan22.md) (VRAM tables, block swap, video and audio datasets, RefMods and every setting) · [Linux](docs/Linux.md).

## 🛠️ Tools for advanced users

`tools\` contains the scripts used to build the NF4 models from the originals (`Run_Conversor_Krea2.bat`, `Run_Conversor_LTX23.bat`, `5_conversor_QwenImage21_NF4.py`, `5_conversor_ZImage_NF4.py`, `5_conversor_Flux1_NF4.py`, `5_conversor_Klein9B_NF4.py`, `5_conversor_Fibo2_NF4.py`) and a `.parquet` dataset extractor for Qwen-Image 2.1 (`6_extract_parquet.py`). They are not needed to train: the trainers download the ready-made NF4 models.

**Before merging changes to the interfaces or servers**, `tools/smoke_test_ui.py` checks every trainer in under a minute: it starts each server and, in a headless Chrome or Edge, does what the **Pre-Cache**, **Start / Resume** and **Save JSON** (while training) buttons do, without launching anything. It fails on a button that never reaches its script, a JavaScript error or a save that does not answer `ok`, and it works on a temporary copy, so your settings are not touched. No extra packages: it needs Chrome, Edge or Chromium installed.

```bash
venv\Scripts\python tools\smoke_test_ui.py                # all trainers, current files (Linux: venv/bin/python tools/smoke_test_ui.py)
venv\Scripts\python tools\smoke_test_ui.py --only sdxl    # one or more trainers, comma-separated
```

## 📁 Structure

```text
OrkiLab-LoRA-TrainerStudio/
├── Start_LoRAlab-TrainerStudio.bat   # Launcher (.sh on Linux)
├── Update_LoRAlab-TrainerStudio.bat  # Updater (.sh on Linux)
├── Install_LoRAlab-TrainerStudio.bat, Install_Triton_SageAtten220.bat (and their .sh)
├── Install_LoRAlab-TrainerStudio_AMD.bat / .sh   # AMD installer (experimental)
├── requirements.txt                  # Dependencies, for your own environment (LORALAB_PYTHON)
├── code/                             # Run_LoRAlab-<Model>.bat / .sh
├── scripts/                          # launcher.py, server_<model>.py, 0_caption / 1_pre_cache / 2_train_lora, remote_access.py, file_transfer.py, i18n.py, lora_options.py, refmod.py, melband/
├── GUI/                              # launcher.html, launcher.json, trainer_ui_<model>.html, i18n.js
│   └── locales/                      # Translations: <language>.json (English is the built-in text)
├── docs/                             # Technical notes per trainer
├── assets/                           # Covers and logos
├── tools/<model>/                    # NF4 converters and dataset tools (tools/all-smi/ on AMD Windows)
├── Example_Dataset/                  # Small example dataset (MiniMax-H3)
├── Models/                           # Downloaded and converted models
├── Outputs/                          # LoRA checkpoints, previews and final LoRAs
├── Cache_Data/                       # Text embeddings and VAE latents
└── settings/                         # Your settings, HF token, network.json and ui.json (created on first use, never uploaded)
```

Models (`Krea-2-NF4`, `LTX23-NF4`, `LTX25-NF4`, `MiniMax-H3-NF4`, `Qwen-Image21-NF4`, `Z-Image_NF4`, `Anima-Base`, `FLUX.1-Dev_NF4`, `FLUX.2-Klein-9B_NF4`, `FLUX.3-Image-Klein_NF4`, `Ideogram4-NF4`, `MOSS-Image-NF4`, `Ming-Image_NF4`, `Fibo2_Dev-NF4`, `Wan22-T2V-A14B-NF4`, `SDXL-Models`, captioners) are created inside `Models/` on first use, and the caches and the LoRA outputs inside `Cache_Data/` and `Outputs/`. Legacy folders in the project root are moved into these folders automatically. A collision keeps both folders and prints a warning, so nothing is overwritten.

---

## 📜 Licenses

The code is released under the **MIT License**. The models keep their own licenses, which also apply to the NF4 versions and to the LoRAs you train — check them before using or sharing results. **Fibo 2.0 is CC BY-NC 4.0: non-commercial use only** (commercial use needs an agreement with BRIA):

| Model | License |
| :--- | :--- |
| Qwen-Image 2.1 (and the Viggle Turbo LoRA) | Qwen Research License — non-commercial |
| Qwen-Image-2512, Qwen-Image-Edit-2511 (and lightx2v's Lightning LoRAs) | Apache 2.0 |
| Krea 2 | Krea 2 Community License |
| LTX-2.3 | LTX-2 Open-Source License |
| LTX-2.5 | LTX-2.x Community License Agreement (free under USD 10 M of annual revenue; LoRAs are derivatives under the same license) |
| MiniMax-H3 | MiniMax-H3 Community License Agreement |
| MiniMax-H3-Image | MiniMax-H3-Image Community License Agreement |
| Wan 2.2 T2V-A14B | Apache 2.0 |
| Z-Image (and the Z-Image-Fun-Lora-Distill preview LoRA) | Apache 2.0 |
| Anima | CircleStone Labs Non-Commercial License (plus the NVIDIA Open Model License for Cosmos). Images you generate can be used commercially |
| FLUX.1 [dev] | FLUX.1 [dev] Non-Commercial License — non-commercial |
| FLUX.2 Klein 9B (and the Klein 9B turbo preview LoRA) | FLUX Non-Commercial License — non-commercial |
| FLUX.3 Image Klein (and NoiseToNova's PDD turbo LoRA) | FLUX Kommunity License (see the model card) |
| MOSS-Image Base and SFT (and darask0's 4-step turbo adapter) | Apache 2.0 |
| MOSS-Image-Edit-HQ armV5 / armV4 LoRAs (akhaliq, downloaded at run time) | Apache-2.0 |
| Moss-Image-Edit LoRA (chinoll, downloaded at run time) | GPL-3.0 (the project's license; no separate license is given for the weights) |
| Boogu-Image-0.1-Edit | Apache 2.0 |
| Ideogram 4 | Ideogram Non-Commercial Model Agreement — non-commercial; LoRAs are model derivatives under the same license |
| SDXL Base 1.0, RealVisXL V5.0 | CreativeML Open RAIL++-M |
| Pony Diffusion V6 XL, Illustrious XL v0.1, NoobAI-XL 1.1 | Fair AI Public License 1.0-SD |
| Juggernaut XI v11 | CC BY-NC-ND 4.0 — non-commercial |
| Qwen3-VL-4B (MiniMax-H3 captioner) | Apache 2.0 |
| InsightFace buffalo_l (optional face likeness, downloaded only after accepting its terms) | Non-commercial research purposes only |

Built with PyTorch, Diffusers, Transformers, PEFT, bitsandbytes, Flask and the Hugging Face Hub.

## 🙏 Contributors

- **[Jonathan Hecl (@jonathanhecl)](https://github.com/jonathanhecl)** — Linux support ([PR #1](https://github.com/AcademiaSD/AcademiaSD_LoRAlab-TrainerStudio/pull/1)). Thank you!
- **[Synergyart (@Synergyart)](https://github.com/Synergyart)** — Training that keeps running after closing the tab, per-file dataset uploads and non-blocking notifications ([PR #10](https://github.com/AcademiaSD/AcademiaSD_LoRAlab-TrainerStudio/pull/10)), the Krea 2 preview fix ([PR #11](https://github.com/AcademiaSD/AcademiaSD_LoRAlab-TrainerStudio/pull/11)), and detailed bug reports such as the missing C compiler in the RunPod image ([#15](https://github.com/AcademiaSD/AcademiaSD_LoRAlab-TrainerStudio/issues/15)). Thank you!
- **[Cappyadams (@Cappyadams)](https://github.com/Cappyadams)** — AMD support: the [guide for AMD GPUs on Windows](https://civitai.com/articles/36293/training-krea-2minimax-h3etc-lora-on-low-vram-low-ram-amd-gpu-windows) the AMD installer is based on, and the first confirmed AMD training on an RX 7800 XT ([#8](https://github.com/AcademiaSD/AcademiaSD_LoRAlab-TrainerStudio/issues/8)). Thank you!

## 🧩 Third-party code and credits

Code adapted or copied from other projects, and the work it builds on:

| Project | Used for | License |
| :--- | :--- | :--- |
| [Fizgig](https://github.com/shootthesound/Fizgig) by [@shootthesound](https://github.com/shootthesound) | MiniMax H3 sigma sampling (`sample_sigmas`) and the video VAE encoder (`MiniMaxH3VideoVAEEncoder`), adapted | Apache-2.0 |
| [ComfyUI](https://github.com/Comfy-Org/ComfyUI) | Origin of the MiniMax H3 video VAE that Fizgig ported; native layer names and LoRA layouts the exports follow | GPL-3.0 |
| [DiffSynth-Studio](https://github.com/modelscope/DiffSynth-Studio) by ModelScope | Boogu Image Edit model, pipeline and training module; `scripts/boogu_diffsynth_train.py` is adapted from its `examples/boogu_image/model_training/train.py` | Apache-2.0 |
| [Diffusers](https://github.com/huggingface/diffusers) | Model classes and pipelines; MiniMax H3 audio positions copied from `build_packed_sequence`; Qwen-Image prompt templates, latent packing and edit sizes from `QwenImagePipeline` / `QwenImageEditPlusPipeline`, followed in `scripts/qwen_image2512_model.py` | Apache-2.0 |
| [Mel-Band-Roformer-Vocal-Model](https://github.com/KimberleyJensen/Mel-Band-Roformer-Vocal-Model) by KimberleyJensen | `scripts/melband/mel_band_roformer.py`, vendored with its source header (vocal separation for MiniMax H3 audio datasets) | not stated |
| [BS-RoFormer](https://github.com/lucidrains/BS-RoFormer) by lucidrains | Architecture the Mel-Band RoFormer code derives from | MIT |
| [librosa](https://github.com/librosa/librosa) | Mel filter bank reimplemented in `scripts/melband/mel_converter.py` | ISC |
| [ai-toolkit](https://github.com/ostris/ai-toolkit) by ostris | Reference for the MiniMax H3 LoRA key layout and the caption text-encoder allowlist | MIT |
| [all-smi](https://github.com/lablup/all-smi) by Lablup | AMD GPU VRAM for the trainers' panel on Windows (`scripts/gpu_stats.py` reads its JSON snapshot; the AMD installer downloads the signed binary) | Apache-2.0 |
| [ADLX](https://github.com/GPUOpen-LibrariesAndSDKs/ADLX) by AMD | AMD GPU VRAM and temperature on Windows (`scripts/gpu_stats.py`, through the `amd-adlx` package the AMD installer installs) | ADLX SDK License |
| [LyCORIS](https://github.com/KohakuBlueleaf/LyCORIS) by KohakuBlueleaf | The LoKr method in `scripts/lora_options.py`: Kronecker factorization, initialization and `lokr_*` key layout (reimplemented for NF4 layers) | Apache-2.0 |
| [rsLoRA](https://arxiv.org/abs/2312.03732) (Kalajdzievski) and [LoRA+](https://arxiv.org/abs/2402.12354) (Hayou, Ghosh, Yu) | The `alpha/√rank` scaling and the separate learning rate for `lora_B` | papers |
| [DoRA](https://arxiv.org/abs/2402.09353) (Liu et al.) | The magnitude / direction decomposition, trained through PEFT's `use_dora` | paper |
| [Diffusers FLUX.1 LoRA trainer](https://github.com/huggingface/diffusers/blob/main/examples/dreambooth/train_dreambooth_lora_flux.py) | FLUX.1 training recipe: velocity target and guidance input, followed in `scripts/2_train_lora_flux1.py` | Apache-2.0 |
| [Diffusers FLUX.3 Klein LoRA trainer](https://github.com/huggingface/diffusers/blob/main/examples/dreambooth/train_dreambooth_lora_flux3_klein.py) | FLUX.3 Klein training recipe: timestep shift, position ids, text window and LoRA targets, followed in `scripts/2_train_lora_flux3klein.py` | Apache-2.0 |
| [MOSS-Image](https://github.com/OpenMOSS/MOSS-Image) by the OpenMOSS Team | The MOSS-Image transformer of `pipeline_moss_image.py`, adapted in `scripts/moss_image_model.py` (NF4 layers, gradient checkpointing); prompt encoding, preview guidance, training noise schedule (technical report) and caption guide | Apache-2.0 |
| [kohya-ss sd-scripts](https://github.com/kohya-ss/sd-scripts) | `ss_*` LoRA metadata convention, SDXL LoRA key format and 75-token caption chunking | Apache-2.0 |
| [InsightFace](https://github.com/deepinsight/insightface) by deepinsight | SCRFD output decoding and ArcFace 5-point face alignment, reimplemented with NumPy and Pillow in `scripts/face_match.py`; its `buffalo_l` models are downloaded on request (non-commercial research only) | MIT (code) |

Models and LoRAs downloaded at run time (not part of this repository): MelBandRoFormer weights by [Kijai](https://huggingface.co/Kijai/MelBandRoFormer_comfy), the Klein 9B turbo preview LoRA by [kalle07](https://huggingface.co/kalle07/FLUX.2-klein-9B-turbo-lora-set), the FLUX.3 Klein PDD turbo LoRA by [NoiseToNova](https://huggingface.co/NoiseToNova/Flux-3-Klein-turbo-pdd-4_8-steps), the Qwen-Image 2.1 turbo LoRA by [Viggle](https://huggingface.co/Viggle/Qwen-Image-2.1-viggle-turbo), the Qwen-Image-2512 and Edit-2511 Lightning LoRAs by [lightx2v](https://huggingface.co/lightx2v/Qwen-Image-2512-Lightning), the MOSS-Image 4-step adapter by [darask0](https://huggingface.co/darask0/MOSS-Image_4-step_adapter_lora) (built on the 8-step adapter by [lodestones](https://huggingface.co/lodestones/MOSS-Image-SFT-8-steps-dmd)), the MOSS-Image-Edit-HQ armV5 and armV4 LoRAs by [akhaliq](https://huggingface.co/akhaliq/MOSS-Image-Edit-HQ), the Moss-Image-Edit LoRA by [chinoll](https://huggingface.co/chinoll/Moss-Image-Edit) (whose reference format, from [ComfyUI-Moss-Image-Edit](https://github.com/Chenkin-x/ComfyUI-Moss-Image-Edit), the trainer reimplements), Z-Image-Fun-Lora-Distill by [Alibaba PAI](https://huggingface.co/alibaba-pai/Z-Image-Fun-Lora-Distill), and the ungated Ideogram 4 NF4 mirror by [Unsloth](https://huggingface.co/unsloth/ideogram-4-nf4-diffusers). Thanks to all of them.

## Community and support

**YouTube** — Coming soon · **X** — Coming soon · **Discord** — Coming soon · **[Ko-fi — Support OrkiLab](https://ko-fi.com/jorgelf)**

Report issues in the [OrkiLab issue tracker](https://github.com/jlopfri921/OrkiLab/issues).

## License and contributors / Licencia y colaboradores

**OrkiLab's original contributions are licensed under Apache License 2.0**, while the **upstream Academia SD LoRAlab core remains MIT**. Original upstream notices are retained and third-party files retain their own terms. See [LICENSING.md](LICENSING.md), [Apache-2.0 text](LICENSE), [upstream MIT text](LICENSES/MIT-ORIGINAL) and [NOTICE](NOTICE).

**Founder and maintainer:** [Jorge López Frías (@jlopfri921)](https://github.com/jlopfri921). See [CONTRIBUTORS.md](CONTRIBUTORS.md) for formal project and upstream credits. The automatic GitHub contributor graph is controlled by commit authorship/email recognition, not the README credits.

## Credits

Maintained by [jlopfri921](https://github.com/jlopfri921). Independent fork of [AcademiaSD LoRAlab Trainer Studio](https://github.com/AcademiaSD/AcademiaSD_LoRAlab-TrainerStudio). Original copyright Academia SD (2026), MIT. All original contributors, third-party credits and model-specific licenses are retained. Historical measurements are inherited, not independently verified by OrkiLab.
