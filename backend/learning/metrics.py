"""
Metrics Tracker for System Learning Curves & Performance Analytics
"""
from typing import List, Dict, Any

class MetricsTracker:
    """
    Computes overall benchmark metrics:
    - Success rate over time (sliding window)
    - Average reward progression
    - Strategy distribution matrix
    - Exploration vs Exploitation ratio
    """
    def compute_summary_metrics(self, episodes: List[Dict[str, Any]]) -> Dict[str, Any]:
        total_tasks = len(episodes)
        if total_tasks == 0:
            return {
                "total_tasks": 0,
                "overall_success_rate": 0.0,
                "mean_reward": 0.0,
                "strategy_distribution": {},
                "selection_mode_breakdown": {},
                "learning_curve": []
            }

        successful_tasks = sum(1 for e in episodes if e.get("success", False))
        overall_success_rate = round(float(successful_tasks) / total_tasks, 4)
        mean_reward = round(sum(float(e.get("reward_score", 0.0)) for e in episodes) / total_tasks, 4)

        # Strategy Distribution
        strategy_counts = {}
        selection_modes = {}
        for e in episodes:
            strat = e.get("strategy_chosen", "Unknown")
            mode = e.get("selection_mode", "Rule+Bandit")
            strategy_counts[strat] = strategy_counts.get(strat, 0) + 1
            selection_modes[mode] = selection_modes.get(mode, 0) + 1

        # Learning Curve (Sliding window of 5 tasks)
        learning_curve = []
        window_size = 5
        for i in range(0, total_tasks):
            window = episodes[max(0, i - window_size + 1): i + 1]
            w_succ = sum(1 for e in window if e.get("success", False)) / float(len(window))
            w_reward = sum(float(e.get("reward_score", 0.0)) for e in window) / float(len(window))
            learning_curve.append({
                "task_index": i + 1,
                "task_id": episodes[i].get("task_id"),
                "window_success_rate": round(w_succ, 3),
                "window_mean_reward": round(w_reward, 3)
            })

        return {
            "total_tasks": total_tasks,
            "overall_success_rate": overall_success_rate,
            "mean_reward": mean_reward,
            "strategy_distribution": strategy_counts,
            "selection_mode_breakdown": selection_modes,
            "learning_curve": learning_curve
        }
