import subprocess
import json
from typing import Dict, Any, List, Optional

class GitHubTool:
    """
    KILAT GitHub & CI/CD Tool.
    Wraps the 'gh' CLI to provide agentic integration for PRs and Issues.
    Based on Qwen-Code 'qwen-code-pr-review.yml' logic.
    """

    def __init__(self):
        self._check_gh_cli()

    def _check_gh_cli(self):
        try:
            subprocess.run(["gh", "--version"], check=True, capture_output=True, shell=True)
        except Exception:
            # Not a fatal error, but functionality will be limited
            pass

    def exec_gh(self, args: List[str]) -> Dict[str, Any]:
        """Execute a GitHub CLI command and return the output."""
        try:
            result = subprocess.run(["gh"] + args, capture_output=True, text=True, check=True)
            return {"success": True, "output": result.stdout}
        except subprocess.CalledProcessError as e:
            return {"success": False, "error": e.stderr, "exit_code": e.returncode}

    def get_pr_details(self, pr_number: int) -> Dict[str, Any]:
        """Get details for a specific Pull Request."""
        args = ["pr", "view", str(pr_number), "--json", "title,body,additions,deletions,changedFiles,baseRefName,headRefName"]
        res = self.exec_gh(args)
        if res["success"]:
            return json.loads(res["output"])
        return res

    def get_pr_diff(self, pr_number: int) -> str:
        """Get the full diff for a Pull Request."""
        res = self.exec_gh(["pr", "diff", str(pr_number)])
        output = res.get("output")
        if output is not None:
            return str(output)
        error = res.get("error")
        return str(error) if error is not None else "Failed to get diff"

    def post_pr_comment(self, pr_number: int, body: str) -> Dict[str, Any]:
        """Post a comment on a Pull Request."""
        return self.exec_gh(["pr", "comment", str(pr_number), "--body", body])

    def list_issues(self, limit: int = 10) -> List[Dict[str, Any]]:
        """List recent issues in the repository."""
        args = ["issue", "list", "--limit", str(limit), "--json", "number,title,state,labels"]
        res = self.exec_gh(args)
        if res["success"]:
            return json.loads(res["output"])
        return []

    def triage_issue(self, issue_number: int, labels: List[str]) -> Dict[str, Any]:
        """Add labels to an issue (Issue Triage)."""
        label_str = ",".join(labels)
        return self.exec_gh(["issue", "edit", str(issue_number), "--add-label", label_str])

    def summarize_ci(self) -> str:
        """Get a summary of recent CI runs."""
        res = self.exec_gh(["run", "list", "--limit", "5"])
        return res.get("output", "No CI runs found.")
