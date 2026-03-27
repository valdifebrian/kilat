# MCP Smart Manager - Selective On-Demand Start

## 🎯 Overview

MCP Smart Manager adalah **intelligent MCP server manager** yang hanya start server ketika dibutuhkan, bukan semua sekaligus. Ini menghemat resource dan membuat sistem lebih efisien.

**Status:** ✅ **PRODUCTION READY**  
**Version:** v0.0.2

---

## 🚀 Features

- ✅ **Auto-Start Servers** - Filesystem & Memory always running
- ✅ **On-Demand Loading** - Load DuckDuckGo, Playwright, dll hanya saat perlu
- ✅ **Zero Windows** - Semua berjalan di background (headless)
- ✅ **Auto-Cleanup** - Stop semua servers ketika exit
- ✅ **CLI Commands** - Start/stop servers dari dalam RooGraph

---

## 📋 MCP Servers Priority

| Priority | Server | Auto-Start | Reason |
|----------|--------|------------|--------|
| 🔴 **High** | Filesystem | ✅ Yes | Core functionality |
| 🔴 **High** | Memory | ✅ Yes | Long-term storage |
| 🟡 **Medium** | DuckDuckGo | ❌ No | Web search (on-demand) |
| 🟡 **Medium** | Sequential Thinking | ❌ No | Complex reasoning |
| 🟡 **Medium** | Godot | ❌ No | Game dev (on-demand) |
| 🟢 **Low** | Context7 | ❌ No | Has quota limit |
| 🟢 **Low** | Playwright | ❌ No | Heavy resource usage |

---

## 💬 Usage Commands

### **Inside RooGraph:**

```bash
# Check status MCP servers
/mcp status

# Start specific server on-demand
/mcp start duckduckgo
/mcp start playwright
/mcp start godot

# Stop specific server
/mcp stop duckduckgo
/mcp stop playwright

# List all available tools (including MCP)
/tools
```

### **Standalone CLI:**

```bash
# Start MCP Smart Manager (auto-start servers only)
py -3.12 mcp_smart_manager.py

# Start specific servers
py -3.12 mcp_smart_manager.py start duckduckgo playwright

# Stop specific servers
py -3.12 mcp_smart_manager.py stop duckduckgo

# Check status
py -3.12 mcp_smart_manager.py status

# List all available servers
py -3.12 mcp_smart_manager.py list
```

---

## 🎮 Example Workflow

### **1. Start RooGraph (Auto-start: Filesystem + Memory)**

```bash
```

Output:
```
🤖 Initializing MCP Smart Manager...
🚀 Starting Filesystem...
✅ Filesystem started (PID: 12345)
🚀 Starting Memory...
✅ Memory started (PID: 12346)

📊 Active: 2 servers
```

### **2. Need Web Search? Start DuckDuckGo On-Demand**

```
💭 Task: Search for latest Python best practices

📡 MCP not active for web search. Starting DuckDuckGo...
/mcp start duckduckgo

✅ Started duckduckgo
```

### **3. Done? Server Auto-Stops When You Exit**

```
💭 Task: quit

👋 Goodbye!
⏹️  Stopping all MCP servers...
⏹️  Filesystem stopped
⏹️  Memory stopped
✅ All MCP servers stopped
```

---

## 🔧 Customization

Edit `config.json` untuk customize auto-start behavior:

```json
{
  "mcp_servers": {
    "duckduckgo": {
      "auto_start": true,    // Always start with RooGraph
      "priority": "high"
    },
    "playwright": {
      "auto_start": false,   // On-demand only
      "priority": "low"
    }
  }
}
```

---

## 💡 Tips

### **When to Use On-Demand:**

- **DuckDuckGo**: When you need web search
- **Playwright**: When you need browser automation
- **Context7**: When you need documentation lookup (watch quota!)
- **Sequential Thinking**: When solving complex problems
- **Godot**: When working with Godot Engine

### **Resource Usage:**

| Server | RAM Usage | CPU Usage |
|--------|-----------|-----------|
| Filesystem | ~50 MB | Low |
| Memory | ~30 MB | Low |
| DuckDuckGo | ~80 MB | Medium |
| Playwright | ~200 MB | High |
| Context7 | ~60 MB | Low |

**Start only what you need!**

---

## 🐛 Troubleshooting

### **Server Won't Start**

```bash
# Check if port is already in use
netstat -ano | findstr ":<port>"

# Kill existing process
taskkill /F /PID <pid>

# Try start again
/mcp start <server>
```

### **Server Not Responding**

```bash
# Force stop
/mcp stop <server>

# Wait 5 seconds
timeout /t 5

# Start again
/mcp start <server>
```

### **Check All Running Processes**

```bash
# From CMD
tasklist | findstr "node"

# From PowerShell
Get-Process | Where-Object {$_.ProcessName -eq "node"}
```

---

## 📊 Architecture

```
┌─────────────────────────────────────┐
│      RooGraph v2.1                  │
│                                     │
│  ┌───────────────────────────────┐ │
│  │  MCP Smart Manager            │ │
│  │  ┌─────────────────────────┐  │ │
│  │  │  Auto-Start (Always On) │  │ │
│  │  │  - Filesystem           │  │ │
│  │  │  - Memory               │  │ │
│  │  └─────────────────────────┘  │ │
│  │  ┌─────────────────────────┐  │ │
│  │  │  On-Demand              │  │ │
│  │  │  - DuckDuckGo ⚡        │  │ │
│  │  │  - Playwright ⚡        │  │ │
│  │  │  - Context7 ⚡          │  │ │
│  │  │  - Sequential ⚡        │  │ │
│  │  │  - Godot ⚡             │  │ │
│  │  └─────────────────────────┘  │ │
│  └───────────────────────────────┘ │
└─────────────────────────────────────┘
```

---

## 🎯 Benefits

### **Before (Load All):**
```
7 MCP Servers = ~500 MB RAM
All running 24/7
Wasted resources
```

### **After (Smart Manager):**
```
2 Auto-Start = ~80 MB RAM
5 On-Demand = Load only when needed
Save ~420 MB RAM (84% reduction!)
```

---

**Happy Coding with Smart MCP Management! 🚀**
