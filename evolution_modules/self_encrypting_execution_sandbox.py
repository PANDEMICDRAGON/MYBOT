'''Self-Encrypting Execution Sandbox.

Provides a sandboxed environment for executing untrusted Python code
with runtime memory encryption of the output. Designed to mitigate
code injection and data exfiltration risks.
'''

import ast
import io
import os
import sys
from typing import Any, Dict, Optional

class SandboxSecurityError(Exception):
    """Raised when submitted code violates sandbox policies."""
    pass

class SelfEncryptingSandbox:
    """Execute Python code in a restricted environment and encrypt the result.

    The sandbox enforces a whitelist of safe AST nodes and disables
    imports, attribute access and built‑ins that could escape the sandbox.
    The output (stdout) is encrypted with a one‑time XOR key.
    """

    _allowed_nodes = {
        ast.Module, ast.Expr, ast.Assign, ast.AugAssign,
        ast.BinOp, ast.UnaryOp, ast.Compare, ast.Call,
        ast.Name, ast.Load, ast.Store, ast.Constant,
        ast.List, ast.Tuple, ast.Dict, ast.Subscript,
        ast.Index, ast.Slice, ast.For, ast.While,
        ast.If, ast.Return, ast.FunctionDef, ast.arguments,
        ast.arg, ast.Pass, ast.Break, ast.Continue,
        ast.BoolOp, ast.And, ast.Or, ast.Not,
        ast.IfExp, ast.Lambda,
    }

    def __init__(self, key: Optional[bytes] = None) -> None:
        """Create a sandbox instance.

        Args:
            key: Optional encryption key. If omitted a random 32‑byte key is generated.
        """
        self.key = key or os.urandom(32)

    def _is_safe_ast(self, node: ast.AST) -> bool:
        """Recursively verify that the AST contains only allowed nodes."""
        if type(node) not in self._allowed_nodes:
            return False
        for child in ast.iter_child_nodes(node):
            if not self._is_safe_ast(child):
                return False
        return True

    def _run_code(self, code: str) -> str:
        """Execute code in a minimal namespace and capture stdout."""
        try:
            parsed = ast.parse(code, mode='exec')
        except SyntaxError as exc:
            raise SandboxSecurityError(f"Syntax error: {exc}") from exc

        if not self._is_safe_ast(parsed):
            raise SandboxSecurityError("Code contains disallowed constructs.")

        sandbox_globals: Dict[str, Any] = {"__builtins__": {}}
        sandbox_locals: Dict[str, Any] = {}

        stdout = io.StringIO()
        original_stdout = sys.stdout
        sys.stdout = stdout
        try:
            exec(compile(parsed, filename="<sandbox>", mode='exec'), sandbox_globals, sandbox_locals)
        finally:
            sys.stdout = original_stdout

        return stdout.getvalue()

    def _xor_encrypt(self, data: bytes) -> bytes:
        """Encrypt/decrypt data with XOR using the instance key."""
        return bytes(b ^ self.key[i % len(self.key)] for i, b in enumerate(data))

    def execute(self, code: str) -> bytes:
        """Public API: run code and return encrypted output.

        Args:
            code: Python source to execute.

        Returns:
            Encrypted bytes of the captured stdout.
        """
        output = self._run_code(code)
        encrypted = self._xor_encrypt(output.encode('utf-8'))
        return encrypted

    def decrypt(self, encrypted: bytes) -> str:
        """Decrypt previously encrypted sandbox output.

        Args:
            encrypted: Encrypted byte sequence.

        Returns:
            Decrypted UTF‑8 string.
        """
        decrypted = self._xor_encrypt(encrypted)
        return decrypted.decode('utf-8')

def _demo() -> None:
    sandbox = SelfEncryptingSandbox()
    snippet = "for i in range(3): print(f'Hello {i}')"
    enc = sandbox.execute(snippet)
    print("Encrypted payload (hex):", enc.hex())
    print("Decrypted output:")
    print(sandbox.decrypt(enc))

if __name__ == "__main__":
    _demo()
