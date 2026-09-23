"""
AdaptiveAgent: Main Self-Learning Autonomous Agent Coordinator
"""
import uuid
import time
from typing import Dict, Any, Optional, List

from backend.core.task_analyzer import TaskAnalyzer
from backend.core.planner import Planner
from backend.core.strategy_generator import StrategyGenerator
from backend.core.strategy_selector import StrategySelector
from backend.core.tool_selector import ToolSelector
from backend.core.execution_engine import ExecutionEngine
from backend.core.evaluator import ResultEvaluator

from backend.tools import (
    PythonSandboxTool, WebSearchTool, MathCalculatorTool, SemanticMemoryLookupTool
)
from backend.memory.short_term import ShortTermMemory
from backend.memory.episodic_memory import EpisodicMemory
from backend.memory.semantic_memory import SemanticMemory
from backend.learning.learning_engine import LearningEngine
from backend.learning.metrics import MetricsTracker

class AdaptiveAgent:
    """
    Main Autonomous Self-Learning Agent enforcing the continuous loop:
    User Goal -> Task Analyzer -> Planner -> Strategy Generator ->
    Strategy Selector (ML+Bandit) -> Tool Selector -> Execution Engine ->
    Result Evaluator -> Episodic Experience Memory -> ML Learning Engine.
    """
    def __init__(self, db_path: str = "data/episodic_memory.db", auto_retrain_interval: int = 5):
        # 1. Initialize Memory & Databases
        self.episodic_memory = EpisodicMemory(db_path=db_path)
        self.semantic_memory = SemanticMemory()
        
        # 2. Initialize Tools
        self.tools = [
            PythonSandboxTool(timeout_seconds=10),
            WebSearchTool(),
            MathCalculatorTool(),
            SemanticMemoryLookupTool(semantic_memory_store=self.semantic_memory)
        ]
        self.tool_selector = ToolSelector(self.tools)

        # 3. Initialize Core Components
        self.task_analyzer = TaskAnalyzer()
        self.planner = Planner()
        self.strategy_generator = StrategyGenerator()
        self.strategy_selector = StrategySelector()
        self.execution_engine = ExecutionEngine()
        self.evaluator = ResultEvaluator()
        
        # 4. Initialize Learning Engine & Metrics Tracker
        self.learning_engine = LearningEngine(self.episodic_memory)
        self.metrics_tracker = MetricsTracker()
        self.auto_retrain_interval = auto_retrain_interval
        self.task_counter = 0

        # Perform initial ML model retrain if DB already has historical episodes
        if self.episodic_memory.get_episode_count() >= 3:
            self.learning_engine.train_model(self.strategy_selector)

    def execute_task(self, user_goal: str, force_strategy: Optional[str] = None) -> Dict[str, Any]:
        task_id = f"task_{uuid.uuid4().hex[:8]}"
        self.task_counter += 1

        # Step 1: Task Understanding & Feature Extraction
        task_info = self.task_analyzer.analyze(user_goal)
        working_memory = ShortTermMemory(task_id, user_goal)

        # Step 2: Strategy Generation & Selection
        candidate_strategies = self.strategy_generator.get_candidate_strategies(task_info)
        
        if force_strategy:
            strategy_chosen = force_strategy
            selection_mode = "User_Override"
            candidate_scores = {force_strategy: 1.0}
        else:
            strategy_chosen, selection_mode, candidate_scores = self.strategy_selector.select_strategy(task_info)

        # Step 3: Planning (Subtask DAG Generation)
        plan_steps = self.planner.create_plan(task_info, strategy_chosen)

        # Step 4: Execution via Selected Tools & Strategy
        exec_result = self.execution_engine.execute_plan(
            task_info=task_info,
            strategy_name=strategy_chosen,
            plan_steps=plan_steps,
            tool_selector=self.tool_selector,
            working_memory=working_memory
        )

        # Step 5: Performance Evaluation & Reward Calculation
        eval_result = self.evaluator.evaluate(exec_result, task_info, strategy_chosen)

        # Step 6: Experience Storage (Episodic & Bandit Updates)
        episode_record = {
            "task_id": task_id,
            "user_goal": user_goal,
            "domain_category": task_info["domain_category"],
            "complexity_score": task_info["complexity_score"],
            "features": task_info,
            "strategy_chosen": strategy_chosen,
            "selection_mode": selection_mode,
            "candidate_scores": candidate_scores,
            "tools_used": exec_result["tools_invoked"],
            "success": eval_result["success"],
            "execution_time": exec_result["execution_time"],
            "step_count": exec_result["step_count"],
            "quality_score": eval_result["quality_score"],
            "reward_score": eval_result["reward_score"],
            "step_logs": working_memory.step_logs,
            "timestamp": time.time()
        }
        self.episodic_memory.save_episode(episode_record)
        self.strategy_selector.update_bandit_stats(
            domain=task_info["domain_category"],
            strategy=strategy_chosen,
            reward=eval_result["reward_score"]
        )

        # Step 7: Continuous Self-Learning Engine (Auto Retrain)
        retrain_info = None
        if self.task_counter % self.auto_retrain_interval == 0:
            retrain_info = self.learning_engine.train_model(self.strategy_selector)

        # Build comprehensive return payload
        return {
            "task_id": task_id,
            "user_goal": user_goal,
            "domain_category": task_info["domain_category"],
            "complexity_score": task_info["complexity_score"],
            "features": task_info,
            "strategy_chosen": strategy_chosen,
            "selection_mode": selection_mode,
            "candidate_scores": candidate_scores,
            "plan_steps": plan_steps,
            "execution": exec_result,
            "evaluation": eval_result,
            "short_term_context": working_memory.get_context_snapshot(),
            "auto_retrained": retrain_info is not None,
            "retrain_metrics": retrain_info
        }

    def trigger_retrain(self) -> Dict[str, Any]:
        return self.learning_engine.train_model(self.strategy_selector)

    def get_system_metrics(self) -> Dict[str, Any]:
        episodes = self.episodic_memory.fetch_all_episodes()
        metrics = self.metrics_tracker.compute_summary_metrics(episodes)
        metrics["ml_model_status"] = self.learning_engine.latest_metrics
        metrics["bandit_stats"] = self.strategy_selector.bandit_stats
        return metrics
