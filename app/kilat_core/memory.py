import json
import os
from pathlib import Path
from typing import Dict, Any

class MemoryManager:
    """
    KILAT Persistent Memory Manager.
    Stores and retrieves project-specific context and user preferences.
    """
    
    def __init__(self, memory_path: str = "config/memory.json"):
        self.memory_path = Path(memory_path)
        self.memory_path.parent.mkdir(parents=True, exist_ok=True)
        self._memory = self._load()

    def _load(self) -> Dict[str, Any]:
        """Load memory from disk."""
        if self.memory_path.exists():
            try:
                with open(self.memory_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except:
                return {}
        return {
            "user_preferences": {},
            "project_context": {},
            "architectural_decisions": []
        }

    def save(self):
        """Save memory to disk."""
        with open(self.memory_path, "w", encoding="utf-8") as f:
            json.dump(self._memory, f, indent=2)

    def update_preference(self, key: str, value: Any):
        """Update a user preference."""
        self._memory["user_preferences"][key] = value
        self.save()

    def update_context(self, key: str, value: Any):
        """Update project context."""
        self._memory["project_context"][key] = value
        self.save()

    def add_decision(self, decision: str):
        """Add an architectural decision."""
        if decision not in self._memory["architectural_decisions"]:
            self._memory["architectural_decisions"].append(decision)
            self.save()

    def get_summary(self) -> str:
        """Get a text summary for prompt injection."""
        summary = "🧠 SESSION MEMORY:\n"
        
        if self._memory["user_preferences"]:
            summary += f"- User Prefs: {self._memory['user_preferences']}\n"
            
        if self._memory["project_context"]:
            summary += f"- Project Context: {self._memory['project_context']}\n"
            
        if self._memory["architectural_decisions"]:
            summary += f"- Key Decisions: {self._memory['architectural_decisions'][-3:]}\n"
            
        return summary if len(summary) > 20 else ""
