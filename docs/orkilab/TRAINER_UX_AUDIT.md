# Trainer UX consolidation — setting finder pilot

## Scope

The existing staged trainer interface already provides Basic/Expert modes and panel navigation. This change adds an in-place setting finder and a basic-first presentation to the **shared** `orkilab-pilot.js` and stylesheet. No trainer settings, IDs, default values, API calls or training scripts are replaced.

- New users start in **Basic** presentation; an existing saved Basic/Expert choice is respected. Expert controls are never deleted and training parameter values are not modified. The navigation announces how many advanced controls are hidden in the current stage.
- Enter at least two characters to filter existing labeled controls; at most eight matches are displayed.
- Choose a match to switch to its current stage, enable Expert mode temporarily, scroll to and focus the original control.
- The search is client-side and never writes input values or submits a training job.
- A clear empty-results message is displayed when nothing matches; labels are read from the current DOM so changes of UI language remain searchable.
- It works with any trainer whose DOM passes the shared pilot's safety checks; unsupported trainer structures continue to fall back to their original interface.

## Validation

Automated static coverage: `python -m unittest tests.test_trainer_setting_finder tests.test_workspace_navigation`.

Manual test on the installed app is still required, including an actual local restart. Verify:

1. Navigate Dashboard → Projects → Training engines → GPU Manager and use contextual help in every section.
2. Open SDXL from the Workspace. Search `Learning Rate` and `Rank`, select an existing field and confirm it receives focus in Expert mode.
3. Verify first-run Basic mode, restart with a saved Expert preference, switch Basic/Expert and check defaults remain unchanged and submit a *non-running* configuration review; avoid starting training for this UX test.
4. Repeat on a video and image trainer with different options, and at narrow screen widths.
5. Confirm GPU monitoring and training jobs are unaffected.

Do not delete classic views until field-by-field audits, accessible interactions, runtime browser testing, translation checks and backend parity are complete.

## Individual trainer audit — first pass (SDXL / FLUX.1 / Qwen-Image 2.1)

This pass inspects the real HTML control IDs, keeping original forms, input values, event handlers and backend behavior. The shared modern presentation continues to use a safe fallback if panels are unfamiliar.

| Trainer | Identified training controls | Essential (examples) | Additional Expert-only controls | Notes |
| --- | ---: | --- | --- | --- |
| SDXL | 33 IDs in the reviewed prefix families | Steps, learning rate, rank, batch size, pre-cache and previews | Shared scheduler, LoRA variations, precision, accumulation, checkpoint and seed settings | Keeps original SDXL forms |
| FLUX.1 | 39 IDs in the reviewed prefix families | Steps, LR, rank, batch size, **automatic VRAM profile** | Resident blocks, block-swap storage, RAM limit and guidance, on top of shared advanced fields | No VRAM value is modified by switching modes |
| Qwen-Image 2.1 | 37 IDs in the reviewed prefix families | Steps, LR, rank, batch size, pre-cache and turbo toggle | Turbo strength (plus shared Expert controls) | Preserve model-specific options and their IDs |

Counts are HTML ID observations, **not** a claim that all controls have passed live training validation. The next pass should include Krea, Z-Image, other FLUX engines, video and audio engines. The new Expert classification only changes visibility. Required, hidden or conditionally displayed fields must still be checked per trainer in browser before classic views can be removed.

## Complete static HTML audit — 20 trainer interfaces (2026-11-20)

All 20 trainer UI templates were examined on this branch, including the shared pilot script, engine identity and required navigation anchors. The shared pilot continues to fail open to the untouched classic layout when its DOM preconditions are not met.

| Family | Engines | Reviewed model-specific Expert controls |
| --- | --- | --- |
| Core image | SDXL, FLUX.1, FLUX.3 Klein, Klein 9B, Krea 2, Z-Image, Qwen-Image 2.1, Qwen-Image 2512 | FLUX.1 manual GPU block swap; Klein 9B manual VRAM and turbo strength; Krea 2 pre-cache sequence limit and turbo strength; Z-Image/Qwen turbo strength; Qwen 2512 GPU block count |
| Further image | Ideogram 4, MOSS Image, ERNIE, Anima, Boogu, Ming Image, FIBO2 | Ideogram/Boogu/Ming Image/FIBO2 manual block-swap tuning; MOSS/ERNIE/FIBO2 turbo strength; shared optimizer/LoRA controls remain accessible in Expert |
| Video | Wan 2.2, LTX 2.3, LTX 2.5, MiniMax H3 | Manual GPU block swap; turbo strength; LTX 2.5 audio-loss weight and reference downscale; MiniMax H3 manual VRAM budgets, adapter strength and preview strength |
| Audio | YuE 2 | Shared Expert training settings; audio-specific pre-cache and dataset parameters remain visible |

**Basic view deliberately retains** total steps, learning rate, LoRA rank, batch size, automatic VRAM profile, use-turbo toggle, video frame count and LTX audio-training toggle. Per-engine Expert choices are only visual classification; their saved values, backend payload and trainer event handlers are unchanged. Existing controls have not been cloned.

**Verification gate before merging or removing classic:** execute `python -m unittest tests.test_trainer_setting_finder`, inspect each trainer's Basic and Expert state in the Windows browser, check label translations, conditional controls and training submission, then run a representative image/video/audio training smoke test on the actual GPU. The static audits and tests do not count as runtime validation.
