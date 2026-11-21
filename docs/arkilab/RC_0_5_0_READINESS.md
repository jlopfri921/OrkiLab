# OrkiLab 0.5.0-rc.1 — operator acceptance register

**Reported:** 2026-11-21
**Scope:** Multiview Studio 0.5.0-rc.1, PRs #80–#85 merged into `main`
**Evidence type:** seven affirmative checks reported by the operator in ChatGPT on the real Windows workstation; **not** independently captured logs, screenshots, or CI output.
**Hardware declared for generation:** NVIDIA RTX 3090 24 GB, local ComfyUI.
**Decision:** operator functional checklist complete (7/7); final stable-release gates **remain open**.

## Operator-reported acceptance

| Test | Reported result | Scope/limitations |
| --- | --- | --- |
| Saved image project visible | PASS (operator report) | Existing project discoverable in Multiview Studio |
| Existing photographs recovered and linked | PASS (operator report) | Linking Dataset Studio references to Multiview subject |
| Project and images persist after restart | PASS (operator report) | Real application restart |
| Real ComfyUI generation on RTX 3090 | PASS (operator report) | Exact workflow, model, ComfyUI version and output lineage not recorded |
| ZIP export and file integrity | PASS (operator report) | ZIP export checked; independent repeated-byte reproducibility evidence not supplied |
| Imported dataset in a trainer | PASS (operator report) | Exact engine, adapter, training stage and successful training not specified |
| Desktop and mobile layout | PASS (operator report) | Browser/OS, viewport and screenshot evidence not recorded |

## Do not infer from the operator checklist

- The trainer check means an import/handoff was reported, **not** that a complete model training pass, every training engine, or every model combination has been validated.
- Real ComfyUI generation has been reported, but no demonstrated multi-angle fidelity, cancelled job, actual workload measurements or complete model compatibility matrix is recorded.
- The ZIP check does not prove identical-byte exports across repeated runs or every optional synthetic capture case without additional evidence.
- Mobile presentation being checked does not authorize remote/LAN-only generation or export endpoints.
- This record does **not** certify the unresolved 0.4.0 stable criteria or promote previously experimental integrations.

## Remaining release gates

1. Verify current `main` SHA and rerun appropriate GitHub Actions Windows/Linux foundation and release checks on the exact candidate SHA; collect statuses and skipped cases.
2. Record at least one supported ComfyUI workflow/model and the exact trainer/engine and actual depth of dataset handoff/training acceptance. Until named, describe both as *one operator-tested local configuration*, not broadly supported.
3. Review the risk-sensitive cases not explicitly included in 7/7: source preservation/upgrade and rollback, synthetic provenance, permissions/local-only boundaries, cancellation and non-destructive repeat export, and blocking regressions. Use existing CI evidence where applicable; perform on-device tests if the risk remains unverified.
4. Update `VERSION_ARKILAB`, launcher metadata, README, changelog, compatibility/limitations matrix and release notes in a subsequent **release-preparation PR** after candidate agreement; verify cross-file version consistency.
5. Publish a `v0.5.0` tag and stable GitHub Release **only** after the candidate SHA passes release checks and blocking findings are resolved.

## Source changes

- [PR #80](https://github.com/jlopfri921/OrkiLab-LoRA-TrainerStudio/pull/80): alpha.1 + mobile navigation
- [PR #81](https://github.com/jlopfri921/OrkiLab-LoRA-TrainerStudio/pull/81): alpha.2 coverage and review
- [PR #82](https://github.com/jlopfri921/OrkiLab-LoRA-TrainerStudio/pull/82): beta.1 generation and provenance
- [PR #83](https://github.com/jlopfri921/OrkiLab-LoRA-TrainerStudio/pull/83): beta.2 ZIP export
- [PR #84](https://github.com/jlopfri921/OrkiLab-LoRA-TrainerStudio/pull/84): existing project discovery
- [PR #85](https://github.com/jlopfri921/OrkiLab-LoRA-TrainerStudio/pull/85): RC.1 photo recovery and persistence

No stable 0.5.0 release is claimed by this document.
