"""adaptive_resource_quota.py

Adaptive Resource Quota Manager
Provides dynamic throttling of CPU-bound functions based on system load.
"""

import os
import time
import threading
from typing import Callable, Any, Optional

try:
    import psutil
except ImportError:  # pragma: no cover
    psutil = None


class ResourceQuotaError(RuntimeError):
    """Raised when a resource quota cannot be satisfied."""
    pass


class AdaptiveResourceQuota:
    """
    Manage execution of callables under adaptive CPU quota constraints.

    The manager monitors system CPU utilization and, if it exceeds a
    configurable threshold, it delays the execution of wrapped callables
    to keep the overall load within safe bounds.
    """

    def __init__(self, cpu_threshold: float = 75.0, check_interval: float = 1.0):
        """
        Initialise the quota manager.

        Args:
            cpu_threshold: Desired maximum CPU usage percentage (0‑100).
            check_interval: Seconds between utilisation checks.
        """
        if not (0 < cpu_threshold <= 100):
            raise ValueError("cpu_threshold must be in (0, 100].")
        if check_interval <= 0:
            raise ValueError("check_interval must be positive.")
        self.cpu_threshold = cpu_threshold
        self.check_interval = check_interval
        self._stop_event = threading.Event()
        self._monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self._current_cpu = 0.0
        self._monitor_thread.start()

    def _monitor_loop(self) -> None:
        """Background thread that updates the latest CPU utilisation measurement."""
        while not self._stop_event.is_set():
            try:
                if psutil:
                    self._current_cpu = psutil.cpu_percent(interval=None)
                else:
                    # Fallback: use os.getloadavg on Unix‑like systems
                    load1, _, _ = os.getloadavg()
                    cpu_count = os.cpu_count() or 1
                    self._current_cpu = min(100.0, (load1 / cpu_count) * 100)
            except Exception:
                self._current_cpu = 0.0
            time.sleep(self.check_interval)

    @property
    def current_cpu(self) -> float:
        """Return the most recent CPU utilisation measurement."""
        return self._current_cpu

    def run(self, func: Callable[..., Any], *args: Any, **kwargs: Any) -> Any:
        """
        Execute *func* respecting the adaptive quota.

        If the current CPU utilisation exceeds the threshold, the call is
        delayed in short increments until utilisation falls below the limit.

        Args:
            func: Callable to execute.
            *args, **kwargs: Arguments forwarded to *func*.

        Returns:
            The result of *func*.

        Raises:
            ResourceQuotaError: If the manager is stopped before execution.
        """
        while self.current_cpu > self.cpu_threshold:
            if self._stop_event.is_set():
                raise ResourceQuotaError("Quota manager stopped before execution.")
            time.sleep(0.2)  # back‑off interval
        return func(*args, **kwargs)

    def shutdown(self) -> None:
        """Terminate the background monitor thread."""
        self._stop_event.set()
        self._monitor_thread.join()


def _cpu_intensive_task(duration: float = 2.0) -> str:
    """A dummy CPU‑bound workload used for the self‑test."""
    end = time.time() + duration
    while time.time() < end:
        # Perform meaningless calculations to keep the CPU busy
        _ = sum(i * i for i in range(10_000))
    return "completed"


if __name__ == "__main__":
    quota = AdaptiveResourceQuota(cpu_threshold=80.0, check_interval=0.5)
    try:
        print(f"Initial CPU: {quota.current_cpu:.1f}%")
        result = quota.run(_cpu_intensive_task, duration=3)
        print(f"Task result: {result}")
        print(f"Post‑run CPU: {quota.current_cpu:.1f}%")
    finally:
        quota.shutdown()
