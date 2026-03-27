"""
Godot MCP Server - Custom MCP tools for Godot 4.6.1 Mono
Run with: python godot_mcp_server.py
"""

from fastmcp import FastMCP
import subprocess
from pathlib import Path

# Initialize MCP server
mcp = FastMCP("Godot")

# Godot paths
GODOT_CLI = r"C:\Kodingan\Godot\Godot_v4.6.1-stable_mono_win64_console.exe"
GODOT_EDITOR = r"C:\Kodingan\Godot\Godot_v4.6.1-stable_mono_win64.exe"
GODOT_PROJECT = r"C:\Kodingan\Godot"


@mcp.tool()
def run_scene(scene_path: str = "main.tscn") -> str:
    """
    Run a Godot scene for testing.
    
    Args:
        scene_path: Path to scene file (relative to project root)
    
    Returns:
        Output from Godot execution
    """
    try:
        result = subprocess.run(
            [GODOT_CLI, "--run-main", scene_path],
            capture_output=True,
            text=True,
            timeout=60,
            cwd=GODOT_PROJECT
        )
        
        return f"🎮 Scene: {scene_path}\nSTDOUT: {result.stdout}\nSTDERR: {result.stderr}\nRC: {result.returncode}"
    except subprocess.TimeoutExpired:
        return "❌ Scene execution timeout (60s)"
    except Exception as e:
        return f"❌ Error running scene: {e}"


@mcp.tool()
def export_project(preset: str = "Windows Desktop", debug: bool = True) -> str:
    """
    Export Godot project to target platform.
    
    Args:
        preset: Export preset (e.g., "Windows Desktop", "Linux/X11", "macOS")
        debug: Use debug export (True) or release (False)
    
    Returns:
        Export output and path
    """
    try:
        flag = "--export-debug" if debug else "--export-release"
        
        result = subprocess.run(
            [GODOT_CLI, flag, preset],
            capture_output=True,
            text=True,
            timeout=300,  # 5 minutes for export
            cwd=GODOT_PROJECT
        )
        
        return f"🎮 Export ({'Debug' if debug else 'Release'}): {preset}\nSTDOUT: {result.stdout}\nSTDERR: {result.stderr}\nRC: {result.returncode}"
    except subprocess.TimeoutExpired:
        return "❌ Export timeout (300s)"
    except Exception as e:
        return f"❌ Error exporting: {e}"


@mcp.tool()
def build_csharp() -> str:
    """
    Build C# solutions in Godot project.
    
    Returns:
        Build output including errors if any
    """
    try:
        result = subprocess.run(
            [GODOT_CLI, "--build-solutions"],
            capture_output=True,
            text=True,
            timeout=120,
            cwd=GODOT_PROJECT
        )
        
        if result.returncode == 0:
            return f"✅ C# Build Success\n{result.stdout}"
        else:
            return f"❌ C# Build Failed\nSTDOUT: {result.stdout}\nSTDERR: {result.stderr}"
    except subprocess.TimeoutExpired:
        return "❌ Build timeout (120s)"
    except Exception as e:
        return f"❌ Error building C#: {e}"


@mcp.tool()
def validate_project() -> str:
    """
    Validate Godot project for errors.
    
    Returns:
        Validation results
    """
    try:
        result = subprocess.run(
            [GODOT_CLI, "--validate-extension-api"],
            capture_output=True,
            text=True,
            timeout=60,
            cwd=GODOT_PROJECT
        )
        
        if result.returncode == 0:
            return f"✅ Project Valid\n{result.stdout}"
        else:
            return f"⚠️ Validation Issues\nSTDOUT: {result.stdout}\nSTDERR: {result.stderr}"
    except subprocess.TimeoutExpired:
        return "❌ Validation timeout (60s)"
    except Exception as e:
        return f"❌ Error validating: {e}"


@mcp.tool()
def list_scenes() -> str:
    """
    List all scene files (.tscn) in the project.
    
    Returns:
        List of scene files with paths
    """
    try:
        scenes = list(Path(GODOT_PROJECT).rglob("*.tscn"))
        
        if not scenes:
            return "📁 No scenes found"
        
        scene_list = "\n".join([f"  - {s.relative_to(GODOT_PROJECT)}" for s in scenes])
        return f"📁 Found {len(scenes)} scenes:\n{scene_list}"
    except Exception as e:
        return f"❌ Error listing scenes: {e}"


@mcp.tool()
def list_scripts() -> str:
    """
    List all script files (.cs, .gd) in the project.
    
    Returns:
        List of script files with paths
    """
    try:
        cs_scripts = list(Path(GODOT_PROJECT).rglob("*.cs"))
        gd_scripts = list(Path(GODOT_PROJECT).rglob("*.gd"))
        
        total = len(cs_scripts) + len(gd_scripts)
        
        if total == 0:
            return "📁 No scripts found"
        
        cs_list = "\n".join([f"  - {s.relative_to(GODOT_PROJECT)}" for s in cs_scripts[:20]])
        gd_list = "\n".join([f"  - {s.relative_to(GODOT_PROJECT)}" for s in gd_scripts[:20]])
        
        return f"📁 Found {total} scripts:\n\nC# ({len(cs_scripts)}):\n{cs_list}\n\nGDScript ({len(gd_scripts)}):\n{gd_list}"
    except Exception as e:
        return f"❌ Error listing scripts: {e}"


@mcp.tool()
def run_headless_test(timeout: int = 60) -> str:
    """
    Run Godot in headless mode for testing.
    
    Args:
        timeout: Max seconds to run
    
    Returns:
        Test output
    """
    try:
        result = subprocess.run(
            [GODOT_CLI, "--headless", "--quit-after", str(timeout)],
            capture_output=True,
            text=True,
            timeout=timeout + 10,
            cwd=GODOT_PROJECT
        )
        
        return f"🎮 Headless Test ({timeout}s)\nSTDOUT: {result.stdout}\nSTDERR: {result.stderr}\nRC: {result.returncode}"
    except subprocess.TimeoutExpired:
        return f"❌ Test timeout ({timeout}s)"
    except Exception as e:
        return f"❌ Error in headless test: {e}"


@mcp.tool()
def get_project_info() -> str:
    """
    Get Godot project information.
    
    Returns:
        Project settings and structure
    """
    try:
        project_godot = Path(GODOT_PROJECT) / "project.godot"
        
        if not project_godot.exists():
            return "❌ project.godot not found"
        
        content = project_godot.read_text(encoding="utf-8")
        
        # Extract basic info
        lines = content.split("\n")[:30]  # First 30 lines
        info = "\n".join(lines)
        
        return f"📋 Project Info:\n```\n{info}\n```"
    except Exception as e:
        return f"❌ Error getting project info: {e}"


if __name__ == "__main__":
    # Run MCP server
    print("🚀 Starting Godot MCP Server...")
    print(f"📁 Project: {GODOT_PROJECT}")
    print(f"🎮 Godot CLI: {GODOT_CLI}")
    print("\nAvailable tools:")
    print("  - run_scene")
    print("  - export_project")
    print("  - build_csharp")
    print("  - validate_project")
    print("  - list_scenes")
    print("  - list_scripts")
    print("  - run_headless_test")
    print("  - get_project_info")
    print("\nRun with: python godot_mcp_server.py")
    
    # Start MCP server (stdio transport)
    mcp.run()
