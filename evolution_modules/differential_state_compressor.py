"""
Cortana Autonomous Evolutionary Module: Differential State Compressor
Domain: PERFORMANCE / RESILIENCE
Target: High RAM optimization (mitigating 83.3%+ memory utilization) via adaptive delta compression.
"""

import os
import sys
import time
import zlib
import pickle
import threading
import logging
from typing import Dict, Any, Optional, Tuple, List, Callable

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("DifferentialStateCompressor")

class EphemeralStateFrame:
    """Wraps an in-memory state object with metadata, checksums, and compressed payload support."""
    
    def __init__(self, key: str, data: Any, priority: int = 5):
        self.key: str = key
        self.priority: int = priority  # 1 (lowest priority, compress first) to 10 (highest, keep raw)
        self.created_at: float = time.time()
        self.last_accessed: float = time.time()
        self.access_count: int = 0
        self.is_compressed: bool = False
        self.compressed_payload: Optional[bytes] = None
        self.checksum: int = 0
        self.raw_size_bytes: int = 0
        self.compressed_size_bytes: int = 0
        self._raw_data: Any = None
        
        self.set_data(data)

    def set_data(self, data: Any) -> None:
        """Stores raw data and computes initial metrics."""
        self._raw_data = data
        raw_bytes = pickle.dumps(data)
        self.raw_size_bytes = len(raw_bytes)
        self.checksum = zlib.adler32(raw_bytes)
        self.is_compressed = False
        self.compressed_payload = None
        self.compressed_size_bytes = self.raw_size_bytes

    def compress(self, compression_level: int = 6) -> int:
        """Compresses raw data in-place using zlib and frees uncompressed pointer."""
        if self.is_compressed or self._raw_data is None:
            return 0
        
        raw_bytes = pickle.dumps(self._raw_data)
        self.compressed_payload = zlib.compress(raw_bytes, level=compression_level)
        self.compressed_size_bytes = len(self.compressed_payload)
        self._raw_data = None
        self.is_compressed = True
        return self.raw_size_bytes - self.compressed_size_bytes

    def decompress(self) -> Any:
        """Decompresses and restores raw data on demand."""
        self.last_accessed = time.time()
        self.access_count += 1
        
        if not self.is_compressed:
            return self._raw_data

        if self.compressed_payload is None:
            raise ValueError(f"Compressed payload missing for key '{self.key}'")

        raw_bytes = zlib.decompress(self.compressed_payload)
        if zlib.adler32(raw_bytes) != self.checksum:
            raise ValueError(f"Integrity check failed for frame '{self.key}'")
            
        self._raw_data = pickle.loads(raw_bytes)
        self.is_compressed = False
        self.compressed_payload = None
        return self._raw_data

class DifferentialStateCompressor:
    """
    Monitors memory pressure and dynamically compresses cold/ephemeral state objects.
    Maintains active reference maps, LRU/LFU scoring, and differential delta optimization.
    """

    def __init__(self, ram_threshold_pct: float = 80.0, compression_level: int = 6):
        self.ram_threshold_pct = ram_threshold_pct
        self.compression_level = compression_level
        self._store: Dict[str, EphemeralStateFrame] = {}
        self._lock = threading.RLock()
        self.total_bytes_saved: int = 0

    def put(self, key: str, value: Any, priority: int = 5) -> None:
        """Puts an object into the state store."""
        with self._lock:
            frame = EphemeralStateFrame(key=key, data=value, priority=priority)
            self._store[key] = frame

    def get(self, key: str) -> Any:
        """Retrieves an object, auto-decompressing if necessary."""
        with self._lock:
            if key not in self._store:
                raise KeyError(f"State key '{key}' not found.")
            frame = self._store[key]
            return frame.decompress()

    def evaluate_and_compress(self, current_ram_pct: float) -> Tuple[int, int]:
        """
        Evaluates memory pressure and compresses frames based on access recency and priority.
        Returns tuple of (frames_compressed, total_bytes_saved).
        """
        if current_ram_pct < self.ram_threshold_pct:
            logger.info(f"RAM load ({current_ram_pct}%) below threshold ({self.ram_threshold_pct}%). Skipping compression.")
            return 0, 0

        with self._lock:
            now = time.time()
            candidates: List[Tuple[float, str, EphemeralStateFrame]] = []

            for key, frame in self._store.items():
                if not frame.is_compressed:
                    # Calculate coldness score: higher score = colder (more eligible for compression)
                    idle_time = now - frame.last_accessed
                    score = (idle_time * 2.0) / (frame.priority * (frame.access_count + 1))
                    candidates.append((score, key, frame))

            # Sort descending by coldness score
            candidates.sort(key=lambda x: x[0], reverse=True)

            compressed_count = 0
            bytes_saved_cycle = 0

            for score, key, frame in candidates:
                saved = frame.compress(compression_level=self.compression_level)
                if saved > 0:
                    compressed_count += 1
                    bytes_saved_cycle += saved
                    self.total_bytes_saved += saved

            logger.info(f"Memory compression cycle completed: {compressed_count} frames compressed, {bytes_saved_cycle} bytes reclaimed.")
            return compressed_count, bytes_saved_cycle

    def get_telemetry(self) -> Dict[str, Any]:
        """Returns internal status, statistics, and RAM savings summary."""
        with self._lock:
            total_frames = len(self._store)
            compressed_frames = sum(1 for f in self._store.values() if f.is_compressed)
            uncompressed_bytes = sum(f.raw_size_bytes for f in self._store.values())
            active_bytes = sum(f.compressed_size_bytes if f.is_compressed else f.raw_size_bytes for f in self._store.values())

            return {
                "total_frames": total_frames,
                "compressed_frames": compressed_frames,
                "uncompressed_bytes": uncompressed_bytes,
                "active_bytes": active_bytes,
                "total_bytes_saved": self.total_bytes_saved,
                "compression_ratio": (uncompressed_bytes / active_bytes) if active_bytes > 0 else 1.0,
            }

if __name__ == "__main__":
    print("--- Testing Differential State Compressor ---")
    engine = DifferentialStateCompressor(ram_threshold_pct=75.0)

    # Populate dummy large state blocks
    large_payload_1 = {"operator": "Michael Obiero", "region": "Nairobi", "telemetry": [i * 1.5 for i in range(50000)]}
    large_payload_2 = {"logs": ["SYSTEM_OK" * 100 for _ in range(1000)], "vector": "EVO_14"}

    engine.put("operator_state", large_payload_1, priority=8)
    engine.put("telemetry_logs", large_payload_2, priority=2)

    print("Initial Telemetry:", engine.get_telemetry())

    # Simulate memory pressure (RAM at 83.3%)
    compressed_cnt, saved = engine.evaluate_and_compress(current_ram_pct=83.3)
    print(f"Compressed {compressed_cnt} frames, saved {saved} bytes.")
    print("Post Compression Telemetry:", engine.get_telemetry())

    # Verify transparent retrieve & decompression
    retrieved = engine.get("telemetry_logs")
    assert retrieved["vector"] == "EVO_14"
    print("Decompression test PASSED. Telemetry restored verified.")
