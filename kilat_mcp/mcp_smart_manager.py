"""
MCP Smart Manager - Selective On-Demand MCP Server Manager
Auto-start MCP servers only when needed, keep idle servers in background
"""

import subprocess
import asyncio
import json
from pathlib import Path
from typing import Dict, Optional
import colorama
from langchain_mcp_adapters.client import MultiServerMCPClient

colorama.init()

# MCP Server Configurations
MCP_SERVERS = {
    "filesystem": {
        "name": "Filesystem",
        "command": ["npx.cmd", "-y", "@modelcontextprotocol/server-filesystem", "C:\\Kodingan"],
        "auto_start": True,  # Always start
        "priority": "high"
    },
    "memory": {
        "name": "Memory",
        "command": ["npx.cmd", "-y", "@modelcontextprotocol/server-memory"],
        "auto_start": True,  # Always start
        "priority": "high"
    },
    "duckduckgo": {
        "name": "DuckDuckGo",
        "command": ["npx.cmd", "-y", "duckduckgo-mcp-server"],
        "auto_start": False,  # Start on-demand
        "priority": "medium"
    },
    "sequential": {
        "name": "Sequential Thinking",
        "command": ["npx.cmd", "-y", "@modelcontextprotocol/server-sequential-thinking"],
        "auto_start": False,  # Start on-demand
        "priority": "medium"
    },
    "context7": {
        "name": "Context7",
        "command": ["npx.cmd", "-y", "@upstash/context7-mcp"],
        "auto_start": False,  # Start on-demand (has quota limit)
        "priority": "low"
    },
    "playwright": {
        "name": "Playwright",
        "command": ["npx.cmd", "-y", "@playwright/mcp@latest"],
        "auto_start": False,  # Start on-demand (heavy)
        "priority": "low"
    },
    "godot": {
        "name": "Godot",
        "command": ["py", "-3.12", "C:\\Kodingan\\RooGraph\\godot_mcp_server.py"],
        "auto_start": False,  # Start on-demand
        "priority": "medium"
    }
}


