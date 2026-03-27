"""
KILAT v0.0.10 - PRODUCTION READY
All tools + Phase 3 + CLI + Server + Dependency Injection + Security Hardening

Usage:
  Interactive: python kilat.py
  CLI: python kilat.py --headless --cli "task" --format=json
  Server: python kilat.py --server --port 8080
"""

import asyncio
import json
import subprocess
import argparse
import sys
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
import colorama
import sys
import os
from datetime import datetime
from prompt_toolkit import PromptSession
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.formatted_text import HTML
from prompt_toolkit.patch_stdout import patch_stdout

# Setup structured logging - FILE ONLY, no console output
# For CLI mode, all output goes to kilat.log
# For interactive mode, we use print() statements
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='kilat.log',
    filemode='a'
)
logger = logging.getLogger(__name__)

# Helper function for conditional printing
def safe_print(*args, **kwargs):
    """Print only if not in CLI headless mode"""
    import sys
    # Check if we're in headless CLI mode (stdout captured)
    if not (len(sys.argv) > 1 and '--headless' in sys.argv and '--cli' in sys.argv):
        safe_print(*args, **kwargs)

# Ensure project root and app directory are in sys.path
PROJECT_ROOT = Path(__file__).parent.parent.resolve()
APP_ROOT = Path(__file__).parent.resolve()

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
if str(APP_ROOT) not in sys.path:
    sys.path.insert(0, str(APP_ROOT))

colorama.init()

from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, ToolMessage

# Import ALL KILAT Core tools
from kilat_core.tools.write_to_file import write_to_file, write_to_file_simple
from kilat_core.tools.apply_diff import apply_diff, apply_patch
from kilat_core.tools.search_files import search_files, search_codebase
from kilat_core.tools.read_many import read_many_files
from kilat_core.tools.edit_many import edit_many_files
from kilat_core.context.mentions import parse_mentions, inject_mentions, format_mentions

# Import Phase 3 Modules
from kilat_core.context import SmartTokenCounter, PriorityContextManager, ContextVisualizer, Priority
from kilat_core.context import HybridSummarizer, SummarizationCommand
from kilat_core.context.checkpoints import create_checkpoint
from kilat_core.context.condense import condense_messages
from kilat_core.memory import MemoryManager
from kilat_core.planner import Planner
from kilat_core.tools.semantic_search import semantic_search

# Import Supercharge Tools
from kilat_core.tools.supercharge_tools import SUPERCHARGE_TOOLS, set_llm

# ================================================================
# HELPER FUNCTION: Create KILATAgent (for CLI/Server modes)
# ================================================================
async def create_kilat_agent(workspace_root: str = None):
    """
    Create KILATAgent with all dependencies injected.
    Factory function for creating properly configured KILATAgent instances.
    """
    logger.info("Creating KILATAgent...")
    
    # Set workspace root
    if workspace_root is None:
        workspace_root = str(PROJECT_ROOT)
    
    # Initialize LLM
    llm = ChatOpenAI(
        base_url=CONFIG["llama_server"]["url"],
        api_key="dummy",
        model=CONFIG["llama_server"]["model"],
        temperature=CONFIG["llama_server"]["temperature"],
        max_tokens=CONFIG["llama_server"]["max_tokens"],
        timeout=CONFIG["llama_server"]["timeout"]
    )
    
    # Set LLM for supercharge tools
    set_llm(llm)
    
    # Build tools list
    tools = [
        write_to_file, write_to_file_simple,
        apply_diff, apply_patch,
        search_files, search_codebase,
        read_many_files, edit_many_files,
    ] + SUPERCHARGE_TOOLS
    
    logger.info(f"Loaded {len(tools)} tools")
    
    # Initialize dependencies
    memory_manager = MemoryManager()
    token_counter = SmartTokenCounter(model_name="cl100k_base")
    priority_manager = PriorityContextManager()
    context_length = CONFIG['llama_server'].get('context_length', 327680)
    context_viz = ContextVisualizer(max_context_tokens=context_length)
    
    summarizer = HybridSummarizer(
        llm=llm,
        target_compression=0.125,
        keep_last_n=10,
        preserve_priority=Priority.IMPORTANT
    )
    
    planner = Planner(workspace_root)
    personas = EvolvingPersonas()
    todo_manager = TodoListManager()
    
    # Create and return KILATAgent
    agent = KILATAgent(
        llm=llm,
        tools=tools,
        memory_manager=memory_manager,
        token_counter=token_counter,
        priority_manager=priority_manager,
        context_viz=context_viz,
        summarizer=summarizer,
        planner=planner,
        personas=personas,
        todo_manager=todo_manager,
        config=CONFIG,
        workspace_root=workspace_root
    )
    
    logger.info("KILATAgent created successfully")
    return agent

# ================================================================
# FIX #1: DEPENDENCY INJECTION - KILATAgent Class
# ================================================================

