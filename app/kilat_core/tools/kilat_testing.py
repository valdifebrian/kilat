import subprocess
import os
from typing import Dict, Any, List, Optional

class TestingTool:
    """
    KILAT Automated Testing & Self-Healing Tool.
    Ported from Qwen-Code's 'Auto-test generation' logic.
    Supports Pytest and basic coverage reporting.
    """

    def __init__(self, workspace_root: str):
        self.workspace_root = workspace_root

    def run_pytest(self, target_path: str) -> Dict[str, Any]:
        """Run pytest on a specific file or directory."""
        try:
            result = subprocess.run(
                ["pytest", target_path, "--tb=short"],
                cwd=self.workspace_root,
                capture_output=True,
                text=True
            )
            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "exit_code": result.returncode
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def run_with_coverage(self, target_path: str) -> Dict[str, Any]:
        """Run pytest with coverage reporting."""
        try:
            result = subprocess.run(
                ["pytest", "--cov=app", target_path],
                cwd=self.workspace_root,
                capture_output=True,
                text=True
            )
            return {
                "success": result.returncode == 0,
                "output": result.stdout,
                "report": self._parse_cov_output(result.stdout)
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _parse_cov_output(self, output: str) -> str:
        """Extract the coverage percentage from pytest-cov output."""
        lines = output.splitlines()
        for line in reversed(lines):
            if "TOTAL" in line:
                return line
        return "Coverage report not found."

    def create_test_file(self, source_file: str, test_content: str) -> str:
        """Write the generated test content to a file."""
        # Standard naming: test_filename.py
        base_name = os.path.basename(source_file)
        dir_name = os.path.dirname(source_file)
        test_file_path = os.path.join(dir_name, f"test_{base_name}")
        
        with open(test_file_path, "w", encoding="utf-8") as f:
            f.write(test_content)
        return test_file_path

    def self_heal_loop(self, source_file: str, test_file: str, max_attempts: int = 3):
        """
        Logic for self-healing:
        1. Run tests.
        2. If fail, provide error to the caller (who will call the LLM to 'fix').
        3. Apply fix and repeat.
        """
        attempt = 0
        while attempt < max_attempts:
            res = self.run_pytest(test_file)
            if res["success"]:
                return {"success": True, "attempts": attempt + 1, "final_output": res["stdout"]}
            
            # If we are here, tests failed. The caller (the Agent) will handle the 'Fix'.
            # We return the failure to indicate a repair is needed.
            return {"success": False, "attempts": attempt + 1, "error": res["stdout"] + res["stderr"]}
            
        return {"success": False, "attempts": max_attempts, "error": "Max attempts reached."}

    def generate_fix_prompt(self, source_content: str, error_msg: str) -> str:
        """Helper to generate a prompt for the LLM to fix the error."""
        return f"The following code has test failures:\n\n```python\n{source_content}\n```\n\nError:\n{error_msg}\n\nPlease provide a fix for this code."
