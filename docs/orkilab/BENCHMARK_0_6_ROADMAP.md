# OrkiLab 0.6.0 — Benchmark Studio delivery plan

**Status:** alpha.1 first isolated persistence slice on feature branch; **not released or integrated into Workspace**. The documented 0.5.0 stable acceptance gates remain independent and must be completed before claiming a stable 0.6.0.

## Goal and boundaries

Benchmark a model/LoRA combination with reproducible prompt, seeds, workflow, weights and recorded observations; distinguish raw measurements from qualitative judgments. A useful benchmark must preserve the precise execution protocol and make clear when model-family parameters cannot be compared directly. Baseline: [OrkiLab roadmap](ROADMAP.md).

## Alpha.1 — isolated engine foundation

- `scripts/benchmark_store.py`: local SQLite registry for project-linked benchmark runs, variants and immutable observations.
- One canonical JSON representation per protocol and variant configuration. Inputs record model/workflow details **only when supplied by a caller**.
- Explicit lifecycle: draft → running → completed/failed/cancelled, or draft → cancelled. A run must have a variant to start.
- Each variant/repetition pair records at most one completed, cancelled or failed observation. Seed, duration (milliseconds), peak GPU VRAM (bytes), SHA-256 of output and error text are optional, never invented.
- Reports expose raw stored observations as JSON-like dictionaries. SQLite foreign keys prevent attaching observations to another run.
- No checkpoint/LoRA/source image deletion or mutation. No model download, GPU scheduling, ComfyUI submission, implicit resumption, benchmark scoring, API route or UI is provided by this slice.
- This store is **not a web endpoint**: authorization, project ownership, local-only restrictions and input-size limits must be enforced in the later HTTP integration.

### Acceptance tests

Run `python -m unittest discover -s tests -p 'test_benchmark_store.py'` from repository root. Tests cover persisted reopening, lifecycle rules, project/run isolation, unique repetitions and validation of numeric/hash inputs. CI and actual Windows/Linux results must be recorded before describing alpha.1 as validated.

## Remaining 0.6 sequence

| Milestone | Concrete deliverable | Gate |
| --- | --- | --- |
| alpha.1 next | Explicit ComfyUI adapter, bounded queue integration, best-effort cancellation, safe preflight and project authorization | Mock queue tests + on-device smoke |
| alpha.2 | Multilingual Benchmark Studio, run creation, status and search | UI/browser + eight locales |
| alpha.3 | Stabilize LoRA Comparator and compare strengths, checkpoints and baseline | Real two-variant RTX 3090 workflow |
| beta.1 | Same-protocol model/checkpoint comparisons, incompatibility warnings | Controlled prompts/seeds + compatible family |
| beta.2 | Optional local evaluation, raw metrics, manual scoring, no universal quality claim | Held-out evaluation and reproducible report |
| beta.3 | Project/Multiview evaluation, provenance-aware grouping | No leakage across subjects; no fake pose claims |
| rc.1 | Reports, export, GPU/Windows/Linux and upgrade acceptance | Evidence on exact release SHA |
| stable | Changelog, supported matrix, signed-off release blockers, tag and GitHub release | No outstanding release blocker |

## Reproducibility contract

A record stores the values actually used, not just user-selected defaults. Later adapters must capture the final prepared API graph or its digest, checkpoint/LoRA identifiers and hashes where available, run-time seeds and output hashes. Use identical prompt/seed/resolution where meaningful; distinguish hardware/environment differences and separate wall-clock latency from ComfyUI processing time. Keep the held-out evaluation set isolated from training data and separate measured numeric metrics from vision-model opinions.

## Deferred

Full conversational Ollama Copilot belongs to 0.7; Hugging Face/Civitai Hub to 0.8; desktop packaging to 0.9. Advanced video and audio quality benchmarking is a separate later compatibility effort, not promised by 0.6 alpha.1.
