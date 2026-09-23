"""
AdaptiveAI Self-Learning Autonomous Agent Benchmark & Demonstration
"""
import os
import time
from backend.agent import AdaptiveAgent

def main():
    print("=" * 80)
    print("      AdaptiveAI — Self-Learning Autonomous AI Agent Demonstration")
    print("=" * 80)

    demo_db = "data/demo_episodic_memory.db"
    if os.path.exists(demo_db):
        try:
            os.remove(demo_db)
        except Exception:
            pass

    agent = AdaptiveAgent(db_path=demo_db, auto_retrain_interval=4)

    benchmark_tasks = [
        # Batch 1: Initial Exploration
        "Write a Python function to generate Fibonacci sequence up to N terms",
        "Calculate 45 * 12 + (300 / 5) ^ 2",
        "Search reference notes on ReAct agent architecture",
        "Transform array data [45, 12, 89, 33, 67] and compute average",

        # Batch 2: Intermediate Learning (ML Model Triggered at Task 4)
        "Write a Python script to sort an array of random integers",
        "Calculate 150 * 3 + 45",
        "Search papers on Multi-Armed Bandit algorithms",
        "Compute prime numbers up to 50 in Python",

        # Batch 3: High Exploitation & Performance Boost (ML Model Retrained at Task 8 & 12)
        "Implement a Python program for binary search on sorted array",
        "Evaluate math equation 25 * 10 + 500 / 2",
        "Search documentation on FastAPI web framework",
        "Write Python script to check if string is palindrome",
        "Calculate 99 * 99 + 1"
    ]

    print(f"\n[Info] Executing batch of {len(benchmark_tasks)} sequential tasks across domains...")
    print(f"{'Task #':<8} | {'Domain':<14} | {'Strategy Chosen':<22} | {'Selection Mode':<24} | {'Reward':<7} | {'Status'}")
    print("-" * 95)

    for idx, goal in enumerate(benchmark_tasks, 1):
        res = agent.execute_task(goal)

        task_domain = res["domain_category"]
        strat = res["strategy_chosen"]
        mode = res["selection_mode"]
        reward = res["evaluation"]["reward_score"]
        status = "SUCCESS" if res["execution"]["success"] else "FAILED"
        retrained = " [ML RETRAINED]" if res.get("auto_retrained") else ""

        print(f"Task #{idx:<3} | {task_domain:<14} | {strat:<22} | {mode:<24} | {reward:<7.2f} | {status}{retrained}")

        time.sleep(0.1)

    print("\n" + "=" * 80)
    print("      FINAL SYSTEM LEARNING BENCHMARK METRICS")
    print("=" * 80)

    metrics = agent.get_system_metrics()
    print(f"Total Tasks Executed     : {metrics['total_tasks']}")
    print(f"Overall Success Rate     : {metrics['overall_success_rate'] * 100:.1f}%")
    print(f"Mean Composite Reward    : {metrics['mean_reward']:.3f}")
    print(f"\nStrategy Distribution    :")
    for strat, count in metrics["strategy_distribution"].items():
        print(f"  - {strat:<22}: {count} tasks")

    print(f"\nSelection Mode Breakdown :")
    for mode, count in metrics["selection_mode_breakdown"].items():
        print(f"  - {mode:<24}: {count} tasks")

    ml_status = metrics.get("ml_model_status", {})
    print(f"\nML Strategy Predictor    :")
    print(f"  - Status               : {ml_status.get('status')}")
    print(f"  - Trained Samples      : {ml_status.get('samples_count')}")
    print(f"  - Classifier Accuracy  : {ml_status.get('accuracy', 0) * 100:.1f}%")
    print("=" * 80)
    print("Demonstration Completed Successfully!")

if __name__ == "__main__":
    main()