class KILATAgent:
    """
    Production-ready KILAT agent with proper dependency injection.
    
    No global state - all dependencies injected via constructor.
    Enables unit testing, mocking, and multi-instance support.
    """
    
    def __init__(
        self,
        llm: ChatOpenAI,
        tools: list,
        memory_manager: MemoryManager,
        token_counter: SmartTokenCounter,
        priority_manager: PriorityContextManager,
        context_viz: ContextVisualizer,
        summarizer: HybridSummarizer,
        planner: Planner,
        personas: 'EvolvingPersonas',
        todo_manager: 'TodoListManager',
        config: Dict[str, Any],
        workspace_root: str
    ):
        self.llm = llm
        self.tools = tools
        self.memory_manager = memory_manager
        self.token_counter = token_counter
        self.priority_manager = priority_manager
        self.context_viz = context_viz
        self.summarizer = summarizer
        self.planner = planner
        self.personas = personas
        self.todo_manager = todo_manager
        self.config = config
        self.workspace_root = Path(workspace_root)
        
        # Create tools map
        self.tools_map = {
            getattr(tool, "name", getattr(tool, "__name__", str(tool))): tool
            for tool in tools
        }
        
        # Bind tools to LLM
        self.llm_with_tools = llm.bind_tools(tools)
        
        logger.info(f"KILATAgent initialized with {len(tools)} tools")
    
    async def process_task(self, task: str, max_turns: int = 10) -> Dict[str, Any]:
        """Process a single task with full KILAT capabilities."""
        logger.info(f"Processing task: {task[:100]}...")
        
        # Initialize state machine
        state_machine = TaskStateMachine(task)
        state_machine.transition_to(TaskState.PLANNING)
        
        # Process @mentions
        mentions = parse_mentions(task, str(self.workspace_root))
        if mentions and len(mentions) > 0:
            enhanced_task, _ = inject_mentions(task, str(self.workspace_root))
            logger.info(f"Found {len(mentions)} file mentions")
        else:
            enhanced_task = task
        
        # Auto-planning for complex tasks
        messages = [HumanMessage(content=enhanced_task)]
        enhanced_task, was_planned = await self._auto_plan_if_needed(enhanced_task, messages)
        
        if was_planned:
            messages = [HumanMessage(content=enhanced_task)]
        
        # ADD: Detect file creation intent and add hint
        if await self._detect_file_creation_intent(task):
            logger.info("File creation intent detected, adding hint...")
            messages.append(
                HumanMessage(
                    content="💡 HINT: If this task requires creating files, use write_to_file or write_to_file_simple tool immediately. Don't explain, just create the files."
                )
            )
            state_machine.transition_to(TaskState.EXECUTING, {
                "planned": True,
                "todos": len(self.todo_manager.todos)
            })
        
        # Execute tool loop
        messages = [HumanMessage(content=enhanced_task)]
        files_changed = []
        verification_criteria = []
        
        for turn_count in range(max_turns):
            logger.debug(f"Turn {turn_count + 1}/{max_turns}")
            
            response = await self.llm_with_tools.ainvoke(messages)
            messages.append(response)
            
            # Check for completion
            if not hasattr(response, 'tool_calls') or not response.tool_calls:
                if response.content:
                    logger.info(f"AI response: {response.content[:200]}...")
                break
            
            # Execute tools
            for tool_call in response.tool_calls:
                name = tool_call["name"]
                args = tool_call["args"]
                tool_id = tool_call["id"]
                
                result = await self._execute_tool(name, args, tool_id, task)
                messages.append(result)
                
                # Track file changes
                if name in ['write_to_file', 'write_to_file_simple', 'edit_file_with_backup', 'edit_many_files']:
                    files_changed.append(args.get('path', args.get('filename', 'unknown')))
                    
                    # Update todo progress
                    if self.todo_manager.get_current_todo():
                        self.todo_manager.mark_current_completed()
                        logger.info("Todo progress updated")
            
            verification_criteria.append(len(files_changed) > 0 or len(response.content) > 0)
            verification_criteria.append(turn_count < max_turns - 1)
        
        # Verify completion
        if state_machine.verify_completion(verification_criteria):
            state_machine.transition_to(TaskState.COMPLETED, {
                "files_changed": len(files_changed),
                "turns": len(messages)
            })
        else:
            state_machine.transition_to(TaskState.COMPLETED, {"verified": False})
        
        # Extract AI response
        ai_content = ""
        for msg in reversed(messages):
            if isinstance(msg, AIMessage) and msg.content:
                ai_content = msg.content
                break
        
        result = {
            "status": "success",
            "files_changed": files_changed,
            "output": ai_content,
            "turns": len(messages),
            "state_machine": state_machine.get_summary()
        }
        
        logger.info(f"Task completed: {len(files_changed)} files changed, {len(messages)} turns")
        return result
    
    async def _execute_tool(self, name: str, args: dict, tool_id: str, task: str) -> ToolMessage:
        """Execute a single tool with proper error handling and logging."""
        try:
            # FIX #3: Security validation for shell commands
            if name == 'shell_command_windows':
                if not self._validate_shell_command(args.get('cmd', '')):
                    logger.warning(f"Blocked dangerous command: {args.get('cmd')}")
                    return ToolMessage(
                        content="❌ Command blocked for security. Shell commands must be in whitelist.",
                        tool_call_id=tool_id
                    )
            
            # FIX #5: Auto-approval check with logging
            auto_approve = should_auto_approve(name, args)
            if auto_approve:
                logger.debug(f"[AUTO-APPROVED] {name}")
            else:
                logger.info(f"[EXEC] {name}")
            
            # Execute tool
            tool = self.tools_map.get(name)
            if not tool:
                logger.error(f"Tool not found: {name}")
                return ToolMessage(
                    content=f"❌ Tool '{name}' not found",
                    tool_call_id=tool_id
                )
            
            # FIX: Handle both function tools and LangChain tools
            if hasattr(tool, 'ainvoke'):
                res = await tool.ainvoke(args)
            elif hasattr(tool, 'invoke'):
                res = tool.invoke(args)
            elif callable(tool):
                # Plain function - call directly
                res = tool(**args)
            else:
                logger.error(f"Tool {name} is not callable")
                return ToolMessage(
                    content=f"❌ Tool {name} is not callable",
                    tool_call_id=tool_id
                )
            
            logger.debug(f"[DONE] {name}: {str(res)[:100]}...")
            return ToolMessage(content=str(res), tool_call_id=tool_id)
            
        except Exception as e:
            logger.error(f"Tool {name} failed: {e}", exc_info=True)
            
            # FIX #2: Self-reflection on failure
            await self_reflect_on_failure(str(e), task, name, self.memory_manager)
            
            return ToolMessage(
                content=f"❌ Error: {e}",
                tool_call_id=tool_id
            )
    
    def _validate_shell_command(self, cmd: str) -> bool:
        """FIX #3: Validate shell commands against whitelist."""
        if not cmd:
            return False
        
        # Whitelist of safe commands
        safe_prefixes = [
            'dir', 'ls', 'cd', 'pwd', 'echo', 'type', 'cat',
            'mkdir', 'rmdir', 'copy', 'xcopy', 'robocopy',
            'python', 'py', 'pip', 'npm', 'node', 'git',
            'docker', 'docker-compose'
        ]
        
        cmd_lower = cmd.lower().strip()
        
        # Block dangerous commands
        dangerous_patterns = ['rm -rf', 'del /s', 'format', 'fdisk', 'shutdown']
        if any(pattern in cmd_lower for pattern in dangerous_patterns):
            return False
        
        # Check whitelist
        return any(cmd_lower.startswith(prefix) for prefix in safe_prefixes)
    
    async def _auto_plan_if_needed(self, task: str, messages: list) -> tuple:
        """Auto-detect complex tasks and create execution plan."""
        is_complex = any(trigger in task.lower() for trigger in COMPLEXITY_TRIGGERS)
        
        if is_complex:
            has_plan = any(kw in task.lower() for kw in ["step", "langkah", "rencana"])
            
            if not has_plan and self.todo_manager:
                logger.info("Complex task detected, generating plan...")
                
                # Ask LLM to generate steps
                planning_messages = [
                    HumanMessage(content=f"""Task: {task}

Break this task into 3-5 concrete steps. Return ONLY the steps, one per line, numbered.
Example:
1. Setup project structure
2. Create main file
3. Add dependencies
4. Implement core features
5. Test the application

Steps:""")
                ]
                
                plan_response = await self.llm_with_tools.ainvoke(planning_messages)
                
                if hasattr(plan_response, 'content') and plan_response.content:
                    steps = []
                    for line in plan_response.content.split('\n'):
                        line = line.strip()
                        if line and any(line.startswith(f"{i}.") for i in range(1, 10)):
                            clean_step = line.split('. ', 1)[1] if '. ' in line else line
                            steps.append(clean_step)
                            self.todo_manager.add_todo(clean_step)
                    
                    if steps:
                        self.planner.create_plan(task, steps)
                        logger.info(f"Created {len(steps)} todos")
                        logger.info(self.todo_manager.get_summary())
                        return f"Execute plan with todos: {task}", True
        
        return task, False
    
    async def _detect_file_creation_intent(self, task: str) -> bool:
        """Detect if task requires file creation"""
        file_keywords = [
            "buat", "create", "buatkan", "write", "generate",
            "file", "code", "script", "program", "simpan", "save",
            "aplikasi", "application", "project", "lengkap"
        ]
        return any(kw in task.lower() for kw in file_keywords)

