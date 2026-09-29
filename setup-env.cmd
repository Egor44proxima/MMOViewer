@echo off
setlocal
cd /d "%~dp0"

set "MM=%~dp0tools\micromamba.exe"
set "MAMBA_ROOT=C:\mmo-mamba"

if not exist "%MM%" (
    echo [ERROR] micromamba.exe not found:
    echo %MM%
    echo.
    echo Put micromamba.exe into tools\ and run this script again.
    pause
    exit /b 1
)

echo ============================================
echo   MMO Viewer - environment setup
echo ============================================
echo Environment root: %MAMBA_ROOT%
echo.

"%MM%" create -r "%MAMBA_ROOT%" -y -n mmoviewer -f "%~dp0environment.yml"

if errorlevel 1 (
    echo.
    echo [ERROR] Environment creation failed.
    pause
    exit /b 1
)

echo.
echo Environment created successfully.
echo Run check-env.cmd and then run.cmd
pause
