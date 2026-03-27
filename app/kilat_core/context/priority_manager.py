"""
KILAT Priority Context Manager
Manage context window with priority-based retention and intelligent trimming.

Priority Levels:
- CRITICAL: Tool calls, file edits, user decisions (NEVER delete)
- IMPORTANT: Architecture decisions, code explanations (delete last)
- NORMAL: Regular chat (delete when needed)
- LOW: Redundant messages, failed attempts (delete first)
"""

from typing import List, Dict, Tuple, Optional
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from enum import Enum
import re


class Priority(Enum):
    """Message priority levels"""
    CRITICAL = 0    # Never delete
    IMPORTANT = 1   # Delete only when absolutely necessary
    NORMAL = 2      # Delete when needed
    LOW = 3         # Delete first


class PriorityContextManager:
    """
    Manage context window with priority-based retention.
    
    Features:
    - Automatic message classification
    - Priority-based trimming
    - Summarization support
    - Critical message preservation
    """
    
    # Classification patterns
    CRITICAL_PATTERNS = [
        r'tool.?call', r'function.?call',
        r'edited', r'created', r'wrote to', r'saved to',
        r'decided to', r'architecture', r'design pattern',
        r'```',  # Code blocks
        r'<file.*?>',  # File operations
    ]
    
    IMPORTANT_PATTERNS = [
        r'explanation', r'rationale', r'reasoning',
        r'implementation', r'algorithm', r'structure',
        r'best practice', r'recommendation',
    ]
    
    LOW_PATTERNS = [
        r'sorry', r'i can\'t', r'unable to',
        r'failed to', r'error:', r'let me try',
        r'one more time', r'actually,', r'wait,',
        r'thinking', r'let me see',
    ]
    
    def __init__(self):
        """Initialize priority context manager"""
        self._priority_cache = {}  # message_index -> Priority
        self._compiled_patterns = {
            'critical': [re.compile(p, re.IGNORECASE) for p in self.CRITICAL_PATTERNS],
            'important': [re.compile(p, re.IGNORECASE) for p in self.IMPORTANT_PATTERNS],
            'low': [re.compile(p, re.IGNORECASE) for p in self.LOW_PATTERNS],
        }
    
    def classify_message(self, message: BaseMessage, index: int = 0) -> Priority:
        """
        Classify message priority based on content analysis.
        
        Args:
            message: Message to classify
            index: Message index in conversation
            
        Returns:
            Priority level
        """
        # Check cache first
        if index in self._priority_cache:
            return self._priority_cache[index]
        
        # Get message content
        content = self._get_message_content(message)
        content_lower = content.lower()
        
        # Rule 1: Tool calls are CRITICAL
        if hasattr(message, 'tool_calls') and message.tool_calls:
            priority = Priority.CRITICAL
        # Rule 2: Check for code blocks (CRITICAL)
        elif '```' in content:
            priority = Priority.CRITICAL
        # Rule 3: Check critical patterns
        elif any(kw in content_lower for kw in ['edited', 'created', 'wrote to', 'saved to', 'decided to', 'architecture', 'design']):
            priority = Priority.CRITICAL
        # Rule 4: Check important patterns
        elif any(kw in content_lower for kw in ['explanation', 'rationale', 'reasoning', 'implementation', 'algorithm', 'structure', 'best practice']):
            priority = Priority.IMPORTANT
        # Rule 5: Check low priority patterns
        elif any(kw in content_lower for kw in ['sorry', 'i can\'t', 'unable to', 'failed to', 'error:', 'let me try', 'actually,', 'wait,']):
            priority = Priority.LOW
        # Rule 6: System messages are IMPORTANT
        elif isinstance(message, SystemMessage):
            priority = Priority.IMPORTANT
        # Rule 7: Recent messages are more important (last 20%)
        elif index > 0.8 * 100:
            priority = Priority.IMPORTANT
        else:
            priority = Priority.NORMAL
        
        # Cache and return
        self._priority_cache[index] = priority
        return priority
    
    def _get_message_content(self, message: BaseMessage) -> str:
        """Extract searchable content from message"""
        parts = []
        
        # Content
        if hasattr(message, 'content') and message.content:
            parts.append(str(message.content))
        
        # Tool calls
        if hasattr(message, 'tool_calls') and message.tool_calls:
            for tc in message.tool_calls:
                parts.append(str(tc))
        
        return ' '.join(parts)
    
    def _matches_patterns(self, text: str, patterns: List[re.Pattern]) -> bool:
        """Check if text matches any pattern"""
        return any(p.search(text) for p in patterns)
    
    def trim_to_fit(
        self,
        messages: List[BaseMessage],
        max_tokens: int,
        current_tokens: int,
        token_counter
    ) -> Tuple[List[BaseMessage], Dict]:
        """
        Trim messages to fit within token limit.
        
        Strategy:
        1. Keep all CRITICAL messages
        2. Keep IMPORTANT until absolutely necessary
        3. Remove LOW priority first
        4. Remove NORMAL if still over limit
        5. Summarize instead of delete when possible
        
        Args:
            messages: List of messages
            max_tokens: Maximum token limit
            current_tokens: Current token count
            token_counter: TokenCounter instance
            
        Returns:
            Tuple of (trimmed_messages, metadata)
        """
        metadata = {
            "original_count": len(messages),
            "original_tokens": current_tokens,
            "removed": [],
            "summarized": [],
            "preserved": []
        }
        
        # Check if trimming is needed
        if current_tokens <= max_tokens * 0.9:  # Keep 10% buffer
            metadata["preserved"] = list(range(len(messages)))
            return messages, metadata
        
        # Classify all messages
        classified = []
        for i, msg in enumerate(messages):
            priority = self.classify_message(msg, i)
            classified.append((i, msg, priority))
        
        # Sort by priority (LOW first, then NORMAL, then IMPORTANT)
        # CRITICAL messages are never removed
        classified.sort(key=lambda x: x[2].value)
        
        # Remove messages until we fit
        trimmed_messages = list(messages)
        tokens_saved = 0
        
        for idx, msg, priority in classified:
            # Never remove CRITICAL
            if priority == Priority.CRITICAL:
                continue
            
            # Check if we fit now
            new_tokens = current_tokens - tokens_saved
            if new_tokens <= max_tokens * 0.9:
                break
            
            # Remove this message
            msg_tokens = token_counter._count_message_tokens(msg)
            trimmed_messages.remove(msg)
            tokens_saved += msg_tokens
            metadata["removed"].append({
                "index": idx,
                "priority": priority.name,
                "tokens": msg_tokens
            })
        
        metadata["final_count"] = len(trimmed_messages)
        metadata["final_tokens"] = current_tokens - tokens_saved
        metadata["tokens_saved"] = tokens_saved
        
        return trimmed_messages, metadata
    
    def compress_messages(
        self,
        messages: List[BaseMessage],
        compression_ratio: float = 0.5
    ) -> Tuple[List[BaseMessage], Dict]:
        """
        Compress messages by summarizing LOW/NORMAL priority.
        
        Args:
            messages: List of messages
            compression_ratio: Target compression (0.5 = 50% reduction)
            
        Returns:
            Tuple of (compressed_messages, metadata)
        """
        metadata = {
            "original_count": len(messages),
            "compressed": [],
            "skipped": []
        }
        
        compressed_messages = []
        
        for i, msg in enumerate(messages):
            priority = self.classify_message(msg, i)
            
            # CRITICAL and IMPORTANT: Keep as-is
            if priority in [Priority.CRITICAL, Priority.IMPORTANT]:
                compressed_messages.append(msg)
                metadata["skipped"].append(i)
                continue
            
            # LOW and NORMAL: Summarize
            if priority in [Priority.LOW, Priority.NORMAL]:
                summary = self._summarize_message(msg)
                compressed_messages.append(summary)
                metadata["compressed"].append({
                    "index": i,
                    "priority": priority.name,
                    "original_tokens": len(str(msg.content)),
                    "compressed_tokens": len(str(summary.content))
                })
        
        metadata["final_count"] = len(compressed_messages)
        
        return compressed_messages, metadata
    
    def _summarize_message(self, message: BaseMessage) -> BaseMessage:
        """
        Create a brief summary of a message.
        
        For now, simple truncation. Later: LLM-based summarization.
        """
        if not hasattr(message, 'content') or not message.content:
            return message
        
        content = str(message.content)
        
        # Truncate to 200 chars + ellipsis
        if len(content) > 200:
            summary = content[:200] + "... [compressed]"
        else:
            summary = content
        
        # Create new message with same type
        if isinstance(message, HumanMessage):
            return HumanMessage(content=summary)
        elif isinstance(message, AIMessage):
            return AIMessage(content=summary)
        elif isinstance(message, SystemMessage):
            return SystemMessage(content=summary)
        else:
            return type(message)(content=summary)
    
    def get_priority_stats(self, messages: List[BaseMessage]) -> Dict:
        """
        Get statistics about message priorities.
        
        Args:
            messages: List of messages
            
        Returns:
            Dictionary with priority statistics
        """
        stats = {
            "total": len(messages),
            "by_priority": {
                "CRITICAL": 0,
                "IMPORTANT": 0,
                "NORMAL": 0,
                "LOW": 0
            }
        }
        
        for i, msg in enumerate(messages):
            priority = self.classify_message(msg, i)
            stats["by_priority"][priority.name] += 1
        
        # Calculate percentages
        for key in stats["by_priority"]:
            if stats["total"] > 0:
                stats["by_priority"][f"{key}_pct"] = (
                    stats["by_priority"][key] / stats["total"] * 100
                )
        
        return stats
    
    def find_compressible(
        self,
        messages: List[BaseMessage],
        min_priority: Priority = Priority.NORMAL
    ) -> List[int]:
        """
        Find messages that can be safely compressed/removed.
        
        Args:
            messages: List of messages
            min_priority: Minimum priority to consider (NORMAL or LOW)
            
        Returns:
            List of compressible message indices
        """
        compressible = []
        
        for i, msg in enumerate(messages):
            priority = self.classify_message(msg, i)
            
            if priority.value >= min_priority.value:
                compressible.append(i)
        
        return compressible
    
    def reset_cache(self):
        """Reset priority cache"""
        self._priority_cache.clear()
