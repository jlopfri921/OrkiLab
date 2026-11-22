# Video and audio trainer compact-panel acceptance

This checklist applies to the modern UI styling introduced for Wan 2.2, LTX 2.3, LTX 2.5, MiniMax-H3 and YuE2. **CSS integration is not runtime validation.** Do not mark the 0.3 release candidate ready on the basis of these selector changes.

## Common visual checks

- Open each engine in the modern layout at 360 px, 768 px and 1280 px widths.
- Compare Basic and Expert modes: all fields, values, units and context help must remain available; no hidden form control may silently change value.
- Verify no horizontal overflow, truncated dropdowns or inaccessible buttons.
- Inspect the navigation, Dataset, Training, Previews, Export, Logs and Credentials stages.
- Confirm settings save/reload, JSON import/export, job queue behavior and start/cancel flows still operate as before.
- Check that the original/classic view remains unaffected.

## Model-specific safeguards

| Engine | Controls to verify remain visible or reachable |
| --- | --- |
| Wan 2.2 | Frame count, resolution, image/video dataset mode, high/low noise expert selection, preview turbo and VRAM/offload parameters |
| LTX 2.3 | Video frame count, duration/resolution constraints, pre-cache settings, memory/offload and preview settings |
| LTX 2.5 | Video, image and audio mode options; audio loss weight, reference downscale, duration and VRAM controls |
| MiniMax-H3 | Image-vs-video mode selection, audio options, manual VRAM budget, adapter strength and RefMod panel |
| YuE2-3B | Music/voice modality settings, duration/clip controls, caching and audio previews |

## Regression requirements

Record screenshots for each width and mode, a saved configuration before and after the CSS change, and (for each engine accepted) a local training or pre-cache smoke run with GPU/CPU telemetry. This work only changes CSS, so any unexpectedly hidden control is a release blocker. Keep the project version unchanged pending full 0.3 RC acceptance.
