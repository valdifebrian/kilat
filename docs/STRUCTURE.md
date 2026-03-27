# 📁 KILAT v0.0.2 - Folder Structure

## 🎯 Overview

KILAT menggunakan struktur folder yang **terorganisir dan clean**:
- ✅ **Root folder** hanya berisi `README.md` dan `.gitignore`
- ✅ **Sub-folders** untuk setiap kategori file
- ✅ **Easy to navigate** dan maintain

**Status:** ✅ **PRODUCTION READY**

---

## 📋 Complete Structure

```
C:\Kodingan\KILAT\
│
├── 📄 README.md                       ← Main documentation (ONLY in root!)
├── 📄 .gitignore                      ← Git ignore rules
│
├── 📁 app/                            ← Application files
│   ├── kilat.py                       ← Main application (33 tools)
│   ├── kilat.bat                      ← Quick launcher
│   └── kilat_core/                    ← Core modules
│       ├── tools/
│       │   ├── write_to_file.py       ← File writing with diff preview
│       │   ├── apply_diff.py          ← Unified diff patching
│       │   └── search_files.py        ← Ripgrep-like codebase search
│       └── context/
│           └── mentions.py            ← @mentions system
│
├── 📁 config/                         ← Configuration
│   ├── config.json                    ← Main configuration
│   │   ├── llama_server settings
│   │   ├── agent settings
│   │   ├── modes configuration
│   │   ├── MCP servers config
│   │   └── paths configuration
│   └── requirements.txt               ← Python dependencies
│
├── 📁 mcp/                            ← MCP servers
│   ├── mcp_smart_manager.py           ← MCP Smart Manager (23 tools)
│   └── godot_mcp_server.py            ← Custom Godot MCP server
│
├── 📁 installers/                     ← Installers & uninstallers
│   ├── install-context-menu.bat       ← Context menu installer
│   ├── uninstall-context-menu.bat     ← Context menu uninstaller
│   ├── add-context-menu.reg           ← Registry add file
│   └── remove-context-menu.reg        ← Registry remove file
│
├── 📁 assets/                         ← Assets & icons
│   └── roograph_icon.png              ← AI Robot icon (512x512)
│
├── 📁 docs/                           ← Documentation
│   ├── KILAT-USAGE.md                 ← Complete usage guide
│   ├── CONTEXT-MENU-GUIDE.md          ← Context menu installation guide
│   ├── MCP-SMART-MANAGER.md           ← MCP server documentation
│   └── REBRANDING-COMPLETE.md         ← Rebranding summary
│
├── 📁 data/                           ← Data files
│   └── history/                       ← Chat history (auto-saved)
│       └── chat_history.json
│
├── 📁 sources/                        ← External sources
│   └── Roo-Code-main/                 ← Roo-Code source code (reference)
│       ├── src/
│       ├── packages/
│       └── README.md
│
└── 📁 venv/                           ← Python virtual environment
    ├── Scripts/
    ├── Lib/
    └── include/
```

---

## 🗂️ Folder Descriptions

### **app/** - Application Core
**Purpose:** Main KILAT application and core modules

| File | Purpose | Lines |
|------|---------|-------|
| `kilat.py` | Main CLI application | ~230 |
| `kilat.bat` | Windows batch launcher | ~20 |
| `kilat_core/` | Python package (core modules) | ~600+ |

**Usage:**
```bash
# Run directly
py -3.12 app\kilat.py

# Or use launcher
kilat.bat
```

---

### **config/** - Configuration
**Purpose:** All configuration files

| File | Purpose |
|------|---------|
| `config.json` | Main KILAT configuration |
| `requirements.txt` | Python package dependencies |

**Edit config.json to change:**
- LLM server settings (URL, model, temperature)
- Context length (default: 320K tokens)
- Default workspace path
- MCP servers configuration
- Agent modes (Code/Architect/Ask)

---

### **mcp/** - MCP Servers
**Purpose:** MCP (Model Context Protocol) server implementations

