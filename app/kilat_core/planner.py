import os
from pathlib import Path
from typing import List, Dict, Any
import colorama

class Planner:
    """
    Handles the Planner-Executor workflow for complex tasks.
    Generates a structured PLAN.md and manages its lifecycle.
    """
    
    def __init__(self, workspace_root: str):
        self.workspace_root = Path(workspace_root)
        self.plan_path = self.workspace_root / "PLAN.md"
        
    def create_plan(self, objective: str, steps: List[str]) -> str:
        """Create a new PLAN.md file."""
        content = f"# 📋 Task Plan: {objective}\n\n"
        content += "## 🎯 Objectives\n- " + objective + "\n\n"
        content += "## 📝 Planned Steps\n"
        for i, step in enumerate(steps, 1):
            content += f"{i}. [ ] {step}\n"
        
        content += "\n## ⚠️ Risk Assessment\n- [ ] Dependency check\n- [ ] Side-effect analysis\n"
        
        self.plan_path.write_text(content, encoding="utf-8")
        return f"✅ Plan created at {self.plan_path.name}. Execute it using '/plan exec'."

    def update_step(self, step_index: int, status: str = "x") -> str:
        """Mark a step as completed [x] or in-progress [/]."""
        if not self.plan_path.exists():
            return "❌ No active plan found."
        
        lines = self.plan_path.read_text(encoding="utf-8").splitlines()
        current_step = 0
        new_lines = []
        
        for line in lines:
            if line.strip().startswith(tuple(f"{i}." for i in range(1, 20))):
                current_step += 1
                if current_step == step_index:
                    # Update status
                    if "[" in line and "]" in line:
                        prefix = line[:line.find("[") + 1]
                        suffix = line[line.find("]"):]
                        line = f"{prefix}{status}{suffix}"
            new_lines.append(line)
            
        self.plan_path.write_text("\n".join(new_lines), encoding="utf-8")
        return f"✅ Step {step_index} updated to [{status}]."

    def get_summary(self) -> str:
        """Return the current state of the plan."""
        if not self.plan_path.exists():
            return "❌ No active plan."
        return self.plan_path.read_text(encoding="utf-8")
