"""
KILAT write_to_file tool - Ported from Roo-Code WriteToFileTool.ts
Creates or writes files with diff preview
"""

import json
import subprocess
from pathlib import Path
from langchain_core.tools import tool
from typing import Optional


def create_unified_diff(old_content: str, new_content: str, filepath: str = "file") -> str:
    """Create unified diff between old and new content"""
    import tempfile
    
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.old') as f1:
        f1.write(old_content)
        old_path = f1.name
    
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.new') as f2:
        f2.write(new_content)
        new_path = f2.name
    
    try:
        result = subprocess.run(
            ['unified_diff', old_path, new_path],
            capture_output=True,
            text=True
        )
        return result.stdout
    except:
        # Fallback: simple diff
        old_lines = old_content.splitlines(keepends=True)
        new_lines = new_content.splitlines(keepends=True)
        
        diff_lines = []
        diff_lines.append(f"--- a/{filepath}\n")
        diff_lines.append(f"+++ b/{filepath}\n")
        
        for line in old_lines:
            if line not in new_lines:
                diff_lines.append(f"-{line}")
        
        for line in new_lines:
            if line not in old_lines:
                diff_lines.append(f"+{line}")
        
        return ''.join(diff_lines)


@tool
def write_to_file(
    path: str,
    content: str,
    show_diff: bool = True
) -> str:
    """
    Create or write to a file with optional diff preview.
    
    Args:
        path: File path to write to
        content: Content to write
        show_diff: If True and file exists, show diff before writing
    
    Returns:
        Success message with file info
    """
    file_path = Path(path)
    
    if not path:
        return "❌ Error: path parameter is required"
    
    if content is None:
        return "❌ Error: content parameter is required"
    
    # Create parent directories if needed
    file_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Check if file exists
    file_exists = file_path.exists()
    
    if file_exists and show_diff:
        old_content = file_path.read_text(encoding='utf-8')
        
        # Create diff preview
        diff = create_unified_diff(old_content, content, path)
        
        # Show diff stats
        old_lines = len(old_content.splitlines())
        new_lines = len(content.splitlines())
        diff_lines = len([l for l in diff.splitlines() if l.startswith('+') or l.startswith('-')])
        
        preview = f"📝 Writing to {path}\n"
        preview += f"   File exists: Yes\n"
        preview += f"   Old lines: {old_lines}\n"
        preview += f"   New lines: {new_lines}\n"
        preview += f"   Changes: ~{diff_lines} lines\n\n"
        preview += f"   Diff preview:\n{diff[:500]}{'...' if len(diff) > 500 else ''}\n"
        
        # For now, auto-approve (later can add approval workflow)
        # In future: return preview and wait for approval
        
    # Write content
    try:
        file_path.write_text(content, encoding='utf-8')
        
        size = file_path.stat().st_size
        action = "Created" if not file_exists else "Updated"
        
        return f"✅ {action} {path} ({size} bytes, {len(content.splitlines())} lines)"
    
    except Exception as e:
        return f"❌ Error writing file: {e}"


@tool
def write_to_file_simple(path: str, content: str) -> str:
    """
    Simple version: Create or write to a file without diff.
    
    Args:
        path: File path to write to
        content: Content to write
    
    Returns:
        Success message
    """
    return write_to_file.func(path, content, show_diff=False)  # type: ignore
