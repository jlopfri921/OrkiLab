# OrkiLab · Official Multiview workflows

## Qué aporta esta biblioteca a OrkiLab

Esta carpeta es la **biblioteca oficial de plantillas para Multiview Studio**.
Su función no es sustituir ComfyUI, sino facilitar un recorrido seguro entre
fotografías reales de un sujeto, un workflow preparado, una vista solicitada y
una imagen sintética que el usuario pueda revisar y exportar.

**Situación de la versión 0.5.0 RC.1:** están disponibles **tres plantillas
Img2Img básicas de una referencia** para checkpoints compatibles con la
arquitectura estándar de Stable Diffusion (SD1.5/SDXL). Las tres son
adaptaciones del mismo grafo con distinta fuerza de transformación.
Usan nodos básicos, pero la compatibilidad efectiva requiere un checkpoint
instalado y validación contra la versión de ComfyUI en ejecución.

| Plantilla disponible | Fotos | Denoise | Para qué sirve | Qué NO garantiza |
| --- | ---: | ---: | --- | --- |
| **OrkiLab · Multiview · Core Preserve** | 1 | 0,30 | Conservación de rasgos y pequeños retoques | Cambiar realmente el punto de vista |
| **OrkiLab · Multiview · Core Img2Img** | 1 | 0,55 | Equilibrio entre fidelidad y modificación | Recuperar una parte oculta del sujeto |
| **OrkiLab · Multiview · Core Variation** | 1 | 0,72 | Probar cambios de aspecto mayores | Mantener identidad y proporciones exactas |

### Qué workflows faltan: planificación, no descargas disponibles

| Próxima mejora | Estado 0.5.0 RC.1 | Requisitos antes de ofrecerla |
| --- | --- | --- |
| **OrkiLab · Multiview · Qwen-Image 2.1 Edit** | **Pendiente de próximas revisiones** | Adaptar un grafo de edición real; verificar los nodos, encoders, VAE y conexión de la imagen |
| **OrkiLab · Multiview · FLUX.3 Klein Image Edit** | **Pendiente de próximas revisiones** | Adaptar el workflow nativo, comprobar la familia/versión de modelo y entradas de imagen |
| **OrkiLab · Multiview · Multi-Reference (2–4)** | **Pendiente de próximas revisiones** | Demostrar condicionamiento conjunto real; varios LoadImage por sí solos no bastan |
| **OrkiLab · Multiview · Camera-Control** | **Pendiente de próximas revisiones** | Modelo con control de cámara contrastado y pruebas de fidelidad |

Los enlaces mostrados en la interfaz a los ejemplos de **Comfy-Org**
para Qwen y FLUX son **referencias externas de investigación**, no
archivos JSON de OrkiLab listos para importar desde la biblioteca ni
una declaración de compatibilidad con ComfyUI Desktop o Portable.
Los workflows propios para esos modelos aparecerán en el catálogo solo
después de una validación real de sus nodos y salidas.

### Flujo recomendado en la web-app

1. Abre un proyecto de imagen y un sujeto en **Multiview Studio**.
2. Selecciona fotografías reales; la orientación estimada por Ollama es
   cualitativa y **no representa un ángulo medido**.
3. En **Generar vista faltante**, selecciona una carpeta `input` existente
   con **Examinar** o proporciona su ruta manual. Alternativamente, usa la API
   de ComfyUI si el servidor no comparte el mismo sistema de archivos.
4. Confirma **Copiar fotografías seleccionadas**. OrkiLab conserva los
   originales y muestra los nombres de las copias transferidas.
5. Si no aparecen workflows compatibles, despliega la **Biblioteca oficial**
   en esta misma pantalla: puedes descargar el ZIP o importar una de las
   tres plantillas básicas (requieren **una sola foto** y un checkpoint).
6. Prepara el workflow; OrkiLab debe comprobar los nodos `LoadImage`,
   las entradas de texto editables y los parámetros antes de generar.
7. Revisa la vista resultante. Guárdala solo mediante la acción explícita
   como **sintética, pendiente de revisión** y sin inventar mediciones.
