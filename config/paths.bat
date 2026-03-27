@echo off
REM KILAT - Central Path Configuration
REM Update paths here, all scripts will use these variables

REM KILAT Installation Directory
set "KILAT_ROOT=C:\Kodingan\KILAT"

REM Subdirectories
set "KILAT_APP=%KILAT_ROOT%\app"
set "KILAT_CONFIG=%KILAT_ROOT%\config"
set "KILAT_MCP=%KILAT_ROOT%\kilat_mcp"
set "KILAT_DATA=%KILAT_ROOT%\data"
set "KILAT_DOCS=%KILAT_ROOT%\docs"
set "KILAT_ASSETS=%KILAT_ROOT%\assets"
set "KILAT_INSTALLERS=%KILAT_ROOT%\installers"
set "KILAT_SOURCES=%KILAT_ROOT%\sources"

REM Python Configuration
set "KILAT_PYTHON=py -3.12"
set "KILAT_PYTHON_PATH=C:\Users\valdi\AppData\Local\Programs\Python\Python312\python.exe"

REM Main Application
set "KILAT_MAIN=%KILAT_APP%\kilat.py"
set "KILAT_LAUNCHER=%KILAT_ROOT%\kilat-launcher.bat"

REM Configuration Files
set "KILAT_CONFIG_JSON=%KILAT_CONFIG%\config.json"
set "KILAT_REQUIREMENTS=%KILAT_CONFIG%\requirements.txt"

REM MCP Files
set "KILAT_MCP_MANAGER=%KILAT_MCP%\mcp_smart_manager.py"
set "KILAT_GODOT_MCP=%KILAT_MCP%\godot_mcp_server.py"

REM Assets
set "KILAT_ICON=%KILAT_ASSETS%\roograph_icon.png"

REM Data
set "KILAT_HISTORY=%KILAT_DATA%\history"

REM Documentation
set "KILAT_README=%KILAT_ROOT%\README.md"

REM Context Menu Registry
set "KILAT_CONTEXT_MENU_ADD=%KILAT_INSTALLERS%\add-context-menu-v5.reg"
set "KILAT_CONTEXT_MENU_REMOVE=%KILAT_INSTALLERS%\remove-context-menu.reg"
set "KILAT_CONTEXT_MENU_INSTALL=%KILAT_INSTALLERS%\install-context-menu.bat"
set "KILAT_CONTEXT_MENU_UNINSTALL=%KILAT_INSTALLERS%\uninstall-context-menu.bat"

REM No export needed - variables are automatically available to child scripts
