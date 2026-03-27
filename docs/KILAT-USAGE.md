# 🚀 KILAT v0.0.1 - Usage Guide

## 💻 Cara Pakai

### **Mode 1: Default Workspace** (dari config.json)

```bash
py -3.12 kilat.py
```

Akan menggunakan workspace default: `C:\Kodingan`

---

### **Mode 2: Custom Workspace** (CLI argument)

```bash
# Kerja di folder project lain
py -3.12 kilat.py "C:\Users\valdi\Projects\MyProject"

# Atau pakai relative path
py -3.12 kilat.py "..\MyOtherProject"

# Current directory
py -3.12 kilat.py "."
```

---

### **Mode 3: Quick Launcher**

```bash
# Default workspace
kilat.bat

# Custom workspace
kilat.bat "C:\Projects\MyApp"
```

---

## 📁 Workspace Features

KILAT akan **hanya akses file dalam workspace** yang ditentukan:

### **File Operations:**
```python
# Aman - file dalam workspace
write_to_file path="src/main.py" content="..."
read_file filename="config.json"

# Aman - dengan path absolut dalam workspace
write_to_file path="C:\\Projects\\MyApp\\test.py" content="..."

# ⚠️ Warning - file di luar workspace
write_to_file path="C:\\Windows\\system32\\file.sys" content="..."
# MCP Filesystem akan reject (security)
```

### **@Mentions:**
```bash
# Auto-search dalam workspace
@main.py        # Cari main.py di workspace
@src/utils.py   # Path relatif ke workspace
@../other.py    # Path absolut juga OK
```

### **Search:**
```bash
# Search dalam workspace
search_files pattern="def main" include="*.py"
# Hanya cari di workspace yang di-set
```

---

## 🔒 Security

KILAT MCP Filesystem **membatasi akses** ke workspace untuk keamanan:

- ✅ File dalam workspace: **Full access**
- ⚠️ File di luar workspace: **Read-only** (dengan warning)
- ❌ System files: **Blocked** (C:\Windows, dll)

---

## 📊 Examples

### **Example 1: Kerja di Project Python**

```bash
py -3.12 kilat.py "C:\Projects\FlaskApp"

# Di KILAT chat:
💭 Task: @app.py @requirements.txt Create a new route for /api/health
💭 Task: write_to_file path="app.py" content="..."
💭 Task: search_files pattern="@app.route" include="*.py"
```

### **Example 2: Kerja di Godot Project**

```bash
py -3.12 kilat.py "C:\Kodingan\Godot"

# Di KILAT chat:
💭 Task: @project.godot Add new input mappings
💭 Task: @src/player.gd Implement jump mechanics
💭 Task: /mcp start godot
💭 Task: godot_command --run-main
```

### **Example 3: Multiple Projects**

```bash
# Terminal 1
py -3.12 kilat.py "C:\Projects\Backend"

# Terminal 2
py -3.12 kilat.py "C:\Projects\Frontend"

# Terminal 3
py -3.12 kilat.py "C:\Projects\Docs"
```

Setiap instance KILAT **isolated** ke workspace masing-masing!

---

## 🎯 Best Practices

### **Do's:**
```bash
✅ Selalu set workspace yang benar
✅ Pakai @mentions untuk file references
✅ Pakai write_to_file untuk create new files
✅ Pakai search_files untuk codebase exploration
```

### **Don'ts:**
```bash
❌ Jangan akses file system critical (C:\Windows)
❌ Jangan modify files di luar workspace tanpa permission
❌ Jangan commit .bak files (auto-generated backups)
```

---

## 🛠️ Commands Summary

| Command | Description |
|---------|-------------|
| `py -3.12 kilat.py` | Default workspace |
| `py -3.12 kilat.py <path>` | Custom workspace |
| `kilat.bat` | Quick launcher (default) |
| `kilat.bat <path>` | Quick launcher (custom) |

---

## 📝 Configuration

Edit `config.json` untuk set default workspace:

```json
{
  "paths": {
    "workspace": "C:\\Kodingan"  // ← Default workspace
  }
}
```

Atau pakai CLI argument untuk override!

---

**Happy Coding with KILAT! 🔥**
