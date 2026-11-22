#!/usr/bin/env bash
# AcademiaSD - LoRAlab Trainer Studio Updater (Linux)
# Equivalente Linux de / Linux equivalent of: Update_LoRAlab-TrainerStudio.bat
set -euo pipefail

cd "$(dirname "${BASH_SOURCE[0]}")"

echo "================================================================"
echo "  ORKILAB - LORA TRAINER STUDIO UPDATER"
echo "  [EN] Repository Update Utility"
echo "  [ES] Utilidad de Actualizacion del Repositorio"
echo "================================================================"
echo

# 1. Check Git
if ! command -v git >/dev/null 2>&1; then
    echo "[ERROR] Git is not installed or not available in PATH."
    echo "[ERROR] Git no esta instalado o no esta disponible en el PATH."
    echo
    echo "[EN] Please install Git:"
    echo "[ES] Por favor instala Git:"
    echo "  Ubuntu/Debian: sudo apt update && sudo apt install -y git"
    echo "  Fedora:        sudo dnf install -y git"
    echo "  Arch:          sudo pacman -S --noconfirm git"
    echo "[EN] Or run ./Install_LoRAlab-TrainerStudio.sh, which tries to install it."
    echo "[ES] O ejecuta ./Install_LoRAlab-TrainerStudio.sh, que intenta instalarlo."
    exit 1
fi

# Safe fork update: never rewrite remotes or discard changes.
fail() { echo "[ERROR] Update refused. Check origin, branch, local changes and remote history." >&2; exit 1; }
git rev-parse --is-inside-work-tree >/dev/null 2>&1 || fail
git remote get-url origin >/dev/null 2>&1 || fail
git diff --quiet || fail
git diff --cached --quiet || fail
BRANCH="$(git symbolic-ref --short -q HEAD)" || fail
[ -n "$BRANCH" ] || fail
git fetch origin "$BRANCH" || fail
git merge --ff-only FETCH_HEAD || fail
echo "[OK] Safe fast-forward update / Actualizacion segura."

if [ "${1:-}" != "--deps" ]; then
    echo "[INFO] Code updated. Use --deps to update Python packages explicitly."
    exit 0
fi
if [ -n "${LORALAB_PYTHON:-}" ]; then
    echo "[ERROR] External Python environment. Update its dependencies manually." >&2
    exit 1
fi

# 6. Librerias nuevas o actualizadas de requirements.txt / New or updated libraries from requirements.txt
PY_EXE="${LORALAB_PYTHON:-./venv/bin/python}"
echo
echo "Actualizando librerias de Python... / Updating Python libraries..."
if [ -x "${PY_EXE}" ]; then
    "${PY_EXE}" -m pip install -r requirements.txt
    # pip no reinstala diffusers si solo cambia el commit de la URL: lo hace este script.
    "${PY_EXE}" scripts/sync_pinned.py
else
    echo "[ERROR] No environment: run ./Install_LoRAlab-TrainerStudio.sh" >&2
    exit 1
fi
