"""
Learning Feature Extractor: Dataset Builder from Episodic Memory
"""
import numpy as np
from typing import List, Dict, Any, Tuple

class LearningFeatureExtractor:
    """
    Extracts tabular dataset (X, y) from Episodic Memory episodes
    to train ML strategy predictor models.
    """
    def build_dataset(self, episodes: List[Dict[str, Any]]) -> Tuple[np.ndarray, np.ndarray, List[str]]:
        X_list = []
        y_list = []

        feature_names = [
            "token_count", "complexity_score", "domain_index",
            "has_code", "has_math", "has_search", "has_data"
        ]

        for ep in episodes:
            feats = ep.get("features", {})
            f_vector = feats.get("feature_vector")

            if not f_vector or len(f_vector) != len(feature_names):
                token_count = float(feats.get("token_count", 5))
                complexity = float(feats.get("complexity_score", ep.get("complexity_score", 1.0)))
                domain_str = ep.get("domain_category", "General")
                domain_map = {"Math": 0, "Coding": 1, "Data Analysis": 2, "Research": 3, "General": 4}
                domain_idx = float(domain_map.get(domain_str, 4))
                has_code = 1.0 if feats.get("has_code_requirement") else 0.0
                has_math = 1.0 if feats.get("has_math_requirement") else 0.0
                has_search = 1.0 if feats.get("has_search_requirement") else 0.0
                has_data = 1.0 if feats.get("has_data_transform") else 0.0

                f_vector = [token_count, complexity, domain_idx, has_code, has_math, has_search, has_data]

            strategy = ep.get("strategy_chosen")
            reward = float(ep.get("reward_score", 0.0))
            success = bool(ep.get("success", False))

            # Include high-performing episodes (success=True & reward >= 0.5) in dataset
            if strategy and (success or reward > 0.0):
                X_list.append(f_vector)
                y_list.append(strategy)

        if not X_list:
            return np.empty((0, len(feature_names))), np.empty((0,)), feature_names

        return np.array(X_list), np.array(y_list), feature_names
