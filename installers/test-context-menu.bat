@echo off
title KILAT Context Menu Test
chcp 65001 >nul

echo =====================================================
echo  KILAT Context Menu - Test Script
echo =====================================================
echo.
echo Testing if KILAT can be launched from context menu...
echo.

echo Current directory: %CD%
echo.

echo Checking files...
if exist "C:\Kodingan\KILAT\app\kilat.py" (
    echo ✅ kilat.py found
) else (
    echo ❌ kilat.py NOT found
)

if exist "C:\Kodingan\KILAT\config\config.json" (
    echo ✅ config.json found
) else (
    echo ❌ config.json NOT found
)

echo.
echo Testing Python...
py -3.12 --version
if errorlevel 1 (
    echo ❌ Python 3.12 NOT found
    pause
    exit /b 1
)

echo.
echo =====================================================
echo  Test Complete!
echo =====================================================
echo.
echo If all checks passed, context menu should work.
echo.
echo To test manually:
echo   1. Right-click this folder
echo   2. Select "Run KILAT Here"
echo   3. KILAT should start and stay open
echo.
pause