8. Exporta el dataset aprobado, con la procedencia real/sintética registrada.

**Desktop/Portable:** la idea es facilitar ambos formatos sin forzar
custom nodes, pero **no afirmar validación universal**. Sus rutas de
`input`, `models` y sus versiones pueden ser distintas. Si no hay
un checkpoint compatible, descargar el ZIP no lo instala automáticamente.

### Criterios para incorporar Qwen o FLUX a la biblioteca oficial

Antes de pasar cada plantilla de *prevista* a *disponible*:
- Obtener un JSON API completo, con conexiones de referencia y prompt reales.
- Especificar el modelo, sus pesos, licencia, VAE y codificadores necesarios.
- Distinguir nodos básicos y terceros, y comprobar versiones de ComfyUI.
- Validar importación, ejecución, cancelación y registro sintético en un
  entorno real; probar Desktop y Portable antes de marcar ambos como compatibles.
- Documentar número de fotografías aceptado, memoria usada y limitaciones
  de coherencia geométrica, sin prometer reconstrucción fotogramétrica.

---

## Compatibility policy: clean ComfyUI Desktop and Windows Portable

Official project-maintained workflows always use the visible name **OrkiLab ·**
followed by the purpose and model family. Do not rename third-party workflows.
They should import in both ComfyUI Desktop and ComfyUI Portable without requiring
OrkiLab-specific ComfyUI custom nodes.

### Level 1 — Core-only baseline (included)

**OrkiLab · Multiview · Core Img2Img**

File: `orkilab-multiview-core-img2img-api.json`

- Uses only core nodes: `LoadImage`, `CheckpointLoaderSimple`,
  `VAEEncode`, two `CLIPTextEncode`, `KSampler`, `VAEDecode`,
  `SaveImage`.
- One reference image. Standard image-to-image conditioning with adjustable
  denoise (initial value 0.55). This **does not guarantee** a viewpoint
  rotation or faithfully create occluded geometry.
- **A compatible checkpoint must already be installed.** Before use, replace
  `REPLACE_WITH_INSTALLED_CHECKPOINT.safetensors` in the loader with its actual
  name from the selected ComfyUI instance; `example.png` is replaced by the
  image selected through OrkiLab. These are deliberate placeholders, not model
  downloads.
- The API-format graph can be imported into OrkiLab's Workflow Library; the
  core node names are shared between Desktop and Portable. ComfyUI installation
  version, model family and runtime schemas are validated again by OrkiLab
  before the job runs. For SDXL/SD1.5-compatible checkpoints; this baseline
  is **not** a drop-in Qwen Image or FLUX editing workflow.
- No LoRA, ControlNet or third-party nodes, no external service required;
  no claim that a fresh ComfyUI install comes with model weights.

### Built-in workflow selector in Multiview Studio (RC.1)

Inside **Generar vista faltante** the official library is available alongside
the workflow selector, and automatically expands when no suitable workflow is
detected. You can:

- Download the offline **OrkiLab-Multiview-Workflows-0.5.0-rc1.zip** directly
  from the running app. It contains three project-authored API JSON graphs,
  this README, and a manifest with SHA-256 hashes and upstream references.
  Internet access is **not required** for these starter templates.
- Copy one photo to the configured ComfyUI input directory, choose one of the
  three included templates and select a checkpoint already installed in the
  running ComfyUI, then click **Import into OrkiLab**. The importer fills the
  actual staged image filename and checkpoint, validates the core-only graph,
  registers it in Workflow Library, and selects it in the generation panel.
  It does **not** launch a generation job.
- Visit the upstream ComfyUI Qwen-Image 2.1 and FLUX.3 Klein example templates
  using their official GitHub links, clearly identified as **external and
  unverified**. Do not expect those visual/template workflows to run through
  OrkiLab's API preparation without a properly compatible converted graph.

The three bundled starter graphs are:

