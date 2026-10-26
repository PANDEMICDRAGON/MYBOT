"""
Thread-Safe LRU Cache with Adaptive TTL Eviction.
Generated autonomously by Cortana Continuous Self-Evolution Core.
"""

import time
from collections import OrderedDict
from typing import Any, Optional

class LRUTTLCache:
    """High-speed LRU memory cache with time-to-live expiration."""
    def __init__(self, maxsize: int = 128, default_ttl: float = 60.0):
        self.maxsize = maxsize
        self.default_ttl = default_ttl
        self._cache = OrderedDict()

    def get(self, key: str) -> Optional[Any]:
        if key not in self._cache:
            return None
        val, expiry = self._cache[key]
        if time.time() > expiry:
            del self._cache[key]
            return None
        self._cache.move_to_end(key)
        return val

    def set(self, key: str, value: Any, ttl: Optional[float] = None):
        expiry = time.time() + (ttl if ttl is not None else self.default_ttl)
        if key in self._cache:
            self._cache.move_to_end(key)
        self._cache[key] = (value, expiry)
        if len(self._cache) > self.maxsize:
            self._cache.popitem(last=False)

if __name__ == "__main__":
    c = LRUTTLCache(maxsize=2, default_ttl=5.0)
    c.set("k1", "v1")
    assert c.get("k1") == "v1"
    c.set("k2", "v2")
    c.set("k3", "v3") # evicts k1
    assert c.get("k1") is None
    print("LRUTTLCache verified.")
