"""self_healing_supervisor.py
Provides a lightweight self‑healing supervisor that can run callables or external commands in separate threads,
monitor their health, and automatically restart them with exponential back‑off.
Designed for resilience on edge devices with limited resources.
"""

import subprocess
import threading
import time
import logging
from typing import Callable, List, Optional, Union

logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(levelname)s: %(message)s')

class SupervisedTask:
    """Encapsulates a task that can be a Python callable or an external command."""
    def __init__(self,
                 name: str,
                 target: Union[Callable[[], None], List[str]],
                 *,
                 restart_limit: int = 5,
                 backoff_base: float = 1.0):
        self.name = name
        self.target = target
        self.restart_limit = restart_limit
        self.backoff_base = backoff_base
        self._restart_count = 0
        self._stop_event = threading.Event()
        self._thread: Optional[threading.Thread] = None

    def _run_callable(self) -> None:
        try:
            self.target()  # type: ignore[arg-type]
        finally:
            if not self._stop_event.is_set():
                raise RuntimeError('Callable terminated unexpectedly')

    def _run_subprocess(self) -> None:
        proc = subprocess.Popen(self.target, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = proc.communicate()
        if proc.returncode != 0:
            raise subprocess.CalledProcessError(proc.returncode, self.target, output=stdout, stderr=stderr)

    def _run(self) -> None:
        while not self._stop_event.is_set():
            try:
                if isinstance(self.target, list):
                    self._run_subprocess()
                else:
                    self._run_callable()
                break
            except Exception as exc:
                self._restart_count += 1
                if self._restart_count > self.restart_limit:
                    logging.error('%s exceeded restart limit (%d). Giving up.', self.name, self.restart_limit)
                    break
                backoff = self.backoff_base * (2 ** (self._restart_count - 1))
                logging.warning('%s crashed: %s. Restarting in %.1f seconds (attempt %d).',
                                self.name, exc, backoff, self._restart_count)
                time.sleep(backoff)

    def start(self) -> None:
        if self._thread and self._thread.is_alive():
            logging.info('%s is already running.', self.name)
            return
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._run, name=self.name, daemon=True)
        self._thread.start()
        logging.info('%s started.', self.name)

    def stop(self) -> None:
        self._stop_event.set()
        if self._thread:
            self._thread.join(timeout=5)
            logging.info('%s stopped.', self.name)

class SelfHealingSupervisor:
    """Manages a collection of SupervisedTask instances."""
    def __init__(self):
        self._tasks: dict[str, SupervisedTask] = {}

    def register(self, task: SupervisedTask) -> None:
        if task.name in self._tasks:
            raise ValueError(f"Task '{task.name}' already registered.")
        self._tasks[task.name] = task
        task.start()

    def deregister(self, name: str) -> None:
        task = self._tasks.pop(name, None)
        if task:
            task.stop()

    def shutdown(self) -> None:
        for name in list(self._tasks):
            self.deregister(name)

if __name__ == "__main__":
    # Demo: a flaky worker that raises after a few seconds
    def flaky_worker():
        import random, sys
        for i in range(5):
            if random.random() < 0.3:
                raise RuntimeError('Simulated failure')
            print(f'Flaky worker iteration {i}')
            time.sleep(0.5)
        sys.exit(0)

    supervisor = SelfHealingSupervisor()
    task = SupervisedTask(name='flaky_worker', target=flaky_worker, restart_limit=3, backoff_base=0.5)
    supervisor.register(task)

    # Let the demo run for 15 seconds then clean up
    time.sleep(15)
    supervisor.shutdown()
