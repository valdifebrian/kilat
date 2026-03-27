# 🖱️ CONTEXT MENU TROUBLESHOOTING

**Date:** 2026-03-27  
**Status:** ✅ Installed, may need refresh

---

## ✅ INSTALLATION VERIFIED

```
✅ Registry key found
✅ Batch file found
✅ Python found
```

---

## 🖱️ HOW TO ACCESS (Windows 11)

### **Windows 11 hides context menus!**

**Step 1:** Open any folder (e.g., `C:\Kodingan`)

**Step 2:** Right-click on **empty space**

**Step 3:** Click **"Show more options"** at bottom

**Step 4:** Look for **"Run KILAT Here"**

---

## 🔄 REFRESH METHODS

### **Method 1: Quick Refresh**
```
1. Press F5 in Windows Explorer
2. Right-click again
```

### **Method 2: Restart Explorer**
```bash
# Run in terminal:
taskkill /F /IM explorer.exe
timeout /t 2
start explorer.exe
```

### **Method 3: Log Out/In**
```
1. Windows + L (lock screen)
2. Log out
3. Log back in
4. Check context menu
```

### **Method 4: Restart Computer**
```
Last resort - full restart
```

---

## 🎯 WHERE TO LOOK

### **Location 1: Folder Background**
```
Open folder → Right-click on EMPTY SPACE → "Run KILAT Here"
```

### **Location 2: Folder Icon**
```
In parent folder → Right-click ON folder → "Run KILAT Here"
```

### **Location 3: Windows 11 More Options**
```
Right-click → "Show more options" → "Run KILAT Here"
```

---

## ⚠️ COMMON MISTAKES

### **❌ Wrong: Right-click on file**
```
Right-click on file.txt → No KILAT menu
```
**Fix:** Right-click on **empty space**, not files

### **❌ Wrong: Right-click on folder in tree**
```
Right-click on folder in left sidebar → No menu
```
**Fix:** Open folder, right-click inside

### **❌ Wrong: Windows 11 hidden menu**
```
Right-click → Don't see it
```
**Fix:** Click "Show more options" first

---

## 🔧 MANUAL TEST

### **Test Registry:**
```bash
# Run in terminal:
reg query HKEY_CLASSES_ROOT\Directory\Background\shell\KILAT

# Should show:
# HKEY_CLASSES_ROOT\Directory\Background\shell\KILAT
```

### **Test Batch File:**
```bash
# Run manually:
C:\Kodingan\KILAT\installers\run_kilat_here.bat "C:\Kodingan"

# Should open KILAT in C:\Kodingan
```

---

## 💡 ALTERNATIVES

### **Option 1: Desktop Shortcut**
```bash
# Create shortcut on desktop:
# Target: C:\Kodingan\KILAT\installers\run_kilat_here.bat "C:\Kodingan"
```

### **Option 2: Taskbar Pin**
```bash
# Pin kilat.py to taskbar
# Right-click → Pin to taskbar
```

### **Option 3: Start Menu**
```bash
# Create shortcut in Start Menu
# Search "KILAT" from Start menu
```

### **Option 4: Keyboard Shortcut**
```bash
# Create desktop shortcut
# Properties → Set "Shortcut key": Ctrl+Alt+K
# Now Ctrl+Alt+K opens KILAT!
```

---

## 🚀 QUICK FIX SCRIPT

Save as `fix-context-menu.bat`:
```batch
@echo off
echo Refreshing context menu...
taskkill /F /IM explorer.exe
timeout /t 2 /nobreak
start explorer.exe
echo Done! Try right-click now.
pause
```

Run it, then test again!

---

## 📊 REGISTRY BACKUP

If you want to restore original:
```bash
# Backup exists at:
C:\context_menu_backup.reg

# To restore:
reg import C:\context_menu_backup.reg
```

---

## ✅ SUCCESS CRITERIA

Context menu is working when:
1. ✅ Right-click in folder shows "Run KILAT Here"
2. ✅ Click it → KILAT opens
3. ✅ KILAT working directory = folder you clicked

---

## 🆘 STILL NOT WORKING?

### **Nuclear Option: Reinstall**
```bash
cd C:\Kodingan\KILAT\installers

# Uninstall
reg import remove-context-menu.reg
timeout /t 2

# Reinstall
reg import add-context-menu.reg
timeout /t 2

# Restart Explorer
taskkill /F /IM explorer.exe
timeout /t 2
start explorer.exe
```

### **Check Logs**
```bash
# Check if batch file runs:
cd C:\Kodingan\KILAT\installers
run_kilat_here.bat "C:\Kodingan"

# Should show error if any
```

---

**Last Updated:** 2026-03-27  
**Version:** v0.0.11
