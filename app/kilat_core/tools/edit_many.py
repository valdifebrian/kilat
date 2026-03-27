import os
from typing import List, Dict, Any
from pathlib import Path

def edit_many_files(edits: List[Dict[str, str]]) -> str:
    """
    Perform atomic multi-file edits.
    Expects a list of dicts: [{'path': '...', 'content': '...'}]
    Rolls back ALL changes if any single edit fails.
    """
    backups = {}
    success_log = []
    
    try:
        # Step 1: Validation & Backup
        for edit in edits:
            path = Path(edit['path'])
            if not path.exists():
                raise FileNotFoundError(f"File not found: {edit['path']}")
            
            # Backup original
            backups[path] = path.read_text(encoding="utf-8")
        
        # Step 2: Apply Edits
        for edit in edits:
            path = Path(edit['path'])
            path.write_text(edit['content'], encoding="utf-8")
            success_log.append(f"✅ {edit['path']} updated.")
            
        return f"🚀 Atomic batch edit successful!\n" + "\n".join(success_log)
        
    except Exception as e:
        # Step 3: Rollback
        rollback_log = []
        for path, original_content in backups.items():
            try:
                path.write_text(original_content, encoding="utf-8")
                rollback_log.append(f"🔄 {path.name} restored.")
            except:
                rollback_log.append(f"❌ Failed to restore {path.name}!")
                
        return (f"❌ Batch edit failed: {str(e)}\n"
                f"⚠️  Rollback triggered:\n" + "\n".join(rollback_log))
