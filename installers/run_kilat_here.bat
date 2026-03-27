@echo off
:: ============================================================================
:: KILAT - Run Here Launcher
:: Changes to selected directory and runs KILAT interactive mode
:: ============================================================================

setlocal EnableDelayedExpansion

:: Get the directory from Windows Explorer
set "WORKDIR=%~1"

:: If no argument passed, use current directory
if "%WORKDIR%"=="" set "WORKDIR=%CD%"

:: Validate directory exists
if not exist "%WORKDIR%" (
    echo [ERROR] Directory not found: %WORKDIR%
    pause
    exit /b 1
)

:: Change to target directory
cd /d "%WORKDIR%"

:: Find Python 3.12
set "PYTHON_CMD="
where py >nul 2>&1
if %errorlevel% equ 0 (
    set "PYTHON_CMD=py -3.12"
) else (
    where python >nul 2>&1
    if %errorlevel% equ 0 (
        set "PYTHON_CMD=python"
    )
)

if "%PYTHON_CMD%"=="" (
    echo [ERROR] Python 3.12 not found! Please install Python 3.12
    pause
    exit /b 1
)

:: Find kilat.py location (assume it's in parent\app\kilat.py from this batch file)
set "SCRIPT_DIR=%~dp0"
set "KILAT_SCRIPT=%SCRIPT_DIR%..\app\kilat.py"

if not exist "%KILAT_SCRIPT%" (
    echo [ERROR] KILAT script not found: %KILAT_SCRIPT%
    pause
    exit /b 1
)

:: Launch KILAT
echo ============================================================================
echo 🚀 KILAT AI Coding Assistant
echo Working Directory: %WORKDIR%
echo ============================================================================
echo.

%PYTHON_CMD% "%KILAT_SCRIPT%"

:: Keep window open if there was an error
if %errorlevel% neq 0 (
    echo.
    echo [FINISHED] Exit code: %errorlevel%
    pause
)

endlocal