| Official workflow | Denoise | Intended use |
| --- | --- | --- |
| **OrkiLab · Multiview · Core Img2Img** | 0.55 | Balanced starter; not guaranteed camera control |
| **OrkiLab · Multiview · Core Preserve** | 0.30 | More fidelity, less change of viewpoint |
| **OrkiLab · Multiview · Core Variation** | 0.72 | Stronger image changes, more hallucination risk |

**Compatibility caveat:** Core baseline graphs target compatible SD1.5/SDXL
checkpoints with a standard VAE/CLIP loader structure. They are **not** correct
drop-ins for Qwen, FLUX or other model families, even if those model filenames
happen to appear in a checkpoint dropdown. The application validates the
selected workflow again against the installed ComfyUI nodes and models before
generation. Desktop and Portable share basic core nodes, but neither includes
model weights by default.

### Level 2 — Family-specific, pending actual graph validation

| Planned official name | Purpose | Dependencies |
| --- | --- | --- |
| **OrkiLab · Multiview · FLUX.3 Klein Image Edit** | 1-photo directional edit | Appropriate editing checkpoint, matching tokenizer/VAE and built-in nodes supported by installed ComfyUI |
| **OrkiLab · Multiview · Qwen Image 2.1 Image Edit** | 1-photo high-detail edits | Compatible Qwen editing model, encoders, VAE and installed ComfyUI node schema |
| **OrkiLab · Multiview · Qwen Multi-Reference** | 2–4 reference photos | Proven multi-image conditioning graph, not simply disconnected LoadImage nodes |
| **OrkiLab · Multiview · Camera-Control** | Explicit camera motion | A camera-conditioned model/workflow; exact angles only when validated |

**Estas cuatro plantillas siguen pendientes de próximas revisiones; no hay JSONs ejecutables incluidos para ellas.** Each must be tested
with actual models and complete connected nodes on ComfyUI Desktop and Portable
before publishing as "compatible". Do not copy an unknown third-party
workflow to the official library without checking its license.

### Using Multiview from OrkiLab

1. Pick 1–4 photos already linked to the subject.
2. Choose **Copy directly to folder**, enter the full path to ComfyUI's
   `input` folder or use **Browse…** on the computer running OrkiLab.
   Or choose **Upload via API** for non-shared/remote ComfyUI installations.
3. Confirm **Copy selected photos**. OrkiLab hashes each original and copies
   it without overwriting, leaving originals untouched. The exact target
   filenames are displayed.
4. The workflow dropdown shows only *likely compatible* workflows by default.
   It checks for connected image inputs and a text field; this **static check
   is not proof of executable compatibility or fidelity**. Toggle the
   filter to inspect all image workflows.
5. Choose an imported workflow. **Prepare workflow** checks its actual nodes
   and editable LoadImage choices on the currently running ComfyUI. Select
   automatic or manual image-to-node assignments and confirm generation.
6. Inspect any result. Import it as *synthetic, unreviewed* with requested
   viewpoint metadata, not invented numerical angles.

**Notes for a clean install:** Desktop and Portable keep data/model folders
in different places. Never guess an `input` path: choose the one configured
for the *running instance*. The OS folder picker runs on OrkiLab's host PC,
not inside a remote web browser. If ComfyUI runs on another computer or in a
container, use the API transfer method instead. A clean ComfyUI still requires
users to install/select model weights; no package downloads them automatically.

### Release requirements

- Test clean ComfyUI Desktop and clean Portable with current core nodes.
- Verify selected image reaches actual loaded `LoadImage` and output comes from
  that connected branch, not from an unrelated text-to-image path.
- Verify missing checkpoint and missing custom nodes fail with clear messages.
- Verify direct copy and API upload, 1–4 references, repeated copy,
  metadata persistence, cancel, synthetic review and no changes to originals.
- Record versions, dependencies, model licenses and real GPU usage before
  marking a graph as tested.

Model/node installation background:
- https://github.com/Comfy-Org/ComfyUI/blob/master/docs/installation.md
- https://github.com/Comfy-Org/ComfyUI/blob/master/nodes.py
