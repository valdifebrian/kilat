@echo off
title KILAT Context Menu - Silent Installer
chcp 65001 >nul

echo =====================================================
echo  KILAT v0.0.1 - Silent Context Menu Installer
echo =====================================================
echo.
echo Installing "Run KILAT Here" to right-click menu...
echo.

echo [1/3] Adding registry entries...
regedit /s "add-context-menu.reg"
if errorlevel 1 (
    echo [ERROR] Failed! Please run as Administrator.
    pause
    exit /b 1
)
echo ✅ Registry entries added!

echo.
echo [2/3] Verifying files...
if exist "C:\Kodingan\KILAT\app\kilat.py" (
    echo ✅ App: app\kilat.py
) else (
    echo ❌ App NOT FOUND: app\kilat.py
)

if exist "C:\Kodingan\KILAT\assets\roograph_icon.png" (
    echo ✅ Icon: assets\roograph_icon.png
) else (
    echo ⚠️  Icon NOT FOUND: assets\roograph_icon.png
)

echo.
echo [3/3] Installation complete!
echo.
echo =====================================================
echo  SUCCESS! "Run KILAT Here" added to right-click menu
echo =====================================================
echo.
echo To test:
echo   1. Open Windows Explorer
echo   2. Right-click any folder
echo   3. Select "Run KILAT Here"
echo.
echo 💡 If menu doesn't appear, restart Windows Explorer
echo.
timeout /t 3 /nobreak >nul
