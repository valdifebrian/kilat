"""
KILAT Git Shadowing (Checkpoints)
Automatically creates git commits to track project state changes.
"""

import subprocess
from pathlib import Path

def create_checkpoint(workspace_path: str, message: str) -> str:
    """
    Creates a git checkpoint of the current workspace state.
    """
    workspace = Path(workspace_path)
    
    # Check if git is initialized
    if not (workspace / ".git").exists():
        # Optional: Initialize git if not present? 
        # For safety, we'll just return an info message for now.
        return "ℹ️  Git not initialized in workspace. Checkpoint skipped."
    
    try:
        # 1. Add all changes
        subprocess.run(["git", "add", "."], capture_output=True, cwd=workspace)
        
        # 2. Check if there are changes to commit
        status = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True, cwd=workspace)
        if not status.stdout.strip():
            return "ℹ️  No changes detected. Checkpoint skipped."
            
        # 3. Create commit
        commit_msg = f"KILAT Checkpoint: {message}"
        result = subprocess.run(["git", "commit", "-m", commit_msg], capture_output=True, text=True, cwd=workspace)
        
        if result.returncode == 0:
            return f"✅ Checkpoint created: {message}"
        else:
            return f"❌ Checkpoint failed: {result.stderr}"
            
    except Exception as e:
        return f"❌ Checkpoint error: {e}"

def list_checkpoints(workspace_path: str, limit: int = 5) -> str:
    """
    Lists the last few KILAT checkpoints.
    """
    workspace = Path(workspace_path)
    try:
        result = subprocess.run(
            ["git", "log", "--oneline", "--grep=KILAT Checkpoint", f"-n {limit}"],
            capture_output=True, text=True, cwd=workspace
        )
        return result.stdout if result.stdout.strip() else "No KILAT checkpoints found."
    except Exception as e:
        return f"❌ Error listing checkpoints: {e}"
