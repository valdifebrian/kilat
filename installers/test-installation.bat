@echo off
:: Test Context Menu Installation
echo ============================================================================
echo Testing KILAT Context Menu Installation
echo ============================================================================
echo.

:: Check registry
echo [1/3] Checking registry...
reg query HKEY_CLASSES_ROOT\Directory\Background\shell\KILAT >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Registry key found
) else (
    echo ❌ Registry key NOT found!
    echo.
    echo Run this to install:
    echo   cd C:\Kodingan\KILAT\installers
    echo   reg import add-context-menu.reg
    exit /b 1
)

:: Check batch file
echo [2/3] Checking batch file...
if exist "C:\Kodingan\KILAT\installers\run_kilat_here.bat" (
    echo ✅ Batch file found
) else (
    echo ❌ Batch file NOT found!
    exit /b 1
)

:: Check Python
echo [3/3] Checking Python...
where py >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Python found
) else (
    echo ⚠️  Python not found in PATH
)

echo.
echo ============================================================================
echo ✅ ALL CHECKS PASSED!
echo ============================================================================
echo.
echo Context menu SHOULD appear when you:
echo   1. Open any folder (e.g., C:\Kodingan)
echo   2. Right-click on EMPTY SPACE (not on files/folders)
echo   3. Look for "Run KILAT Here" in the menu
echo.
echo If still not visible:
echo   - Press F5 to refresh Windows Explorer
echo   - Try logging out and back in
echo   - Restart your computer
echo.
pause
