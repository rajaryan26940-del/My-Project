"""
Math Calculator Tool for Arithmetic and Algebraic Operations
"""
import time
import math
from typing import Dict, Any
from backend.tools.base import BaseTool

class MathCalculatorTool(BaseTool):
    def __init__(self):
        super().__init__(
            name="math_calculator",
            description="Evaluates mathematical, algebraic, and statistical expressions safely.",
            category="math"
        )

    def execute(self, expression: str, **kwargs) -> Dict[str, Any]:
        start_time = time.time()
        if not expression or not isinstance(expression, str):
            return {
                "success": False,
                "result": None,
                "error": "Math expression string is required.",
                "execution_time": time.time() - start_time
            }

        # Clean expression
        clean_expr = expression.replace("^", "**").strip()

        # Safe math namespace
        allowed_names = {
            "abs": abs,
            "round": round,
            "min": min,
            "max": max,
            "sum": sum,
            "pow": pow,
            "sin": math.sin,
            "cos": math.cos,
            "tan": math.tan,
            "sqrt": math.sqrt,
            "log": math.log,
            "log10": math.log10,
            "exp": math.exp,
            "pi": math.pi,
            "e": math.e,
            "factorial": math.factorial,
            "ceil": math.ceil,
            "floor": math.floor
        }

        try:
            # Check for disallowed characters or statements
            if any(char in clean_expr for char in [";", "__", "import", "exec", "eval", "lambda"]):
                return {
                    "success": False,
                    "result": None,
                    "error": "Expression contains prohibited language syntax.",
                    "execution_time": time.time() - start_time
                }

            val = eval(clean_expr, {"__builtins__": {}}, allowed_names)
            return {
                "success": True,
                "result": val,
                "error": None,
                "execution_time": time.time() - start_time,
                "expression": expression
            }
        except Exception as e:
            return {
                "success": False,
                "result": None,
                "error": f"Math Evaluation Error: {str(e)}",
                "execution_time": time.time() - start_time
            }
