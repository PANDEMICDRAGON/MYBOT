"""Adaptive Quantum Entropy Sharding Engine.

Provides sharding of arbitrary bytes using a quantum entropy source (simulated via os.urandom)
to distribute data across shards for scalable storage and processing.
"""

import os
import base64
from dataclasses import dataclass
from typing import List

class ShardingError(Exception):
    """Base exception for sharding errors."""
    pass

@dataclass
class Shard:
    """Container for a data shard."""
    index: int
    payload: bytes

class QuantumEntropySharder:
    """Shard data using quantum entropy to randomize distribution.

    The algorithm generates cryptographically random split points, ensuring that
    shard boundaries are non‑deterministic and thus resistant to pattern‑based
    attacks. It also enforces a configurable minimum shard size to keep each
    fragment useful for downstream processing.
    """

    def __init__(self, shard_count: int = 4, min_shard_size: int = 1) -> None:
        if shard_count < 2:
            raise ValueError("shard_count must be at least 2")
        if min_shard_size < 1:
            raise ValueError("min_shard_size must be positive")
        self.shard_count = shard_count
        self.min_shard_size = min_shard_size

    def shard(self, data: bytes) -> List[Shard]:
        """Split *data* into ``shard_count`` shards.

        The split points are derived from quantum entropy to avoid deterministic
        patterns. Raises :class:`ShardingError` if the data is too small for the
        requested configuration.
        """
        if not isinstance(data, (bytes, bytearray)):
            raise TypeError("data must be bytes-like")
        if len(data) < self.shard_count * self.min_shard_size:
            raise ShardingError("Data too small for requested shard configuration")

        # Generate random split offsets (unique, sorted)
        offsets = sorted({int.from_bytes(os.urandom(2), "big") % len(data) for _ in range(self.shard_count - 1)})
        offsets = [0] + offsets + [len(data)]

        shards: List[Shard] = []
        for i in range(self.shard_count):
            start, end = offsets[i], offsets[i + 1]
            payload = data[start:end]
            # Ensure each shard meets the minimum size requirement
            if len(payload) < self.min_shard_size:
                if i + 1 < self.shard_count:
                    needed = self.min_shard_size - len(payload)
                    extra = data[end : end + needed]
                    payload += extra
                    offsets[i + 1] += needed
                else:
                    raise ShardingError("Unable to satisfy min_shard_size for final shard")
            shards.append(Shard(index=i, payload=payload))
        return shards

    @staticmethod
    def reconstruct(shards: List[Shard]) -> bytes:
        """Reassemble the original data from *shards*.

        Shards may be supplied in any order; they are sorted by their ``index``
        before concatenation. Validation ensures a contiguous index range.
        """
        if not shards:
            raise ShardingError("No shards provided")
        indices = sorted(s.index for s in shards)
        if indices != list(range(len(shards))):
            raise ShardingError("Shard indices are missing or duplicated")
        ordered = [s.payload for s in sorted(shards, key=lambda s: s.index)]
        return b"".join(ordered)

def _demo() -> None:
    """Simple demonstration when run as a script."""
    sample = b"The quick brown fox jumps over the lazy dog" * 10
    sharder = QuantumEntropySharder(shard_count=5, min_shard_size=10)
    shards = sharder.shard(sample)
    reconstructed = QuantumEntropySharder.reconstruct(shards)
    assert reconstructed == sample, "Reconstruction failed"
    print("Sharding successful. Number of shards:", len(shards))
    for shard in shards:
        preview = base64.b64encode(shard.payload[:6]).decode()
        print(f"Shard {shard.index}: {len(shard.payload)} bytes, preview: {preview}…")

if __name__ == "__main__":
    _demo()
