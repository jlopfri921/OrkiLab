# OrkiLab 0.7.0 — Copilot Studio
## Hoja de ruta de producto, arquitectura, desarrollo y aceptación

**Estado:** planificación inicial (C0); funcionalidades NO implementadas en este documento.  
**Fecha:** 2026-11-23  
**Repositorio:** [OrkiLab](https://github.com/jlopfri921/OrkiLab)  
**Rama de trabajo:** `feat/0.7-copilot-studio`  
**Base estable:** [v0.6.0 — Benchmark Studio](https://github.com/jlopfri921/OrkiLab/releases/tag/v0.6.0)  
**Horizonte:** `0.7.0-alpha.1` → `alpha.2` → `alpha.3` → `beta.1` → `beta.2` → `rc1` → `0.7.0`. Las fases son hitos de trabajo; no constituyen tags publicados.

> **Principio rector:** Copilot sugiere, explica y prepara; **la persona decide**. Ninguna respuesta del modelo puede ejecutar entrenamientos, generar imágenes, sobrescribir proyectos, descargar archivos ni modificar configuraciones sin validación y confirmación explícita. Por defecto todo es de solo lectura.

## 1. Visión y alcance

Copilot Studio será un asistente transversal, **local-first**, para comprender y mejorar las tareas ya disponibles en OrkiLab: proyectos, Dataset Studio, configuración y seguimiento de entrenamiento LoRA, ComfyUI y Benchmark Studio. Su primera plataforma de inferencia será **Ollama** local. La disponibilidad o elección de un modelo no debe bloquear las funciones ordinarias de OrkiLab.

### Qué se entrega en 0.7.0

1. Pantalla Copilot integrada en Workspace, compatible con navegación y temas claro/oscuro.
2. Conexión opcional a Ollama, comprobación de salud, selección explícita de modelo y limitaciones de capacidad.
3. Chat contextual y herramientas **acotadas de lectura** con datos de proyecto elegidos por el usuario.
4. Diagnóstico de Dataset (duplicados, tamaños, captions y cobertura según evidencias existentes).
5. Diagnóstico de entrenamiento LoRA (parámetros, logs, memoria estimada y contradicciones), sin promesas de éxito o calidad.
6. Asistencia para preparar/explicar workflows ComfyUI y errores del Bridge, sin garantizar compatibilidad universal.
7. Explicación conservadora de resultados Benchmark, sin declarar un ganador a partir de mediana descriptiva.
8. Propuestas de modificación con **diff, preflight, autorización y auditoría**, inicialmente restringidas a operaciones seguras y reversibles.
9. Persistencia local y separada por proyecto para conversaciones, recomendaciones y decisiones.
10. Pruebas en Windows/Linux, integración real con Ollama/ComfyUI/RTX 3090, protección de datos y accesibilidad básica.

### Fuera de alcance deliberadamente

- Entrenar LLM mediante LoRA/QLoRA o fine-tuning completo (etapa posterior a 1.0.0).
- Descargas/publicaciones de Hugging Face y Civitai: **0.8 Hub**.
- Instaladores, actualizador/portable de producto: **0.9 Desktop**.
- Agentes autónomos que operen sin autorización; ejecución en segundo plano no solicitada.
- Acceso arbitrario a consola, Python, filesystem, Git, red o APIs externas desde instrucciones del modelo.
- Promesas de evaluación científica reproducible o compatibilidad con todos los nodos ComfyUI.
- Dependencia de un proveedor de IA en la nube para el funcionamiento básico.

## 2. Arquitectura prevista

```text
Workspace / Copilot Studio (chat, contexto, evidencias, historial)
   |
   v
Copilot API local — autenticación local y límites de carga
   |
   +--> Gestor de contexto y permisos: proyecto activo + consentimiento
   |      +--> Adaptadores de lectura: Projects / Dataset / Training / ComfyUI / Benchmark
   |
   +--> Orquestador conversacional: Ollama local, timeouts, cancelación, streaming opcional
   |
   +--> Validador de propuestas: esquema, reglas, simulación/diff y capacidad
   |      +--> Confirmación humana separada
   |             +--> Adaptadores de escritura **limitados**, atómicos y auditables
   |
   +--> SQLite local: conversaciones, fuentes, propuestas, decisiones y eventos
```

**Separación de responsabilidades:** el LLM aporta texto y propuestas estructuradas; el código de OrkiLab decide qué datos se exponen, valida cada argumento y ejecuta las herramientas autorizadas. Ningún texto proveniente de un prompt, log, caption, nombre de archivo o workflow será tratado como una orden de sistema.

**Contrato de salida sugerido:** cada recomendación tendrá `summary`, `reasoning_summary` (explicación breve y verificable, no cadena de pensamiento interna), `evidence_refs`, `confidence` cualitativa si procede, `known_unknowns` y `proposed_action` opcional. Las acciones se representarán con un esquema cerrado, idempotency key, permisos concretos y una vista previa de diferencias.

**Estados de una acción:** `proposed → validated → awaiting_confirmation → applied/rejected/expired/failed`. Al cerrar página, caducar la propuesta o cambiar de proyecto, **no** se debe ejecutar nada.

## 3. Fases C0–C11

| Fase | Nombre | Entregables principales | Criterio mínimo de salida |
| --- | --- | --- | --- |
| **C0** | Preparación 0.7 | Documento de alcance, arquitectura/ADR, matriz de riesgos, rama, backlog, compatibilidad de 0.6 | No modificar el binario/versión estable; pruebas de base en verde |
| **C1** | Núcleo Copilot | Página/módulo, rutas, estados vacío/error, controles de habilitación, estilos e i18n base | Navegación y estado desconectado sin Ollama |
| **C2** | Ollama | Detección endpoint local, /api/tags, capacidades reales, modelos, disponibilidad, timeout/cancel | Modelo ausente o servidor caído no bloquea OrkiLab |
| **C3** | Chat contextual | Sesiones por proyecto, recuperación de fuentes autorizadas, respuestas con referencias y límites | No se filtran datos de otro proyecto; chat no escribe |
| **C4** | Dataset | Herramientas read-only de calidad/captions/duplicados; sugerencias no destructivas | No se mueven ni alteran imágenes originales |
| **C5** | Entrenamiento | Lectura de parámetros y logs; recomendaciones justificadas para LoRA/VRAM | No lanza/cambia entrenamiento automáticamente |
| **C6** | ComfyUI | Inspección de grafo/esquema, diagnóstico Bridge y sugerencias de compatibilidad | No reescribe workflow ni envía prompt sin confirmación |
| **C7** | Benchmark | Explicar observaciones, calidad de comparación y datos ausentes | No infiere ranking ni speedup no demostrados |
| **C8** | Acciones supervisadas | Diff, simulación/preflight, confirmación, allowlist, rollback cuando sea posible | Pruebas de denegación, expiración, concurrencia y reintento |
| **C9** | Historial/auditoría | SQLite, evidencias, acciones, exportación y borrado selectivo | Integridad, restauración y separación por proyecto |
| **C10** | Integración/UX | Tema, ocho idiomas, móvil, rendimiento, privacidad, concurrencia Ollama/GPU | Matriz manual y automatizada documentada |
| **C11** | Estabilización | Beta/RC, changelog, release notes, CI Windows/Linux, aceptación real y rollback | Publicación solo tras autorización explícita y SHA verificado |

### Secuencia de entregas

| Candidata | Fases | Resultado esperado |
| --- | --- | --- |
| `0.7.0-alpha.1` | C0–C3 | Shell + Ollama + chat seguro, de solo lectura |
| `0.7.0-alpha.2` | C4–C5 | Dataset y entrenamiento asistidos |
| `0.7.0-alpha.3` | C6–C7 | Diagnóstico ComfyUI y Benchmark |
| `0.7.0-beta.1` | C8 | Acciones confirmadas con auditoría |
| `0.7.0-beta.2` | C9–C10 | Persistencia, idiomas, móvil, privacidad, estabilidad |
| `0.7.0-rc1` | C11 | Congelación de funciones y aceptación |
| `v0.7.0` | C11 | Release estable tras validación y autorización |

**Regla:** cada incremento puede subdividirse en Cx.1, Cx.2, etc. sin crear automáticamente un tag. No prometer fechas ni interpretar pruebas simuladas como validación real de GPU.

## 4. Experiencia de usuario

- Entrada `Copilot Studio` desde el menú principal, con explicación de propósito, requisitos y estado de Ollama.
- Selector de proyecto visible; selección de modelo Ollama y fuente de contexto visible.
- Chat con citas internas/identificadores de evidencia accesibles y separación entre **Dato**, **Inferencia** y **Propuesta**.
- Tarjetas de sugerencias con impacto, advertencias, diff, botón de confirmar y de descartar.
- Indicador visible de actividad, consumo aproximado de recursos cuando exista medición fiable, progreso/cancelación y aviso de modelos descargados por separado.
- Respuestas ante errores comprensibles y recuperables; soporte de ocho idiomas en el shell y textos controlados. El idioma de respuesta del LLM debe ser configurable y no asumirse universalmente disponible.
- No mostrar controles de acción si no existe conexión/capacidad/permiso suficientes; nunca ocultar una ejecución en curso.

## 5. Contrato de seguridad, privacidad y fiabilidad

1. **Local por defecto:** Ollama escuchando en loopback en la configuración normal. Permitir un endpoint de red solo tras advertencia y autorización explícita; no conectar automáticamente servicios externos.
2. **Aislamiento por proyecto:** cada herramienta comprueba el `project_id` desde el servidor; la entrada del modelo no puede sustituirlo.
3. **Mínimo privilegio:** allowlist de adaptadores; lectura por defecto y acciones de escritura concretas/explicables. Sin comandos arbitrarios.
4. **Prompt injection:** logs, captions, prompts de workflow y salidas externas son datos no confiables. Nunca conceden capacidades ni amplían permisos.
5. **Consentimiento:** vista previa del cambio, revalidación al aplicar, confirmación separada, protección contra doble envío y registro de quién autorizó.
6. **Datos sensibles:** redacción de tokens, rutas privadas y posibles datos personales en logs; política de retención y borrado de historial; exportaciones explícitas.
7. **Integridad:** transacciones SQLite, backups y recuperación; no modificar archivos originales de datasets y modelos. Identificar referencias a archivos eliminados sin inventar datos.
8. **Recursos:** evitar competencia silenciosa GPU entre Ollama, ComfyUI y entrenadores; disponibilidad de CPU/GPU dependiente de Ollama y del hardware, no garantizada. El asistente podrá estar desactivado sin afectar a OrkiLab.
9. **Determinismo del control:** pruebas sin LLM real mediante respuestas simuladas, schemas validados y registros de auditoría; el texto generado no es una prueba de exactitud.
10. **Licencias:** código original OrkiLab bajo Apache-2.0, núcleo heredado de Academia SD bajo MIT, dependencias y modelos con sus licencias respectivas.

## 6. Contratos funcionales por área

### Dataset Studio (C4)
- Entradas permitidas: inventario, tamaño, formato, hashes/metadatos existentes, captions e indicadores ya calculados.
- Salidas: lista de incidencias con referencia a archivo, motivo, recomendación y datos desconocidos.
- Prohibido: sobrescribir fotos, cambiar captions o realizar recortes sin validación/confirmación y copia o reversión.

### Entrenamiento LoRA (C5)
- Entradas: configuración visible, perfil de VRAM, historial y logs acotados del entrenamiento seleccionado.
- Salidas: diagnóstico de coherencia y recomendaciones sobre rank/alpha, batch, grad accumulation, steps, LR y resolución **cuando el motor concreto los soporte**.
- No confundir estimación de memoria con medición real; no garantizar calidad ni tiempos.

### ComfyUI (C6)
- Entradas: workflow importado (copia de trabajo), esquema de nodos del ComfyUI conectado, errores de preflight y ejecución.
- Salidas: incompatibilidades exactas cuando puedan deducirse, pasos de reparación, ejemplo de cambio revisable.
- Mantener los problemas conocidos: tipos COMBO/SAMPLER, nodos personalizados, esquema API frente a UI y controles dinámicos V3.
- Nunca auto-iniciar generaciones ni editar la copia original sin permiso explícito.

### Benchmark Studio (C7)
- Entradas: ejecuciones, variantes, metadatos de comparabilidad, históricos, mediciones y faltantes reales.
- Salidas: comparaciones descriptivas con alcance, advertencias, causas de no comparabilidad y propuestas de experimento.
- Prohibido: inferir GPU/cache equivalentes, VRAM por tarea o superioridad estadística sin medición y protocolo justificables.

## 7. Dependencias técnicas y decisiones diferidas

**Dependencias iniciales:** Python/Flask y rutas OrkiLab existentes; almacenamiento SQLite compatible; cliente HTTP local con límites; APIs existentes de proyectos, Dataset, ComfyUI, entrenamiento y Benchmark; Ollama instalado de manera independiente.

**Decisiones que deben quedar fijadas mediante ADR en C0/C1:**
- Conversación SQLite global vs base por proyecto; estrategia de migración compatible.
- Selección del modelo, multimodalidad real y validación de capacidades (no inferir visión por nombre).
- Política de retención de prompts, ficheros y respuestas; exportación y borrado.
- Política de uso de RAM/VRAM y concurrencia: pausar solicitudes del asistente si colisionan con generación/entrenamiento activo.
- Contrato JSON/schema de tool-calling y fallback si un modelo no lo soporta.
- Versión de API local, formatos de error, cancelación y timeouts.
- Opciones futuras: más de un proveedor solo mediante adaptadores explícitos y aceptación independiente.

## 8. Matriz mínima de pruebas y gates

| Identificador | Caso | Gate |
| --- | --- | --- |
| A01 | Arranque con Ollama apagado | Copilot informa, resto de OrkiLab funciona |
| A02 | Detección modelo disponible/no disponible | Sin nombres/capacidades inventadas |
| A03 | Contexto de proyecto A frente a B | Sin filtración cruzada |
| A04 | Entrada maliciosa incrustada en caption/log | No ejecuta instrucciones del contenido |
| A05 | Dataset con duplicados/captions incompletos | Recomendación referenciada y no destructiva |
| A06 | Configuración LoRA inválida | Explicación específica, sin arranque automático |
| A07 | Workflow con nodo personalizado incompatible | Diagnóstico legible, sin mutación ni envío |
| A08 | Benchmark con observaciones incompletas | No hay ranking ni inferencias inválidas |
| A09 | Confirmación de propuesta | Diff y validación previa; acción solo tras consentimiento |
| A10 | Rechazo/cancelación/caducidad de propuesta | Cero cambios |
| A11 | Reinicio/backup/restore de conversaciones | Integridad e historial separados |
| A12 | Modo claro/oscuro, idioma, pantalla estrecha | Navegable y legible |
| A13 | ComfyUI generando mientras Ollama recibe consulta | No existe envío/saturación silenciosa |
| A14 | Fallo de Ollama, timeout, salida de modelo malformada | Error controlado y cancelable |
| A15 | Regresión OrkiLab 0.6.0: E1–E6 | No perder proyectos, ComfyUI, Benchmark ni seguridad |
| A16 | CI Ubuntu/Windows y pruebas sobre SHA exacto | Ambas suites en verde antes de merge/tag |

**Evidencia:** registrar PASS/FAIL/NO PROBADO, commit SHA, configuración Ollama/ComfyUI, modelo seleccionado, hardware y evidencia no sensible. Tests unitarios simulados ≠ aceptación real de Ollama/RTX 3090. Las acciones destructivas no se prueban sobre datos de producción.

## 9. Backlog inicial y definición de terminado de C0

- [x] Crear documento maestro de hoja de ruta 0.7.0.
- [x] Crear rama de desarrollo `feat/0.7-copilot-studio`.
- [ ] Actualizar índice de `docs/orkilab/ROADMAP.md` y referencias generales con el estado real publicado de 0.6.0, tras revisión.
- [ ] Inventariar rutas/adaptadores de lectura y superficies de permisos existentes.
- [ ] Aprobar ADR de almacenamiento, contexto, privacidad, control de concurrencia y tool-calling.
- [ ] Definir contrato de API y esquemas de propuesta.
- [ ] Establecer fixture y tests no-GPU de la base 0.6.0.
- [ ] Abrir PR inicial de C0 y verificar CI.
- [ ] Planificar el primer incremento C1 sin cambiar `VERSION_ORKILAB` en `main`.

**C0 terminado** cuando los documentos, contratos y riesgos estén revisados y el CI de la rama esté en verde. C0 no valida aún funciones de IA ni autoriza un `alpha.1`.

## 10. Condiciones para lanzar v0.7.0 estable

- [ ] Funciones acordadas C0–C10 implementadas y verificadas en PRs integrados.
- [ ] Registro de aceptación C11 con pruebas A01–A16 (incluidas reales y de fallo).
- [ ] Ninguna acción sin consentimiento o fuga de datos entre proyectos.
- [ ] Datos y modelos originales intactos; migración/rollback probado sobre copia aislada.
- [ ] Licencias, README, ayuda, changelog y limitaciones actualizados.
- [ ] CI de Windows y Linux validado en el **SHA exacto de main**.
- [ ] Publicación manual protegida por aprobación expresa, versión y commit; sin mover tags existentes.

## 11. Posición en la hoja de ruta general

| Versión | Objetivo |
| --- | --- |
| **0.6.0** | Benchmark Studio — **estable publicada** el 2026-11-23 |
| **0.7.0** | Copilot Studio — **planificación y desarrollo** |
| **0.8.0** | Model Hub: Hugging Face / Civitai, licencias y transferencias supervisadas |
| **0.9.0** | Desktop: distribución/instaladores, actualización y rollback |
| **1.0.0** | Consolidación y matriz documentada de soporte |
| **Posterior a 1.0.0** | Evaluación de entrenamiento LLM LoRA/QLoRA y fine-tuning |

---

**Documento de planificación.** No representa una implementación existente ni una garantía de calendario. Las decisiones de producto y aprobación de release se tomarán explícitamente por fase.
