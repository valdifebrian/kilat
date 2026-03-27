# 🖱️ KILAT Context Menu - "Run KILAT Here"

## 🎯 What is it?

Windows Explorer context menu integration that allows you to:
- **Right-click** any folder
- Select **"Run KILAT Here"**
- KILAT opens with that folder as workspace!

---

## 📦 Installation Status

| Item | Status | Location |
|------|--------|----------|
| **Registry Entries** | ⚠️ Needs Update | Windows Registry |
| **App Path** | ✅ Updated | `app\kilat.py` |
| **Icon Path** | ✅ Updated | `assets\roograph_icon.png` |

---

## 🔧 Installation Options

### **Option 1: Fresh Install** (Recommended)

```bash
cd C:\Kodingan\KILAT\installers
install-context-menu.bat
```

### **Option 2: Reinstall/Update** (If already installed)

```bash
cd C:\Kodingan\KILAT\installers
reinstall-context-menu.bat
```

This will:
1. Remove old registry entries
2. Add NEW registry entries with updated paths
3. Verify files exist

### **Option 3: Manual Registry Import**

```bash
# Import directly
regedit "C:\Kodingan\KILAT\installers\add-context-menu.reg"
```

---

## 📝 Registry Details

### **What gets added:**

```
HKEY_CLASSES_ROOT\Directory\shell\KILAT
  (Default) = "Run KILAT Here"
  Icon = "C:\Kodingan\KILAT\assets\roograph_icon.png"
  
HKEY_CLASSES_ROOT\Directory\shell\KILAT\command
  (Default) = "cmd.exe /c "cd /d "%V" && start "KILAT - %V" py -3.12 C:\Kodingan\KILAT\app\kilat.py "%V""
```

### **What it does:**

1. **Adds menu item** to folder right-click menu
2. **Sets icon** to AI Robot image
3. **Command executed:**
   - Changes directory to clicked folder (`cd /d "%V"`)
   - Starts KILAT with that folder as workspace
   - Opens in new window

---

## ✅ Verification

### **Check if installed:**

1. Right-click any folder in Windows Explorer
2. Look for **"Run KILAT Here"** in the menu
3. If you see it → ✅ Installed!
4. If not → ❌ Not installed, run installer

### **Test it works:**

1. Right-click a test folder (e.g., `C:\Test`)
2. Click **"Run KILAT Here"**
3. KILAT should open with workspace: `C:\Test`

---

## 🐛 Troubleshooting

### **Problem: Menu item doesn't appear**

**Solutions:**

1. **Restart Windows Explorer:**
   - Task Manager → Windows Explorer → Restart
   - Or log out and back in

2. **Re-run installer as Administrator:**
   ```bash
   Right-click install-context-menu.bat → Run as Administrator
   ```

3. **Check registry manually:**
   ```
   regedit
   Navigate to: HKEY_CLASSES_ROOT\Directory\shell\KILAT
   Should exist with "Run KILAT Here" value
   ```

### **Problem: Icon doesn't show**

**Solutions:**

1. **Check icon file exists:**
   ```bash
   dir C:\Kodingan\KILAT\assets\roograph_icon.png
   ```

2. **Update registry with correct path:**
   - Open `add-context-menu.reg`
   - Verify path: `C:\\Kodingan\\KILAT\\assets\\roograph_icon.png`
   - Re-run installer

### **Problem: KILAT doesn't start**

**Solutions:**

1. **Check Python 3.12 installed:**
   ```bash
   py -3.12 --version
   ```

2. **Check kilat.py exists:**
   ```bash
   dir C:\Kodingan\KILAT\app\kilat.py
   ```

3. **Try manual launch:**
   ```bash
   cd C:\Kodingan\KILAT
   py -3.12 app\kilat.py "C:\Test"
   ```

### **Problem: Wrong workspace opens**

**Solution:**

The workspace is determined by the folder you right-clicked. Make sure you're clicking the correct folder!

---

## 🗑️ Uninstallation

### **Easy Way:**

```bash
cd C:\Kodingan\KILAT\installers
uninstall-context-menu.bat
```

### **Manual Way:**

1. Open Registry Editor (`regedit`)
2. Navigate to: `HKEY_CLASSES_ROOT\Directory\shell\`
3. Delete key: `KILAT`
4. Navigate to: `HKEY_CLASSES_ROOT\Directory\Background\shell\`
5. Delete key: `KILAT`

---

## 📊 Before vs After Folder Reorganization

### **Before (Old Structure):**

```
Command: py -3.12 C:\Kodingan\KILAT\kilat.py "%V"
Icon: C:\Kodingan\KILAT\roograph_icon.png
```

### **After (New Structure):**

```
Command: py -3.12 C:\Kodingan\KILAT\app\kilat.py "%V"
Icon: C:\Kodingan\KILAT\assets\roograph_icon.png
```

**✅ Updated to match new folder structure!**

---

## 🎯 Usage Examples

### **Example 1: Python Project**

```
1. Navigate to: C:\Projects\FlaskApp
2. Right-click on "FlaskApp" folder
3. Click: "Run KILAT Here"
4. KILAT opens with workspace: C:\Projects\FlaskApp
5. Start coding!
```

### **Example 2: Godot Project**

```
1. Navigate to: C:\Kodingan\Godot
2. Right-click on "Godot" folder
3. Click: "Run KILAT Here"
4. KILAT opens with workspace: C:\Kodingan\Godot
5. Work with Godot files!
```

### **Example 3: Any Folder**

```
1. Navigate to: ANY folder
2. Right-click (or right-click background)
3. Click: "Run KILAT Here"
4. KILAT opens with that folder as workspace!
```

---

## 📋 Files in This Folder

| File | Purpose |
|------|---------|
| `install-context-menu.bat` | Fresh installation |
| `reinstall-context-menu.bat` | Update/reinstall |
| `uninstall-context-menu.bat` | Remove integration |
| `add-context-menu.reg` | Registry add file |
| `remove-context-menu.reg` | Registry remove file |
| `CONTEXT-MENU-README.md` | This documentation |

---

## 🔒 Security Notes

- ✅ **Safe**: Only adds registry entries
- ✅ **Reversible**: Easy to uninstall anytime
- ✅ **No system files modified**: User-mode registry only
- ⚠️ **Admin Required**: Registry changes need admin privileges

---

## 📞 Need Help?

If you encounter issues:

1. Check this documentation first
2. Try troubleshooting steps above
3. Run installer as Administrator
4. Restart Windows Explorer

---

**Happy Coding with KILAT! 🚀**

**Version:** 0.0.1  
**Last Updated:** March 2026
