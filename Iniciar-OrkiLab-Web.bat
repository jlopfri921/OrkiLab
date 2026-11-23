@echo off
setlocal EnableExtensions
title OrkiLab - Iniciar pagina web
cd /d "%~dp0"

rem Launcher oficial: utiliza venv\Scripts\python.exe o LORALAB_PYTHON.
rem El launcher abre la pagina web automaticamente cuando el servidor responde.
if not exist "%~dp0Start_LoRAlab-TrainerStudio.bat" (
    echo [ERROR] No se encuentra Start_LoRAlab-TrainerStudio.bat.
    echo Ejecuta este archivo desde la carpeta principal de OrkiLab.
    pause
    exit /b 1
)

call "%~dp0Start_LoRAlab-TrainerStudio.bat"
exit /b %errorlevel%
