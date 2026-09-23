"""
Planner: Task Breakdown and Execution Graph Generation
"""
from typing import Dict, Any, List

class Planner:
    """
    Decomposes top-level goals into atomic execution steps / DAG nodes.
    """
    def create_plan(self, task_info: Dict[str, Any], strategy_name: str) -> List[Dict[str, Any]]:
        domain = task_info.get("domain_category", "General")
        goal = task_info.get("user_goal", "")

        steps = []

        if strategy_name == "DirectExecution":
            steps.append({
                "step_number": 1,
                "name": "Direct Execution",
                "description": f"Perform immediate solution synthesis for goal: '{goal}'",
                "required_capability": "python" if task_info.get("has_code_requirement") else ("math" if task_info.get("has_math_requirement") else "general")
            })

        elif strategy_name == "ReActReasoning":
            steps.append({
                "step_number": 1,
                "name": "Reasoning & Context Search",
                "description": f"Gather relevant domain knowledge and search memory for '{goal}'",
                "required_capability": "search"
            })
            steps.append({
                "step_number": 2,
                "name": "Target Action Execution",
                "description": "Execute core logic/tool computation based on gathered observations",
                "required_capability": "python" if task_info.get("has_code_requirement") else ("math" if task_info.get("has_math_requirement") else "general")
            })
            steps.append({
                "step_number": 3,
                "name": "Result Verification & Reflection",
                "description": "Verify step observations against initial user goal expectations",
                "required_capability": "general"
            })

        elif strategy_name == "DecompositionPipeline":
            steps.append({
                "step_number": 1,
                "name": "Subtask Decomposition & Memory Lookup",
                "description": "Break goal into modular components and lookup prior solution patterns",
                "required_capability": "memory"
            })
            steps.append({
                "step_number": 2,
                "name": "Sub-component Execution",
                "description": "Execute specialized sub-computations using domain tools",
                "required_capability": "math" if domain == "Math" else ("python" if domain == "Coding" else "search")
            })
            steps.append({
                "step_number": 3,
                "name": "Synthesis & Integration",
                "description": "Combine subtask outputs into unified final result",
                "required_capability": "general"
            })

        elif strategy_name == "ToolHeavyPipeline":
            steps.append({
                "step_number": 1,
                "name": "Tool Selection & Argument Parsing",
                "description": "Formulate exact input payload for primary target tool",
                "required_capability": "general"
            })
            steps.append({
                "step_number": 2,
                "name": "Primary Sandbox / Solver Invocation",
                "description": "Run tool execution inside isolated environment",
                "required_capability": "python" if task_info.get("has_code_requirement") or domain == "Coding" else ("math" if domain == "Math" else "search")
            })
            steps.append({
                "step_number": 3,
                "name": "Output Formatting & Payload Extraction",
                "description": "Parse raw tool output into structured final response",
                "required_capability": "general"
            })

        elif strategy_name == "IterativeRefinement":
            steps.append({
                "step_number": 1,
                "name": "Initial Draft Generation",
                "description": "Generate candidate solution code/text",
                "required_capability": "python" if task_info.get("has_code_requirement") else "general"
            })
            steps.append({
                "step_number": 2,
                "name": "Evaluation & Sandbox Test",
                "description": "Run sandbox execution or math verification test",
                "required_capability": "python" if task_info.get("has_code_requirement") else ("math" if task_info.get("has_math_requirement") else "general")
            })
            steps.append({
                "step_number": 3,
                "name": "Refinement & Polish",
                "description": "Fix errors identified during step 2 test run and finalize output",
                "required_capability": "general"
            })
        else:
            steps.append({
                "step_number": 1,
                "name": "General Execution",
                "description": goal,
                "required_capability": "general"
            })

        return steps
