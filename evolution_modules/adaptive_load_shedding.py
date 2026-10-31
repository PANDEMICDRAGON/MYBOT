"""
adaptive_load_shedding.py

Provides AdaptiveLoadShedding class to monitor system metrics and
throttle registered callables when resource usage exceeds thresholds.
"""

import threading
import time
import psutil
from typing import Callable, List, Tuple

class LoadSheddingError(RuntimeError):
    """Custom exception for load shedding failures."""
    pass

class AdaptiveLoadShedding:
    """Adaptive load shedding orchestrator.

    Register callables (tasks) with an associated weight. The orchestrator
    periodically checks CPU and memory usage; if thresholds are exceeded,
    it pauses or cancels lower‑priority tasks to keep the system responsive.
    """

    def __init__(self, cpu_threshold: float = 75.0, mem_threshold: float = 80.0, check_interval: float = 5.0) -> None:
        """Initialise the orchestrator.

        Args:
            cpu_threshold: CPU usage percentage above which shedding starts.
            mem_threshold: Memory usage percentage above which shedding starts.
            check_interval: Seconds between metric checks.
        """
        if not (0 < cpu_threshold <= 100):
            raise ValueError("cpu_threshold must be between 0 and 100")
        if not (0 < mem_threshold <= 100):
            raise ValueError("mem_threshold must be between 0 and 100")
        self.cpu_threshold = cpu_threshold
        self.mem_threshold = mem_threshold
        self.check_interval = check_interval
        self._tasks: List[Tuple[Callable[[], None], int, threading.Event]] = []
        self._stop_event = threading.Event()
        self._monitor_thread = threading.Thread(target=self._monitor, daemon=True)
        self._monitor_thread.start()

    def register_task(self, task: Callable[[], None], weight: int = 1) -> None:
        """Register a task for potential shedding.

        Args:
            task: Callable with no arguments.
            weight: Relative importance; higher weight = higher priority.
        """
        if weight <= 0:
            raise ValueError("weight must be positive")
        stop_event = threading.Event()
        thread = threading.Thread(target=self._run_task, args=(task, stop_event), daemon=True)
        self._tasks.append((thread.start, weight, stop_event))
        thread.start()

    def _run_task(self, task: Callable[[], None], stop_event: threading.Event) -> None:
        """Execute the task while respecting a stop signal."""
        try:
            while not stop_event.is_set():
                task()
                time.sleep(0)  # Yield to other threads
        except Exception as exc:
            raise LoadSheddingError(f"Task raised an exception: {exc}") from exc

    def _monitor(self) -> None:
        """Background monitor that triggers shedding when needed."""
        while not self._stop_event.is_set():
            cpu = psutil.cpu_percent(interval=None)
            mem = psutil.virtual_memory().percent
            if cpu > self.cpu_threshold or mem > self.mem_threshold:
                self._shed_load(cpu, mem)
            time.sleep(self.check_interval)

    def _shed_load(self, cpu: float, mem: float) -> None:
        """Pause or cancel lowest‑priority tasks until usage falls below thresholds."""
        # Sort tasks by weight ascending (lowest priority first)
        for _, weight, stop_event in sorted(self._tasks, key=lambda t: t[1]):
            if cpu <= self.cpu_threshold and mem <= self.mem_threshold:
                break
            stop_event.set()
            self._tasks = [t for t in self._tasks if t[2] is not stop_event]
            cpu = psutil.cpu_percent(interval=None)
            mem = psutil.virtual_memory().percent

    def shutdown(self) -> None:
        """Terminate monitoring and all registered tasks."""
        self._stop_event.set()
        for _, _, stop_event in self._tasks:
            stop_event.set()
        self._monitor_thread.join(timeout=self.check_interval * 2)

if __name__ == "__main__":
    # Simple demonstration: a CPU‑intensive dummy task.
    def busy_work():
        sum(i * i for i in range(10_000))

    orchestrator = AdaptiveLoadShedding(cpu_threshold=10.0, mem_threshold=30.0, check_interval=1.0)
    orchestrator.register_task(busy_work, weight=1)
    try:
        time.sleep(5)
    finally:
        orchestrator.shutdown()
        print("AdaptiveLoadShedding demo completed.")
