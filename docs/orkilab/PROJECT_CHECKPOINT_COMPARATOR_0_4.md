# Comparing project checkpoints in OrkiLab 0.4

## Purpose

For image projects, OrkiLab discovers intermediate LoRA files saved as `*_step_<number>.safetensors` within the project's dedicated trainer output folder. It does not read checkpoint contents, alter or delete any training artifact, or run ComfyUI merely by listing them.

### Procedure

1. Finish or pause the current training. Checkpoints can be listed during training, but OrkiLab blocks ComfyUI generation while a training process is active.
2. In **Projects**, press **View checkpoints** to see the steps stored for a project, then **Compare in ComfyUI**.
3. Open **ComfyUI Zone → LoRA Comparator** and select **Project checkpoints** instead of **LoRA strengths**.
4. Copy the selected project `.safetensors` files into the LoRA directory used by your ComfyUI installation, normally `ComfyUI/models/loras`. **OrkiLab never copies them automatically.** Refresh the available models in ComfyUI. If ComfyUI uses another model directory, follow its actual configuration.
5. Choose a saved and compatible image workflow. It must contain an editable standard `LoraLoader` or `LoraLoaderModelOnly` node. The base model and LoRA format must be mutually compatible: a FLUX.3 Image Klein LoRA is not necessarily loadable by an unrelated FLUX or SDXL workflow.
6. Prepare the workflow, choose the LoRA loader and project, select **2–6** checkpoints (default suggestions: steps **300, 500, 700 and 1000** when present), confirm, and run the comparison.
7. OrkiLab creates separate one-use API graphs that change **only the selected node's `lora_name`**. The original prompt, negative prompt, random seed, sampler, dimensions, guidance, LoRA strength and all other parameters remain unchanged. Each comparison image is submitted sequentially, displayed alongside the corresponding step and recorded in the existing generation history.

## Safety and limitations

- The filename must both belong to the selected project's output inventory **and** appear in ComfyUI's current list of installable LoRA choices. If it does not, comparison preparation fails with an instruction to copy and refresh the file.
- A matching filename is not proof that the ComfyUI file's contents are identical to the project artifact. This initial version does not hash or automatically synchronize checkpoints.
- LoRA compatibility, image quality, and the selected step's superiority require visual inspection.
- This mode does not modify the training process or provide resume-training guarantees.
- **Stop after current** prevents additional submissions; it does not kill a running ComfyUI job. The existing generation safety gate rejects submissions while training is running.
- When the project has no matching intermediate checkpoints, the inventory shows an empty list.
