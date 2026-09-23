"""
Strategy Selector: Rules + Multi-Armed Bandit (UCB1) + ML Strategy Predictor
"""
import random
import math
import os
import joblib
import numpy as np
from typing import Dict, Any, List, Tuple

class StrategySelector:
    """
    Selects optimal execution strategy by combining:
    1. Heuristic Rule Prior
    2. Multi-Armed Bandit UCB1 (Exploration vs Exploitation)
    3. Machine Learning Predictor Model (Scikit-Learn Random Forest / Classifier)
    """
    def __init__(self, model_path: str = "models/ml_strategy_model.pkl", epsilon: float = 0.2):
        self.model_path = model_path
        self.epsilon = epsilon
        self.ml_model = None
        self.feature_names = [
            "token_count", "complexity_score", "domain_index",
            "has_code", "has_math", "has_search", "has_data"
        ]
        self.strategy_list = [
            "DirectExecution", "ReActReasoning", "DecompositionPipeline",
            "ToolHeavyPipeline", "IterativeRefinement"
        ]
        # Multi-armed bandit counts & rewards per (domain, strategy)
        # bandit_stats[domain][strategy] = {"pulls": N, "total_reward": R}
        self.bandit_stats: Dict[str, Dict[str, Dict[str, float]]] = {}
        self._load_ml_model()

    def _load_ml_model(self):
        if os.path.exists(self.model_path):
            try:
                self.ml_model = joblib.load(self.model_path)
            except Exception:
                self.ml_model = None

    def update_bandit_stats(self, domain: str, strategy: str, reward: float):
        if domain not in self.bandit_stats:
            self.bandit_stats[domain] = {
                s: {"pulls": 0.0, "total_reward": 0.0} for s in self.strategy_list
            }
        stats = self.bandit_stats[domain][strategy]
        stats["pulls"] += 1.0
        stats["total_reward"] += max(-1.0, min(3.0, reward))

    def _get_heuristic_scores(self, task_info: Dict[str, Any]) -> Dict[str, float]:
        domain = task_info.get("domain_category", "General")
        has_code = task_info.get("has_code_requirement", False)
        has_math = task_info.get("has_math_requirement", False)
        has_search = task_info.get("has_search_requirement", False)
        complexity = task_info.get("complexity_score", 1.0)

        scores = {s: 0.5 for s in self.strategy_list}

        if domain == "Coding" or has_code:
            scores["ToolHeavyPipeline"] += 0.4
            scores["IterativeRefinement"] += 0.35
            scores["DecompositionPipeline"] += 0.2
        elif domain == "Math" or has_math:
            scores["ToolHeavyPipeline"] += 0.45
            scores["DirectExecution"] += 0.2
        elif domain == "Research" or has_search:
            scores["ReActReasoning"] += 0.45
            scores["DecompositionPipeline"] += 0.25
        elif domain == "Data Analysis":
            scores["DecompositionPipeline"] += 0.4
            scores["ToolHeavyPipeline"] += 0.3

        if complexity < 2.0:
            scores["DirectExecution"] += 0.3
        elif complexity > 5.0:
            scores["DecompositionPipeline"] += 0.3
            scores["IterativeRefinement"] += 0.25

        return scores

    def _get_ucb1_scores(self, domain: str) -> Dict[str, float]:
        if domain not in self.bandit_stats:
            return {s: 0.5 for s in self.strategy_list}

        domain_stats = self.bandit_stats[domain]
        total_pulls = sum(s["pulls"] for s in domain_stats.values())
        if total_pulls == 0:
            return {s: 0.5 for s in self.strategy_list}

        ucb_scores = {}
        for s in self.strategy_list:
            pulls = domain_stats[s]["pulls"]
            if pulls == 0:
                ucb_scores[s] = 2.0  # Encourage initial exploration
            else:
                avg_reward = domain_stats[s]["total_reward"] / pulls
                exploration_bonus = math.sqrt((2.0 * math.log(total_pulls)) / pulls)
                ucb_scores[s] = avg_reward + exploration_bonus
        return ucb_scores

    def _get_ml_probabilities(self, feature_vector: List[float]) -> Dict[str, float]:
        if self.ml_model is None:
            return {}

        try:
            # Predict probabilities for each strategy
            # Input format: [feature_vector]
            X = np.array([feature_vector])
            if hasattr(self.ml_model, "predict_proba"):
                probas = self.ml_model.predict_proba(X)
                classes = self.ml_model.classes_
                # Handle multi-class probas array
                res = {}
                if isinstance(probas, list):  # multi-output case
                    for idx, c in enumerate(classes):
                        res[str(c)] = float(probas[idx][0][1])
                else:
                    for idx, c in enumerate(classes):
                        res[str(c)] = float(probas[0][idx])
                return res
        except Exception:
            pass
        return {}

    def select_strategy(self, task_info: Dict[str, Any], force_exploration: bool = False) -> Tuple[str, str, Dict[str, float]]:
        domain = task_info.get("domain_category", "General")
        feature_vector = task_info.get("feature_vector", [5.0, 2.0, 0.0, 0.0, 0.0, 0.0, 0.0])

        heuristic_scores = self._get_heuristic_scores(task_info)
        ucb_scores = self._get_ucb1_scores(domain)
        ml_probas = self._get_ml_probabilities(feature_vector)

        candidate_scores = {}
        selection_mode = "Rule+Bandit"

        # Epsilon-Greedy Exploration Decision
        if force_exploration or (random.random() < self.epsilon and not ml_probas):
            selection_mode = "Exploration_Random"
            chosen_strategy = random.choice(self.strategy_list)
            for s in self.strategy_list:
                candidate_scores[s] = round(ucb_scores.get(s, 0.5), 3)
            return chosen_strategy, selection_mode, candidate_scores

        # Combine scores if ML model exists
        if ml_probas:
            selection_mode = "ML_Predictor_Exploitation"
            for s in self.strategy_list:
                ml_p = ml_probas.get(s, 0.2)
                h_p = heuristic_scores.get(s, 0.5)
                u_p = ucb_scores.get(s, 0.5)
                # Weighted blend: 60% ML prediction, 25% UCB bandit, 15% heuristic
                candidate_scores[s] = round(0.60 * ml_p + 0.25 * u_p + 0.15 * h_p, 4)
        else:
            selection_mode = "Bandit_UCB1"
            for s in self.strategy_list:
                h_p = heuristic_scores.get(s, 0.5)
                u_p = ucb_scores.get(s, 0.5)
                candidate_scores[s] = round(0.65 * u_p + 0.35 * h_p, 4)

        # Select strategy with highest composite score
        best_strategy = max(candidate_scores, key=candidate_scores.get)
        return best_strategy, selection_mode, candidate_scores
