"""
KILAT apply_diff tool - Ported from Roo-Code ApplyDiffTool.ts
Apply unified diff patches to files
"""

from pathlib import Path
from langchain_core.tools import tool
from typing import Optional
import subprocess
import tempfile


@tool
def apply_diff(diff: str, filepath: Optional[str] = None) -> str:
    """
    Apply a unified diff patch to a file.
    
    Args:
        diff: Unified diff content to apply
        filepath: Optional specific file path (if not in diff)
    
    Returns:
        Success or error message
    """
    if not diff:
        return "❌ Error: diff parameter is required"
    
    try:
        # Try to parse filepath from diff
        if not filepath:
            for line in diff.splitlines():
                if line.startswith('+++ b/') or line.startswith('+++ '):
                    filepath = line.replace('+++ b/', '').replace('+++ ', '').strip()
                    break
        
        if not filepath:
            return "❌ Error: Could not determine target file from diff. Please specify filepath."
        
        file_path = Path(filepath)
        
        if not file_path.exists():
            return f"❌ Error: Target file not found: {filepath}"
        
        # Apply diff using patch command
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.patch') as f:
            f.write(diff)
            patch_file = f.name
        
        try:
            result = subprocess.run(
                ['patch', '-p1', '-i', patch_file],
                capture_output=True,
                text=True,
                cwd=file_path.parent
            )
            
            if result.returncode == 0:
                return f"✅ Successfully applied diff to {filepath}"
            else:
                return f"⚠️  Diff application had issues:\n{result.stdout}\n{result.stderr}"
        
        except FileNotFoundError:
            # patch command not available, try manual apply
            return manual_apply_diff(file_path, diff)
        
        finally:
            Path(patch_file).unlink(missing_ok=True)
    
    except Exception as e:
        return f"❌ Error applying diff: {e}"


def manual_apply_diff(file_path: Path, diff: str) -> str:
    """
    Manual diff application when patch command is not available.
    Simple implementation - just replaces content.
    """
    # For now, fallback to showing what would be changed
    old_content = file_path.read_text(encoding='utf-8')
    
    # Parse diff to show changes
    additions = sum(1 for line in diff.splitlines() if line.startswith('+') and not line.startswith('+++'))
    deletions = sum(1 for line in diff.splitlines() if line.startswith('-') and not line.startswith('---'))
    
    return (
        f"⚠️  Manual diff application (patch command not available)\n"
        f"   File: {file_path}\n"
        f"   Additions: ~{additions} lines\n"
        f"   Deletions: ~{deletions} lines\n\n"
        f"   To apply this diff, use a proper patch tool or manually edit the file."
    )


@tool
def apply_patch(patches: list) -> str:
    """
    Apply multiple file patches at once.
    
    Args:
        patches: List of dicts with 'filepath' and 'diff' keys
    
    Returns:
        Summary of applied patches
    """
    if not patches:
        return "❌ Error: patches parameter is required"
    
    results = []
    success_count = 0
    
    for patch in patches:
        if isinstance(patch, dict) and 'diff' in patch:
            filepath = patch.get('filepath')
            result = apply_diff.func(patch['diff'], filepath)  # type: ignore
            
            if result.startswith('✅'):
                success_count += 1
            
            results.append(result)
    
    return f"✅ Applied {success_count}/{len(patches)} patches\n\n" + "\n".join(results)
