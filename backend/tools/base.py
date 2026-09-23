"""
Base Tool Interface for AdaptiveAI Tools
"""
from abc import ABC, abstractmethod
from typing import Dict, Any

class BaseTool(ABC):
    def __init__(self, name: str, description: str, category: str):
        self.name = name
        self.description = description
        self.category = category

    @abstractmethod
    def execute(self, **kwargs) -> Dict[str, Any]:
        """
        Execute tool action.
        Returns dict containing:
        - success (bool)
        - result (Any)
        - error (str or None)
        - metadata (dict)
        """
        pass
