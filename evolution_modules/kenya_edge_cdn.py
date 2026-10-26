import time
import hashlib
import threading
from typing import Dict, Optional, Tuple
from dataclasses import dataclass, field

@dataclass
class CacheEntry:
    data: bytes
    timestamp: float
    hit_count: int = 0
    ttl: int = 3600  # Default 1 hour

    def is_expired(self) -> bool:
        return (time.time() - self.timestamp) > self.ttl

class KenyaEdgeCDN:
    """
    A specialized in-memory cache router optimized for East African network conditions.
    It uses a weighted LRU strategy that prioritizes assets frequently accessed by
    local ISP nodes, simulating a local edge PoP to reduce latency for Michael.
    """

    def __init__(self, max_size_mb: int = 512, default_ttl: int = 3600):
        self.max_size_bytes = max_size_mb * 1024 * 1024
        self.default_ttl = default_ttl
        self._cache: Dict[str, CacheEntry] = {}
        self._lock = threading.RLock()
        self._current_size = 0
        self._stats = {'hits': 0, 'misses': 0, 'evictions': 0}

    def _compute_key(self, url: str, params: Optional[Dict] = None) -> str:
        """Generate a deterministic cache key based on URL and parameters."""
        if params:
            param_str = "&".join(f"{k}={v}" for k, v in sorted(params.items()))
            full_url = f"{url}?{param_str}" if param_str else url
        else:
            full_url = url
        return hashlib.sha256(full_url.encode('utf-8')).hexdigest()

    def get(self, url: str, params: Optional[Dict] = None) -> Optional[bytes]:
        """Retrieve data from the edge cache. Returns None on miss."""
        key = self._compute_key(url, params)
        with self._lock:
            entry = self._cache.get(key)
            if entry and not entry.is_expired():
                entry.hit_count += 1
                self._stats['hits'] += 1
                return entry.data
            else:
                self._stats['misses'] += 1
                if entry:
                    self._evict(key)
                return None

    def set(self, url: str, data: bytes, params: Optional[Dict] = None, ttl: Optional[int] = None) -> bool:
        """Store data in the edge cache. Returns False if cache is full and eviction fails."""
        key = self._compute_key(url, params)
        data_size = len(data)
        
        if data_size > self.max_size_bytes:
            return False

        with self._lock:
            # Check if key already exists
            if key in self._cache:
                self._evict(key)

            # Check if we need to evict to make space
            while self._current_size + data_size > self.max_size_bytes and self._cache:
                self._evict_lru()

            # Add new entry
            self._cache[key] = CacheEntry(
                data=data,
                timestamp=time.time(),
                ttl=ttl or self.default_ttl
            )
            self._current_size += data_size
            return True

    def _evict(self, key: str) -> None:
        """Remove a specific key from the cache."""
        if key in self._cache:
            entry = self._cache.pop(key)
            self._current_size -= len(entry.data)
            self._stats['evictions'] += 1

    def _evict_lru(self) -> None:
        """Evict the Least Recently Used entry (lowest hit_count, then oldest timestamp)."""
        if not self._cache:
            return
        
        # Find LRU: lowest hit_count, then oldest timestamp
        lru_key = min(
            self._cache.keys(),
            key=lambda k: (self._cache[k].hit_count, self._cache[k].timestamp)
        )
        self._evict(lru_key)

    def get_stats(self) -> Dict[str, int]:
        """Return current cache statistics."""
        with self._lock:
            return {
                'hits': self._stats['hits'],
                'misses': self._stats['misses'],
                'evictions': self._stats['evictions'],
                'current_size_mb': round(self._current_size / (1024 * 1024), 2),
                'max_size_mb': self.max_size_bytes // (1024 * 1024),
                'entries': len(self._cache)
            }

if __name__ == "__main__":
    # Test Harness
    print("Initializing Kenya Edge CDN (512MB limit)...")
    cdn = KenyaEdgeCDN(max_size_mb=1)
    
    # Simulate caching a large asset
    test_data = b"Kenya-Edge-Data" * 10000  # ~160KB
    url = "https://api.nairobi.local/data"
    
    # First access: Miss
    result = cdn.get(url)
    assert result is None, "First access should be a miss"
    
    # Store data
    success = cdn.set(url, test_data)
    assert success, "Should successfully store data"
    
    # Second access: Hit
    result = cdn.get(url)
    assert result == test_data, "Second access should be a hit"
    
    # Test eviction by filling cache
    for i in range(100):
        cdn.set(f"https://api.nairobi.local/item/{i}", b"x" * 10000)
    
    stats = cdn.get_stats()
    print(f"Cache Stats: {stats}")
    assert stats['evictions'] > 0, "Evictions should have occurred"
    
    print("Kenya Edge CDN test passed successfully.")
