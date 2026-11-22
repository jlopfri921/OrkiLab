# OrkiLab licensing policy / Política de licencias

OrkiLab is a derivative of [AcademiaSD LoRAlab Trainer Studio](https://github.com/AcademiaSD/AcademiaSD_LoRAlab-TrainerStudio). The repository contains material with **more than one applicable license**.

## 1. Original work and upstream core: MIT

The original forked code, files and portions inherited from Academia SD remain governed by their original **MIT** license and copyright notice. The full, unmodified upstream notice is preserved in [LICENSES/MIT-ORIGINAL](LICENSES/MIT-ORIGINAL). Forking, renaming, updating or distributing upstream code does **not** replace the upstream copyright or remove its MIT conditions.

A modified upstream file may include upstream MIT-covered material **and** subsequently authored OrkiLab contributions; preserve both notices where applicable. Apache-2.0 does not retroactively change the license of MIT-origin content.

## 2. Original OrkiLab contributions: Apache License 2.0

**Original source code, documentation, user interfaces, workflow templates and other original contributions authored for the OrkiLab project from 2026 onward** are made available under the **Apache License, Version 2.0**, unless a file, dependency or asset carries a distinct license. The full text is in [LICENSE](LICENSE).

Copyright (c) 2026 Jorge López Frías and OrkiLab contributors, **for their respective original contributions only**.

This attribution does not claim exclusive ownership over the inherited MIT core or over third-party components. To use or redistribute modified files, comply with **all applicable notices and licenses** for the portions they contain.

## 3. Dependencies, models and media

Third-party dependencies, model weights, checkpoints, LoRA adapters, ComfyUI extensions, bundled fonts and artwork retain their **own** license terms. A mention in the README, a workflow integration or an example download does not relicense any such third-party material. Check the corresponding upstream source, bundled notice, or model card before redistribution.

## 4. Identifying provenance

For source developed independently for OrkiLab, prefer this SPDX marker on new files when appropriate:

```text
SPDX-License-Identifier: Apache-2.0
```

For files that preserve material derived from the Academia SD core, **do not** blindly replace an existing MIT header with Apache-2.0. Keep the existing provenance and license notices. Where a particular file has separately identifiable MIT and Apache-2.0 contributions, add precise annotations rather than implying the whole file is exclusively Apache-2.0.

The repository root `LICENSE` specifies the license of original OrkiLab contributions, **not an exclusive blanket license for every byte in the fork**. `LICENSES/MIT-ORIGINAL` remains part of all source distributions that contain inherited upstream code.

## 5. Contributing

By contributing, you represent that you can license your **original contribution** under Apache-2.0, unless a different license is agreed and documented. Existing upstream copyright, third-party author credits and applicable notices must be retained. See [CONTRIBUTORS.md](CONTRIBUTORS.md) for project recognition.

---

## Resumen en español

- **Núcleo heredado del fork de Academia SD:** licencia **MIT**; se conserva el copyright original y la licencia íntegra en `LICENSES/MIT-ORIGINAL`.
- **Desarrollos originales de OrkiLab:** **Apache 2.0**; texto completo en `LICENSE`.
- **Archivos mixtos:** respetar los avisos de ambos titulares y las licencias aplicables a cada parte.
- **Dependencias, modelos y recursos de terceros:** sus licencias originales prevalecen sobre cualquier descripción general de OrkiLab.
- Cambiar el nombre del proyecto, su logo o su README **no cambia** la licencia de las partes heredadas.
