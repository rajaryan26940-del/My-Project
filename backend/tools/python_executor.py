"""
Python Sandbox Executor Tool
"""
import sys
import subprocess
import tempfile
import os
import time
from typing import Dict, Any
from backend.tools.base import BaseTool

class PythonSandboxTool(BaseTool):
    def __init__(self, timeout_seconds: int = 10):
        super().__init__(
            name="python_sandbox",
            description="Executes Python code in a controlled subprocess and captures output, return values, or syntax/runtime errors.",
            category="coding"
        )
        self.timeout_seconds = timeout_seconds

    def execute(self, code: str, **kwargs) -> Dict[str, Any]:
        start_time = time.time()
        if not code or not isinstance(code, str):
            return {
                "success": False,
                "result": None,
                "error": "No Python code provided.",
                "execution_time": time.time() - start_time
            }

        # Clean code block indicators if any
        clean_code = code.strip()
        if clean_code.startswith("```python"):
            clean_code = clean_code[9:]
        elif clean_code.startswith("```"):
            clean_code = clean_code[3:]
        if clean_code.endswith("```"):
            clean_code = clean_code[:-3]
        clean_code = clean_code.strip()

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as temp_file:
            temp_file.write(clean_code)
            temp_path = temp_file.name

        try:
            process = subprocess.run(
                [sys.executable, temp_path],
                capture_output=True,
                text=True,
                timeout=self.timeout_seconds
            )
            elapsed = time.time() - start_time
            if process.returncode == 0:
                output = process.stdout.strip()
                return {
                    "success": True,
                    "result": output if output else "Executed successfully (no output).",
                    "error": None,
                    "execution_time": elapsed,
                    "stdout": process.stdout,
                    "stderr": process.stderr
                }
            else:
                return {
                    "success": False,
                    "result": None,
                    "error": process.stderr.strip() or f"Process exited with code {process.returncode}",
                    "execution_time": elapsed,
                    "stdout": process.stdout,
                    "stderr": process.stderr
                }
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "result": None,
                "error": f"Execution timed out after {self.timeout_seconds} seconds.",
                "execution_time": time.time() - start_time
            }
        except Exception as e:
            return {
                "success": False,
                "result": None,
                "error": str(e),
                "execution_time": time.time() - start_time
            }
        finally:
            if os.path.exists(temp_path):
                try:
                    os.remove(temp_path)
                except Exception:
                    pass