| File | Purpose | Tools |
|------|---------|-------|
| `mcp_smart_manager.py` | MCP Smart Manager | 23 tools |
| `godot_mcp_server.py` | Custom Godot MCP | 8 tools |

**Total MCP Tools:** 31 tools available!

---

### **installers/** - Installation Scripts
**Purpose:** Windows integration installers

| File | Purpose |
|------|---------|
| `install-context-menu.bat` | Add "Run KILAT Here" to right-click menu |
| `uninstall-context-menu.bat` | Remove context menu integration |
| `add-context-menu.reg` | Registry entries to add |
| `remove-context-menu.reg` | Registry entries to remove |

**Usage:**
```bash
# Install context menu
.\installers\install-context-menu.bat

# Uninstall context menu
.\installers\uninstall-context-menu.bat
```

---

### **assets/** - Visual Assets
**Purpose:** Icons and visual assets

| File | Purpose | Size |
|------|---------|------|
| `roograph_icon.png` | AI Robot icon | 512x512 |

**Used in:**
- Windows context menu icon
- Desktop shortcut icon
- Documentation

---

### **docs/** - Documentation
**Purpose:** User guides and documentation

| File | Purpose |
|------|---------|
| `KILAT-USAGE.md` | Complete usage guide with examples |
| `CONTEXT-MENU-GUIDE.md` | Context menu installation & troubleshooting |
| `MCP-SMART-MANAGER.md` | MCP server management guide |
| `REBRANDING-COMPLETE.md` | Rebranding history (RooGraph → KILAT) |

---

### **data/** - Data Files
**Purpose:** Runtime data and user data

| Subfolder | Purpose |
|-----------|---------|
| `history/` | Chat history (auto-saved JSON files) |

**Note:** History files are auto-generated and should NOT be committed to Git.

---

### **sources/** - External Sources
**Purpose:** Third-party source code for reference

| Subfolder | Purpose |
|-----------|---------|
| `Roo-Code-main/` | Roo-Code VS Code extension source (reference) |

**Why kept:** Used as reference for porting features to KILAT Core.

---

### **venv/** - Virtual Environment
**Purpose:** Python virtual environment (isolated dependencies)

**Auto-generated:** Created when you run `pip install -r config\requirements.txt`

**Should NOT be committed to Git** (see `.gitignore`)

---

## 🔒 Files in Root (ONLY 2!)

| File | Purpose |
|------|---------|
| `README.md` | Main documentation |
| `.gitignore` | Git ignore rules |

**That's it!** Clean and professional! 🎯

---

## 📊 Folder Size Estimate

| Folder | Estimated Size | Content |
|--------|----------------|---------|
| `app/` | ~50 KB | Core application |
| `config/` | ~5 KB | Configuration |
| `mcp/` | ~30 KB | MCP servers |
| `installers/` | ~10 KB | Installers |
| `assets/` | ~50 KB | Icons |
| `docs/` | ~100 KB | Documentation |
| `data/` | ~1 KB | User data (grows with usage) |
| `sources/` | ~50 MB | External sources |
| `venv/` | ~500 MB | Python packages |

**Total:** ~550 MB (mostly venv and sources)

---

## 🎯 Benefits of This Structure

| Benefit | Description |
|---------|-------------|
| ✅ **Clean Root** | Only README and .gitignore |
| ✅ **Organized** | Clear separation of concerns |
| ✅ **Maintainable** | Easy to find and update files |
| ✅ **Professional** | Follows industry best practices |
| ✅ **Git-Friendly** | Proper .gitignore, clean commits |
| ✅ **Scalable** | Easy to add new features |

---

## 🚀 Quick Navigation

```bash
# Go to app
cd C:\Kodingan\KILAT\app

# Go to config
cd C:\Kodingan\KILAT\config

# Go to docs
cd C:\Kodingan\KILAT\docs

# Go to installers
cd C:\Kodingan\KILAT\installers
```

---

**Happy Coding with KILAT! 🚀**

**Version:** 0.0.1  
**Last Updated:** March 2026
