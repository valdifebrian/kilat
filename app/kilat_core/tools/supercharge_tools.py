from langchain_core.tools import tool
from .kilat_ci_cd import GitHubTool
from .kilat_testing import TestingTool
from .kilat_architecture import ArchitectureTool
from .kilat_review import ReviewManager
import os
import asyncio

# Initialize tools
# Note: workspace_root will be set dynamically during tool call or via a global
WORKSPACE_ROOT = os.getcwd() # Default, should be updated by kilat.py

gh_tool = GitHubTool()
test_tool = TestingTool(WORKSPACE_ROOT)
arch_tool = ArchitectureTool(WORKSPACE_ROOT)
review_manager = None

def set_llm(llm_instance):
    global review_manager
    review_manager = ReviewManager(llm_instance)

@tool
def github_action(command: str, params: str = "") -> str:
    """
    Perform GitHub actions like viewing PRs, posting comments, or listing issues.
    Commands: 'view_pr', 'diff_pr', 'comment_pr', 'list_issues', 'triage_issue', 'ci_summary'.
    Params: PR number, or JSON string for triage.
    """
    if command == 'view_pr':
        return str(gh_tool.get_pr_details(int(params)))
    elif command == 'diff_pr':
        return gh_tool.get_pr_diff(int(params))
    elif command == 'comment_pr':
        # Expecting "pr_number:body"
        try:
            pr_num, body = params.split(":", 1)
            return str(gh_tool.post_pr_comment(int(pr_num), body))
        except:
            return "❌ Invalid params. Format: 'pr_number:body'"
    elif command == 'list_issues':
        return str(gh_tool.list_issues())
    elif command == 'ci_summary':
        return gh_tool.summarize_ci()
    return f"❌ Unknown command: {command}"

@tool
def auto_test(action: str, target: str = ".") -> str:
    """
    Automated testing and self-healing.
    Actions: 'run', 'coverage', 'create_test'.
    Target: file path or directory.
    """
    if action == 'run':
        res = test_tool.run_pytest(target)
        return f"🧪 Test Result ({target}):\n{'✅ PASS' if res['success'] else '❌ FAIL'}\n\n{res.get('stdout', '')}\n{res.get('stderr', '')}"
    elif action == 'coverage':
        res = test_tool.run_with_coverage(target)
        return f"📊 Coverage ({target}):\n{res.get('report', 'Error')}"
    return f"❌ Unknown action: {action}"

@tool
def analyze_codebase(action: str, target: str = "") -> str:
    """
    Deep codebase architecture analysis.
    Actions: 'map', 'imports', 'entry_points', 'summary'.
    Target: file path or module name.
    """
    if action == 'map':
        files = arch_tool.list_all_files()
        return f"📁 Project Structure ({len(files)} files):\n" + "\n".join(files[:50]) + ("\n..." if len(files) > 50 else "")
    elif action == 'imports':
        return f"🔗 Imports in {target}:\n" + str(arch_tool.analyze_imports(target))
    elif action == 'entry_points':
        return f"🚦 Entry Points:\n" + str(arch_tool.identify_entry_points())
    elif action == 'summary':
        return str(arch_tool.get_module_summary(target))
    return f"❌ Unknown action: {action}"

@tool
def code_review(file_path: str) -> str:
    """
    Perform a multi-dimensional parallel code audit (Security, Performance, Best Practices).
    Leverages RTX 3090 for concurrent agent execution.
    """
    if not os.path.exists(file_path):
        return f"❌ File not found: {file_path}"
    
    if review_manager is None:
        return "❌ ReviewManager not initialized. LLM instance required."
    
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    loop = asyncio.get_event_loop()
    report = loop.run_until_complete(review_manager.audit_file(file_path, content))
    
    return report

SUPERCHARGE_TOOLS = [github_action, auto_test, analyze_codebase, code_review]
