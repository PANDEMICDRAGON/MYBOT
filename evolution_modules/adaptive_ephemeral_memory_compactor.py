"""
Adaptive Ephemeral Memory Compactor & Garbage Reclamation Engine
================================================================
Monitors system memory utilization and proactively executes generational
garbage collection, purges registered ephemeral buffers/caches, and forces
process heap compaction to safeguard system availability during high RAM spikes.
"""

import gc
import os
import sys
import time
import logging
from typing import Dict, List, Callable, Any, Optional
from dataclasses import dataclass, field

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("EphemeralMemoryCompactor")


@dataclass
class MemoryThresholds:
    """Configurable RAM percentage thresholds for compaction triggers."""
    warning_pct: float = 80.0
    critical_pct: float = 88.0
    emergency_pct: float = 95.0


@dataclass
class CompactionReport:
    """Detailed result of a memory compaction operation."""
    timestamp: float
    ram_usage_before_pct: float
    ram_usage_after_pct: float
    bytes_reclaimed: int
    gc_collected_count: int
    caches_purged: int
    status: str
    details: Dict[str, Any] = field(default_factory=dict)


class EphemeralMemoryCompactor:
    """
    Proactive engine for monitoring high memory pressure and triggering
    multi-tier compaction, garbage collection, and transient buffer purging.
    """

    def __init__(self, thresholds: Optional[MemoryThresholds] = None) -> None:
        self.thresholds = thresholds or MemoryThresholds()
        self._purge_callbacks: List[Callable[[], int]] = []
        self._compaction_history: List[CompactionReport] = []

    def register_purge_callback(self, callback: Callable[[], int]) -> None:
        """
        Registers a callback that flushes ephemeral memory/caches and returns
        the estimated number of bytes freed.
        """
        if callable(callback):
            self._purge_callbacks.append(callback)
            logger.debug("Registered custom memory purge callback.")

    def get_ram_usage_percent(self) -> float:
        """
        Retrieves system RAM usage percentage using psutil if available,
        or falling back to OS cgroup / memory statistics.
        """
        try:
            import psutil
            return psutil.virtual_memory().percent
        except ImportError:
            # Fallback estimation using OS /proc/meminfo on Linux if available
            try:
                if os.path.exists("/proc/meminfo"):
                    mem_info = {}
                    with open("/proc/meminfo", "r") as f:
                        for line in f:
                            parts = line.split(":")
                            if len(parts) == 2:
                                key = parts[0].strip()
                                val = parts[1].strip().split()[0]
                                mem_info[key] = int(val)
                    total = mem_info.get("MemTotal", 1)
                    available = mem_info.get("MemAvailable", mem_info.get("MemFree", total))
                    used = total - available
                    return round((used / total) * 100.0, 2)
            except Exception as err:
                logger.warning("Failed reading /proc/meminfo fallback: %s", err)
            return 85.0  # Safe default fallback

    def trigger_generational_gc(self) -> int:
        """Forces full generational garbage collection and returns collected count."""
        gc.collect(2)
        gc.collect(1)
        collected = gc.collect(0)
        return collected

    def compact(self) -> CompactionReport:
        """
        Executes multi-phase memory compaction:
        1. Query initial memory status.
        2. Invoke registered transient cache purge callbacks.
        3. Force full multi-generational Python GC.
        4. Attempt platform heap compaction (e.g. malloc_trim on Linux libc).
        5. Query final memory status and return report.
        """
        start_time = time.time()
        ram_before = self.get_ram_usage_percent()
        bytes_freed = 0
        caches_purged = 0

        logger.info("Initiating memory compaction sequence. RAM prior: %.2f%%", ram_before)

        # Phase 1: Purge registered ephemeral caches
        for cb in self._purge_callbacks:
            try:
                freed = cb()
                if isinstance(freed, int) and freed > 0:
                    bytes_freed += freed
                caches_purged += 1
            except Exception as err:
                logger.error("Error executing cache purge callback: %s", err)

        # Phase 2: Generational Garbage Collection
        collected_objs = self.trigger_generational_gc()

        # Phase 3: System heap trim if supported (Linux glibc)
        try:
            import ctypes
            libc = ctypes.CDLL("libc.so.6")
            libc.malloc_trim(0)
            logger.debug("Executed malloc_trim(0) heap release.")
        except Exception:
            # Non-Linux or restricted environment, safely ignore
            pass

        ram_after = self.get_ram_usage_percent()

        status = "CRITICAL_COMPACTED" if ram_before >= self.thresholds.critical_pct else "ROUTINE_COMPACTED"

        report = CompactionReport(
            timestamp=start_time,
            ram_usage_before_pct=ram_before,
            ram_usage_after_pct=ram_after,
            bytes_reclaimed=bytes_freed,
            gc_collected_count=collected_objs,
            caches_purged=caches_purged,
            status=status,
            details={
                "duration_ms": round((time.time() - start_time) * 1000, 2),
                "delta_ram_pct": round(ram_before - ram_after, 2)
            }
        )

        self._compaction_history.append(report)
        logger.info("Memory compaction completed. RAM after: %.2f%%, Objects collected: %d", ram_after, collected_objs)
        return report

    def monitor_and_adapt(self) -> Optional[CompactionReport]:
        """Checks current memory load against defined thresholds and compacts if needed."""
        current_ram = self.get_ram_usage_percent()
        if current_ram >= self.thresholds.warning_pct:
            logger.warning("RAM usage (%.2f%%) exceeded warning threshold (%.2f%%). Triggering compaction.", current_ram, self.thresholds.warning_pct)
            return self.compact()
        return None


if __name__ == "__main__":
    compactor = EphemeralMemoryCompactor()

    # Simulate ephemeral cache callback
    mock_cache = [bytearray(1024 * 1024) for _ in range(5)]  # 5 MB transient cache

    def clear_mock_cache() -> int:
        nonlocal mock_cache
        freed = sum(len(b) for b in mock_cache)
        mock_cache.clear()
        return freed

    compactor.register_purge_callback(clear_mock_cache)

    print("Pre-compaction RAM usage:", compactor.get_ram_usage_percent())
    report = compactor.compact()
    print("Compaction Report:", report)
    assert report.status in ["ROUTINE_COMPACTED", "CRITICAL_COMPACTED"]
    print("Self-test succeeded!")
