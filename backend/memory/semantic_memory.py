"""
Semantic Memory Store for Concept & Template Retrieval
"""
import math
import re
from typing import List, Dict, Any

class SemanticMemory:
    """
    Stores vector embeddings, concept associations, reusable code snippets,
    and task solution templates.
    """
    def __init__(self):
        self.kb_items: List[Dict[str, Any]] = [
            {
                "id": "sem_math_01",
                "domain": "Math",
                "keywords": ["math", "calculation", "formula", "equation", "evaluate", "algebra"],
                "strategy": "ToolHeavyPipeline",
                "template": "Step 1: Parse expression into standard arithmetic form. Step 2: Use MathCalculator tool to evaluate. Step 3: Verify numerical bounds.",
                "embedding": [0.9, 0.1, 0.2, 0.8, 0.0]
            },
            {
                "id": "sem_code_01",
                "domain": "Coding",
                "keywords": ["python", "code", "function", "script", "algorithm", "debug", "array", "fibonacci", "sort"],
                "strategy": "IterativeRefinement",
                "template": "Step 1: Formulate Python function implementation. Step 2: Run in PythonSandbox tool. Step 3: If error occurs, catch stderr and refine code.",
                "embedding": [0.1, 0.95, 0.3, 0.1, 0.1]
            },
            {
                "id": "sem_research_01",
                "domain": "Research",
                "keywords": ["search", "find", "information", "paper", "what is", "explain", "overview"],
                "strategy": "ReActReasoning",
                "template": "Step 1: Query web search tool for core concepts. Step 2: Extract factual synthesis. Step 3: Compose comprehensive explanation.",
                "embedding": [0.2, 0.2, 0.9, 0.3, 0.1]
            },
            {
                "id": "sem_analysis_01",
                "domain": "Data Analysis",
                "keywords": ["data", "statistics", "dataset", "average", "transform", "trend", "chart", "metrics"],
                "strategy": "DecompositionPipeline",
                "template": "Step 1: Decompose data into features. Step 2: Run Python data transformation script. Step 3: Aggregate summary statistics.",
                "embedding": [0.4, 0.6, 0.4, 0.9, 0.2]
            }
        ]

    def _simple_tokenize(self, text: str) -> List[str]:
        return re.findall(r'\w+', text.lower())

    def search_similar_tasks(self, text_query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        query_tokens = set(self._simple_tokenize(text_query))
        results = []

        for item in self.kb_items:
            # Calculate Jaccard similarity keyword match + domain bonus
            item_keywords = set(item["keywords"])
            intersection = query_tokens.intersection(item_keywords)
            union = query_tokens.union(item_keywords)
            score = len(intersection) / float(len(union)) if union else 0.0

            # Domain keyword match bonus
            if item["domain"].lower() in text_query.lower():
                score += 0.4

            results.append({
                "id": item["id"],
                "domain": item["domain"],
                "recommended_strategy": item["strategy"],
                "solution_template": item["template"],
                "similarity_score": round(score, 3)
            })

        results.sort(key=lambda x: x["similarity_score"], reverse=True)
        return results[:top_k]

    def add_solution_template(self, domain: str, strategy: str, template: str, keywords: List[str]):
        new_item = {
            "id": f"sem_custom_{len(self.kb_items) + 1:03d}",
            "domain": domain,
            "keywords": keywords,
            "strategy": strategy,
            "template": template,
            "embedding": [0.5, 0.5, 0.5, 0.5, 0.5]
        }
        self.kb_items.append(new_item)
