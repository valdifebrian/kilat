"""
KILAT Context Visualizer
Visual representation of context window usage with actionable insights.
"""

import colorama


class ContextVisualizer:
    """
    Visualize context window usage with colors, progress bars, and actionable recommendations.
    """
    
    # Warning thresholds
    WARNING_THRESHOLD = 0.80  # 80% - Yellow
    CRITICAL_THRESHOLD = 0.90  # 90% - Orange
    DANGER_THRESHOLD = 0.95  # 95% - Red
    
    def __init__(self, max_context_tokens: int = 327680):
        """
        Initialize context visualizer.
        
        Args:
            max_context_tokens: Maximum context window size (default: 320K for OmniCoder-VL)
        """
        self.max_context_tokens = max_context_tokens
        colorama.init()
    
    def get_usage_percentage(self, current_tokens: int) -> float:
        """Calculate usage percentage."""
        return min(current_tokens / self.max_context_tokens, 1.0)
    
    def get_status_color(self, percentage: float) -> str:
        """Get color code based on usage percentage."""
        if percentage >= self.DANGER_THRESHOLD:
            return colorama.Fore.RED
        elif percentage >= self.CRITICAL_THRESHOLD:
            return colorama.Fore.YELLOW
        elif percentage >= self.WARNING_THRESHOLD:
            return colorama.Fore.CYAN
        else:
            return colorama.Fore.GREEN
    
    def get_status_emoji(self, percentage: float) -> str:
        """Get emoji based on usage percentage."""
        if percentage >= self.DANGER_THRESHOLD:
            return "🔴"
        elif percentage >= self.CRITICAL_THRESHOLD:
            return "🟠"
        elif percentage >= self.WARNING_THRESHOLD:
            return "🟡"
        else:
            return "🟢"
    
    def format_tokens(self, tokens: int) -> str:
        """Format token count with K/M suffixes."""
        if tokens >= 1_000_000:
            return f"{tokens / 1_000_000:.1f}M"
        elif tokens >= 1_000:
            return f"{tokens / 1_000:.1f}K"
        else:
            return str(tokens)
    
    def create_progress_bar(self, percentage: float, width: int = 20) -> str:
        """Create ASCII progress bar."""
        filled_width = int(width * percentage)
        empty_width = width - filled_width
        
        color = self.get_status_color(percentage)
        
        bar = (
            color +
            "█" * filled_width +
            "░" * empty_width +
            colorama.Fore.RESET
        )
        
        return bar
    
    def visualize(self, current_tokens: int, show_bar: bool = True) -> str:
        """Create full context usage visualization."""
        percentage = self.get_usage_percentage(current_tokens)
        status_emoji = self.get_status_emoji(percentage)
        status_color = self.get_status_color(percentage)
        
        # Format: "🟢 45.2K/320K (14.1%)"
        current_str = self.format_tokens(current_tokens)
        max_str = self.format_tokens(self.max_context_tokens)
        pct_str = f"{percentage * 100:.1f}%"
        
        base_text = f"{status_emoji} {current_str}/{max_str} ({pct_str})"
        colored_text = f"{status_color}{base_text}{colorama.Fore.RESET}"
        
        if show_bar:
            bar = self.create_progress_bar(percentage)
            return f"{colored_text} {bar}"
        
        return colored_text
    
    def visualize_with_insights(
        self,
        insights: dict,
        show_bar: bool = True
    ) -> str:
        """
        Create visualization with actionable insights.
        
        Args:
            insights: Dictionary from SmartTokenCounter.get_insights()
            show_bar: Whether to show progress bar
            
        Returns:
            Formatted visualization with recommendations
        """
        # Base visualization
        base = self.visualize(insights["total_tokens"], show_bar)
        
        # Add status and recommendation
        lines = [base]
        
        # Status line
        status_line = f"\n{insights['status']}: {insights['remaining_messages']} messages remaining"
        if insights['status'] == "CRITICAL":
            status_line = colorama.Fore.RED + status_line + colorama.Fore.RESET
        elif insights['status'] == "HIGH":
            status_line = colorama.Fore.YELLOW + status_line + colorama.Fore.RESET
        elif insights['status'] == "MODERATE":
            status_line = colorama.Fore.CYAN + status_line + colorama.Fore.RESET
        
        lines.append(status_line)
        
        # Recommendation
        if insights['recommendation']:
            lines.append(f"\n{insights['recommendation']}")
        
        return "\n".join(lines)
    
    def get_actionable_warning(
        self,
        current_tokens: int,
        insights: dict = None
    ) -> str:
        """
        Get actionable warning message with specific recommendations.
        
        Args:
            current_tokens: Current token count
            insights: Optional insights dict (if None, uses basic warning)
            
        Returns:
            Warning message or empty string
        """
        percentage = self.get_usage_percentage(current_tokens)
        
        # Use insights if available
        if insights:
            return insights.get('recommendation', '')
        
        # Fallback to basic warning
        if percentage >= self.DANGER_THRESHOLD:
            remaining = self.max_context_tokens - current_tokens
            return (
                f"{colorama.Fore.RED}⚠️  CRITICAL: Only {self.format_tokens(remaining)} "
                f"tokens remaining! Run: /compress --auto{colorama.Fore.RESET}"
            )
        elif percentage >= self.CRITICAL_THRESHOLD:
            remaining = self.max_context_tokens - current_tokens
            return (
                f"{colorama.Fore.YELLOW}⚠️  WARNING: High context usage "
                f"({self.format_tokens(remaining)} remaining). Consider /compress{colorama.Fore.RESET}"
            )
        elif percentage >= self.WARNING_THRESHOLD:
            return (
                f"{colorama.Fore.CYAN}💡 Tip: Context at {percentage * 100:.1f}% "
                f"- use @mentions wisely{colorama.Fore.RESET}"
            )
        
        return ""
    
    def should_warn(self, current_tokens: int) -> bool:
        """Check if warning should be shown."""
        percentage = self.get_usage_percentage(current_tokens)
        return percentage >= self.WARNING_THRESHOLD
    
    def estimate_messages_remaining(
        self,
        avg_message_tokens: int,
        current_tokens: int
    ) -> int:
        """Estimate how many more messages can fit in context."""
        if avg_message_tokens <= 0:
            return 0
        
        remaining_tokens = self.max_context_tokens - current_tokens
        return max(0, int(remaining_tokens / avg_message_tokens))
    
    def get_session_summary(
        self,
        current_tokens: int,
        message_count: int,
        avg_tokens: float
    ) -> str:
        """
        Get session summary with statistics.
        
        Args:
            current_tokens: Current token count
            message_count: Number of messages
            avg_tokens: Average tokens per message
            
        Returns:
            Formatted summary string
        """
        percentage = self.get_usage_percentage(current_tokens)
        remaining = self.max_context_tokens - current_tokens
        remaining_msgs = self.estimate_messages_remaining(avg_tokens, current_tokens)
        
        lines = [
            f"\n{colorama.Fore.CYAN}{'='*50}{colorama.Fore.RESET}",
            f"{colorama.Fore.CYAN}📊 Session Summary{colorama.Fore.RESET}",
            f"{'='*50}",
            f"Messages: {message_count}",
            f"Tokens: {self.format_tokens(current_tokens)}/{self.format_tokens(self.max_context_tokens)} ({percentage*100:.1f}%)",
            f"Average: {avg_tokens:.0f} tokens/message",
            f"Remaining: {self.format_tokens(remaining)} (~{remaining_msgs} messages)",
            f"{'='*50}{colorama.Fore.RESET}"
        ]
        
        return "\n".join(lines)