class MCPSmartManager:
    """Smart MCP server manager with selective on-demand start"""
    
    def __init__(self, config_path: Optional[str] = None):
        self.processes: Dict[str, subprocess.Popen] = {}
        # Determine config path: prioritize constructor, then PROJECT_ROOT/config/config.json, then current dir
        if config_path:
            self.config_path = Path(config_path)
        else:
            project_root = Path(__file__).parent.parent.resolve()
            alt_path = project_root / "config" / "config.json"
            if alt_path.exists():
                self.config_path = alt_path
            else:
                self.config_path = Path(__file__).parent / "config.json"
        
        self.servers = MCP_SERVERS.copy()
        
        # Load custom config if exists
        if self.config_path.exists():
            print(colorama.Fore.CYAN + f"📝 Loading MCP config from {self.config_path}")
            with open(self.config_path, "r", encoding="utf-8") as f:
                custom_config = json.load(f)
                if "mcp_servers" in custom_config:
                    # Update internal servers with custom config
                    for key, s_cfg in custom_config["mcp_servers"].items():
                        if key not in self.servers:
                            self.servers[key] = s_cfg
                        else:
                            self.servers[key].update(s_cfg)
                        
                        # Map 'enabled' to 'auto_start' for consistency with base logic
                        if s_cfg.get("enabled") is True:
                            self.servers[key]["auto_start"] = True
                        
                        # Resolve {PROJECT_ROOT} in command and args
                        project_root = str(Path(__file__).parent.parent.resolve())
                        if "command" in self.servers[key]:
                            cmd = self.servers[key]["command"]
                            if isinstance(cmd, str):
                                self.servers[key]["command"] = cmd.replace("{PROJECT_ROOT}", project_root)
                            elif isinstance(cmd, list):
                                self.servers[key]["command"] = [c.replace("{PROJECT_ROOT}", project_root) for c in cmd]
                        
                        if "args" in self.servers[key]:
                            self.servers[key]["args"] = [a.replace("{PROJECT_ROOT}", project_root) for a in self.servers[key]["args"]]
    
    def start_server(self, server_key: str) -> bool:
        """Start a specific MCP server"""
        if server_key not in self.servers:
            print(colorama.Fore.RED + f"❌ Server '{server_key}' not found")
            return False
        
        if server_key in self.processes:
            print(colorama.Fore.YELLOW + f"⚠️  Server '{server_key}' already running")
            return True
        
        server = self.servers[server_key]
        print(colorama.Fore.CYAN + f"🚀 Starting {server['name']}...")
        
        try:
            # Start process (hidden window)
            proc = subprocess.Popen(
                server["command"],
                creationflags=subprocess.CREATE_NO_WINDOW,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            
            self.processes[server_key] = proc
            print(colorama.Fore.GREEN + f"✅ {server['name']} started (PID: {proc.pid})")
            return True
            
        except Exception as e:
            print(colorama.Fore.RED + f"❌ Failed to start {server['name']}: {e}")
            return False
    
    def stop_server(self, server_key: str) -> bool:
        """Stop a specific MCP server"""
        if server_key not in self.processes:
            return False
        
        proc = self.processes[server_key]
        proc.terminate()
        proc.wait(timeout=5)
        
        del self.processes[server_key]
        print(colorama.Fore.YELLOW + f"⏹️  {self.servers[server_key]['name']} stopped")
        return True
    
    def start_auto_servers(self):
        """Start all servers marked as auto_start"""
        print(colorama.Fore.CYAN + "\n📡 Starting auto-start MCP servers...\n")
        
        for key, server in self.servers.items():
            if server.get("auto_start", False):
                self.start_server(key)
        
        print()
    
    def start_on_demand(self, server_keys: list):
        """Start specific servers on-demand"""
        for key in server_keys:
            if key in self.servers:
                self.start_server(key)
    
    def get_running_servers(self) -> list:
        """Get list of currently running servers"""
        return list(self.processes.keys())
    
    async def get_langchain_tools(self) -> list:
        """
        Connect to all enabled servers and return LangChain tools.
        """
        server_configs = {}
        for key, server in self.servers.items():
            # Check for 'enabled' (from config.json) or 'auto_start' (from internal)
            if server.get("enabled", False) or server.get("auto_start", False):
                cmd = server["command"]
                # Convert list command to string if necessary (though MultiServerMCPClient handles list)
                server_configs[key] = {
                    "transport": "stdio",
                    "command": cmd[0] if isinstance(cmd, list) else cmd,
                    "args": cmd[1:] if isinstance(cmd, list) else server.get("args", [])
                }
        
        if not server_configs:
            print(colorama.Fore.YELLOW + "⚠️  No enabled MCP servers found in configuration.")
            return []
            
        print(colorama.Fore.CYAN + f"🧩 Connecting to {len(server_configs)} MCP servers: {', '.join(server_configs.keys())}")
        
        all_tools = []
        print(colorama.Fore.CYAN + f"🧩 Connecting to {len(server_configs)} MCP servers: {', '.join(server_configs.keys())}")
        
        for name, config in server_configs.items():
            try:
                print(colorama.Fore.CYAN + f"⏳ Handshaking with {name} (Timeout: 15s)...")
                # Create a client for JUST THIS server to isolate failures
                client = MultiServerMCPClient({name: config})
                
                # Wrap in wait_for
                tools = await asyncio.wait_for(client.get_tools(), timeout=15.0)
                
                print(colorama.Fore.GREEN + f"  ✅ {name}: {len(tools)} tools added")
                all_tools.extend(tools)
            except asyncio.TimeoutError:
                print(colorama.Fore.RED + f"  ❌ {name}: Timeout after 15s")
            except Exception as e:
                print(colorama.Fore.RED + f"  ❌ {name}: Error: {e}")
        
        print(colorama.Fore.GREEN + f"\n✅ Successfully bridged {len(all_tools)} MCP tools to LLM.")
        return all_tools

    def stop_all(self):
        """Stop all running MCP servers"""
        print(colorama.Fore.YELLOW + "\n⏹️  Stopping all MCP servers...\n")
        
        for key in list(self.processes.keys()):
            self.stop_server(key)
        
        print(colorama.Fore.GREEN + "✅ All MCP servers stopped\n")
    
    def __enter__(self):
        """Context manager entry"""
        self.start_auto_servers()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - cleanup all servers"""
        self.stop_all()


# CLI Interface
if __name__ == "__main__":
    import sys
    
    manager = MCPSmartManager()
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "start":
            # Start specific servers
            servers_to_start = sys.argv[2:] if len(sys.argv) > 2 else list(MCP_SERVERS.keys())
            manager.start_on_demand(servers_to_start)
        
        elif command == "stop":
            # Stop specific servers
            servers_to_stop = sys.argv[2:] if len(sys.argv) > 2 else list(manager.processes.keys())
            for key in servers_to_stop:
                manager.stop_server(key)
        
        elif command == "status":
            # Show running servers
            running = manager.get_running_servers()
            if running:
                print(colorama.Fore.GREEN + "Running MCP servers:")
                for key in running:
                    print(f"  ✅ {MCP_SERVERS[key]['name']} (PID: {manager.processes[key].pid})")
            else:
                print(colorama.Fore.YELLOW + "No MCP servers running")
        
        elif command == "list":
            # List all available servers
            print(colorama.Fore.CYAN + "Available MCP servers:\n")
            for key, server in MCP_SERVERS.items():
                auto = "🟢 Auto" if server.get("auto_start") else "🔴 On-demand"
                print(f"  {key:15} - {server['name']:20} [{auto}]")
    
    else:
        # Run as manager (start auto servers + keep running)
        print(colorama.Fore.CYAN + "=" * 60)
        print("MCP Smart Manager - Selective On-Demand Start")
        print("=" * 60)
        
        with MCPSmartManager() as mgr:
            print(colorama.Fore.GREEN + "✅ MCP servers running!")
            print(f"📊 Active: {len(mgr.get_running_servers())} servers\n")
            
            print(colorama.Fore.YELLOW + "Press Ctrl+C to stop all servers...\n")
            
            try:
                # Keep running
                while True:
                    asyncio.run(asyncio.sleep(1))
            except KeyboardInterrupt:
                print(colorama.Fore.CYAN + "\n👋 Shutting down...")
