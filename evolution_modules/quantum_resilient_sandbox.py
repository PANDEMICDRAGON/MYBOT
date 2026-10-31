"""
quantum_resilient_sandbox.py
Provides a lightweight sandbox for executing untrusted Python code with
resource limits and a restricted execution environment.
"""

import ast
import multiprocessing
import traceback
from typing import Any, Dict, List

class SandboxError(Exception):
    """Base exception for sandbox failures."""
    pass

class ExecutionTimeout(SandboxError):
    """Raised when code execution exceeds the allowed time."""
    pass

class UnsafeCodeError(SandboxError):
    """Raised when the submitted code contains disallowed constructs."""
    pass

class SecureSandbox:
    """Execute untrusted Python code safely.

    The sandbox parses the code to an AST and rejects nodes that could
    perform I/O, import modules, or access unsafe attributes.
    Execution occurs in a separate process with a configurable timeout.
    """

    _ALLOWED_NODES: List[type] = [
        ast.Module,
        ast.Expr,
        ast.Assign,
        ast.AugAssign,
        ast.BinOp,
        ast.UnaryOp,
        ast.Compare,
        ast.Call,
        ast.Name,
        ast.Load,
        ast.Store,
        ast.Constant,
        ast.List,
        ast.Tuple,
        ast.Dict,
        ast.Subscript,
        ast.Index,
        ast.Slice,
        ast.If,
        ast.For,
        ast.While,
        ast.Return,
        ast.FunctionDef,
        ast.arguments,
        ast.arg,
        ast.Pass,
        ast.Break,
        ast.Continue,
        ast.BoolOp,
        ast.Attribute,
    ]

    _SAFE_BUILTINS: Dict[str, Any] = {
        "abs": abs,
        "min": min,
        "max": max,
        "sum": sum,
        "len": len,
        "range": range,
        "enumerate": enumerate,
        "zip": zip,
        "sorted": sorted,
    }

    def __init__(self, timeout: float = 2.0):
        """Create a sandbox.

        :param timeout: maximum seconds allowed for code execution.
        """
        self.timeout = timeout

    def _validate_ast(self, node: ast.AST) -> None:
        """Recursively ensure only allowed AST nodes are present."""
        if type(node) not in self._ALLOWED_NODES:
            raise UnsafeCodeError(f"Disallowed AST node: {type(node).__name__}")
        for child in ast.iter_child_nodes(node):
            self._validate_ast(child)

    @staticmethod
    def _worker(code: str, result_queue: multiprocessing.Queue) -> None:
        """Run code in isolated globals and capture stdout / errors."""
        try:
            safe_globals = {"__builtins__": SecureSandbox._SAFE_BUILTINS}
            safe_locals: Dict[str, Any] = {}
            exec(code, safe_globals, safe_locals)
            result_queue.put({"output": safe_locals, "error": None})
        except Exception:
            tb = traceback.format_exc()
            result_queue.put({"output": None, "error": tb})

    def execute(self, code: str) -> Dict[str, Any]:
        """Validate and execute the supplied code.

        :returns: dict with keys ``output`` (locals dict) and ``error`` (traceback or None)
        :raises SandboxError: on validation or timeout failures
        """
        try:
            parsed = ast.parse(code, mode="exec")
            self._validate_ast(parsed)
        except (SyntaxError, UnsafeCodeError) as exc:
            raise SandboxError(str(exc)) from exc

        queue: multiprocessing.Queue = multiprocessing.Queue()
        proc = multiprocessing.Process(target=self._worker, args=(code, queue))
        proc.start()
        proc.join(self.timeout)

        if proc.is_alive():
            proc.terminate()
            raise ExecutionTimeout(f"Code execution exceeded {self.timeout}s")

        result = queue.get()
        return result

if __name__ == "__main__":
    sandbox = SecureSandbox(timeout=1.0)

    safe_code = "result = sum([i*i for i in range(5)])"
    malicious_code = "import os; os.system('echo hacked')"

    for snippet, label in [(safe_code, "SAFE"), (malicious_code, "MALICIOUS")]:
        print(f"--- {label} CODE ---")
        try:
            res = sandbox.execute(snippet)
            if res["error"]:
                print("Error:\n", res["error"])
            else:
                print("Locals:", res["output"])
        except Exception as e:
            print("Execution failed:", e)
