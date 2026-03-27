# 📍 KILAT Path Configuration Guide

## 🎯 Purpose

Centralized path configuration makes it easy to:
- **Move KILAT** to different folder
- **Update paths** in one place
- **Share config** across scripts

---

## 📁 Configuration Files

### **1. paths.bat** (For Batch Scripts)

**Location:** `config/paths.bat`

**Usage:**
```batch
@echo off
call "%~dp0config\paths.bat"

REM Now you can use all path variables
cd /d "%KILAT_ROOT%"
%KILAT_PYTHON% "%KILAT_MAIN%"
```

**Available Variables:**
```batch
%KILAT_ROOT%           # C:\Kodingan\KILAT
%KILAT_APP%            # C:\Kodingan\KILAT\app
%KILAT_CONFIG%         # C:\Kodingan\KILAT\config
%KILAT_MCP%            # C:\Kodingan\KILAT\mcp
%KILAT_DATA%           # C:\Kodingan\KILAT\data
%KILAT_ASSETS%         # C:\Kodingan\KILAT\assets
%KILAT_PYTHON%         # py -3.12
%KILAT_MAIN%           # C:\Kodingan\KILAT\app\kilat.py
%KILAT_LAUNCHER%       # C:\Kodingan\KILAT\kilat-launcher.bat
```

### **2. paths.json** (For Python Scripts)

**Location:** `config/paths.json`

**Usage:**
```python
import json
from pathlib import Path

# Load paths configuration
PATHS_CONFIG_PATH = Path(__file__).parent.parent / "config" / "paths.json"
with open(PATHS_CONFIG_PATH, "r", encoding="utf-8") as f:
    PATHS = json.load(f)

# Use paths
root = PATHS["root"]  # "C:/Kodingan/KILAT"
app = PATHS["app"]    # "C:/Kodingan/KILAT/app"
```

---

## 🔄 How to Move KILAT

### **Step 1: Move Folder**

```bash
# Example: Move from C:\Kodingan\KILAT to D:\AI\KILAT
xcopy /E /I C:\Kodingan\KILAT D:\AI\KILAT
```

### **Step 2: Update paths.bat**

Edit `D:\AI\KILAT\config\paths.bat`:

```batch
REM OLD
set "KILAT_ROOT=C:\Kodingan\KILAT"

REM NEW
set "KILAT_ROOT=D:\AI\KILAT"
```

### **Step 3: Update paths.json**

Edit `D:\AI\KILAT\config\paths.json`:

```json
{
  "root": "D:/AI/KILAT",
  "app": "D:/AI/KILAT/app",
  "config": "D:/AI/KILAT/config",
  ...
}
```

### **Step 4: Reinstall Context Menu**

```bash
cd D:\AI\KILAT\installers
install-context-menu.bat
```

**Done!** All paths updated! ✅

---

## 📝 Example: Update Single Path

If you only need to change one path (e.g., data directory):

**paths.bat:**
```batch
REM Change data directory to different drive
set "KILAT_DATA=D:\KILAT-Data\history"
```

**paths.json:**
```json
{
  "data": "D:/KILAT-Data/history"
}
```

---

## 🔧 Script Templates

### **Batch Script Template:**

```batch
@echo off
REM Load KILAT paths
call "%~dp0config\paths.bat"

REM Use paths
cd /d "%KILAT_ROOT%"
%KILAT_PYTHON% "%KILAT_MAIN%" %*
```

### **Python Script Template:**

```python
from pathlib import Path
import json

# Load paths
PATHS_CONFIG = Path(__file__).parent.parent / "config" / "paths.json"
PATHS = json.loads(PATHS_CONFIG.read_text(encoding="utf-8"))

# Use paths
root = Path(PATHS["root"])
app = root / "app"
config = root / "config"
```

---

## ✅ Benefits

| Benefit | Description |
|---------|-------------|
| ✅ **Single Source** | All paths in one place |
| ✅ **Easy to Move** | Update 2 files only |
| ✅ **Consistent** | All scripts use same paths |
| ✅ **Maintainable** | Easy to find and update |
| ✅ **Flexible** | Can override per-script if needed |

---

## 🐛 Troubleshooting

### **Problem: "paths.bat not found"**

**Solution:**
```batch
REM Use absolute path
call "C:\Kodingan\KILAT\config\paths.bat"
```

### **Problem: "paths.json not found"**

**Solution:**
Python script will use default paths (relative to script location)

### **Problem: Context menu uses old path**

**Solution:**
```bash
cd C:\New\Path\KILAT\installers
uninstall-context-menu.bat
install-context-menu.bat
```

---

## 📋 Quick Reference

| File | Purpose | Format |
|------|---------|--------|
| `paths.bat` | Batch scripts | Windows batch variables |
| `paths.json` | Python scripts | JSON |
| `config.json` | App configuration | JSON |

---

**Happy Coding! 🚀**

**Version:** 0.0.1  
**Last Updated:** March 2026
