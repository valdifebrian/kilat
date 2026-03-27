import os
import glob
from typing import List, Dict, Any
from pathlib import Path

def read_many_files(paths: List[str]) -> str:
    """
    Read multiple files in a single tool call.
    Supports exact paths and glob patterns (e.g., 'src/**/*.py').
    """
    results = []
    processed_paths = set()
    
    for pattern in paths:
        # Resolve globs
        matches = glob.glob(pattern, recursive=True)
        if not matches:
            # Try direct path if glob fails
            matches = [pattern]
            
        for path in matches:
            if path in processed_paths:
                continue
            
            p = Path(path)
            if p.is_file():
                try:
                    content = p.read_text(encoding="utf-8")
                    results.append(f"--- FILE: {path} ---\n{content}\n")
                    processed_paths.add(path)
                except Exception as e:
                    results.append(f"--- FILE: {path} (Error) ---\n{str(e)}\n")
            elif p.is_dir():
                results.append(f"--- PATH: {path} ---\n(Is a directory, use search_files or list_files instead)\n")
            else:
                results.append(f"--- PATH: {path} ---\n(File not found)\n")
                
    if not results:
        return "❌ No files found for the provided paths."
    
    return "\n".join(results)
