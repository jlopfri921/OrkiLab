# Project-aware ComfyUI workflow selection (OrkiLab 0.4)

In **Projects → View checkpoints → Compare in ComfyUI**, OrkiLab selects the project automatically and filters the workflow picker to the project's **base-model family**. It does not assume that an arbitrary LoRA loader, a workflow title containing a model name or a matching LoRA filename proves compatibility.

The server inspects the saved workflow graph: model-loading filenames, distinctive custom loader types, media category and the presence of a standard `LoraLoader` or `LoraLoaderModelOnly`. Workflows are classified as:

- **Candidate:** base-model family and LoRA loader both detected. It remains necessary to validate the actual ComfyUI node schemas, available models and inference.
- **Unverified:** model family missing/ambiguous, multiple model families or unknown trainer family. Excluded by default.
- **Incompatible:** known different model family, non-image workflow or no supported standard LoRA loader. Excluded by default.

Select **Show workflows without verified compatibility** to inspect other workflows and the reasons, but unsupported options cannot be prepared through the checkpoint comparator. The server repeats the compatibility check when preparing checkpoint-generation variants; switching the browser UI cannot bypass it. Normal, non-project LoRA-strength comparison keeps its existing workflow picker unchanged.

**Limitations:** Detection is conservative and may exclude legitimate custom FLUX.3 workflows if they don't expose their model family in a filename or recognizable loader class, or if they use a custom LoRA loader. These require a compatible standard loader or future metadata/adapter support. A candidate is not guaranteed compatible with the installed checkpoint contents. OrkiLab does not automatically copy LoRA files into ComfyUI; the user must install them in the effective ComfyUI LoRA model directory and refresh its model list before comparison.
