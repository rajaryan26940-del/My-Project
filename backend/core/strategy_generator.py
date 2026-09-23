"""
Strategy Generator: Candidate Strategy Definitions
"""
from typing import List, Dict, Any

class StrategyGenerator:
    """
    Provides candidate execution strategies for task solving.
    """
    STRATEGIES = [
        {
            "name": "DirectExecution",
            "description": "Fast single-step execution for lightweight or routine tasks.",
            "base_cost": 1.0,
            "base_time": 0.5
        },
        {
            "name": "ReActReasoning",
            "description": "Interleaved Thought-Action-Observation loop combining search and reasoning.",
            "base_cost": 2.5,
            "base_time": 1.5
        },
        {
            "name": "DecompositionPipeline",
            "description": "Divide-and-conquer strategy splitting goal into modular subtasks.",
            "base_cost": 3.0,
            "base_time": 2.0
        },
        {
            "name": "ToolHeavyPipeline",
            "description": "Tool-centric execution emphasizing Python sandbox and mathematical engines.",
            "base_cost": 2.0,
            "base_time": 1.2
        },
        {
            "name": "IterativeRefinement",
            "description": "Self-correcting strategy that runs tests and refines answer in feedback loop.",
            "base_cost": 3.5,
            "base_time": 2.5
        }
    ]

    def get_candidate_strategies(self, task_info: Dict[str, Any]) -> List[Dict[str, Any]]:
        # All strategies available for selection
        return [dict(s) for s in self.STRATEGIES]
