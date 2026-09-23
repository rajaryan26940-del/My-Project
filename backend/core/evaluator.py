"""
Result Evaluator: Task Performance & Reward Scoring Engine
"""
from typing import Dict, Any

class ResultEvaluator:
    """
    Evaluates task outcomes across objective metrics (Success, Execution Time, Step Count, Error Count)
    and computes composite scalar reward for Reinforcement Learning & ML Strategy Predictor training.
    """
    def __init__(
        self,
        weight_success: float = 1.5,
        weight_quality: float = 1.0,
        weight_time: float = 0.05,
        weight_cost: float = 0.02
    ):
        self.w_success = weight_success
        self.w_quality = weight_quality
        self.w_time = weight_time
        self.w_cost = weight_cost

    def evaluate(self, execution_result: Dict[str, Any], task_info: Dict[str, Any], strategy_name: str) -> Dict[str, Any]:
        success = execution_result.get("success", False)
        exec_time = execution_result.get("execution_time", 0.0)
        step_count = execution_result.get("step_count", 1)
        step_results = execution_result.get("step_results", [])

        # 1. Quality Score Assessment (0.0 to 1.0)
        error_count = sum(1 for s in step_results if not s.get("success", True))
        if not success:
            quality_score = 0.1
        elif error_count > 0:
            quality_score = 0.6
        else:
            # Reward efficiency for appropriate strategy choice
            complexity = task_info.get("complexity_score", 1.0)
            if strategy_name == "DirectExecution" and complexity <= 2.0:
                quality_score = 0.95
            elif strategy_name in ["ToolHeavyPipeline", "IterativeRefinement"] and task_info.get("has_code_requirement"):
                quality_score = 0.92
            else:
                quality_score = 0.85

        # 2. Token & Complexity Cost Estimate
        estimated_cost = step_count * 0.1

        # 3. Composite Scalar Reward Calculation
        # R = w1*Success + w2*Quality - w3*Latency - w4*Cost
        reward_score = (
            (self.w_success if success else -1.0)
            + (self.w_quality * quality_score)
            - (self.w_time * min(10.0, exec_time))
            - (self.w_cost * estimated_cost)
        )
        reward_score = round(reward_score, 4)

        return {
            "success": success,
            "quality_score": round(quality_score, 2),
            "reward_score": reward_score,
            "error_count": error_count,
            "estimated_cost": round(estimated_cost, 2),
            "execution_time": exec_time,
            "step_count": step_count
        }
