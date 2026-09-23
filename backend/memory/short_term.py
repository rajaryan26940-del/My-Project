"""
Short-Term Working Memory Context Buffer
"""
import time
from typing import List, Dict, Any, Optional

class ShortTermMemory:
    """
    Manages active task session state, current plan steps, scratchpad,
    tool invocation traces, and temporary variable scope.
    """
    def __init__(self, task_id: str, goal: str):
        self.task_id = task_id
        self.goal = goal
        self.start_time = time.time()
        self.scratchpad: List[Dict[str, Any]] = []
        self.step_logs: List[Dict[str, Any]] = []
        self.active_variables: Dict[str, Any] = {}

    def log_step(self, step_number: int, step_name: str, strategy: str, tool_used: Optional[str], result: Any, success: bool):
        entry = {
            "step_number": step_number,
            "step_name": step_name,
            "strategy": strategy,
            "tool_used": tool_used,
            "result": str(result),
            "success": success,
            "timestamp": time.time()
        }
        self.step_logs.append(entry)

    def add_thought(self, thought: str):
        self.scratchpad.append({
            "type": "thought",
            "content": thought,
            "timestamp": time.time()
        })

    def get_summary(self) -> Dict[str, Any]:
        return {
            "task_id": self.task_id,
            "goal": self.goal,
            "steps_count": len(self.step_logs),
            "scratchpad_entries": len(self.scratchpad)
        }

    def get_context_snapshot(self) -> Dict[str, Any]:
        return {
            "task_id": self.task_id,
            "goal": self.goal,
            "elapsed_seconds": round(time.time() - self.start_time, 3),
            "steps_count": len(self.step_logs),
            "step_logs": self.step_logs,
            "scratchpad": self.scratchpad
        }
