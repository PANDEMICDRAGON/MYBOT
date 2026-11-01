"""
Adaptive Memory Footprint Shranker & Dynamic GC Governor
Architected for Cortana / Michael Obiero (Nairobi, Kenya)

Dynamically regulates Python runtime garbage collection thresholds, evaluates heap
pressure, executes tiered generational garbage collection, and invokes registered
cache eviction hooks during high memory pressure scenarios.
"""

import gc
import sys
import os
import time
import threading
import logging
from typing import Dict, List, Optional, Tuple, Callable, Any
from dataclasses import dataclass, field
from enum import Enum

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("MemoryGCGovernor")

class MemoryPressureLevel(Enum):
    NORMAL = "NORMAL"
    ELEVATED = "ELEVATED"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

@dataclass
class MemoryPressureStats:
    rss_bytes: int
    ram_percentage: float
    pressure_level: MemoryPressureLevel
    gc_collections: Tuple[int, int, int]
    gc_uncollectable: int
    timestamp: float = field(default_factory=time.time)

@dataclass
class GCTuningProfile:
    threshold0: int
    threshold1: int
    threshold2: int
    description: str

class AdaptiveMemoryGCGovernor:
    """
    Monitors memory utilization, adjusts Python GC generational thresholds dynamically,
    and executes optimized GC cycles to preserve workstation stability.
    """
    
    PROFILES: Dict[MemoryPressureLevel, GCTuningProfile] = {
        MemoryPressureLevel.NORMAL: GCTuningProfile(700, 10, 10, "Standard balance"),
        MemoryPressureLevel.ELEVATED: GCTuningProfile(400, 8, 8, "Increased GC frequency"),
        MemoryPressureLevel.HIGH: GCTuningProfile(200, 5, 5, "Aggressive collection"),
        MemoryPressureLevel.CRITICAL: GCTuningProfile(100, 3, 3, "Maximum heap compaction"),
    }

    def __init__(self, target_ram_limit_percent: float = 85.0):
        self.target_ram_limit_percent = target_ram_limit_percent
        self._cleanup_hooks: List[Callable[[], int]] = []
        self._lock = threading.Lock()
        self._current_level = MemoryPressureLevel.NORMAL
        self._governance_history: List[MemoryPressureStats] = []
        self._initial_gc_thresholds = gc.get_threshold()

    def register_cleanup_hook(self, hook: Callable[[], int]) -> None:
        """Register a callback function that frees memory (returns bytes released)."""
        with self._lock:
            if hook not in self._cleanup_hooks:
                self._cleanup_hooks.append(hook)

    def _estimate_ram_usage(self) -> float:
        """Estimates system RAM percentage cleanly without external deps."""
        if os.path.exists("/proc/meminfo"):
            try:
                mem_total = 0
                mem_avail = 0
                with open("/proc/meminfo", "r") as f:
                    for line in f:
                        if line.startswith("MemTotal:"):
                            mem_total = int(line.split()[1])
                        elif line.startswith("MemAvailable:"):
                            mem_avail = int(line.split()[1])
                if mem_total > 0:
                    return ((mem_total - mem_avail) / mem_total) * 100.0
            except Exception as e:
                logger.warning(f"Error reading /proc/meminfo: {e}")
        return 91.6

    def _get_process_rss(self) -> int:
        """Returns approximate RSS bytes for current process."""
        try:
            import resource
            return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * 1024
        except Exception:
            return 0

    def assess_memory_pressure(self, ram_override: Optional[float] = None) -> MemoryPressureStats:
        """Evaluates current system memory status."""
        ram_percent = ram_override if ram_override is not None else self._estimate_ram_usage()
        
        if ram_percent >= 90.0:
            level = MemoryPressureLevel.CRITICAL
        elif ram_percent >= 80.0:
            level = MemoryPressureLevel.HIGH
        elif ram_percent >= 65.0:
            level = MemoryPressureLevel.ELEVATED
        else:
            level = MemoryPressureLevel.NORMAL

        stats = MemoryPressureStats(
            rss_bytes=self._get_process_rss(),
            ram_percentage=ram_percent,
            pressure_level=level,
            gc_collections=gc.get_count(),
            gc_uncollectable=len(gc.garbage)
        )
        return stats

    def apply_gc_profile(self, level: MemoryPressureLevel) -> None:
        """Applies dynamic GC threshold profile based on pressure level."""
        profile = self.PROFILES.get(level, self.PROFILES[MemoryPressureLevel.NORMAL])
        gc.set_threshold(profile.threshold0, profile.threshold1, profile.threshold2)
        self._current_level = level
        logger.info(f"Tuned GC Thresholds to ({profile.threshold0}, {profile.threshold1}, {profile.threshold2}) under {level.value} pressure.")

    def force_compact_heap(self, generation: int = 2) -> Tuple[int, int]:
        """
        Executes generational garbage collection and runs cleanup hooks.
        Returns tuple of (unreachable_objects_freed, external_bytes_freed).
        """
        with self._lock:
            external_freed = 0
            for hook in self._cleanup_hooks:
                try:
                    external_freed += hook()
                except Exception as ex:
                    logger.error(f"Error executing memory cleanup hook: {ex}")

            collected = gc.collect(generation)
            logger.info(f"Heap compaction completed. Reclaimed {collected} Python objects, {external_freed} external bytes.")
            return collected, external_freed

    def run_governance_cycle(self, ram_override: Optional[float] = None) -> MemoryPressureStats:
        """Main execution routine for memory pressure governance."""
        stats = self.assess_memory_pressure(ram_override=ram_override)
        self._governance_history.append(stats)
        
        if len(self._governance_history) > 100:
            self._governance_history.pop(0)

        if stats.pressure_level != self._current_level:
            self.apply_gc_profile(stats.pressure_level)

        if stats.pressure_level in (MemoryPressureLevel.HIGH, MemoryPressureLevel.CRITICAL):
            self.force_compact_heap(generation=2)
        elif stats.pressure_level == MemoryPressureLevel.ELEVATED:
            self.force_compact_heap(generation=1)

        return stats

    def restore_defaults(self) -> None:
        """Restores baseline GC parameters."""
        gc.set_threshold(*self._initial_gc_thresholds)
        logger.info("Restored baseline GC thresholds.")


if __name__ == "__main__":
    governor = AdaptiveMemoryGCGovernor()
    
    cache_store = [f"data_{i}" * 1000 for i in range(5000)]
    
    def purge_cache() -> int:
        nonlocal cache_store
        bytes_cleared = sys.getsizeof(cache_store)
        cache_store.clear()
        return bytes_cleared
        
    governor.register_cleanup_hook(purge_cache)
    
    print("[+] Test 1: Normal Memory Pressure Governance")
    stats1 = governor.run_governance_cycle(ram_override=50.0)
    assert stats1.pressure_level == MemoryPressureLevel.NORMAL
    
    print("[+] Test 2: Critical Memory Pressure Governance Trigger")
    stats2 = governor.run_governance_cycle(ram_override=92.5)
    assert stats2.pressure_level == MemoryPressureLevel.CRITICAL
    assert len(cache_store) == 0
    
    print("[+] Test 3: Baseline Restoration")
    governor.restore_defaults()
    print("[✓] All AdaptiveMemoryGCGovernor verification tests passed.")
