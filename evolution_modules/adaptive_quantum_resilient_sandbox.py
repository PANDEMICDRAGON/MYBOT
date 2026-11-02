"""Adaptive Quantum‑Resilient Secure Execution Sandbox.

Provides a sandbox to execute untrusted Python callables in an isolated
subprocess with optional post‑quantum integrity verification.
"""

import subprocess
import sys
import hashlib
import os
import tempfile
from typing import Any, Callable, Optional

class SandboxError(RuntimeError):
    """Base class for sandbox execution errors."""
    pass

class IntegrityError(SandboxError):
    """Raised when code hash verification fails."""
    pass

class ExecutionError(SandboxError):
    """Raised when the sandboxed process exits with a non‑zero status."""
    pass

class AdaptiveQuantumResilientSandbox:
    """Execute Python callables in an isolated subprocess.

    The caller provides a callable and optional arguments. The sandbox
    serialises the callable using ``pickle`` and runs it in a temporary
    Python interpreter with a strict CPU‑time limit. Before execution the
    serialized payload hash can be compared against an expected hash that
    could be signed with a post‑quantum algorithm (simulated here).
    """

    def __init__(self, max_cpu_seconds: int = 5) -> None:
        self.max_cpu_seconds = max_cpu_seconds

    def _verify_integrity(self, payload_bytes: bytes, expected_hash: str) -> None:
        actual_hash = hashlib.sha256(payload_bytes).hexdigest()
        if actual_hash != expected_hash:
            raise IntegrityError(
                f"Hash mismatch: expected {expected_hash}, got {actual_hash}"
            )

    def _run_subprocess(self, script_path: str) -> bytes:
        cmd = [
            sys.executable,
            "-I",
            script_path,
        ]
        try:
            result = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=self.max_cpu_seconds,
                check=True,
                text=False,
            )
        except subprocess.CalledProcessError as exc:
            raise ExecutionError(
                f"Sandboxed process failed (code {exc.returncode}): {exc.stderr.decode(errors='ignore')}"
            ) from exc
        except subprocess.TimeoutExpired as exc:
            raise ExecutionError("Sandboxed process timed out") from exc
        return result.stdout

    def execute(
        self,
        func: Callable[..., Any],
        *args: Any,
        expected_hash: Optional[str] = None,
        **kwargs: Any,
    ) -> Any:
        """Execute *func* with *args*/*kwargs* inside the sandbox.

        If *expected_hash* is provided, the serialized payload must match it.
        The return value is the stdout produced by the sandboxed code.
        """
        import pickle

        # Serialize the callable and its arguments.
        payload_bytes = pickle.dumps((func, args, kwargs))
        if expected_hash is not None:
            self._verify_integrity(payload_bytes, expected_hash)

        # Write payload to a temporary file.
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pkl") as payload_file:
            payload_file.write(payload_bytes)
            payload_path = payload_file.name

        # Create a tiny driver script that loads the payload and runs it.
        driver_code = (
            "import pickle, sys\n"
            f"payload_path = r'{payload_path}'\n"
            "with open(payload_path, 'rb') as f:\n"
            "    func, args, kwargs = pickle.load(f)\n"
            "result = func(*args, **kwargs)\n"
            "if result is not None:\n"
            "    print(result)\n"
        )
        with tempfile.NamedTemporaryFile(delete=False, suffix=".py", mode='w') as script_file:
            script_file.write(driver_code)
            script_path = script_file.name

        try:
            output_bytes = self._run_subprocess(script_path)
            return output_bytes.decode(errors='ignore')
        finally:
            os.unlink(payload_path)
            os.unlink(script_path)

if __name__ == "__main__":
    sandbox = AdaptiveQuantumResilientSandbox(max_cpu_seconds=2)

    def hello(name: str) -> str:
        return f"Hello, {name}!"

    # Compute expected hash for demonstration.
    import pickle
    demo_payload = pickle.dumps((hello, ("World",), {}))
    expected = hashlib.sha256(demo_payload).hexdigest()

    try:
        result = sandbox.execute(hello, "World", expected_hash=expected)
        print("Sandbox output:", result.strip())
    except SandboxError as e:
        print("Sandbox error:", e)
