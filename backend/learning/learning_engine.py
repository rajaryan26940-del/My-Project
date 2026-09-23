"""
Learning Engine: ML Model Retraining & Continuous Adaptation Pipeline
"""
import os
import time
import joblib
import numpy as np
from typing import Dict, Any, List

from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score

from backend.memory.episodic_memory import EpisodicMemory
from backend.learning.feature_extractor import LearningFeatureExtractor

class LearningEngine:
    """
    Orchestrates continuous self-learning by:
    1. Extracting execution dataset from Episodic Memory
    2. Training/Updating Scikit-Learn strategy classifier
    3. Persisting updated model artifact (.pkl)
    4. Updating Multi-Armed Bandit stats
    5. Computing model accuracy improvements
    """
    def __init__(
        self,
        episodic_memory: EpisodicMemory,
        model_dir: str = "models",
        min_samples_to_train: int = 3
    ):
        self.episodic_memory = episodic_memory
        self.model_dir = model_dir
        self.min_samples_to_train = min_samples_to_train
        self.feature_extractor = LearningFeatureExtractor()
        os.makedirs(model_dir, exist_ok=True)
        self.model_path = os.path.join(model_dir, "ml_strategy_model.pkl")
        self.last_retrain_time: float = 0.0
        self.latest_metrics: Dict[str, Any] = {
            "status": "Initialized",
            "samples_count": 0,
            "accuracy": 0.0,
            "classes_trained": []
        }

    def train_model(self, strategy_selector=None) -> Dict[str, Any]:
        start_time = time.time()
        episodes = self.episodic_memory.fetch_all_episodes()

        X, y, feature_names = self.feature_extractor.build_dataset(episodes)
        samples_count = len(X)

        if samples_count < self.min_samples_to_train:
            res = {
                "status": "Skipped",
                "reason": f"Not enough samples to train (found {samples_count}, required {self.min_samples_to_train})",
                "samples_count": samples_count,
                "accuracy": 0.0,
                "execution_time": round(time.time() - start_time, 4)
            }
            self.latest_metrics = res
            return res

        unique_classes = np.unique(y)
        if len(unique_classes) < 2:
            # Add synthetic baseline samples for diversity if needed
            synthetic_X = [
                [5, 1.5, 0, 0, 1, 0, 0],  # Math
                [10, 4.0, 1, 1, 0, 0, 0], # Coding
                [8, 3.0, 3, 0, 0, 1, 0]   # Research
            ]
            synthetic_y = ["ToolHeavyPipeline", "IterativeRefinement", "ReActReasoning"]
            X = np.vstack([X, synthetic_X])
            y = np.concatenate([y, synthetic_y])
            unique_classes = np.unique(y)

        # Train Random Forest Classifier
        try:
            model = RandomForestClassifier(n_estimators=25, max_depth=6, random_state=42)
            model.fit(X, y)
        except Exception:
            model = LogisticRegression(max_iter=200)
            model.fit(X, y)

        preds = model.predict(X)
        acc = float(accuracy_score(y, preds))

        # Save model checkpoint
        joblib.dump(model, self.model_path)
        self.last_retrain_time = time.time()

        # Update StrategySelector's model instance if passed
        if strategy_selector:
            strategy_selector.ml_model = model
            # Also sync bandit stats from episodic memory
            for ep in episodes:
                domain = ep.get("domain_category", "General")
                strat = ep.get("strategy_chosen")
                reward = float(ep.get("reward_score", 0.0))
                if domain and strat:
                    strategy_selector.update_bandit_stats(domain, strat, reward)

        res = {
            "status": "Successfully Retrained",
            "samples_count": len(X),
            "accuracy": round(acc, 4),
            "classes_trained": list(unique_classes),
            "model_path": self.model_path,
            "execution_time": round(time.time() - start_time, 4),
            "retrain_timestamp": self.last_retrain_time
        }
        self.latest_metrics = res
        return res
