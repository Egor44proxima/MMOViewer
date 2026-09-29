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
echo   MMO Viewer - environment check
echo ============================================
echo.

"%MM%" run -r "%MAMBA_ROOT%" -n mmoviewer python -c "import sys; print('PYTHON_OK'); print(sys.executable); import PySide6; print('PYSIDE6_OK', PySide6.__version__)"

if errorlevel 1 (
    echo.
    echo [ERROR] Environment check failed.
    pause
    exit /b 1
)

echo.
echo ENVIRONMENT_OK
pause
