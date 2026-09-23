"""
Tool Selector: Dynamic Tool Matching and Selection
"""
from typing import Dict, Any, List, Optional
from backend.tools.base import BaseTool

class ToolSelector:
    """
    Matches plan step capabilities with registered agent tools.
    """
    def __init__(self, tools: List[BaseTool]):
        self.tools_by_name = {t.name: t for t in tools}
        self.tools_by_category = {}
        for t in tools:
            if t.category not in self.tools_by_category:
                self.tools_by_category[t.category] = []
            self.tools_by_category[t.category].append(t)

    def select_tool_for_step(self, step_info: Dict[str, Any]) -> Optional[BaseTool]:
        capability = step_info.get("required_capability", "general")

        if capability == "coding" or capability == "python":
            return self.tools_by_name.get("python_sandbox")
        elif capability == "math":
            return self.tools_by_name.get("math_calculator") or self.tools_by_name.get("python_sandbox")
        elif capability == "search":
            return self.tools_by_name.get("web_search")
        elif capability == "memory":
            return self.tools_by_name.get("memory_lookup")

        # Fallback to python sandbox if step description mentions python code
        desc = step_info.get("description", "").lower()
        if "python" in desc or "code" in desc or "script" in desc:
            return self.tools_by_name.get("python_sandbox")
        elif "calc" in desc or "math" in desc or "formula" in desc:
            return self.tools_by_name.get("math_calculator")
        elif "search" in desc or "find" in desc:
            return self.tools_by_name.get("web_search")

        return None
