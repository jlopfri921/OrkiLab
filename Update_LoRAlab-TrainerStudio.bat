@echo off
setlocal EnableExtensions EnableDelayedExpansion

title OrkiLab - LoRA Trainer Studio Updater
color 0B

cd /d "%~dp0"

echo ================================================================
echo   ORKILAB - LORA TRAINER STUDIO UPDATER
echo   [EN] Repository Update Utility
echo   [ES] Utilidad de Actualizacion del Repositorio
echo ================================================================
echo.

rem 1. Check Git
where git >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Git is not installed or not available in PATH.
    echo [ERROR] Git no esta instalado o no esta disponible en el PATH.
    echo.
    echo [EN] Please install Git from https://git-scm.com/
    echo [ES] Por favor instala Git desde https://git-scm.com/
    echo [EN] Or run Install_LoRAlab-TrainerStudio.bat, which installs it.
    echo [ES] O ejecuta Install_LoRAlab-TrainerStudio.bat, que lo instala.
    echo.
    pause
    exit /b 1
)

rem Safe fork update: never rewrite remotes or discard changes.
git rev-parse --is-inside-work-tree >nul 2>&1 || goto SAFE_FAIL
git remote get-url origin >nul 2>&1 || goto SAFE_FAIL
git diff --quiet || goto SAFE_FAIL
git diff --cached --quiet || goto SAFE_FAIL
set "BRANCH="
for /f "delims=" %%b in ('git symbolic-ref --short -q HEAD 2^>nul') do set "BRANCH=%%b"
if not defined BRANCH goto SAFE_FAIL
git fetch origin "!BRANCH!" || goto SAFE_FAIL
git merge --ff-only FETCH_HEAD || goto SAFE_FAIL
echo [OK] Safe fast-forward update / Actualizacion segura.
goto SAFE_DONE
:SAFE_FAIL
echo [ERROR] Update refused. Check origin, branch, local changes and remote history.
echo [ERROR] Actualizacion rechazada. Revisa origin, rama y cambios locales.
pause
exit /b 1
:SAFE_DONE

if /I not "%~1"=="--deps" (
    echo [INFO] Code updated. Run this updater with --deps to update Python packages explicitly.
    exit /b 0
)

rem 6. Librerias nuevas o actualizadas de requirements.txt / New or updated libraries from requirements.txt
echo Actualizando librerias de Python... / Updating Python libraries...
set "PY_EXE=%~dp0venv\Scripts\python.exe"
if defined LORALAB_PYTHON (
    echo [ERROR] External Python environment detected. Update its dependencies manually.
    exit /b 1
)
if exist "!PY_EXE!" (
    "!PY_EXE!" -m pip install -r "%~dp0requirements.txt"
    if errorlevel 1 exit /b 1
    rem AMD: amd-adlx lee la VRAM de toda la GPU / AMD: amd-adlx reads the VRAM of the whole GPU
    "!PY_EXE!" -c "import sys, importlib.metadata as m; sys.exit(0 if 'rocm' in m.version('torch') else 1)" >nul 2>&1 && "!PY_EXE!" -m pip install -q amd-adlx
    rem pip no reinstala diffusers si solo cambia el commit de la URL: lo hace este script.
    "!PY_EXE!" "%~dp0scripts\sync_pinned.py"
    if errorlevel 1 exit /b 1
) else (
    echo [ERROR] No environment: run Install_LoRAlab-TrainerStudio.bat
    exit /b 1
)
echo.
pause
