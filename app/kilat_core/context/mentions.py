"""
KILAT @mentions - File mention system ported from Roo-Code
Parse @filename syntax and auto-read mentioned files
"""

import re
import subprocess
from pathlib import Path
from typing import List, Tuple
from langchain_core.tools import tool


def parse_mentions(text: str, base_path: str = ".") -> List[Tuple[str, str]]:
    """
    Parse @mentions from text and return list of (filepath, content) tuples.
    
    Args:
        text: User input text containing @mentions
        base_path: Base path for resolving file paths
    
    Returns:
        List of (filepath, content) tuples for each mentioned file
    """
    mentions = []
    base = Path(base_path)
    
    # Pattern: @filename or @path/to/file
    pattern = r'@([^\s,;]+)'
    
    for match in re.finditer(pattern, text):
        mention = match.group(1)
        
        if mention == "terminal":
            try:
                # Simple way to get some terminal context on Windows: last few commands or just a placeholder
                # Real implementation would need a way to capture the parent terminal buffer.
                # For now, we'll try to get the last 50 lines of the console if possible, 
                # or just provide a helpful message.
                content = "[Terminal output capture not fully implemented in CLI mode, please copy-paste manually for now]"
                mentions.append(("terminal", content))
            except:
                pass
        
        elif mention == "git-changes":
            try:
                result = subprocess.run(["git", "diff"], capture_output=True, text=True, cwd=base)
                content = result.stdout if result.stdout else "No changes detected in git diff."
                mentions.append(("git-changes", content))
            except:
                pass
        
        else:
            # Try to resolve file
            file_path = resolve_file(mention, base)
            
            if file_path and file_path.exists():
                try:
                    content = file_path.read_text(encoding='utf-8')
                    mentions.append((str(file_path), content))
                except:
                    pass  # Skip binary files
    
    return mentions


def resolve_file(filepath: str, base: Path) -> Path:
    """
    Resolve a file path, trying multiple strategies.
    
    Args:
        filepath: File path from mention
        base: Base directory
    
    Returns:
        Resolved Path or None if not found
    """
    # Strategy 1: Absolute path
    if Path(filepath).is_absolute():
        return Path(filepath)
    
    # Strategy 2: Relative to base
    relative = base / filepath
    if relative.exists():
        return relative
    
    # Strategy 3: Search in workspace
    # Try to find file by name
    for file_path in base.rglob(Path(filepath).name):
        if file_path.is_file():
            return file_path
    
    # Strategy 4: Add common extensions
    for ext in ['.py', '.js', '.ts', '.java', '.cpp', '.h', '.hpp', '.go', '.rs', '.md', '.txt']:
        test_path = base / f"{filepath}{ext}"
        if test_path.exists():
            return test_path
    
    return None


def format_mentions(mentions: List[Tuple[str, str]]) -> str:
    """
    Format mentions as context for LLM.
    
    Args:
        mentions: List of (filepath, content) tuples
    
    Returns:
        Formatted context string
    """
    if not mentions:
        return ""
    
    formatted = []
    formatted.append("📎 Referenced files:\n")
    
    for filepath, content in mentions:
        if filepath in ["terminal", "git-changes"]:
            formatted.append(f"\n--- {filepath} ---")
            formatted.append(f"```")
            formatted.append(content)
            formatted.append(f"```")
            continue

        # Smart Truncation for files
        limit = 5000
        formatted.append(f"\n--- {filepath} ---")
        if len(content) > limit:
            formatted.append("⚠️  File content truncated for efficiency.")
            formatted.append(f"Status: Showing first {limit} characters of {len(content)} total.")
            formatted.append("To read more: Use 'read_file_with_backup' or specific tools.")
            formatted.append(f"```")
            formatted.append(content[:limit])
            formatted.append(f"\n... (truncated)")
        else:
            formatted.append(f"```")
            formatted.append(content)
        formatted.append(f"```")
    
    return "\n".join(formatted)


def inject_mentions(text: str, base_path: str = ".") -> Tuple[str, List[Tuple[str, str]]]:
    """
    Parse @mentions and inject file contents into text.
    
    Args:
        text: User input with @mentions
        base_path: Base path for file resolution
    
    Returns:
        Tuple of (enhanced_text, mentions_list)
    """
    mentions = parse_mentions(text, base_path)
    
    if not mentions:
        return text, []
    
    # Format mentions as context
    context = format_mentions(mentions)
    
    # Append to original text
    enhanced = f"{text}\n\n{context}"
    
    return enhanced, mentions


@tool
def read_mentioned_files(text: str, base_path: str = ".") -> str:
    """
    Tool version: Read all files mentioned with @syntax.
    
    Args:
        text: Text containing @mentions
        base_path: Base path for file resolution
    
    Returns:
        Formatted file contents
    """
    mentions = parse_mentions(text, base_path)
    
    if not mentions:
        return "📎 No file mentions found"
    
    return format_mentions(mentions)
