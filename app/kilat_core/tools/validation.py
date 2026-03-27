"""
KILAT Tool Validation Layer
Validates tool parameters before execution to prevent agent hallucinations.
"""

from typing import Dict, Any, List

def validate_tool_call(tool_name: str, arguments: Dict[str, Any]) -> List[str]:
    """
    Validate tool arguments. Returns a list of error messages.
    Empty list means validation passed.
    """
    errors = []
    
    if tool_name == "write_to_file":
        if "path" not in arguments:
            errors.append("Missing required parameter: 'path'")
        if "content" not in arguments:
            errors.append("Missing required parameter: 'content'")
            
    elif tool_name == "apply_diff":
        if "path" not in arguments:
            errors.append("Missing required parameter: 'path'")
        if "diff" not in arguments:
            errors.append("Missing required parameter: 'diff'")
            
    elif tool_name == "search_files":
        if "pattern" not in arguments:
            errors.append("Missing required parameter: 'pattern'")
            
    elif tool_name == "shell_command_windows":
        if "cmd" not in arguments:
            errors.append("Missing required parameter: 'cmd'")
            
    return errors
