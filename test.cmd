@echo off
setlocal
cd /d "%~dp0"

set "MM=%~dp0tools\micromamba.exe"
set "MAMBA_ROOT=C:\mmo-mamba"

if not exist "%MM%" (
    echo [ERROR] micromamba.exe not found:
    echo %MM%
    pause
    exit /b 1
)

"%MM%" run -r "%MAMBA_ROOT%" -n mmoviewer python "%~dp0run_tests.py"

if errorlevel 1 (
    echo.
    echo [ERROR] Tests failed.
    pause
    exit /b 1
)

pause