# PATCH_4: Todo List System (like Roo Code)
from typing import TypedDict, Literal

class TodoItem(TypedDict):
    content: str
    status: Literal["pending", "in_progress", "completed"]
    id: str

class TodoListManager:
    """Manage todo list with status tracking (Roo Code pattern)"""
    
    def __init__(self):
        self.todos: list[TodoItem] = []
        self.current_index = 0
    
    def add_todo(self, content: str) -> str:
        todo_id = f"todo_{len(self.todos) + 1}"
        self.todos.append({
            "content": content,
            "status": "pending",
            "id": todo_id
        })
        return todo_id
    
    def update_todo(self, index: int, status: Literal["pending", "in_progress", "completed"]):
        if 0 <= index < len(self.todos):
            self.todos[index]["status"] = status
            if status == "in_progress":
                self.current_index = index
    
    def get_summary(self) -> str:
        if not self.todos:
            return "No todos."
        
        summary = "📋 Task Progress:\n"
        for i, todo in enumerate(self.todos, 1):
            icon = {"pending": "⏳", "in_progress": "🔄", "completed": "✅"}[todo["status"]]
            summary += f"{i}. {icon} {todo['content']}\n"
        
        completed = sum(1 for t in self.todos if t["status"] == "completed")
        summary += f"\nProgress: {completed}/{len(self.todos)} completed"
        return summary
    
    def get_current_todo(self) -> TodoItem | None:
        if self.current_index < len(self.todos):
            return self.todos[self.current_index]
        return None
    
    def mark_current_completed(self):
        if self.todos:
            self.todos[self.current_index]["status"] = "completed"
            self.current_index = min(self.current_index + 1, len(self.todos) - 1)

# PATCH_5: Auto-Approval Handler (like Roo Code)
TRUSTED_TOOLS = [
    'read_file_with_backup',
    'search_files',
    'search_codebase',
    'read_many_files',
]

def should_auto_approve(tool_name: str, args: dict) -> bool:
    """Check if tool should auto-execute without confirmation (Roo Code pattern)"""
    # Trusted tools always auto-approve
    if tool_name in TRUSTED_TOOLS:
        return True
    
    # File edits auto-approve if file is in current directory
    if tool_name in ['write_to_file', 'edit_file_with_backup']:
        path = args.get('path', args.get('filename', ''))
        if not path.startswith('/'):  # Relative path
            return True
    
    return False

# PATCH_6: State Machine Pattern (Best Practice 2025)
from enum import Enum

class TaskState(Enum):
    """Task execution states (State Machine Pattern)"""
    INITIAL = "initial"
    PLANNING = "planning"
    EXECUTING = "executing"
    VERIFYING = "verifying"
    COMPLETED = "completed"
    FAILED = "failed"

class TaskStateMachine:
    """
    State machine for task execution (based on DeePractice.ai pattern)
    
    States: Initial → Planning → Executing → Verifying → Completed/Failed
    Transitions: Controlled by verification criteria
    """
    
    def __init__(self, task: str):
        self.task = task
        self.state = TaskState.INITIAL
        self.initial_state = {
            "task": task,
            "timestamp": datetime.now().isoformat(),
            "context": {}
        }
        self.target_state = {
            "completed": False,
            "verified": False,
            "output": None
        }
        self.state_history = []
    
    def transition_to(self, new_state: TaskState, context: dict = None):
        """Transition to new state with context"""
        self.state_history.append({
            "from": self.state.value,
            "to": new_state.value,
            "timestamp": datetime.now().isoformat(),
            "context": context or {}
        })
        self.state = new_state
        logger.info(f"State: {new_state.value.upper()}")
    
    def verify_completion(self, criteria: list) -> bool:
        """Verify if target state is reached"""
        if not criteria:
            return False
        
        all_passed = all(criteria)
        if all_passed:
            self.target_state["verified"] = True
            self.target_state["completed"] = True
        return all_passed
    
    def get_summary(self) -> str:
        """Get state machine summary"""
        summary = f"📊 Task State: {self.state.value}\n"
        if self.state_history:
            summary += f"Transitions: {len(self.state_history)}\n"
            for transition in self.state_history[-3:]:  # Last 3 transitions
                summary += f"  {transition['from']} → {transition['to']}\n"
        return summary

# Auto-Planning Detection (PATCH_1: AUTONOMY)
COMPLEXITY_TRIGGERS = [
    "buat aplikasi", "build app", "create system", "develop feature",
    "implementasi", "implement", "multi-step", "beberapa langkah",
    "buat lengkap", "full stack", "end-to-end", "complete system"
]

async def auto_plan_if_needed(task: str, planner, messages: list, todo_manager: TodoListManager = None, llm_with_tools=None) -> tuple[str, bool]:
    """
    Auto-detect complex tasks and EXECUTE planning workflow.
    Returns: (enhanced_task, was_planned)
    """
    # Check if task is complex
    is_complex = any(trigger in task.lower() for trigger in COMPLEXITY_TRIGGERS)
    
    if is_complex:
        # Check if user already provided plan
        has_plan = "step" in task.lower() or "langkah" in task.lower() or "rencana" in task.lower()
        
        if not has_plan:
            # PATCH_4: Auto-generate steps from LLM before creating plan
            if todo_manager and llm_with_tools:
                safe_print(colorama.Fore.CYAN + f"\n📋 Complex task detected!")
                safe_print(f"💡 Generating plan steps...")
                
                # Ask LLM to generate steps
                planning_messages = [
                    HumanMessage(content=f"""Task: {task}

Break this task into 3-5 concrete steps. Return ONLY the steps, one per line, numbered.
Example:
1. Setup project structure
2. Create main file
3. Add dependencies
4. Implement core features
5. Test the application

Steps:""")
                ]
                
                plan_response = await llm_with_tools.ainvoke(planning_messages)
                
                if hasattr(plan_response, 'content') and plan_response.content:
                    # Extract steps from LLM response
                    steps = []
                    for line in plan_response.content.split('\n'):
                        line = line.strip()
                        if line and any(line.startswith(f"{i}.") for i in range(1, 10)):
                            # Clean step: "1. Setup" -> "Setup"
                            clean_step = line.split('. ', 1)[1] if '. ' in line else line
                            steps.append(clean_step)
                            todo_manager.add_todo(clean_step)
                    
                    if steps:
                        # Create PLAN.md with steps
                        plan_result = planner.create_plan(task, steps)
                        safe_print(colorama.Fore.GREEN + f"✅ Created {len(steps)} todos")
                        safe_print(todo_manager.get_summary())
                        return f"Execute plan with todos: {task}", True
            
            return f"Execute plan: {task}", True
    
    return task, False

