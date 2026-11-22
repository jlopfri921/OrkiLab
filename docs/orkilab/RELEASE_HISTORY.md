# OrkiLab — Version history and phase ledger (0.1 → 1.0)

This ledger differentiates **features in source**, **development candidates**, **published GitHub prereleases** and **stable releases**. A version heading in a changelog is not proof of a GitHub Release or successful GPU acceptance. Do not infer missing alpha/beta releases retroactively.

## Quick chronology

| Version family | Documented phases / candidates | Delivery focus | Verified publication evidence in this repository | Remaining qualification |
| --- | --- | --- | --- | --- |
| **0.1.0 — Foundation** | `0.1.0-dev` → `0.1.0-rc.1` → `0.1.0-rc.2` | Identity, documentation, safe updater, basic regression/CI | Historical changelog entries; **no verified public release link included in this ledger** | Historical CI/device checks are not independently re-certified here |
| **0.2.0 — Workspace** | `0.2.0-dev.1` → `0.2.0-rc.1` | Projects, local SQLite, dashboard and modern navigation | Historical changelog entries; **no verified public release link included in this ledger** | Trainer smoke test was user-reported; GPU/regression evidence incomplete |
| **0.3.0 — Connect** | Development increments → `0.3.0-rc.1` | ComfyUI Zone, Bridge, generation/history, GPU monitoring | [Published prerelease v0.3.0-rc.1](https://github.com/jlopfri921/OrkiLab-LoRA-TrainerStudio/releases/tag/v0.3.0-rc.1) | Not stable; representative real GPU and workflow matrix |
| **0.4.0 — Dataset** | Incremental development / beta.1 slices → `0.4.0-rc.1` | Dataset Studio, captions, LoRA library, checkpoint management | [Published prerelease v0.4.0-rc.1](https://github.com/jlopfri921/OrkiLab-LoRA-TrainerStudio/releases/tag/v0.4.0-rc.1) | Trainer-specific exports and full data-to-training validation |
| **0.5.0 — Multiview** | `alpha.1` → `alpha.2` → `beta.1` → `beta.2` → `rc.1` and follow-ups | Subjects, angles, photo linkage, synthetic generation, grouped export | [Published prerelease v0.5.0-rc.1](https://github.com/jlopfri921/OrkiLab-LoRA-TrainerStudio/releases/tag/v0.5.0-rc.1) | Stable hardware/workflow/security/rollback gates remain |
| **0.6.0 — Benchmark** | Proposed `alpha.1` → `alpha.2` → `alpha.3` → `beta.1` → `beta.2` → `beta.3` → `rc.1` → stable | Reproducible tests, LoRA/model comparisons, evaluation and reports | **Not published.** Development PR #104 is a draft, not a release | Hardware, automation, evaluation and release gates |

The names **alpha.1**, **beta.1** and similar within the development history describe work phases unless they are explicitly associated with a published GitHub tag. The same distinction applies to the 0.6 plan.

## 0.1.0 — Foundation

| Phase | What changed | Status / evidence |
| --- | --- | --- |
| **0.1.0-dev** | Independent OrkiLab SVG/logo and favicon, launcher title/palette, About panel, preserved third-party credits, MIT licensing; updater made fast-forward-only with protected local data/model weights and documentation/ignore rules | Development snapshot described in [changelog](../../CHANGELOG_ORKILAB.md); runtime validation pending at that stage |
| **0.1.0-rc.1** | Basic regression tests for version/branding/updater and Git update guards; Windows/Linux CI without GPU/model download; explicit `--deps` updates and external Python environment guard; launcher, queue and scripts aligned; acceptance checklist | Release **candidate in source history**, not demonstrated to be a published GitHub release |
| **0.1.0-rc.2** | Original identity on engine covers/README hero, English public README, maintainer attribution, removed promotional links while retaining upstream/model attribution | Historical RC.2 candidate; no independently confirmed stable `0.1.0` |
| **Post-candidate branding follow-up** | Uniform covers across catalogued engines, compatibility aliases for old assets, trainer/Dataset Forge branding and regression checks | Follow-up changes are not automatically part of the earlier immutable RC commits |

**Product result:** a distinct OrkiLab identity and safer foundation, without claiming that training engines were functionally redesigned at 0.1.0.

**Acceptance boundary:** historical change descriptions alone do not certify an installed training GPU workflow or a published stable 0.1.0.

## 0.2.0 — Workspace

| Phase | What changed | Status / evidence |
| --- | --- | --- |
| **0.2.0-dev.1** | Optional modern dashboard, trainer/engine filters, local hardware summary, SQLite project registry, create/archive/restore projects without touching source training files | Workspace preview, with classic entry still preserved |
| **0.2.0-rc.1** | Modern Workspace becomes the sole launcher entry point, including old `/legacy` bookmarks; preview label removed; navigation and documentation aligned; existing trainer engines and compatibility assets retained | Historical release candidate; trainer navigation smoke test user-reported successful; comprehensive regression/GPU validation still outstanding |
| **Transition to 0.3** | Introduced focused Workspace navigation and later ComfyUI Zone as follow-on development | Do **not** attribute the entire later 0.3 ComfyUI feature set to 0.2 |

**Product result:** the project began operating as a coherent local workbench with reusable project metadata rather than only an interface over individual training engines.

**Acceptance boundary:** no stable 0.2.0 release or exhaustive training compatibility should be inferred from the candidate name.

## 0.3.0 — Connect

| Phase | What changed | Status / evidence |
| --- | --- | --- |
| **Development increments** | ComfyUI connection modes, read-only node/model inventory, workflow library and Bridge, Generation Studio, progress and cancellation, generation history, GPU Manager and RAM/VRAM instrumentation | Development entries in the changelog and [roadmap](ROADMAP.md); exact alpha/beta tags are **not** established here |
| **0.3.0-rc.1** | Candidate for ComfyUI connection, safe graph preparation/execution and generation monitoring with a dedicated navigable UI | [Published prerelease](https://github.com/jlopfri921/OrkiLab-LoRA-TrainerStudio/releases/tag/v0.3.0-rc.1), dated 2026-11-21; [acceptance register](RC_0_3_0_READINESS.md) |
| **Deferred / experimental** | LoRA comparison, every custom workflow, full replacement of legacy trainer UI and exhaustive GPU/engine compatibility | Not certified by the 0.3 candidate |

## 0.4.0 — Dataset

| Phase | What changed | Status / evidence |
| --- | --- | --- |
| **Dataset development** | Project image references, quality/duplicate review, Caption Studio edit/history, separate caption ZIP export | Development slices (including beta.1 work), not independently published beta tags |
| **Dataset/integration expansion** | Optional local vision caption suggestions, reviewed batch operations, derived image-and-caption export, selected trainer draft handoff, trained LoRA catalog, ComfyUI checkpoint identification/management | Incremental development in source; no universal trainer adapter guarantee |
| **0.4.0-rc.1** | Consolidated Dataset Studio and curated LoRA candidate, multilingual polish and automated checks | [Published prerelease](https://github.com/jlopfri921/OrkiLab-LoRA-TrainerStudio/releases/tag/v0.4.0-rc.1), dated 2026-11-21; [acceptance register](RC_0_4_0_READINESS.md) |
| **Stable readiness** | Per-engine compatible exports, reproducible split, real GPU full training, rollback and upgrade safety | **Pending:** not automatically satisfied by prerelease publication |

## 0.5.0 — Multiview

| Phase | What changed | Status / evidence |
| --- | --- | --- |
| **Alpha.1 · PR #80** | Image-project subjects, photo/capture references, provenance, persistent metadata, responsive navigation | Merged development phase |
| **Alpha.2 · PR #81** | Twelve-sector angle coverage, missing-view hints, quality/review and image comparison | Merged development phase |
| **Beta.1 · PR #82** | Explicit compatible ComfyUI generation, output review, synthetic lineage | Merged development phase |
| **Beta.2 · PR #83** | Non-destructive deterministic train/validation grouped ZIP | Merged development phase |
| **RC.1 · PRs #84–#85** | Existing project/photo discovery and persisted linkage | Merged RC preparation |
| **RC.1 follow-ups · PRs #86–#99** | Guidance and eight-language UI, local vision orientation, safe input reference staging, curated official workflow templates, branding/docs | Later source refinements; inclusion in a tag must be checked against that tag's actual commit |
| **Published v0.5.0-rc.1** | Current prerelease; see full [0.5 readiness register](RC_0_5_0_READINESS.md) and [Multiview roadmap](MULTIVIEW_0_5_ROADMAP.md) | [Published prerelease](https://github.com/jlopfri921/OrkiLab-LoRA-TrainerStudio/releases/tag/v0.5.0-rc.1), dated 2026-11-22; no stable v0.5.0 yet |

## 0.6.0 — Benchmark (planned/in development)

| Phase | Planned delivery | Gate |
| --- | --- | --- |
| **Alpha.1** | Isolated benchmark persistence, variant protocols and observation schema; later ComfyUI queue adapter | Test state isolation and true recorded metrics |
| **Alpha.2** | Multilingual Benchmark Studio UI and job/history controls | Browser/mobile acceptance |
| **Alpha.3** | Stabilized LoRA strength and checkpoint comparator | Real paired GPU comparison |
| **Beta.1** | Compatible model/checkpoint comparisons | Exact reproducible prompts/seeds and compatibility caveats |
| **Beta.2** | Optional local scoring and quality review, including held-out evaluation | Quality claims labeled as measurements/opinions |
| **Beta.3** | Project and Multiview-aware benchmark | Provenance-preserving and subject-separated evaluation |
| **RC.1** | Exportable reproducible reports and hardware/CI checks | Final exact-SHA validation |
| **Stable** | Release documentation, supported matrix and non-destructive upgrades | All blockers resolved |

See [Benchmark 0.6 roadmap](BENCHMARK_0_6_ROADMAP.md) for the draft implementation scope.

## Beyond 0.6

| Version | Planned focus |
| --- | --- |
| **0.7 Copilot** | Optional Ollama-assisted guidance; explicit user confirmation for changes |
| **0.8 Hub** | Hugging Face/Civitai integrations, licenses, verified downloads and uploads |
| **0.9 Desktop** | Portable/installed desktop deployment and rollback |
| **1.0 Stable** | Documented supported hardware/engine matrix and full regression acceptance |

## Source-of-truth rules

1. **README** introduces the product and links here for the complete chronology.
2. **CHANGELOG_ORKILAB.md** records detailed historical changes and candidate-level notes.
3. **ROADMAP.md** records what is next and acceptance gates, without overwriting history.
4. **RC_*_READINESS.md** records actual test evidence, not assumed passes.
5. A **GitHub release/tag** is the source of truth for public publication. Main-branch additions after a tag are not necessarily included in that tag.
6. Never rename historical dev/RC stages as stable, or invent intermediate alpha/beta tags for 0.1–0.4.
