"""
KILAT Token Counter
Real-time token counting for context window management
"""

import tiktoken
from typing import List, Union
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage


class TokenCounter:
    """
    Count tokens for messages, code, and conversations.
    
    Supports multiple tokenizers:
    - cl100k_base: GPT-4, GPT-3.5-turbo, text-embedding-ada-002
    - p50k_base: Code models, text-davinci-002, text-davinci-003
    - r50k_base: GPT-3 models like davinci
    
    For local models (OmniCoder-VL), we use cl100k_base as approximation.
    """
    
    def __init__(self, model_name: str = "cl100k_base"):
        """
        Initialize token counter.
        
        Args:
            model_name: Tiktoken encoding name or model name
        """
        self.model_name = model_name
        try:
            self.encoding = tiktoken.get_encoding(model_name)
        except KeyError:
            # Fallback to cl100k_base if model not found
            self.encoding = tiktoken.get_encoding("cl100k_base")
            self.model_name = "cl100k_base"
    
    def count_text(self, text: str) -> int:
        """
        Count tokens in a text string.
        
        Args:
            text: Text to count tokens for
            
        Returns:
            Number of tokens
        """
        if not text:
            return 0
        return len(self.encoding.encode(text))
    
    def count_message(self, message: BaseMessage) -> int:
        """
        Count tokens in a LangChain message.
        
        Args:
            message: LangChain message object
            
        Returns:
            Number of tokens
        """
        if isinstance(message, HumanMessage):
            # Human message: count content only
            return self.count_text(message.content)
        elif isinstance(message, AIMessage):
            # AI message: count content + tool calls if present
            tokens = self.count_text(message.content)
            if hasattr(message, 'tool_calls') and message.tool_calls:
                for tool_call in message.tool_calls:
                    tokens += self.count_text(str(tool_call))
            return tokens
        elif isinstance(message, SystemMessage):
            # System message: count content
            return self.count_text(message.content)
        else:
            # Generic message: count string representation
            return self.count_text(str(message))
    
    def count_messages(self, messages: List[BaseMessage]) -> int:
        """
        Count tokens in a list of messages.
        
        Args:
            messages: List of LangChain messages
            
        Returns:
            Total number of tokens
        """
        total = 0
        for msg in messages:
            total += self.count_message(msg)
        
        # Add overhead for message formatting (approx 4 tokens per message)
        total += len(messages) * 4
        
        return total
    
    def count_code(self, code: str, language: str = "python") -> int:
        """
        Count tokens in code snippet.
        
        Args:
            code: Code to count tokens for
            language: Programming language (for future use)
            
        Returns:
            Number of tokens
        """
        # Code typically has different tokenization patterns
        # For now, use standard counting
        return self.count_text(code)
    
    def count_file(self, filepath: str, max_chars: int = 100000) -> int:
        """
        Count tokens in a file.
        
        Args:
            filepath: Path to file
            max_chars: Maximum characters to read (safety limit)
            
        Returns:
            Number of tokens, or -1 if file not found
        """
        from pathlib import Path
        
        file_path = Path(filepath)
        if not file_path.exists():
            return -1
        
        try:
            content = file_path.read_text(encoding="utf-8")[:max_chars]
            return self.count_text(content)
        except Exception:
            return -1
    
    def estimate_cost(self, tokens: int, price_per_1k: float = 0.0001) -> float:
        """
        Estimate cost for token usage.
        
        Args:
            tokens: Number of tokens
            price_per_1k: Price per 1000 tokens (default: $0.0001 for local)
            
        Returns:
            Estimated cost in USD
        """
        return (tokens / 1000) * price_per_1k
    
    def get_stats(self, messages: List[BaseMessage]) -> dict:
        """
        Get detailed token statistics.
        
        Args:
            messages: List of messages
            
        Returns:
            Dictionary with token statistics
        """
        total_tokens = self.count_messages(messages)
        
        # Count by message type
        human_tokens = sum(
            self.count_message(msg) for msg in messages if isinstance(msg, HumanMessage)
        )
        ai_tokens = sum(
            self.count_message(msg) for msg in messages if isinstance(msg, AIMessage)
        )
        system_tokens = sum(
            self.count_message(msg) for msg in messages if isinstance(msg, SystemMessage)
        )
        
        return {
            "total": total_tokens,
            "human": human_tokens,
            "ai": ai_tokens,
            "system": system_tokens,
            "message_count": len(messages),
            "avg_per_message": total_tokens / len(messages) if messages else 0
        }