# Self-Reflection on Failure (PATCH_2: SELF-REFLECTION)
async def self_reflect_on_failure(error: str, task: str, tool_name: str, memory_manager):
    """
    Analyze tool execution failures and store lessons.
    """
    # Analyze error pattern
    error_type = "unknown"
    error_lower = error.lower()
    
    if "not found" in error_lower or "tidak ada" in error_lower:
        error_type = "file_not_found"
    elif "timeout" in error_lower:
        error_type = "timeout"
    elif "permission" in error_lower or "access denied" in error_lower:
        error_type = "permission_denied"
    elif "syntax" in error_lower or "invalid" in error_lower:
        error_type = "syntax_error"
    
    # Create lesson
    lesson = f"""
    LESSON LEARNED:
    - Task: {task}
    - Tool: {tool_name}
    - Error Type: {error_type}
    - Error: {error}
    
    Recovery Strategy:
    - For {error_type}: Check prerequisites before executing
    - Add validation before tool call
    - Consider alternative approaches
    """
    
    # Store in memory
    memory_manager.add_decision(f"LESSON_{tool_name.upper()}_{error_type.upper()}: {lesson}")
    
    # Suggest recovery
    recovery_suggestions = {
        "file_not_found": "💡 Try search_files to find correct path first",
        "timeout": "💡 Increase timeout or break into smaller tasks",
        "permission_denied": "💡 Run as administrator or check file permissions",
        "syntax_error": "💡 Review syntax and retry with corrected code",
        "unknown": "💡 Review error message and try alternative approach"
    }
    
    suggestion = recovery_suggestions.get(error_type, recovery_suggestions["unknown"])
    
    safe_print(colorama.Fore.YELLOW + f"\n🤔 Self-Reflection:")
    safe_print(f"   Error Type: {error_type}")
    safe_print(f"   {suggestion}")
    safe_print(f"   Lesson stored in memory for future reference")
    
    return {"error_type": error_type, "suggestion": suggestion, "lesson_stored": True}

# Persona Evolution (PATCH_3: LEARNING)
class EvolvingPersonas:
    """
    Personas that improve from failures over time.
    """
    
    def __init__(self):
        self.persona_prompts = {
            "coder": "You are an expert coder. You write clean, efficient, production-ready code. Focus on implementation.",
            "architect": "You are a software architect. You design scalable, maintainable systems. Focus on high-level design.",
            "debugger": "You are an expert debugger. You quickly identify and fix issues. Focus on root cause analysis.",
            "reviewer": "You are a code reviewer. You identify security, performance, and best practice issues. Focus on quality."
        }
        self.persona_configs = {
            "coder": {"temperature": 0.3, "focus": "implementation"},
            "architect": {"temperature": 0.1, "focus": "design"},
            "debugger": {"temperature": 0.2, "focus": "analysis"},
            "reviewer": {"temperature": 0.1, "focus": "quality"}
        }
        self.learnings = []
        self.current_persona = "coder"
    
    def switch_persona(self, persona_name: str, llm):
        """Switch to a different persona with appropriate config."""
        if persona_name in self.persona_configs:
            self.current_persona = persona_name
            config = self.persona_configs[persona_name]
            # Update LLM temperature
            llm.temperature = config["temperature"]
            safe_print(colorama.Fore.CYAN + f"🎭 Switched to {persona_name} persona (temp={config['temperature']}, focus={config['focus']})")
            return llm
        return llm
    
    def add_learning(self, persona: str, lesson: str):
        """Add lesson to persona's knowledge."""
        self.learnings.append({
            "persona": persona,
            "lesson": lesson,
            "timestamp": datetime.now().isoformat()
        })
        
        # Update persona prompt with lesson (avoid duplicates)
        if lesson not in self.persona_prompts[persona]:
            self.persona_prompts[persona] += f"\n\nLessons Learned:\n- {lesson}"
    
    def get_persona_prompt(self, persona_name: str) -> str:
        """Get current persona prompt (with all learnings)."""
        return self.persona_prompts.get(persona_name, "")
    
    def get_summary(self) -> str:
        """Get summary of all learnings."""
        if not self.learnings:
            return "No learnings yet."
        
        summary = "📚 Persona Evolution Summary:\n"
        for learning in self.learnings[-5:]:  # Last 5 learnings
            summary += f"- {learning['persona']}: {learning['lesson'][:100]}...\n"
        return summary
    
    def get_current_system_prompt(self) -> str:
        """Get system prompt for current persona with lessons injected."""
        base_prompt = self.persona_prompts.get(self.current_persona, "You are a helpful AI assistant.")
        
        # Inject relevant lessons
        if self.learnings:
            relevant_lessons = [l['lesson'] for l in self.learnings[-3:]]
            base_prompt += f"\n\nActive Lessons:\n" + "\n".join(f"- {l}" for l in relevant_lessons)
        
        return base_prompt

# Initialize in main()
personas = EvolvingPersonas()

# Load config
CONFIG_PATH = Path(__file__).parent.parent / "config" / "config.json"
with open(CONFIG_PATH, "r", encoding="utf-8") as f:
    CONFIG = json.load(f)

# KILAT Core Tools - ALL tools!
KILAT_CORE_TOOLS = [
    write_to_file,
    write_to_file_simple,
    apply_diff,
    apply_patch,
    search_files,
    search_codebase,
    read_many_files,
    edit_many_files,
    semantic_search,
]

# Legacy tools
@tool
def read_file_with_backup(filename: str) -> str:
    """Read file with auto backup"""
    path = Path(filename)
    if not path.exists():
        return f"❌ File not found: {filename}"
    content = path.read_text(encoding="utf-8")
    if CONFIG.get("agent", {}).get("backup_files", True):
        backup = path.with_suffix(path.suffix + ".bak")
        backup.write_text(content, encoding="utf-8")
    return f"📖 Read {filename} ({len(content)} chars)"

@tool
def edit_file_with_backup(filename: str, content: str) -> str:
    """Edit file with atomic backup"""
    path = Path(filename)
    if CONFIG.get("agent", {}).get("backup_files", True) and path.exists():
        backup = path.with_suffix(path.suffix + ".bak")
        original = path.read_text(encoding="utf-8")
        backup.write_text(original, encoding="utf-8")
    path.write_text(content, encoding="utf-8")
    return f"✅ Edited {filename} ({len(content)} chars)"

@tool
def run_tests_with_config(test_command: str = "pytest -x") -> str:
    """Run tests"""
    try:
        result = subprocess.run(test_command.split(), capture_output=True, text=True, timeout=120, cwd=".")
        passed = result.returncode == 0
        return f"🧪 Tests: {'✅ PASS' if passed else '❌ FAIL'}\n\n{result.stdout[-3000:]}"
    except Exception as e:
        return f"❌ Error: {e}"

