# OrkiLab 0.6.0 — B10.5 acceptance and RC1 release gate

**State: B10.5 accepted on operator report (283 benchmark tests); `0.6.0-rc1` source metadata staged on feature branch; NOT tagged, merged or published.**

Target repo: [jlopfri921/OrkiLab](https://github.com/jlopfri921/OrkiLab)  
Feature branch: `feat/0.6-benchmark-core`  
Review: [PR #104](https://github.com/jlopfri921/OrkiLab/pull/104) — keep **open/unmerged**.  
Baseline: `main` carries stable 0.5.0 metadata; the feature branch now stages `0.6.0-rc1`. Branches remain **diverged** (at initial inspection: 277 feature commits ahead, four main commits behind). The 0.5 stable acceptance file and publication workflow differ and require careful reconciliation, without rewriting history. Actual v0.5.0 GitHub Release status and CI on the 0.6 head still need verification.

## Estado actualizado — 2026-11-23 (validación en hardware pendiente)

**Candidato comprobado:** `4087149b3ea42f762319b8acf0c6339e0c1fac1c`, rama `feat/0.6-benchmark-core`.
La reconciliación con `main` ya está realizada; en la comparación revisada, la rama tenía 0 commits por detrás. La PR #104 sigue abierta y no se ha publicado tag ni GitHub Release.

- [x] [OrkiLab RC validation #45180067863](https://github.com/jlopfri921/OrkiLab/actions/runs/45180067863) — **success** en Windows y Ubuntu (pruebas, sintaxis de JS y metadatos).
- [x] [OrkiLab foundation checks #45180067858](https://github.com/jlopfri921/OrkiLab/actions/runs/45180067858) — **success** en Windows y Ubuntu (regresión completa automatizada).
- [x] Corrección de contraste claro/oscuro `eb45d52` y guardia estática `4087149`.
- [x] Operador respondió `tok` tras solicitarse comprobación del tema, **sin adjuntar capturas, matriz de navegadores ni log local**.
- [ ] Ejecución real en ComfyUI con un único trabajo explícitamente confirmado.
- [ ] Verificación de alcance por proyecto, ausencia de envío automático y persistencia del historial.
- [ ] Copia de seguridad y ensayo de restauración sobre copia independiente.
- [ ] Revisión visual completa, incluidos controles deshabilitados, móvil, iframes e interfaces de entrenamiento.
- [ ] Aprobación explícita de publicación RC1 después de revisar las pruebas.

**Importante:** las referencias históricas a divergencia, CI pendiente o fallos en secciones de 2026-11-22 son registros de aquel momento, no el estado actual. Al crear cualquier nuevo commit de aceptación se deberá verificar el CI de su **SHA exacto**.

### Prueba manual controlada de Benchmark (sin lote)

1. Guardar una copia externa de `settings/orkilab`, bases SQLite de proyectos, dataset y resultados LoRA; no modificar los originales.
2. Comprobar que ComfyUI está conectado y ocioso, y que no hay entrenamientos o generaciones en curso.
3. Abrir `http://127.0.0.1:4990/workspace/comfyui#benchmark` (o entrar desde el menú ComfyUI).
4. Elegir un proyecto de prueba con workflow API compatible y modelos locales presentes; verificar que los proyectos ajenos no se mezclan.
5. Crear o seleccionar un protocolo de comparación; comprobar validación de modelos, semilla y parámetros declarados. No interpretar hashes declarados como archivos verificados.
6. Activar el borrador, preparar **una sola variante y repetición**; revisar que no se envía nada a ComfyUI sin una confirmación adicional.
7. **Solo si el operador desea gastar GPU:** confirmar explícitamente el envío de esa única generación. Vigilar cola/progreso/errores, resultado, historial, vínculo de prompt y memoria GPU; no realizar envíos automáticos posteriores.
8. Inspeccionar el informe, tiempos y diferencias descriptivas sin declarar ganador; comprobar recarga de página y persistencia en el proyecto correcto.
9. Alternar modo claro/oscuro en Benchmark embebido, Dataset, Queue, Projects y un entrenador; revisar texto, fondos, botones, foco, estados deshabilitados y pantalla estrecha.
10. Restaurar una **copia de prueba** en ubicación separada y comprobar que abre sin alterar los datos originales.

Registrar resultado real por paso (PASS/FAIL/NO PROBADO), incidencia, SHA probado y evidencia no sensible. La generación GPU y el ensayo de restauración **no** quedan aprobados por responder simplemente `tok` sin haberlos realizado.

## 0.6 scope and completed engineering

- B1–B9: local Benchmark SQLite observations, project/run lineage, strict local-only/report access, reproducibility declarations, conservative timing/cache diagnostics and historical ComfyUI graph fingerprint inspection.
- B10.1: declaration-only candidate checks.
- B10.2: user-invoked, bounded comparison of literal checkpoint/LoRA options advertised by ComfyUI for supported API graphs.
- B10.3: deliberate run activation, one-variant preparation, explicit user confirmation, existing safe ComfyUI queue/binding handling; **no automatic batch**.
- B10.4: read-only descriptive A/B median differences (B−A); missing values remain unknown; **never ranking or verified speedup**.
- B10.5: conservative, code-generated release checklist plus a **manual** light/dark web theme with persistent local browser preference, visible header toggle and eight locale labels. Main Workspace, Benchmark, Dataset Studio, Queue and pages using the common shell share the preference. Browser/visual validation of every trainer interface remains pending.

**Limitations that must remain visible:** verified full model weight bytes, input-file content and dynamic positive/negative prompt polarity, GPU equivalence, seeds and cold/warm cache are not attested by local histories. Real full inference, representative Desktop/Portable graph compatibility, VRAM-per-job and reliable experimental speed rankings require separate controlled testing. Never label the descriptive B10.4 differences as a benchmark winner. Original upstream MIT core and original OrkiLab Apache-2.0 contributions remain separately attributed; see `LICENSING.md`.

## Main-to-feature reconciliation completed — 2026-11-22

**Merged `main` into `feat/0.6-benchmark-core`** through true two-parent merge commit [`11134e78f9c4`](https://github.com/jlopfri921/OrkiLab/commit/11134e78f9c42b3f3d829d48ef2247afefdefc2c). Verified GitHub comparison now reports **0 behind `main`**. This did **not** merge the feature into `main` and did not create an RC tag or GitHub Release.

Resolved mixed documentation/metadata deliberately: preserved `0.6.0-rc1` on the feature branch while retaining 0.5.0 stable operator H1–H7 signoff, guarded publisher workflow, updated stable-regression guards, historical phase ledger, original upstream MIT license and OrkiLab Apache-2.0 licensing notices. README, changelog and roadmap combine the complete stable-history content from `main` with the B1–B10.5 candidate description.

**Regression evidence:** 288 benchmark tests were accepted by the operator **before** the merge. These must be rerun on the **new exact merge commit**, including `test_release_0_5_stable_guards.py` and the entire application suite. Never transfer a pre-merge test result automatically to the merged commit.

At first CI inspection on exact merge SHA `11134e78f9c42b3f3d829d48ef2247afefdefc2c`, GitHub reported two workflows **in progress**: `OrkiLab foundation checks` (run 45071223625) and `OrkiLab RC validation` (run 45071223618). No passing result can be claimed until both are completed and verified.

```powershell
git remote set-url origin https://github.com/jlopfri921/OrkiLab.git
git switch feat/0.6-benchmark-core
git pull --ff-only
git log -1 --oneline
.\\venv\\Scripts\\python.exe -m unittest discover -s tests -p "test_benchmark*.py" -v
.\\venv\\Scripts\\python.exe -m unittest discover -s tests -p "test_release_0_5_stable_guards.py" -v
.\\venv\\Scripts\\python.exe -m unittest discover -s tests -p "test_*.py" -v
```

The full suite may contain tests requiring dependencies or infrastructure unavailable in the local environment; record any errors rather than assuming a PASS. Only independent acceptance and explicit maintainer authorization can allow the prerelease.

## RC1 staging progress — 2026-11-22

- B10.5 **283 benchmark tests operator-reported PASS** after the operator's `tok`; no independently attached full-suite transcript.
- The source `VERSION_ORKILAB`, `GUI/launcher.json`, README and changelog now label **`0.6.0-rc1` as staged on the feature branch only**. No release tag, publication, installer or PR merge has been created.
- Draft release notes: `.github/RELEASE_0_6_0_RC1_DRAFT.md`.
- **Five new version/license/publication safety tests** in `tests/test_benchmark_rc_metadata.py` mean **288 benchmark tests expected**, pending fresh Windows execution.
- `main` and the feature branch remain **diverged**; 0.5 stable acceptance and version changes must be reconciled before the PR can merge, without dropping B1–B10.5 implementation.
- The status query on the intermediate staging SHA returned no combined commit statuses and no PR-triggered runs; **exact-final-SHA Windows/Linux CI is not yet verified**.
- Staged source metadata is not approval to publish or a substitute for the remaining manual checklist.

## Test evidence classification

- Up to B10.4: **267 tests operator-reported PASS** via the shorthand `tok`, without an attached independent CI transcript for every slice.
- B10.5: **16 additional checks** (7 pure release gates, 1 read-only Flask report, 2 bilingual UI checks and 6 shared light/dark tests), now **283 benchmark tests operator-reported PASS** through `tok`. The operator did not attach the raw rerun transcript in this exchange; no claim of independent CI or real GPU execution from synthetic fixtures.
- Frontend inline JavaScript syntax check can be performed independently. An automated test cannot substitute for a real light/dark responsive browser assessment.

## Required automated checks

From your Windows checkout and virtualenv:

```powershell
git remote -v
git branch --show-current
git pull --ff-only

.\venv\Scripts\python.exe -m unittest discover -s tests -p "test_benchmark_b10_release_gate.py" -v
.\venv\Scripts\python.exe -m unittest discover -s tests -p "test_benchmark_b10_theme.py" -v
.\venv\Scripts\python.exe -m unittest discover -s tests -p "test_benchmark_rc_metadata.py" -v
.\venv\Scripts\python.exe -m unittest discover -s tests -p "test_benchmark_reporting_routes.py" -v
.\venv\Scripts\python.exe -m unittest discover -s tests -p "test_benchmark_workspace_integration.py" -v
.\venv\Scripts\python.exe -m unittest discover -s tests -p "test_benchmark*.py" -v
```

**Expected last suite after RC metadata checks:** `Ran 288 tests ... OK`. Prior 283 were operator-reported PASS; five new checks are pending. If not, retain the exact failing traceback and do not authorize the RC.

Also run the application's **full regression suite** and review actual Windows/Linux CI. These Benchmark-only tests are not enough to certify all existing trainers, datasets, Multiview or the installer. Keep source data and models backed up before accepting any release.

## Manual acceptance — operator checklist

| ID | Acceptance condition | Evidence required | Current status |
| --- | --- | --- | --- |
| B10.5-A | Benchmark 283 automated tests PASS | Operator `tok` (no full console log attached) | **PASS — operator reported; log still requested** |
| B10.5-B | Whole-app regression (Workspace, Queue, trainers, projects, Dataset, Multiview) | terminal logs and functional notes | Pending |
| B10.5-C | Linux/Windows CI at **exact candidate commit** | linked CI run and SHA | Pending |
| B10.5-D | Benchmark standalone and ComfyUI embedded page remain readable and project-scoped | local browser screenshots/observations | Pending |
| B10.5-E | **Light/dark** preference survives refresh/navigation/iframe, mobile responsive, keyboard accessible, both languages and remaining six locales | local browser checks | Pending |
| B10.5-F | A recorded, compatible representative ComfyUI execution and binding on actual GPU **only with explicit operator consent** | local job history, cache and statuses | Pending |
| B10.5-G | No unauthorized automatic generation, project cross-scope reads or mutated original media | review + acceptance | Pending |
| B10.5-H | README, changelog, guides, version metadata, license notices and known limitations reviewed | document review | Pending |
| B10.5-I | Backup/rollback plan accepted for user's persistent SQLite projects and LoRA files | backup and restoration drill | Pending |
| B10.5-J | Maintainer explicitly authorizes `0.6.0-rc1` publication | recorded approval | Pending |

**Light/dark test steps:** Open `http://127.0.0.1:4990/workspace`. Locate the **Claro / Oscuro** header toggle. Switch to light; open Projects, Queue, Dataset, ComfyUI Zone and Benchmark. Verify text/input/hover/focus contrast and table legibility at desktop and mobile widths; refresh and confirm the theme remains light. Check the Benchmark iframe inherits the same preference. Switch to dark and ensure the prior look returns. Check one representative trainer interface and a separate open tab. The theme must be **visual only** and must not reset any training or benchmark data.

**Benchmark tests:** Open `http://127.0.0.1:4990/workspace/comfyui#benchmark`. Select an existing run and inspect **Validación final y publicación (B10.5)**. It must display **Publicación aún no autorizada** regardless of existing result medians. Do not click **Enviar una generación confirmada** unless you intend a genuine GPU job. Do not enable a tag or merge based on a local checklist.

## Deferred or separately scoped

- Workflow-specific repair/error catalogue; custom-node compatibility guarantees.
- Proved cold-cache, model weight attestation, image/input-file equality or comparable speed leaderboard.
- Model-family additions such as LLM QLoRA, fine-tuning, wider GPU scheduling or desktop package features planned for later versions.

## Release decision

**No release tag, GitHub Release, branch merge, installer or 0.6.0-rc1 publication is authorized by this document.** `VERSION_ORKILAB`, GUI launcher metadata and README are now staged as `0.6.0-rc1` on the feature branch only. Next reconcile the stable 0.5 baseline (`main`) with feature development, fix any failing regression, obtain fresh Windows/Linux CI on the exact resulting SHA, review PR #104, complete B–J evidence and explicitly authorize publication. Stable `0.6.0` requires a separate explicit signoff after the RC. Stable `0.6.0` requires a separate explicit signoff after RC observations.
