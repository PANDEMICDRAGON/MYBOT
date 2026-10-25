import asyncio
import time
import random
import logging
from typing import Optional, Tuple
from dataclasses import dataclass

# Configure logging for the module
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Cortana.KenyaLatencyOptimizer")

@dataclass
class LatencyProfile:
    """Stores statistical data about network latency."""
    min_ms: float
    max_ms: float
    avg_ms: float
    p95_ms: float
    sample_count: int

class KenyaLatencyOptimizer:
    """
    Proactively profiles network latency to optimize timeout settings
    for operations in Kenya (Kitengela/Nairobi). Adapts to local ISP conditions.
    """
    
    def __init__(self, base_timeout: float = 5.0, min_timeout: float = 1.0, max_timeout: float = 30.0):
        """
        Initialize the optimizer.
        
        Args:
            base_timeout: Default timeout in seconds.
            min_timeout: Hard floor for timeout to prevent immediate failure.
            max_timeout: Hard ceiling to prevent indefinite hangs.
        """
        self.base_timeout = base_timeout
        self.min_timeout = min_timeout
        self.max_timeout = max_timeout
        self._recent_latencies: list[float] = []
        self._lock = asyncio.Lock()
        self._last_profile: Optional[LatencyProfile] = None
        
    async def measure_latency(self, host: str = "1.1.1.1", port: int = 443) -> float:
        """
        Measure TCP connection latency to a stable host.
        Uses 1.1.1.1 (Cloudflare) as a reliable benchmark for global reachability.
        
        Args:
            host: Target host for latency test.
            port: Target port.
            
        Returns:
            Latency in milliseconds.
        """
        start = time.perf_counter_ns() / 1_000_000  # Convert to ms
        try:
            reader, writer = await asyncio.open_connection(host, port)
            writer.close()  # Close immediately, we only care about connection time
            if writer.transport:
                writer.transport.close() 
        except (ConnectionError, OSError) as e:
            logger.warning(f"Latency probe failed for {host}: {e}")
            return float('inf')
        
        end = time.perf_counter_ns() / 1_000_000
        latency_ms = end - start
        
        # Store for profiling
        async with self._lock:
            self._recent_latencies.append(latency_ms)
            if len(self._recent_latencies) > 100:
                self._recent_latencies.pop(0)
        
        return latency_ms

    def get_adaptive_timeout(self) -> float:
        """
        Calculate an adaptive timeout based on recent latency history.
        
        Returns:
            Recommended timeout in seconds.
        """
        if not self._recent_latencies:
            return self.base_timeout

        # Calculate P95 latency
        sorted_latencies = sorted(self._recent_latencies)
        p95_index = int(len(sorted_latencies) * 0.95)
        p95_latency_ms = sorted_latencies[min(p95_index, len(sorted_latencies) - 1)]

        # Convert to seconds and add buffer (2x P95 to account for jitter)
        adaptive_timeout = (p95_latency_ms / 1000.0) * 2.0

        # Clamp between min and max
        return max(self.min_timeout, min(self.max_timeout, adaptive_timeout))

    async def run_proactive_profile(self, iterations: int = 5) -> LatencyProfile:
        """
        Run a series of latency measurements to build a profile.
        
        Args:
            iterations: Number of probes to run.
            
        Returns:
            LatencyProfile object.
        """
        latencies = []
        for _ in range(iterations):
            latency = await self.measure_latency()
            if latency != float('inf'):
                latencies.append(latency)
            await asyncio.sleep(0.1)  # Small delay between probes

        if not latencies:
            logger.error("No valid latency samples collected.")
            return LatencyProfile(0, 0, 0, 0, 0)

        sorted_lat = sorted(latencies)
        p95_index = int(len(sorted_lat) * 0.95)
        
        profile = LatencyProfile(
            min_ms=min(latencies),
            max_ms=max(latencies),
            avg_ms=sum(latencies) / len(latencies),
            p95_ms=sorted_lat[min(p95_index, len(sorted_lat) - 1)],
            sample_count=len(latencies)
        )
        
        self._last_profile = profile
        logger.info(f"Latency Profile Updated: Avg={profile.avg_ms:.2f}ms, P95={profile.p95_ms:.2f}ms")
        return profile

if __name__ == "__main__":
    async def main():
        optimizer = KenyaLatencyOptimizer(base_timeout=5.0)
        
        # Run proactive profile
        profile = await optimizer.run_proactive_profile(iterations=3)
        
        # Get adaptive timeout
        adaptive_timeout = optimizer.get_adaptive_timeout()
        
        print(f"Current Adaptive Timeout: {adaptive_timeout:.2f}s")
        print(f"Profile: {profile}")

    asyncio.run(main())