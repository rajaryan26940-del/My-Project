"""
Episodic Memory Database for Persistent Task Experience Storage
"""
import sqlite3
import json
import time
import os
from typing import List, Dict, Any, Optional

class EpisodicMemory:
    """
    Stores long-term historical records of task executions, task features,
    chosen strategy, evaluation scores, execution times, token cost, and final reward.
    Provides data extraction routines for ML strategy model training.
    """
    def __init__(self, db_path: str = "data/episodic_memory.db"):
        self.db_path = db_path
        os.makedirs(os.path.dirname(os.path.abspath(db_path)), exist_ok=True)
        self._init_db()

    def _get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        with self._get_connection() as conn:
            conn.execute("""
            CREATE TABLE IF NOT EXISTS episodes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_id TEXT UNIQUE,
                user_goal TEXT,
                domain_category TEXT,
                complexity_score REAL,
                features_json TEXT,
                strategy_chosen TEXT,
                selection_mode TEXT,
                candidate_scores_json TEXT,
                tools_used_json TEXT,
                success INTEGER,
                execution_time REAL,
                step_count INTEGER,
                quality_score REAL,
                reward_score REAL,
                feedback_rating INTEGER,
                step_logs_json TEXT,
                timestamp REAL
            )
            """)
            conn.commit()

    def save_episode(self, episode_data: Dict[str, Any]) -> int:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            INSERT OR REPLACE INTO episodes (
                task_id, user_goal, domain_category, complexity_score,
                features_json, strategy_chosen, selection_mode,
                candidate_scores_json, tools_used_json, success,
                execution_time, step_count, quality_score,
                reward_score, feedback_rating, step_logs_json, timestamp
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                episode_data.get("task_id"),
                episode_data.get("user_goal"),
                episode_data.get("domain_category", "General"),
                float(episode_data.get("complexity_score", 1.0)),
                json.dumps(episode_data.get("features", {})),
                episode_data.get("strategy_chosen"),
                episode_data.get("selection_mode", "Rule+Bandit"),
                json.dumps(episode_data.get("candidate_scores", {})),
                json.dumps(episode_data.get("tools_used", [])),
                1 if episode_data.get("success", False) else 0,
                float(episode_data.get("execution_time", 0.0)),
                int(episode_data.get("step_count", 1)),
                float(episode_data.get("quality_score", 0.5)),
                float(episode_data.get("reward_score", 0.0)),
                episode_data.get("feedback_rating"),
                json.dumps(episode_data.get("step_logs", [])),
                float(episode_data.get("timestamp", time.time()))
            ))
            conn.commit()
            return cursor.lastrowid

    def update_user_feedback(self, task_id: str, rating: int, quality_score_boost: float = 0.2):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            SELECT success, execution_time, step_count, quality_score FROM episodes WHERE task_id = ?
            """, (task_id,))
            row = cursor.fetchone()
            if row:
                current_quality = row["quality_score"]
                new_quality = min(1.0, max(0.0, (current_quality + (rating - 3) * 0.1)))
                # Recalculate reward
                success_val = row["success"]
                exec_time = row["execution_time"]
                new_reward = (1.5 * success_val) + (1.0 * new_quality) - (0.05 * exec_time) + (0.1 * rating)
                
                cursor.execute("""
                UPDATE episodes
                SET feedback_rating = ?, quality_score = ?, reward_score = ?
                WHERE task_id = ?
                """, (rating, new_quality, new_reward, task_id))
                conn.commit()

    def fetch_recent_episodes(self, limit: int = 50) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            SELECT * FROM episodes ORDER BY id DESC LIMIT ?
            """, (limit,))
            rows = cursor.fetchall()
            results = []
            for r in rows:
                item = dict(r)
                item["features"] = json.loads(item["features_json"]) if item["features_json"] else {}
                item["candidate_scores"] = json.loads(item["candidate_scores_json"]) if item["candidate_scores_json"] else {}
                item["tools_used"] = json.loads(item["tools_used_json"]) if item["tools_used_json"] else []
                item["step_logs"] = json.loads(item["step_logs_json"]) if item["step_logs_json"] else []
                results.append(item)
            return results

    def fetch_all_training_samples(self) -> List[Dict[str, Any]]:
        return self.fetch_all_episodes()

    def fetch_all_episodes(self) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM episodes ORDER BY id ASC")
            rows = cursor.fetchall()
            results = []
            for r in rows:
                item = dict(r)
                item["features"] = json.loads(item["features_json"]) if item["features_json"] else {}
                item["candidate_scores"] = json.loads(item["candidate_scores_json"]) if item["candidate_scores_json"] else {}
                item["tools_used"] = json.loads(item["tools_used_json"]) if item["tools_used_json"] else []
                item["step_logs"] = json.loads(item["step_logs_json"]) if item["step_logs_json"] else []
                results.append(item)
            return results

    def get_episode_count(self) -> int:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM episodes")
            return cursor.fetchone()[0]
