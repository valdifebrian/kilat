@echo off
title KILAT v0.0.1 - Context Menu Re-Installer
chcp 65001 >nul

echo =====================================================
echo  KILAT v0.0.1 - Context Menu Re-Installer
echo =====================================================
echo.
echo This will UPDATE "Run KILAT Here" context menu
echo with the NEW folder structure!
echo.
echo New paths:
echo   - App: C:\Kodingan\KILAT\app\kilat.py
echo   - Icon: C:\Kodingan\KILAT\assets\roograph_icon.png
echo.
echo =====================================================
echo.

set /p "CONFIRM=Continue? (y/n): "
if /i not "%CONFIRM%"=="y" (
    echo Cancelled.
    pause
    exit /b 1
)

echo [1/3] Removing old registry entries...
regedit /s "remove-context-menu.reg"
timeout /t 1 /nobreak >nul

echo [2/3] Adding NEW registry entries...
regedit /s "add-context-menu.reg"

if errorlevel 1 (
    echo.
    echo [ERROR] Failed to add registry entries!
    echo Please run as Administrator.
    echo.
    pause
    exit /b 1
)

echo ✅ Registry entries updated successfully!

echo.
echo [3/3] Verifying files...
if exist "C:\Kodingan\KILAT\app\kilat.py" (
    echo ✅ App found: app\kilat.py
) else (
    echo ❌ App NOT found: app\kilat.py
    echo Please check file location!
)

if exist "C:\Kodingan\KILAT\assets\roograph_icon.png" (
    echo ✅ Icon found: assets\roograph_icon.png
) else (
    echo ⚠️  Icon NOT found: assets\roograph_icon.png
)

echo.
echo =====================================================
echo  Update Complete!
echo =====================================================
echo.
echo To test:
echo   1. Right-click any folder
echo   2. Select "Run KILAT Here"
echo   3. KILAT should start with new structure
echo.
echo 💡 If menu doesn't appear, restart Windows Explorer
echo     or log out and back in.
echo.
pause
