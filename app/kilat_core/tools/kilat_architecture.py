import os
import glob
import re
from typing import Dict, Any, List, Set, Optional

class ArchitectureTool:
    """
    KILAT Codebase Architecture Analysis Tool.
    Ported from Qwen-Code's 'Explore' agent and LSP logic.
    Provides deep mapping of project structures and dependencies.
    """

    def __init__(self, workspace_root: str):
        self.workspace_root = workspace_root

    def list_all_files(self, ignore_patterns: Optional[List[str]] = None) -> List[str]:
        """Glob all files in the project, respecting common ignore patterns."""
        if ignore_patterns is None:
            ignore_patterns = ["node_modules", ".git", "__pycache__", "venv", ".venv", "build", "dist"]
        
        all_files = []
        for root, dirs, files in os.walk(self.workspace_root):
            # Skip ignored directories
            if ignore_patterns:
                dirs[:] = [d for d in dirs if d not in ignore_patterns]
            for file in files:
                all_files.append(os.path.relpath(os.path.join(root, file), self.workspace_root))
        return all_files

    def analyze_imports(self, file_path: str) -> List[str]:
        """Simple regex-based import analysis for Python/JS/TS."""
        full_path = os.path.join(self.workspace_root, file_path)
        if not os.path.exists(full_path):
            return []

        with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()

        imports = []
        # Python: from x import y, import z
        if file_path.endswith(".py"):
            imports.extend(re.findall(r"^(?:from|import)\s+([\w.]+)", content, re.MULTILINE))
        
        # JS/TS: import { x } from 'y', import z from 'y'
        elif file_path.endswith((".js", ".ts", ".tsx")):
            imports.extend(re.findall(r"from\s+['\"]([^'\"]+)['\"]", content))
        
        return list(set(imports))

    def identify_entry_points(self) -> List[str]:
        """Heuristically find entry points (main.py, index.ts, etc.)."""
        common_entry_files = ["main.py", "app.py", "index.ts", "index.js", "kilat.py"]
        found = []
        for file in common_entry_files:
            if os.path.exists(os.path.join(self.workspace_root, file)):
                found.append(file)
        return found

    def get_module_summary(self, module_name: str) -> Dict[str, Any]:
        """Get summary of a specific module (directory)."""
        module_path = os.path.join(self.workspace_root, module_name)
        if not os.path.isdir(module_path):
            return {"error": "Not a directory"}
        
        files = os.listdir(module_path)
        return {
            "name": module_name,
            "file_count": len(files),
            "files": files,
            "has_init": "__init__.py" in files
        }
