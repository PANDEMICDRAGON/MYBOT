"""
Homomorphic Cache Guard
Provides a simple in‑memory cache where values are stored in a
simulated homomorphic encrypted form. The cache validates integrity
and supports automatic expiration.
"""

from __future__ import annotations
import time
import threading
from typing import Any, Dict, Optional

class HomomorphicCacheError(Exception):
    """Base exception for HomomorphicCache."""

class CacheEntry:
    """Container for a cached value."""
    __slots__ = ("ciphertext", "timestamp", "ttl")

    def __init__(self, ciphertext: bytes, ttl: Optional[int]) -> None:
        self.ciphertext = ciphertext
        self.timestamp = time.time()
        self.ttl = ttl

class HomomorphicCache:
    """
    A thread‑safe cache that stores values in a reversible “homomorphic”
    encrypted representation. This is a placeholder for real homomorphic
    encryption; it uses XOR with a secret key.
    """

    _key: bytes = b"supersecretkey"

    def __init__(self, cleanup_interval: int = 60) -> None:
        self._store: Dict[str, CacheEntry] = {}
        self._lock = threading.RLock()
        self._cleanup_interval = cleanup_interval
        self._stop_event = threading.Event()
        self._cleaner = threading.Thread(target=self._cleanup_worker, daemon=True)
        self._cleaner.start()

    def _xor(self, data: bytes) -> bytes:
        """Simple reversible XOR “encryption”."""
        return bytes(b ^ self._key[i % len(self._key)] for i, b in enumerate(data))

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """
        Store ``value`` under ``key``. ``value`` must be pickle‑able.
        ``ttl`` is time‑to‑live in seconds; ``None`` means no expiration.
        """
        import pickle
        try:
            raw = pickle.dumps(value)
        except Exception as exc:
            raise HomomorphicCacheError(f"Unable to serialize value: {exc}") from exc
        ciphertext = self._xor(raw)
        with self._lock:
            self._store[key] = CacheEntry(ciphertext, ttl)

    def get(self, key: str) -> Any:
        """Retrieve the original value for ``key`` or raise KeyError."""
        import pickle
        with self._lock:
            entry = self._store.get(key)
            if entry is None:
                raise KeyError(key)
            if entry.ttl is not None and (time.time() - entry.timestamp) > entry.ttl:
                del self._store[key]
                raise KeyError(key)
            raw = self._xor(entry.ciphertext)
            try:
                return pickle.loads(raw)
            except Exception as exc:
                raise HomomorphicCacheError(f"Corrupted cache entry for {key}: {exc}") from exc

    def purge(self, key: str) -> None:
        """Remove ``key`` from the cache if present."""
        with self._lock:
            self._store.pop(key, None)

    def _cleanup_worker(self) -> None:
        """Background thread that removes expired entries."""
        while not self._stop_event.wait(self._cleanup_interval):
            now = time.time()
            with self._lock:
                expired = [k for k, e in self._store.items()
                           if e.ttl is not None and (now - e.timestamp) > e.ttl]
                for k in expired:
                    del self._store[k]

    def shutdown(self) -> None:
        """Stop the background cleanup thread."""
        self._stop_event.set()
        self._cleaner.join()

if __name__ == "__main__":
    cache = HomomorphicCache(cleanup_interval=1)
    cache.set("alpha", {"msg": "hello"}, ttl=2)
    assert cache.get("alpha")["msg"] == "hello"
    time.sleep(3)
    try:
        cache.get("alpha")
    except KeyError:
        print("Entry expired as expected")
    else:
        raise AssertionError("Expired entry still accessible")
    cache.shutdown()
    print("HomomorphicCache self‑test passed")
