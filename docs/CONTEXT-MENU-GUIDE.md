# 🖱️ KILAT v0.0.2 - Windows Context Menu Integration

## 🎯 Fitur: "Run KILAT Here"

Klik kanan folder mana saja → Pilih **"Run KILAT Here"** → KILAT otomatis buka dengan folder tersebut sebagai workspace!

**Status:** ✅ **PRODUCTION READY**

---

## 📦 Installation

### **Step 1: Run Installer**

```bash
cd C:\Kodingan\KILAT\installers
install-context-menu.bat
```

### **Step 2: Confirm**

- Ketik `y` dan tekan Enter
- Registry entries akan ditambahkan
- Tunggu konfirmasi "Installation Complete!"

### **Step 3: Test**

1. Buka **Windows Explorer**
2. **Right-click** pada folder mana saja (contoh: `C:\Projects\MyApp`)
3. Pilih **"Run KILAT Here"** dari menu
4. KILAT akan start dengan workspace: `C:\Projects\MyApp`

---

## 🔧 Updated Paths (v0.0.1)

**New folder structure requires updated paths!**

| Component | Old Path | New Path |
|-----------|----------|----------|
| **App** | `kilat.py` | `app\kilat.py` ✅ |
| **Icon** | `roograph_icon.png` | `assets\roograph_icon.png` ✅ |
| **Installer** | `install-context-menu.bat` | `installers\install-context-menu.bat` ✅ |

**✅ All paths updated in registry files!**

---

## 🖼️ Screenshot

```
📁 C:\Projects\MyApp
  ├── src/
  ├── tests/
  └── README.md

Right-click pada folder "MyApp":
┌────────────────────────────┐
│ 📂 Open                    │
│ 📂 Open in new window      │
│ ...                        │
│ 🚀 Run KILAT Here   ← NEW! │
│ ...                        │
│ Properties                 │
└────────────────────────────┘
```

---

## 🎨 Icon

Default: **AI Robot Icon** (`roograph_icon.png`)

Jika icon tidak muncul:
2. Atau edit registry manual dengan icon favorit Anda

---

## 🔧 Manual Installation (Advanced)

Jika batch file tidak work, bisa manual via Registry Editor:

### **Step 1: Open Registry Editor**

```
Win + R → regedit → Enter
```

### **Step 2: Navigate to**

```
HKEY_CLASSES_ROOT\Directory\shell\
```

### **Step 3: Create New Key**

- Right-click `shell` → New → Key
- Name: `KILAT`

### **Step 4: Set Default Value**

- Double-click `(Default)` in right pane
- Value: `Run KILAT Here`

### **Step 5: Add Icon (Optional)**

- Right-click `KILAT` → New → String Value
- Name: `Icon`

### **Step 6: Create Command Key**

- Right-click `KILAT` → New → Key
- Name: `command`

### **Step 7: Set Command**

- Double-click `(Default)` in right pane
- Value:
```
```

---

## 🗑️ Uninstallation

### **Easy Way:**

```bash
uninstall-context-menu.bat
```

### **Manual Way:**

1. Open Registry Editor (`regedit`)
2. Navigate to: `HKEY_CLASSES_ROOT\Directory\shell\`
3. Delete key: `KILAT`
4. Navigate to: `HKEY_CLASSES_ROOT\Directory\Background\shell\`
5. Delete key: `KILAT`

---

## 💡 Usage Examples

### **Example 1: Python Project**

```
1. Navigate to: C:\Projects\FlaskApp
2. Right-click → Run KILAT Here
3. KILAT opens with workspace: C:\Projects\FlaskApp
4. Start coding:
   💭 Task: @app.py Create a new route
```

### **Example 2: Godot Project**

```
1. Navigate to: C:\Kodingan\Godot
2. Right-click → Run KILAT Here
3. KILAT opens with workspace: C:\Kodingan\Godot
4. Start working:
   💭 Task: @src/player.gd Add double jump
```

### **Example 3: Documentation Folder**

```
1. Navigate to: C:\Docs\ProjectX
2. Right-click → Run KILAT Here
3. KILAT opens with workspace: C:\Docs\ProjectX
4. Start writing:
   💭 Task: Create README.md with project overview
```

---

## ⚡ How It Works

When you click "Run KILAT Here":

1. **Windows** passes folder path as `%V`
2. **CMD** changes directory to that folder (`cd /d "%V"`)
3. **Python** runs KILAT with folder as argument (`py -3.12 kilat.py "%V"`)
4. **KILAT** sets that folder as workspace
5. **MCP Filesystem** points to that folder
6. **Ready to code!** 🚀

---

## 🔒 Security Notes

- ✅ **Safe**: Only adds registry entries, no system files modified
- ✅ **Reversible**: Easy to uninstall anytime
- ✅ **Scoped**: KILAT only accesses specified workspace
- ⚠️ **Admin Required**: Registry changes need admin privileges

---

## 🐛 Troubleshooting

### **Problem: Menu item doesn't appear**

**Solution:**
1. Restart Windows Explorer:
   - Task Manager → Windows Explorer → Restart
2. Or log out and back in
3. Or reboot computer

### **Problem: Icon doesn't show**

**Solution:**
1. Check if `roograph_icon.png` exists
2. Try absolute path in registry
3. Use default Python icon instead

### **Problem: KILAT doesn't start**

**Solution:**
1. Check if Python 3.12 is installed: `py -3.12 --version`
3. Try running manually: `py -3.12 kilat.py "C:\Projects\MyApp"`

### **Problem: Workspace not set correctly**

**Solution:**
1. Check KILAT startup message
2. It should show: `📁 Workspace: <your-folder>`
3. If not, try manual launch with path argument

---

## 📋 Registry Keys Added

```
HKEY_CLASSES_ROOT\Directory\shell\KILAT
  (Default) = "Run KILAT Here"
  
HKEY_CLASSES_ROOT\Directory\shell\KILAT\command

HKEY_CLASSES_ROOT\Directory\Background\shell\KILAT
  (Same as above)
```

---

## 🎉 Benefits

| Before | After |
|--------|-------|
| ❌ Open terminal | ✅ Right-click folder |
| ❌ cd to folder | ✅ Auto-sets workspace |
| ❌ Run KILAT manually | ✅ One-click launch |
| ❌ Type workspace path | ✅ Auto-detects path |

---

**Enjoy one-click KILAT launching! 🚀**
