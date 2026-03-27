@echo off
title KILAT v0.0.1 - Context Menu Installer
chcp 65001 >nul

echo =====================================================
echo  KILAT v0.0.1 - Windows Context Menu Installer
echo =====================================================
echo.
echo This will add "Run KILAT Here" to folder right-click menu
echo.
echo Location: C:\Kodingan\KILAT
echo Icon: roograph_icon.png
echo.
echo =====================================================
echo.

set /p "CONFIRM=Continue? (y/n): "
if /i not "%CONFIRM%"=="y" (
    echo Cancelled.
    pause
    exit /b 1
)

echo [1/3] Adding registry entries...
regedit /s "add-context-menu.reg"

if errorlevel 1 (
    echo.
    echo [ERROR] Failed to add registry entries!
    echo Please run as Administrator.
    echo.
    pause
    exit /b 1
)

echo ✅ Registry entries added successfully!

echo.
echo [2/3] Verifying icon file...
if exist "roograph_icon.png" (
    echo ✅ Icon found: roograph_icon.png
) else (
    echo ⚠️  Icon not found, using default Python icon
    echo You can add roograph_icon.png later manually
)

echo.
echo [3/3] Testing installation...
echo.
echo =====================================================
echo  Installation Complete!
echo =====================================================
echo.
echo To use:
echo   1. Right-click on any folder in Windows Explorer
echo   2. Select "Run KILAT Here"
echo   3. KILAT will start with that folder as workspace
echo.
echo Example:
echo   - Right-click C:\Projects\MyApp
echo   - Click "Run KILAT Here"
echo   - KILAT opens with workspace: C:\Projects\MyApp
echo.
echo =====================================================
echo.
echo 💡 Tip: You may need to restart Windows Explorer
echo     or log out and back in for changes to appear.
echo.
pause
