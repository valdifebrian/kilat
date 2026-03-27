"""
KILAT Context Condensation
Handles message pruning and summarization to manage long conversations.
"""

from typing import List, Any

def condense_messages(messages: List[Any], threshold: int = 15) -> List[Any]:
    """
    Prunes the message history if it exceeds the threshold.
    Keeps the system message and the last N messages.
    """
    if len(messages) <= threshold:
        return messages
    
    # Always keep the first message (usually system prompt)
    system_message = messages[0]
    
    # Keep the last N messages
    # We want an even number to keep user/assistant pairs intact
    keep_count = threshold - 1
    if keep_count % 2 != 0:
        keep_count -= 1
        
    pruned_messages = [system_message] + messages[-keep_count:]
    
    print(f"✂️  Context condensed: Kept {len(pruned_messages)}/{len(messages)} messages.")
    return pruned_messages
