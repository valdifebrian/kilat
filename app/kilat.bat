@echo off
title KILAT v0.0.1 - Quick Launcher
chcp 65001 >nul

echo =====================================================
echo  KILAT v0.0.1 - Quick Launcher
echo =====================================================
echo.

REM Check if workspace argument provided
if "%~1"=="" (
    echo Using default workspace from config.json
    echo.
    py -3.12 kilat.py
) else (
    echo Using workspace: %~1
    echo.
    py -3.12 kilat.py "%~1"
)

pause
