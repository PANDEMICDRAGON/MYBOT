"""Predictive Edge Cache Warmup Engine.

Provides a lightweight scheduler that predicts future cache keys based on recent
access patterns and prefetches them using a pluggable fetcher.
"""

import logging
import threading
import time
from collections import Counter, deque
from typing import Callable, Deque, List, Tuple

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class PredictiveCacheWarmup:
    """Continuously learns request frequencies and prefetches hot keys.

    Attributes
    ----------
    window_size: int
        Number of recent requests to keep for frequency analysis.
    top_k: int
        Number of keys to prefetch each cycle.
    fetcher: Callable[[str], None]
        Function that performs the actual prefetch for a given key.
    """

    def __init__(self, fetcher: Callable[[str], None], window_size: int = 1000, top_k: int = 10, interval: float = 5.0):
        if window_size <= 0:
            raise ValueError("window_size must be positive")
        if top_k <= 0:
            raise ValueError("top_k must be positive")
        if interval <= 0:
            raise ValueError("interval must be positive")
        self.fetcher = fetcher
        self.window_size = window_size
        self.top_k = top_k
        self.interval = interval
        self._history: Deque[str] = deque(maxlen=window_size)
        self._stop_event = threading.Event()
        self._thread = threading.Thread(target=self._run, daemon=True)

    def start(self) -> None:
        """Start the background warm‑up thread."""
        if self._thread.is_alive():
            logger.warning("Warmup thread already running")
            return
        logger.info("Starting PredictiveCacheWarmup")
        self._stop_event.clear()
        self._thread.start()

    def stop(self) -> None:
        """Signal the background thread to stop and wait for it."""
        logger.info("Stopping PredictiveCacheWarmup")
        self._stop_event.set()
        self._thread.join()

    def record_request(self, key: str) -> None:
        """Record a cache key request observed by the edge node."""
        if not isinstance(key, str):
            raise TypeError("key must be a string")
        self._history.append(key)

    def _run(self) -> None:
        while not self._stop_event.is_set():
            try:
                self._prefetch_hot_keys()
            except Exception as exc:  # pragma: no cover
                logger.exception("Unexpected error in warmup loop: %s", exc)
            time.sleep(self.interval)

    def _prefetch_hot_keys(self) -> None:
        if not self._history:
            logger.debug("No request history yet")
            return
        counter: Counter = Counter(self._history)
        hot_keys: List[Tuple[str, int]] = counter.most_common(self.top_k)
        logger.info("Prefetching %d hot keys: %s", len(hot_keys), [k for k, _ in hot_keys])
        for key, _ in hot_keys:
            try:
                self.fetcher(key)
            except Exception as exc:
                logger.error("Failed to prefetch key %s: %s", key, exc)

def _dummy_fetcher(key: str) -> None:
    """Placeholder fetcher used in the __main__ demo."""
    logger.info("Prefetching key %s (simulated)", key)

def _demo() -> None:
    warmup = PredictiveCacheWarmup(fetcher=_dummy_fetcher, window_size=50, top_k=3, interval=2.0)
    warmup.start()
    sample_keys = ["home", "profile", "dashboard", "settings", "home", "home", "profile"]
    for _ in range(20):
        warmup.record_request(sample_keys[_ % len(sample_keys)])
        time.sleep(0.3)
    warmup.stop()

if __name__ == "__main__":
    _demo()
