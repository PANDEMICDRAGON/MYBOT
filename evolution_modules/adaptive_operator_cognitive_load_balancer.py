"""
adaptive_operator_cognitive_load_balancer.py
"""

from __future__ import annotations
import random
import time
from dataclasses import dataclass
from typing import Callable, List

class CognitiveLoadError(Exception):
    """Raised when load metrics are out of expected bounds."""
    pass

@dataclass
class LoadMetric:
    """Single load measurement."""
    timestamp: float
    cpu_percent: float
    ram_percent: float
    heart_rate: float  # beats per minute

class AdaptiveOperatorCognitiveLoadBalancer:
    """Balances system interaction intensity based on the operator's cognitive load.
    The balancer receives continuous LoadMetric samples, computes a weighted
    load score and decides whether to throttle non‑essential notifications.
    """

    def __init__(self,
                 cpu_weight: float = 0.4,
                 ram_weight: float = 0.3,
                 hr_weight: float = 0.3,
                 threshold: float = 0.7,
                 on_throttle: Callable[[bool], None] | None = None) -> None:
        if not 0 <= cpu_weight <= 1 or not 0 <= ram_weight <= 1 or not 0 <= hr_weight <= 1:
            raise ValueError("Weights must be between 0 and 1.")
        total = cpu_weight + ram_weight + hr_weight
        if not 0.99 <= total <= 1.01:
            raise ValueError("Weights must sum to 1.")
        self.cpu_weight = cpu_weight
        self.ram_weight = ram_weight
        self.hr_weight = hr_weight
        self.threshold = threshold
        self.on_throttle = on_throttle
        self.history: List[LoadMetric] = []

    def ingest(self, metric: LoadMetric) -> None:
        """Add a new metric to the history after basic validation."""
        if not (0 <= metric.cpu_percent <= 100):
            raise CognitiveLoadError("CPU percent out of range.")
        if not (0 <= metric.ram_percent <= 100):
            raise CognitiveLoadError("RAM percent out of range.")
        if not (30 <= metric.heart_rate <= 180):
            raise CognitiveLoadError("Heart rate out of plausible range.")
        self.history.append(metric)
        # Keep only the last 30 seconds of data
        cutoff = time.time() - 30
        self.history = [m for m in self.history if m.timestamp >= cutoff]

    def _normalize(self, value: float) -> float:
        """Normalize a metric (0‑100) to a 0‑1 float."""
        return max(0.0, min(1.0, value / 100.0))

    def compute_load_score(self) -> float:
        """Compute weighted average load score from recent metrics."""
        if not self.history:
            return 0.0
        avg_cpu = self._normalize(sum(m.cpu_percent for m in self.history) / len(self.history))
        avg_ram = self._normalize(sum(m.ram_percent for m in self.history) / len(self.history))
        # Heart rate is normalized around a resting baseline of 70 BPM
        avg_hr_raw = sum(m.heart_rate for m in self.history) / len(self.history)
        avg_hr = max(0.0, min(1.0, (avg_hr_raw - 50) / 100))
        score = (self.cpu_weight * avg_cpu +
                 self.ram_weight * avg_ram +
                 self.hr_weight * avg_hr)
        return score

    def evaluate_and_act(self) -> bool:
        """Evaluate current load and invoke the throttle callback.
        Returns True if throttling is engaged, False otherwise.
        """
        score = self.compute_load_score()
        throttle = score >= self.threshold
        if self.on_throttle:
            try:
                self.on_throttle(throttle)
            except Exception as exc:
                raise CognitiveLoadError(f"Throttle callback failed: {exc}") from exc
        return throttle

def _demo_callback(throttle: bool) -> None:
    state = "THROTTLED" if throttle else "NORMAL"
    print(f"[Demo] System state changed to: {state}")

def _generate_random_metric() -> LoadMetric:
    return LoadMetric(
        timestamp=time.time(),
        cpu_percent=random.uniform(10, 95),
        ram_percent=random.uniform(15, 90),
        heart_rate=random.uniform(60, 120)
    )

if __name__ == "__main__":
    balancer = AdaptiveOperatorCognitiveLoadBalancer(on_throttle=_demo_callback)
    for _ in range(20):
        balancer.ingest(_generate_random_metric())
        balancer.evaluate_and_act()
        time.sleep(0.5)
