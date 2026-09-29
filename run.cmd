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

echo ============================================
echo   MMO Viewer
echo ============================================
echo Project: %CD%
echo Environment root: %MAMBA_ROOT%
echo.

"%MM%" run -r "%MAMBA_ROOT%" -n mmoviewer python "%~dp0launcher.py" %*

if errorlevel 1 (
    echo.
    echo [ERROR] MMO Viewer terminated with an error.
    pause
    exit /b 1
)
