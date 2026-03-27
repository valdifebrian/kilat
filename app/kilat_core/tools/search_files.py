"""
KILAT search_files tool - Ported from Roo-Code SearchFilesTool.ts
Ripgrep-like codebase search
"""

from pathlib import Path
from langchain_core.tools import tool
import subprocess
import fnmatch


@tool
def search_files(
    pattern: str,
    path: str = ".",
    include: str = "*",
    exclude: str = "",
    max_results: int = 50,
    case_sensitive: bool = False
) -> str:
    """
    Search for files/content in the codebase.
    
    Args:
        pattern: Search pattern (regex supported)
        path: Base path to search in (default: current directory)
        include: Glob pattern for files to include (default: *)
        exclude: Glob pattern for files to exclude
        max_results: Maximum number of results (default: 50)
        case_sensitive: Case-sensitive search (default: False)
    
    Returns:
        Search results with file paths and matching lines
    """
    if not pattern:
        return "❌ Error: pattern parameter is required"
    
    search_path = Path(path)
    
    if not search_path.exists():
        return f"❌ Error: Search path not found: {path}"
    
    # Try ripgrep (rg) first - fastest
    try:
        return search_with_ripgrep(pattern, search_path, include, exclude, max_results, case_sensitive)
    except FileNotFoundError:
        # Fallback to Python search
        return search_with_python(pattern, search_path, include, exclude, max_results, case_sensitive)


def search_with_ripgrep(pattern: str, search_path: Path, include: str, exclude: str, 
                       max_results: int, case_sensitive: bool) -> str:
    """Search using ripgrep (rg)"""
    
    cmd = ['rg', '--json', '--max-count', str(max_results)]
    
    if not case_sensitive:
        cmd.append('--ignore-case')
    
    if include and include != '*':
        cmd.extend(['--glob', include])
    
    if exclude:
        cmd.extend(['--glob', f'!{exclude}'])
    
    cmd.extend([pattern, str(search_path)])
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode == 0:
        lines = result.stdout.strip().split('\n')
        results = []
        
        for line in lines[:max_results]:
            if line:
                try:
                    import json
                    match = json.loads(line)
                    if 'data' in match:
                        data = match['data']
                        filepath = data.get('path', {}).get('text', 'unknown')
                        text = data.get('lines', {}).get('text', '')
                        line_num = data.get('line_number', 0)
                        
                        results.append(f"{filepath}:{line_num}: {text.strip()}")
                except:
                    pass
        
        if results:
            return f"🔍 Found {len(results)} matches:\n\n" + "\n".join(results[:max_results])
        else:
            return "🔍 No matches found"
    
    return "🔍 No matches found"


def search_with_python(pattern: str, search_path: Path, include: str, exclude: str,
                      max_results: int, case_sensitive: bool) -> str:
    """Fallback Python search when ripgrep not available"""
    
    import re
    
    # Compile regex
    flags = 0 if case_sensitive else re.IGNORECASE
    try:
        regex = re.compile(pattern, flags)
    except re.error as e:
        return f"❌ Invalid regex pattern: {e}"
    
    results = []
    files_searched = 0
    
    # Walk through files
    for file_path in search_path.rglob('*'):
        if not file_path.is_file():
            continue
        
        # Check include/exclude patterns
        rel_path = str(file_path.relative_to(search_path))
        
        if include != '*' and not fnmatch.fnmatch(rel_path, include):
            continue
        
        if exclude and fnmatch.fnmatch(rel_path, exclude):
            continue
        
        # Skip common non-text directories
        if any(part in ['.git', 'node_modules', '__pycache__', 'venv', '.venv'] 
               for part in file_path.parts):
            continue
        
        try:
            content = file_path.read_text(encoding='utf-8', errors='ignore')
            files_searched += 1
            
            # Search for pattern
            for i, line in enumerate(content.splitlines(), 1):
                if regex.search(line):
                    results.append(f"{rel_path}:{i}: {line.strip()}")
                    
                    if len(results) >= max_results:
                        break
            
            if len(results) >= max_results:
                break
        
        except Exception:
            pass  # Skip binary files
    
    if results:
        return (
            f"🔍 Found {len(results)} matches in {files_searched} files:\n\n" +
            "\n".join(results[:max_results])
        )
    else:
        return f"🔍 No matches found (searched {files_searched} files)"


@tool
def search_codebase(query: str, max_results: int = 20) -> str:
    """
    High-level codebase search - searches common patterns.
    
    Args:
        query: Search query (function name, class name, etc)
        max_results: Maximum results to return
    
    Returns:
        Search results
    """
    # Search for function definitions
    func_pattern = rf'(def|function|func)\s+{query}'
    func_results = search_files.func(func_pattern, max_results=max_results // 2)  # type: ignore
    
    # Search for class definitions
    class_pattern = rf'(class|interface|type)\s+{query}'
    class_results = search_files.func(class_pattern, max_results=max_results // 2)  # type: ignore
    
    # Combine results
    combined = f"🔍 Codebase search for '{query}':\n\n"
    
    if func_results and "No matches" not in func_results:
        combined += f"\n📌 Functions:\n{func_results}\n"
    
    if class_results and "No matches" not in class_results:
        combined += f"\n📌 Classes:\n{class_results}\n"
    
    return combined if "Functions:" in combined or "Classes:" in combined else "🔍 No matches found"
