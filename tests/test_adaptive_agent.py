"""
Unit and Integration Test Suite for AdaptiveAI Autonomous Agent
"""
import pytest
import tempfile
import os
from backend.core.task_analyzer import TaskAnalyzer
from backend.core.planner import Planner
from backend.core.strategy_generator import StrategyGenerator
from backend.core.strategy_selector import StrategySelector
from backend.tools import PythonSandboxTool, MathCalculatorTool, WebSearchTool
from backend.memory.episodic_memory import EpisodicMemory
from backend.memory.semantic_memory import SemanticMemory
from backend.learning.learning_engine import LearningEngine
from backend.agent import AdaptiveAgent

def test_task_analyzer():
    analyzer = TaskAnalyzer()

    # Coding task
    res1 = analyzer.analyze("Write a Python function to sort an array")
    assert res1["domain_category"] == "Coding"
    assert res1["has_code_requirement"] is True
    assert len(res1["feature_vector"]) == 7

    # Math task
    res2 = analyzer.analyze("Calculate 25 * 4 + 10")
    assert res2["domain_category"] == "Math"
    assert res2["has_math_requirement"] is True

    # Search task
    res3 = analyzer.analyze("Search latest news on space exploration")
    assert res3["domain_category"] == "Research"
    assert res3["has_search_requirement"] is True

def test_tools():
    py_tool = PythonSandboxTool()
    res_py = py_tool.execute(code="print('AdaptiveAI Sandbox Success')")
    assert res_py["success"] is True
    assert "AdaptiveAI Sandbox Success" in res_py["result"]

    math_tool = MathCalculatorTool()
    res_math = math_tool.execute(expression="50 * 4 + 25")
    assert res_math["success"] is True
    assert res_math["result"] == 225

    search_tool = WebSearchTool()
    res_search = search_tool.execute(query="Multi-Armed Bandit")
    assert res_search["success"] is True
    assert "Multi-Armed Bandit" in res_search["result"]

def test_episodic_memory_and_learning():
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
        db_path = tmp.name

    try:
        mem = EpisodicMemory(db_path=db_path)
        assert mem.get_episode_count() == 0

        # Save dummy episodes
        ep1 = {
            "task_id": "test_001",
            "user_goal": "Write python sorting script",
            "domain_category": "Coding",
            "complexity_score": 3.0,
            "features": {"token_count": 5, "has_code_requirement": True},
            "strategy_chosen": "ToolHeavyPipeline",
            "selection_mode": "Rule+Bandit",
            "success": True,
            "execution_time": 0.5,
            "step_count": 2,
            "quality_score": 0.9,
            "reward_score": 2.1
        }
        mem.save_episode(ep1)
        assert mem.get_episode_count() == 1

        # Train ML model
        learning_engine = LearningEngine(episodic_memory=mem, min_samples_to_train=1)
        strategy_selector = StrategySelector()
        res_retrain = learning_engine.train_model(strategy_selector)

        assert res_retrain["status"] == "Successfully Retrained"
        assert res_retrain["samples_count"] > 0
    finally:
        try:
            if os.path.exists(db_path):
                os.remove(db_path)
        except PermissionError:
            pass

def test_agent_end_to_end_loop():
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
        db_path = tmp.name

    try:
        agent = AdaptiveAgent(db_path=db_path, auto_retrain_interval=3)

        # Run 4 tasks to trigger auto-retraining
        tasks = [
            "Write a Python script to compute Fibonacci sequence",
            "Calculate 100 * 5 + (20 / 4)",
            "Search reference information about Python programming",
            "Sort list of numbers [5, 2, 8, 1, 9] in Python"
        ]

        for t in tasks:
            res = agent.execute_task(t)
            assert "task_id" in res
            assert res["execution"]["success"] is True
            assert "reward_score" in res["evaluation"]

        metrics = agent.get_system_metrics()
        assert metrics["total_tasks"] == 4
        assert metrics["overall_success_rate"] == 1.0
    finally:
        try:
            if os.path.exists(db_path):
                os.remove(db_path)
        except PermissionError:
            pass