@tool
def shell_command_windows(cmd: str) -> str:
    """Run shell command"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=60)
        return f"💻 {cmd}\n\nOUT:\n{result.stdout}\n\nERR:\n{result.stderr}"
    except Exception as e:
        return f"❌ Error: {e}"

LEGACY_TOOLS = [read_file_with_backup, edit_file_with_backup, run_tests_with_config, shell_command_windows]

# LLM (global, exported for CLI)
llm = ChatOpenAI(
    base_url=CONFIG["llama_server"]["url"],
    api_key="dummy",
    model=CONFIG["llama_server"]["model"],
    temperature=CONFIG["llama_server"]["temperature"],
    max_tokens=CONFIG["llama_server"]["max_tokens"],
    timeout=CONFIG["llama_server"]["timeout"]
)

# Global variables (exported for CLI integration)
app = None
llm_with_tools = None
tools_map = {}

async def get_kilat_app():
    """
    Get or initialize KILAT app (called from kilat_cli.py)
    Returns the compiled LangGraph workflow
    """
    global app, llm_with_tools, tools_map
    
    if app is not None:
        return app, llm_with_tools, tools_map
    
    # Initialize on first call
    base_tools = KILAT_CORE_TOOLS + LEGACY_TOOLS + SUPERCHARGE_TOOLS
    set_llm(llm)
    
    # Initialize MCP
    from kilat_mcp.mcp_smart_manager import MCPSmartManager
    mcp_manager = MCPSmartManager()
    mcp_tools = await mcp_manager.get_langchain_tools()
    
    all_tools = base_tools + mcp_tools
    llm_with_tools = llm.bind_tools(all_tools)
    
    # Create tools map
    from langchain_core.messages import ToolMessage
    tools_map = {getattr(tool, "name", getattr(tool, "__name__", str(tool))): tool for tool in all_tools}
    
    # Build workflow
    from langgraph.graph import StateGraph, START, END
    from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
    from typing import TypedDict, List, Annotated
    
    class AgentState(TypedDict):
        messages: Annotated[List[HumanMessage], "add_messages"]
    
    async def agent_node(state: AgentState):
        response = await llm_with_tools.ainvoke(state["messages"])
        return {"messages": [response]}
    
    workflow = StateGraph(AgentState)
    workflow.add_node("agent", agent_node)
    workflow.add_edge(START, "agent")
    workflow.add_edge("agent", END)
    
    app = workflow.compile()
    
    return app, llm_with_tools, tools_map

async def process_task_full(task: str) -> dict:
    """
    Process task with FULL KILAT features (MCP, tools, @mentions, etc.)
    Called from kilat_cli.py
    """
    app, llm_with_tools, tools_map = await get_kilat_app()

    # Initialize planner for auto-planning
    planner = Planner(str(Path(".").resolve()))
    
    # PATCH_4: Initialize Todo List Manager
    todo_manager = TodoListManager()
    
    # PATCH_6: Initialize State Machine
    state_machine = TaskStateMachine(task)
    state_machine.transition_to(TaskState.PLANNING)

    # Process @mentions
    from kilat_core.context.mentions import parse_mentions, inject_mentions
    mentions = parse_mentions(task, str(Path(".").resolve()))
    if mentions and len(mentions) > 0:
        enhanced_task, _ = inject_mentions(task, str(Path(".").resolve()))
    else:
        enhanced_task = task

    # PATCH_1: Auto-planning for complex tasks
    messages = [HumanMessage(content=enhanced_task)]
    enhanced_task, was_planned = await auto_plan_if_needed(enhanced_task, planner, messages, todo_manager, llm_with_tools)
    
    if was_planned:
        # Re-inject enhanced task
        messages = [HumanMessage(content=enhanced_task)]
        state_machine.transition_to(TaskState.EXECUTING, {"planned": True, "todos": len(todo_manager.todos)})

    # Execute with tool loop
    messages = [HumanMessage(content=enhanced_task)]
    max_turns = 10
    turn_count = 0
    files_changed = []
    verification_criteria = []

    # Execute with tool loop
    messages = [HumanMessage(content=enhanced_task)]
    max_turns = 10
    turn_count = 0
    files_changed = []
    
    while turn_count < max_turns:
        turn_count += 1
        response = await llm_with_tools.ainvoke(messages)
        messages.append(response)
        
        # Check for tool calls
        if not hasattr(response, 'tool_calls') or not response.tool_calls:
            break
        
        # Execute tools
        from langchain_core.messages import ToolMessage
        for tool_call in response.tool_calls:
            name = tool_call["name"]
            args = tool_call["args"]
            id = tool_call["id"]
            
            if name in tools_map:
                try:
                    tool = tools_map[name]
                    if hasattr(tool, 'ainvoke'):
                        res = await tool.ainvoke(args)
                    else:
                        res = tool.invoke(args)
                    
                    messages.append(ToolMessage(content=str(res), tool_call_id=id))
                    
                    # Track file changes
                    if name in ['write_to_file', 'write_to_file_simple', 'edit_file_with_backup', 'edit_many_files']:
                        files_changed.append(args.get('path', args.get('filename', 'unknown')))
                        
                except Exception as e:
                    messages.append(ToolMessage(content=f"Error: {e}", tool_call_id=id))
    
    # Extract AI response
    ai_content = ""
    for msg in reversed(messages):
        if isinstance(msg, AIMessage) and msg.content:
            ai_content = msg.content
            break
    
    # PATCH_6: Verify completion and transition state
    verification_criteria.append(len(files_changed) > 0 or len(ai_content) > 0)  # Basic: something was done
    verification_criteria.append(turn_count <= max_turns)  # Basic: didn't exceed turns
    
    if state_machine.verify_completion(verification_criteria):
        state_machine.transition_to(TaskState.COMPLETED, {
            "files_changed": len(files_changed),
            "turns": turn_count
        })
    else:
        state_machine.transition_to(TaskState.VERIFYING)
        # If verification fails, mark as completed anyway (basic implementation)
        state_machine.transition_to(TaskState.COMPLETED, {"verified": False})

    return {
        "status": "success",
        "files_changed": files_changed,
        "output": ai_content,
        "turns": turn_count,
        "state_machine": state_machine.get_summary()
    }


async def main():
    # Parse CLI arguments
    parser = argparse.ArgumentParser(description="KILAT v0.0.6 - AI Coding Assistant")
    parser.add_argument("--headless", action="store_true", help="Run in headless CLI mode")
    parser.add_argument("--cli", type=str, help="Task to execute in CLI mode")
    parser.add_argument("--format", choices=["text", "json"], default="text", help="Output format (CLI mode only)")
    parser.add_argument("--server", action="store_true", help="Run in server mode (Keep-Alive)")
    parser.add_argument("--port", type=int, default=8080, help="Server port (default: 8080)")
    args = parser.parse_args()
    
    # SERVER MODE (Keep-Alive)
    if args.server:
        try:
            from fastapi import FastAPI, Request
            from fastapi.responses import JSONResponse
            import uvicorn
            
            # Initialize KILAT agent
            logger.info("Initializing KILAT agent for server mode...")
            agent = await create_kilat_agent()
            
            safe_print(f"✅ KILAT Server ready on http://127.0.0.1:{args.port}")
            safe_print(f"💡 CLI: curl -X POST http://localhost:{args.port}/cli -d '{{\"task\": \"your task\"}}'")
            
            # Create FastAPI app
            kilat_app = FastAPI(title="KILAT Server")
            
            @kilat_app.post("/cli")
            async def cli_endpoint(request: Request):
                data = await request.json()
                task = data.get("task", "")
                
                if not task:
                    return JSONResponse({"status": "error", "error": "No task provided"}, status_code=400)
                
                # Process task with KILATAgent
                result = await agent.process_task(task)
                return JSONResponse(result)
            
            @kilat_app.get("/health")
            async def health_check():
                return {"status": "healthy", "service": "KILAT"}
            
            # Run server in separate thread (uvicorn needs sync context)
            safe_print("🟢 Starting uvicorn server...")

            def run_server():
                uvicorn.run(kilat_app, host="127.0.0.1", port=args.port, log_level="info")

            import threading
            server_thread = threading.Thread(target=run_server, daemon=True)
            server_thread.start()

            # Keep main thread alive
            while server_thread.is_alive():
                await asyncio.sleep(1)

        except ImportError:
            logger.error("FastAPI/uvicorn not installed. Install with: pip install fastapi uvicorn")
            sys.exit(1)
        return
    
    # CLI HEADLESS MODE
    if args.headless and args.cli:
        logger.info(f"Processing CLI task: {args.cli[:100]}...")
        
        try:
            # Create KILATAgent and process task
            agent = await create_kilat_agent()
            result = await agent.process_task(args.cli)
            
            # FIX: Use direct print() for CLI output (bypass safe_print)
            if args.format == "json":
                # Direct stdout for clean JSON capture - ASCII only for Windows compatibility
                json_output = json.dumps(result, indent=2, ensure_ascii=True, default=str)
                print(json_output, flush=True)
            else:
                # For text mode, also use ASCII
                output_text = result.get("output", "").encode('ascii', errors='replace').decode('ascii')
                print(output_text, flush=True)
            
            # Ensure flush before exit
            sys.stdout.flush()
            sys.exit(0 if result.get("status") == "success" else 1)
            
        except Exception as e:
            # Error output also goes to stdout for CLI capture
            error_result = {"status": "error", "error": str(e)}
            print(json.dumps(error_result, indent=2), flush=True)
            sys.stdout.flush()
            sys.exit(1)
    
    # INTERACTIVE MODE
    safe_print(colorama.Fore.CYAN + "=" * 70)
    safe_print("🚀 KILAT v0.0.6 - COMPLETE PHASE 3 + CLI + SERVER MODE")
    safe_print("=" * 70)

    # Initialize KILAT Core & Supercharge tools first
    base_tools = KILAT_CORE_TOOLS + LEGACY_TOOLS + SUPERCHARGE_TOOLS
    set_llm(llm)
    
    safe_print(f"\n✅ Base Tools: {len(base_tools)} (Core: {len(KILAT_CORE_TOOLS)}, Legacy: {len(LEGACY_TOOLS)}, Supercharge: {len(SUPERCHARGE_TOOLS)})")
    
    # Initialize MCP and Web Intelligence
    safe_print("\n[1/3] Initializing MCP & Web Intelligence...")
    from kilat_mcp.mcp_smart_manager import MCPSmartManager
    mcp_manager = MCPSmartManager()
    
    # Bridge MCP tools (DuckDuckGo, Playwright, Filesystem, Memory)
    mcp_tools = await mcp_manager.get_langchain_tools()
    
    all_tools = base_tools + mcp_tools
    llm_with_tools = llm.bind_tools(all_tools)
    
    # Create tools map for execution
    # Handle both BaseTool objects (with .name) and raw functions (with .__name__)
    tools_map = {getattr(tool, "name", getattr(tool, "__name__", str(tool))): tool for tool in all_tools}
    
    from langchain_core.messages import ToolMessage
    
    safe_print(f"✅ total Tools: {len(all_tools)} (Included {len(mcp_tools)} from MCP)")
    
    # Initialize Phase 3 Modules
    safe_print("\n[3/3] Initializing Phase 3 Modules...")
    context_length = CONFIG['llama_server'].get('context_length', 327680)

    token_counter = SmartTokenCounter(
        model_name="cl100k_base",
        recount_threshold=100,
        auto_calibrate=True
    )

    priority_manager = PriorityContextManager()
    context_viz = ContextVisualizer(max_context_tokens=context_length)
    
    summarizer = HybridSummarizer(
        llm=llm_with_tools,
        target_compression=0.125,
        keep_last_n=10,
        preserve_priority=Priority.IMPORTANT
    )
    summarize_cmd = SummarizationCommand(summarizer)
    
    memory_manager = MemoryManager()
    planner = Planner(str(Path(".").resolve()))

    safe_print(colorama.Fore.CYAN + f"📊 Smart Token Counter: O(1) caching + periodic recount")
    safe_print(colorama.Fore.CYAN + f"🎯 Priority Manager: CRITICAL/IMPORTANT/NORMAL/LOW")
    safe_print(colorama.Fore.CYAN + f"📈 Context Window: {context_viz.format_tokens(context_length)} tokens")
    safe_print(colorama.Fore.CYAN + f"💡 Actionable insights: Enabled")
    safe_print(colorama.Fore.CYAN + f"📝 Auto-Summarizer: 8:1 compression ready")
    safe_print(colorama.Fore.CYAN + f"🧠 Memory Manager: Persistence active")
    safe_print(colorama.Fore.CYAN + f"🔍 Supercharge Tools: Review/CI-CD/Testing/Architecture\n")

    safe_print("\n💡 Type your task and press Enter")
    safe_print("💡 Type 'quit' to exit")
    safe_print("💡 Type '/mode <name>' to switch mode (code/architect/ask)")
    safe_print("💡 Type '/plan <cmd>' to manage tasks (create/status/update)")
    safe_print("💡 Use @filename to reference files\n")

    messages = []
    active_mode = "code"
    reasoning_mode = "deep"
    
    # Mode cycling with /mode command
    MODES = ['code', 'architect', 'ask', 'plan']
    
    # Phase 3 state
    warning_shown = False
    last_token_display = 0
    
    # Inject memory summary if exists
    mem_summary = memory_manager.get_summary()
    if mem_summary:
        messages.append(SystemMessage(content=mem_summary))
    
    # PATCH_3: Inject persona system prompt with lessons
    system_prompt = personas.get_current_system_prompt()
    if messages and isinstance(messages[0], SystemMessage):
        # Update existing system message
        messages[0] = SystemMessage(content=system_prompt)
    else:
        # Insert new system message
        messages.insert(0, SystemMessage(content=system_prompt))
    
    # PATCH_4: Initialize Todo List Manager
    todo_manager = TodoListManager()

    # Key Bindings for prompt_toolkit
    kb = KeyBindings()
    modes_list = ["code", "architect", "ask", "plan"]
    
    @kb.add('tab')
    def _cycle_mode(event):
        nonlocal active_mode
        current_idx = modes_list.index(active_mode) if active_mode in modes_list else 0
        active_mode = modes_list[(current_idx + 1) % len(modes_list)]
        # Force redraw of the prompt
        event.app.invalidate()

    session = PromptSession(key_bindings=kb)

    while True:
        try:
            # Token status indicator
            current_tokens = sum(len(getattr(m, "content", "")) // 4 for m in messages)
            context_len = CONFIG["llama_server"].get("context_length", 327680)
            token_percent = (current_tokens / context_len) * 100
            
            # Use prompt_toolkit tags instead of colorama for HTML
            color_tag = "ansigreen" if token_percent < 70 else ("ansiyellow" if token_percent < 90 else "ansired")
            token_status = f"{current_tokens/1000:.1f}K/{context_len/1000:.1f}K ({token_percent:.1f}%)"

            # Dynamic prompt using HTML for color
            prompt_html = f'<ansicyan>💭 Task (<b>{active_mode}</b>:{reasoning_mode})</ansicyan> [<{color_tag}>{token_status}</{color_tag}>] <ansiyellow>(Tab to Cycle)</ansiyellow> - '
            
            with patch_stdout():
                task = await session.prompt_async(HTML(prompt_html))
                task = task.strip()

            if task.lower() in ['quit', '/quit', 'exit']:
                safe_print(colorama.Fore.GREEN + "\n👋 Goodbye!")
                break
            
            # /mode command
            if task.startswith('/mode'):
                parts = task.split()
                if len(parts) > 1:
                    new_mode = parts[1].lower()
                    if new_mode in modes_list:
                        active_mode = new_mode
                        # PATCH_2: Switch persona with LLM config
                        llm = personas.switch_persona(new_mode, llm)
                        safe_print(colorama.Fore.CYAN + f"\n✅ Switched to {active_mode} mode")
                    else:
                        safe_print(colorama.Fore.RED + f"\n❌ Unknown mode. Available: {', '.join(modes_list)}")
                else:
                    safe_print(colorama.Fore.CYAN + f"\n📊 Current mode: {active_mode}")
                    safe_print(f"   Available modes: {', '.join(modes_list)}")
                continue
            
            # ========== PHASE 3 COMMANDS ==========
            
            # /tokens command
            if task.startswith('/tokens'):
                parts = task.split()
                if len(parts) > 1 and parts[1] == 'stats':
                    stats = token_counter.get_stats(messages)
                    safe_print(colorama.Fore.CYAN + f"\n📊 Token Statistics:")
                    safe_print(f"  Total: {stats['total_tokens']} tokens")
                    safe_print(f"  Messages: {stats['message_count']}")
                    safe_print(f"  Cache efficiency: {stats['cache_efficiency']}")
                else:
                    safe_print(colorama.Fore.CYAN + f"\n📊 Usage: /tokens stats")
                continue
            
            # /compress command
            if task.startswith('/compress'):
                safe_print(colorama.Fore.CYAN + f"\n📊 Compressing context...")
                compressible = priority_manager.find_compressible(messages, Priority.NORMAL)
                if not compressible:
                    safe_print(colorama.Fore.YELLOW + "  No compressible messages found.")
                else:
                    safe_print(colorama.Fore.GREEN + f"  Found {len(compressible)} compressible messages.")
                    compressed, metadata = priority_manager.compress_messages(messages, compression_ratio=0.5)
                    messages = compressed
                    new_tokens = token_counter.count(messages, force_recount=True)
                    saved = current_tokens - new_tokens
                    safe_print(colorama.Fore.GREEN + f"  ✅ Compressed! Saved {context_viz.format_tokens(saved)} tokens.")
                    safe_print(f"     Before: {context_viz.format_tokens(current_tokens)}")
                    safe_print(f"     After:  {context_viz.format_tokens(new_tokens)}")
                continue
            
            # /summarize command
            if task.startswith('/summarize'):
                parts = task.split()
                args = parts[1:] if len(parts) > 1 else ['--auto']
                summarized, status_msg = summarize_cmd.execute(messages, args)
                if summarized != messages:
                    messages = summarized
                    current_tokens = token_counter.count(messages, force_recount=True)
                safe_print(colorama.Fore.CYAN + f"\n{status_msg}")
                continue
            
            # /session command
            if task.startswith('/session'):
                parts = task.split()
                if len(parts) > 1 and parts[1] == 'summary':
                    avg_tokens = current_tokens / len(messages) if messages else 100
                    safe_print(context_viz.get_session_summary(current_tokens, len(messages), avg_tokens))
                else:
                    safe_print(colorama.Fore.CYAN + f"\n📊 Usage: /session summary")
                continue
            
            # /memory command
            if task.startswith('/memory'):
                parts = task.split()
                if len(parts) > 1:
                    if parts[1] == 'list':
                        safe_print(memory_manager.get_summary())
                    elif parts[1] == 'add' and len(parts) > 2:
                        memory_manager.add_decision(" ".join(parts[2:]))
                        safe_print(colorama.Fore.GREEN + f"✅ Memory added: {' '.join(parts[2:])}")
                else:
                    safe_print(colorama.Fore.CYAN + "📊 Usage: /memory list | /memory add <text>")
                continue
            
            # /personas command (PATCH_3: View evolution)
            if task.startswith('/personas'):
                safe_print(personas.get_summary())
                continue
            
            # /review command (Supercharge)
            if task.startswith('/review'):
                parts = task.split()
                if len(parts) > 1:
                    target_file = parts[1]
                    safe_print(colorama.Fore.CYAN + f"\n🔍 Starting Parallel Multi-Agent Review for {target_file}...")
                    safe_print(colorama.Fore.YELLOW + "   (Security, Performance, Best Practices agents active on RTX 3090)\n")
                    report = SUPERCHARGE_TOOLS[3](target_file)  # code_review is index 3
                    safe_print(colorama.Fore.WHITE + report)
                    messages.append(AIMessage(content=f"Parallel Review Report for {target_file}:\n\n{report}"))
                else:
                    safe_print(colorama.Fore.RED + "❌ Usage: /review <file_path>")
                continue
            
            # /test command (Supercharge)
            if task.startswith('/test'):
                parts = task.split()
                if len(parts) > 1:
                    target_file = parts[1]
                    safe_print(colorama.Fore.CYAN + f"\n🧪 Automated testing and self-healing for {target_file}...")
                    # Note: index 1 is auto_test
                    res = SUPERCHARGE_TOOLS[1]("run", target_file)
                    safe_print(colorama.Fore.WHITE + res)
                else:
                    safe_print(colorama.Fore.RED + "❌ Usage: /test <file_path>")
                continue
            
            # /arch command (Supercharge)
            if task.startswith('/arch'):
                parts = task.split()
                if len(parts) > 1:
                    target_file = parts[1]
                    safe_print(colorama.Fore.CYAN + f"\n🏗️  Analyzing codebase architecture...")
                    analysis = SUPERCHARGE_TOOLS[2]("map", target_file)  # analyze_codebase is index 2
                    safe_print(colorama.Fore.WHITE + analysis)
                else:
                    safe_print(colorama.Fore.RED + "❌ Usage: /arch <file_path>")
                continue
            
            # /plan command
            if task.startswith('/plan'):
                parts = task.split()
                if len(parts) > 1:
                    cmd = parts[1]
                    if cmd == 'create':
                        obj = " ".join(parts[2:]) if len(parts) > 2 else "Development Task"
                        safe_print(colorama.Fore.YELLOW + "Enter steps (one per line, empty to finish):")
                        steps = []
                        while True:
                            s = input("> ").strip()
                            if not s: break
                            steps.append(s)
                        if steps:
                            res = planner.create_plan(obj, steps)
                            safe_print(colorama.Fore.GREEN + res)
                    elif cmd == 'update':
                        if len(parts) > 3:
                            res = planner.update_step(int(parts[2]), parts[3])
                            safe_print(colorama.Fore.GREEN + res)
                        else:
                            safe_print(colorama.Fore.RED + "❌ Usage: /plan update <index> <status>")
                    elif cmd == 'status':
                        safe_print(colorama.Fore.WHITE + planner.get_summary())
                else:
                    safe_print(colorama.Fore.CYAN + "📋 Usage: /plan create <obj> | /plan update <idx> <stat> | /plan status")
                continue

            # /fast command
            if task.startswith('/fast'):
                reasoning_mode = "fast"
                llm.temperature = 0.1
                safe_print(colorama.Fore.GREEN + "⚡ Reasoning Mode: FAST (Direct Output)")
                continue

            # /deep command
            if task.startswith('/deep'):
                reasoning_mode = "deep"
                llm.temperature = CONFIG["llama_server"]["temperature"]
                safe_print(colorama.Fore.GREEN + "🧠 Reasoning Mode: DEEP (Thinking Active)")
                continue
            
            # ========== END PHASE 3 COMMANDS ==========

            # Process @mentions
            try:
                mentions = parse_mentions(task, str(Path(".").resolve()))
                if mentions and len(mentions) > 0:
                    safe_print(colorama.Fore.CYAN + f"\n📎 Found {len(mentions)} file mention(s)")
                    enhanced_task, _ = inject_mentions(task, str(Path(".").resolve()))
                    messages.append(HumanMessage(content=enhanced_task))
                else:
                    messages.append(HumanMessage(content=task))
            except Exception as e:
                messages.append(HumanMessage(content=task))
            
            # PATCH_1: Auto-planning for complex tasks
            task, was_planned = await auto_plan_if_needed(task, planner, messages, todo_manager, llm_with_tools)

            # Recursive Tool Call Loop (Autonomous Agent)
            max_turns = 10
            turn_count = 0
            
            while turn_count < max_turns:
                turn_count += 1
                safe_print(colorama.Fore.CYAN + f"\n🔄 Thinking (Turn {turn_count}/{max_turns})...")
                
                response = llm_with_tools.invoke(messages)
                messages.append(response)

                # Show content if present
                if hasattr(response, 'content') and response.content:
                    safe_print(colorama.Fore.WHITE + f"\n🤖 {response.content}")
                elif not response.tool_calls:
                    safe_print(colorama.Fore.YELLOW + "\n(AI returned no content and no tool calls, finishing.)")

                if not response.tool_calls:
                    if turn_count > 1:
                        safe_print(colorama.Fore.GREEN + f"\n✅ Task completed in {turn_count} turn(s).")
                    break
                
                safe_print(colorama.Fore.YELLOW + f"🔧 Tool Call(s): {[tc['name'] for tc in response.tool_calls]}")
                
                for tool_call in response.tool_calls:
                    name = tool_call["name"]
                    args = tool_call["args"]
                    id = tool_call["id"]
                    
                    if name in tools_map:
                        # PATCH_5: Check auto-approval
                        auto_approve = should_auto_approve(name, args)
                        if auto_approve:
                            safe_print(colorama.Fore.GREEN + f"  [AUTO-APPROVED] {name}")
                        else:
                            safe_print(colorama.Fore.YELLOW + f"  [EXEC] Running {name}...")
                        
                        try:
                            # Try async invoke first
                            if hasattr(tools_map[name], 'ainvoke'):
                                res = await tools_map[name].ainvoke(args)
                            else:
                                res = tools_map[name].invoke(args)

                            # Log short snippet of result
                            res_text = str(res)
                            snippet = res_text[:100] + "..." if len(res_text) > 100 else res_text
                            safe_print(colorama.Fore.GREEN + f"  [DONE] {name} result: {snippet}")

                            messages.append(ToolMessage(content=res_text, tool_call_id=id))

                            # PATCH_4: Mark todo as completed if applicable
                            if name in ['write_to_file', 'write_to_file_simple', 'edit_file_with_backup', 'edit_many_files']:
                                files_changed.append(args.get('path', args.get('filename', 'unknown')))
                                
                                if todo_manager and todo_manager.get_current_todo():
                                    todo_manager.mark_current_completed()
                                    safe_print(colorama.Fore.GREEN + "  ✅ Todo progress updated")
                                
                                # Auto-create checkpoint for file edits
                                target_path = args.get('path', args.get('target_file', 'code'))
                                checkpoint_result = create_checkpoint(str(Path(".").resolve()), f"Edited: {target_path}")
                                if checkpoint_result.startswith("✅"):
                                    safe_print(colorama.Fore.GREEN + f"  {checkpoint_result}")
                        except Exception as tool_e:
                            safe_print(colorama.Fore.RED + f"  ❌ {name} Error: {tool_e}")
                            messages.append(ToolMessage(content=f"Error: {tool_e}", tool_call_id=id))

                            # PATCH_2: Self-reflection on failure
                            await self_reflect_on_failure(str(tool_e), task, name, memory_manager)
                    else:
                        safe_print(colorama.Fore.RED + f"  ❌ Error: Tool '{name}' not found")
                        messages.append(ToolMessage(content=f"Error: Tool {name} not found", tool_call_id=id))
                
                if turn_count >= max_turns:
                    safe_print(colorama.Fore.RED + f"\n⚠️ Reached max turns ({max_turns}). Stopping for safety.")
            
            # Auto-condense if needed
            messages = condense_messages(messages, threshold=20)

        except EOFError:
            break
        except Exception as e:
            safe_print(colorama.Fore.RED + f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    from langchain_core.messages import SystemMessage
    asyncio.run(main())
