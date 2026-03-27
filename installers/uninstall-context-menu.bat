@echo off
title KILAT v0.0.1 - Context Menu Uninstaller
chcp 65001 >nul

echo =====================================================
echo  KILAT v0.0.1 - Context Menu Uninstaller
echo =====================================================
echo.
echo This will remove "Run KILAT Here" from folder right-click menu
echo.
echo =====================================================
echo.

set /p "CONFIRM=Continue? (y/n): "
if /i not "%CONFIRM%"=="y" (
    echo Cancelled.
    pause
    exit /b 1
)

echo [1/2] Removing registry entries...
regedit /s "remove-context-menu.reg"

if errorlevel 1 (
    echo.
    echo [ERROR] Failed to remove registry entries!
    echo Please run as Administrator.
    echo.
    pause
    exit /b 1
)

echo ✅ Registry entries removed successfully!

echo.
echo [2/2] Cleanup complete!
echo.
echo =====================================================
echo  Uninstallation Complete!
echo =====================================================
echo.
echo "Run KILAT Here" has been removed from right-click menu.
echo.
echo You can re-install anytime with: install-context-menu.bat
echo.
pause
