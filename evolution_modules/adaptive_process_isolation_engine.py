"""Adaptive Process Isolation Engine.

Provides utilities to execute external commands within confined
resource limits (CPU time, memory, execution timeout). Designed to
mitigate risk from untrusted workloads.
"""

import subprocess
import threading
import os
import sys
import signal
from typing import List, Optional, Tuple

class ProcessIsolationError(RuntimeError):
    """Base class for isolation errors."""
    pass

class ProcessTimeoutError(ProcessIsolationError):
    """Raised when a process exceeds the allowed execution time."""
    pass

class ProcessResourceLimitError(ProcessIsolationError):
    """Raised when a process exceeds memory or CPU limits."""
    pass

class AdaptiveProcessIsolationEngine:
    """Execute commands with configurable isolation constraints."""

    def __init__(self, timeout: Optional[float] = None,
                 memory_limit_mb: Optional[int] = None,
                 cpu_time_limit_sec: Optional[int] = None):
        """
        Parameters
        ----------
        timeout: max wall‑clock seconds the process may run.
        memory_limit_mb: maximum resident set size in megabytes (Unix only).
        cpu_time_limit_sec: maximum CPU time in seconds (Unix only).
        """
        self.timeout = timeout
        self.memory_limit_mb = memory_limit_mb
        self.cpu_time_limit_sec = cpu_time_limit_sec

    def _apply_unix_limits(self):
        """Apply resource limits to the child process (Unix only)."""
        if self.memory_limit_mb is not None:
            import resource
            soft = hard = self.memory_limit_mb * 1024 * 1024
            resource.setrlimit(resource.RLIMIT_AS, (soft, hard))
        if self.cpu_time_limit_sec is not None:
            import resource
            soft = hard = self.cpu_time_limit_sec
            resource.setrlimit(resource.RLIMIT_CPU, (soft, hard))

    def run(self, cmd: List[str], cwd: Optional[str] = None,
            env: Optional[dict] = None) -> Tuple[int, str, str]:
        """
        Execute *cmd* under the configured limits.

        Returns
        -------
        (returncode, stdout, stderr)

        Raises
        ------
        ProcessTimeoutError
            If the process runs longer than *self.timeout*.
        ProcessResourceLimitError
            If the OS kills the process due to a resource limit.
        ProcessIsolationError
            For other execution failures.
        """
        try:
            proc = subprocess.Popen(
                cmd,
                cwd=cwd,
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                preexec_fn=self._apply_unix_limits if os.name != 'nt' else None,
                text=True
            )
        except Exception as exc:
            raise ProcessIsolationError(f"Failed to start process: {exc}") from exc

        timer = None
        if self.timeout is not None:
            timer = threading.Timer(self.timeout, self._kill_process, args=(proc,))
            timer.start()

        try:
            stdout, stderr = proc.communicate()
        finally:
            if timer:
                timer.cancel()

        if proc.returncode < 0:
            sig = -proc.returncode
            if self.timeout is not None and sig == signal.SIGKILL:
                raise ProcessTimeoutError("Process exceeded timeout")
            raise ProcessResourceLimitError(f"Process killed by signal {sig}")

        return proc.returncode, stdout, stderr

    @staticmethod
    def _kill_process(proc: subprocess.Popen):
        """Forcefully terminate the process."""
        try:
            proc.kill()
        except Exception:
            pass

def _demo():
    engine = AdaptiveProcessIsolationEngine(timeout=2, memory_limit_mb=50, cpu_time_limit_sec=1)
    try:
        rc, out, err = engine.run([sys.executable, "-c", "print('hello')"])
        print(f"Return code: {rc}\nStdout: {out}\nStderr: {err}")
    except ProcessIsolationError as e:
        print(f"Isolation error: {e}")

if __name__ == "__main__":
    _demo()
