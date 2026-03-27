import asyncio
from typing import List, Dict, Any
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

class ReviewManager:
    """
    KILAT Parallel Review Manager.
    Leverages multi-core/GPU capabilities (like RTX 3090) to run specialized 
    audit agents in parallel.
    Inspired by Qwen-Code 'Parallel Multi-Dimensional Review'.
    """

    def __init__(self, llm: ChatOpenAI):
        self.llm = llm

    async def audit_file(self, file_path: str, file_content: str) -> str:
        """Run parallel audits on a single file."""
        
        # Define specialized agent prompts
        agents = {
            "Security": "You are a cybersecurity expert. Audit this code for vulnerabilities, injection risks, and data leaks.",
            "Performance": "You are a software performance engineer. Audit this code for bottlenecks, memory leaks, and O(n) inefficiencies.",
            "Best Practices": "You are a principal engineer. Audit this code for readability, SOLID principles, and clean code patterns."
        }
        
        # Spawn parallel tasks
        tasks = []
        for name, prompt in agents.items():
            tasks.append(self._run_audit_task(name, prompt, file_content))
        
        # Wait for all to complete
        results = await asyncio.gather(*tasks)
        
        # Synthesize report
        report = f"# 🔬 KILAT Code Audit: {file_path}\n\n"
        for name, res in results:
            report += f"## 🛡️ {name} Findings\n{res}\n\n"
        
        return report

    async def _run_audit_task(self, name: str, system_prompt: str, content: str) -> tuple:
        """Single audit task for a sub-agent."""
        try:
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=f"Audit this code:\n\n```python\n{content}\n```")
            ]
            response = await self.llm.ainvoke(messages)
            return (name, response.content)
        except Exception as e:
            return (name, f"❌ Audit failed: {str(e)}")

    def generate_report_file(self, report_content: str, output_path: str = "review_report.md"):
        """Save the synthesized report to a file."""
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(report_content)
        return output_path
