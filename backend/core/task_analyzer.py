"""
Task Analyzer: Intent Parser and Feature Extractor
"""
import re
from typing import Dict, Any, List

class TaskAnalyzer:
    """
    Parses user goals into structured task objects and extracts numerical & categorical
    features for strategy prediction and memory indexing.
    """
    DOMAINS = ["Math", "Coding", "Data Analysis", "Research", "General"]

    KEYWORDS_MATH = ["calculate", "math", "evaluate", "solve", "formula", "equation", "sum", "integral", "multiply", "divide", "matrix", "algebra"]
    KEYWORDS_CODING = ["code", "python", "script", "function", "program", "debug", "algorithm", "class", "array", "string", "loop", "implement", "fibonacci", "sort"]
    KEYWORDS_SEARCH = ["search", "find", "who is", "what is", "where", "latest", "news", "history", "definition", "paper", "explain", "research"]
    KEYWORDS_DATA = ["data", "dataset", "dataframe", "csv", "json", "transform", "average", "mean", "chart", "plot", "filter", "aggregate"]

    def analyze(self, user_goal: str) -> Dict[str, Any]:
        goal_clean = user_goal.strip()
        tokens = re.findall(r'\w+', goal_clean.lower())
        token_count = len(tokens)

        # 1. Domain Detection
        math_score = sum(1 for t in tokens if t in self.KEYWORDS_MATH)
        coding_score = sum(1 for t in tokens if t in self.KEYWORDS_CODING)
        search_score = sum(1 for t in tokens if t in self.KEYWORDS_SEARCH)
        data_score = sum(1 for t in tokens if t in self.KEYWORDS_DATA)

        scores = {
            "Math": math_score,
            "Coding": coding_score,
            "Research": search_score,
            "Data Analysis": data_score
        }

        best_domain = max(scores, key=scores.get)
        if scores[best_domain] == 0:
            best_domain = "General"

        # 2. Boolean Requirement Flags
        has_code_requirement = coding_score > 0 or "python" in goal_clean.lower() or "def " in goal_clean.lower()
        has_math_requirement = math_score > 0 or any(char in goal_clean for char in ["+", "*", "/", "=", "^"])
        has_search_requirement = search_score > 0 or "?" in goal_clean
        has_data_transform = data_score > 0 or "csv" in goal_clean.lower() or "list" in goal_clean.lower()

        # 3. Estimated Complexity Score (1.0 - 10.0)
        base_complexity = min(10.0, max(1.0, (token_count / 5.0) + (1.5 if has_code_requirement else 0) + (1.0 if has_data_transform else 0)))

        # 4. Dense Feature Vector (for ML Classifier input)
        # [token_count, complexity_score, domain_index, has_code, has_math, has_search, has_data]
        domain_idx = self.DOMAINS.index(best_domain) if best_domain in self.DOMAINS else 4
        feature_vector = [
            float(token_count),
            round(base_complexity, 2),
            float(domain_idx),
            1.0 if has_code_requirement else 0.0,
            1.0 if has_math_requirement else 0.0,
            1.0 if has_search_requirement else 0.0,
            1.0 if has_data_transform else 0.0
        ]

        return {
            "user_goal": user_goal,
            "domain_category": best_domain,
            "complexity_score": round(base_complexity, 2),
            "token_count": token_count,
            "has_code_requirement": has_code_requirement,
            "has_math_requirement": has_math_requirement,
            "has_search_requirement": has_search_requirement,
            "has_data_transform": has_data_transform,
            "feature_vector": feature_vector
        }
