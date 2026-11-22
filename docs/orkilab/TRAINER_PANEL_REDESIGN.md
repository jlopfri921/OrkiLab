# Trainer panel redesign — OrkiLab 0.3 UX foundation

Status: **foundation only**. This change does not yet migrate individual trainer UIs or modify training behavior. Version remains unchanged until release gates pass.

## Target behavior

Every trainer should offer a focused **Essentials** view, collapsed **Advanced settings**, contextual field-level help, and a clear run/status action area, with no forced navigation to legacy controls.

### Essentials (model-aware)
- Model/checkpoint selection and dataset.
- Output name/path or project association.
- Training duration/steps or epochs (where supported), learning rate, rank/alpha (where supported).
- Resolution/frame count/clip duration where relevant to the selected modality.
- GPU/VRAM feasibility warnings and a clear start action.

### Advanced (collapsible by default)
- Optimizers, schedulers, precision, gradient accumulation/checkpointing.
- Cache, offload, memory techniques, specialized LoRA modes.
- Preview generation, checkpoint cadence, metadata, modality-specific options.
- Keep every existing control, underlying field ID, validation, default and event handler. **Never clone controls** to move them: relocate existing DOM nodes while preserving references, or use the existing render lifecycle.

## Reusable opt-in CSS

Shared `assets/orkilab/orkilab-ui.css` now provides:
- `.orki-trainer-layout`: stacked responsive panels.
- `.orki-trainer-panel`: section surface.
- `.orki-trainer-fields`: adaptive two-or-more-column field grid.
- `details.orki-trainer-advanced` plus `.orki-trainer-advanced-body`: accessible collapsible advanced controls.
- `.orki-trainer-actions`: compact sticky run-action area on desktop, normal flow on small screens.

These are **opt-in** styles: nothing changes in a trainer until its markup adopts these classes.

## Pilot migration checklist

1. Select one image LoRA trainer as pilot. Inventory every existing control, DOM ID, handler and hidden dependency before modifying markup.
2. Apply the reusable panel classes to the pilot, preserving original controls; do not reimplement training APIs.
3. Implement translated headings and short help for ambiguous parameters using the existing i18n and contextual-help infrastructure. English fallback is required for missing locale keys.
4. Test expanded/collapsed state while editing and when starting/canceling a job; collapsing must not reset values or block validation.
5. Confirm keyboard navigation, visible focus, labels, errors, screen widths 360/768/1280px, and no overflow or clipped buttons.
6. Run a smoke test with a real training configuration and verify the submitted payload is identical to the legacy panel given identical inputs.
7. Repeat one trainer family at a time (image, video, audio), respecting modality-specific controls; remove legacy entry points only after parity.

## Acceptance gates for actual panel migration

- No parameter is lost, misclassified, or silently changed.
- Essentials and Advanced work in all eight interface languages; untranslated keys receive fallback.
- Narrow displays do not need horizontal scrolling; vertical scrolling is reduced without hiding essential status.
- Start, pause/cancel, validation and saved settings behave as before.
- End-to-end test evidence for each supported trainer family is recorded before claiming the migration complete.

This scoped PR establishes the visual building blocks, **not** the finished trainer redesign or a 0.3.0-rc.1 release.
