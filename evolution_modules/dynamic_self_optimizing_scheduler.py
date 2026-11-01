from __future__ import annotations
import threading
import time
import os
from concurrent.futures import ThreadPoolExecutor, Future
from typing import Callable, Any, List

class SchedulerError(Exception):
    """Base exception for the scheduler."""

class ResourceScheduler:
    """Dynamically adjusts a thread pool based on system load.

    The scheduler monitors CPU load and memory usage every ``interval`` seconds.
    If the load exceeds ``cpu_threshold`` or memory usage exceeds ``mem_threshold``,
    the pool size is reduced; otherwise it is increased up to ``max_workers``.
    """

    def __init__(
        self,
        max_workers: int = 10,
        cpu_threshold: float = 0.75,
        mem_threshold: float = 0.80,
        interval: float = 5.0,
    ) -> None:
        if max_workers < 1:
            raise SchedulerError("max_workers must be >= 1")
        self.max_workers = max_workers
        self.cpu_threshold = cpu_threshold
        self.mem_threshold = mem_threshold
        self.interval = interval
        self._executor = ThreadPoolExecutor(max_workers=1)
        self._lock = threading.Lock()
        self._stop_event = threading.Event()
        self._monitor_thread = threading.Thread(target=self._monitor, daemon=True)
        self._monitor_thread.start()

    def _current_cpu(self) -> float:
        """Return the recent CPU utilization as a float between 0 and 1."""
        try:
            load1, _, _ = os.getloadavg()
            cpu_count = os.cpu_count() or 1
            return min(load1 / cpu_count, 1.0)
        except OSError:
            return 0.0

    def _current_mem(self) -> float:
        """Return memory usage as a float between 0 and 1."""
        try:
            import psutil  # type: ignore
            mem = psutil.virtual_memory()
            return mem.percent / 100.0
        except Exception:
            return 0.0

    def _adjust_workers(self, target: int) -> None:
        with self._lock:
            self._executor.shutdown(wait=False)
            self._executor = ThreadPoolExecutor(max_workers=target)

    def _monitor(self) -> None:
        while not self._stop_event.is_set():
            cpu = self._current_cpu()
            mem = self._current_mem()
            current = self._executor._max_workers  # type: ignore
            if cpu > self.cpu_threshold or mem > self.mem_threshold:
                new_size = max(1, current - 1)
            else:
                new_size = min(self.max_workers, current + 1)
            if new_size != current:
                self._adjust_workers(new_size)
            time.sleep(self.interval)

    def submit(self, fn: Callable[..., Any], *args: Any, **kwargs: Any) -> Future:
        """Submit a callable to the managed thread pool."""
        if self._stop_event.is_set():
            raise SchedulerError("Scheduler is shutting down")
        return self._executor.submit(fn, *args, **kwargs)

    def shutdown(self, wait: bool = True) -> None:
        """Stop monitoring and shut down the executor."""
        self._stop_event.set()
        self._monitor_thread.join()
        self._executor.shutdown(wait=wait)

def _demo_task(duration: float, identifier: int) -> str:
    time.sleep(duration)
    return f"Task {identifier} completed after {duration}s"

if __name__ == "__main__":
    scheduler = ResourceScheduler(max_workers=4, interval=2.0)
    futures: List[Future] = []
    for i in range(8):
        futures.append(scheduler.submit(_demo_task, 1 + (i % 3) * 0.5, i))
    for f in futures:
        print(f.result())
    scheduler.shutdown()