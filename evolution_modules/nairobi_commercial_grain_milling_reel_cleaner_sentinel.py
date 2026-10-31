import time
import random
from dataclasses import dataclass
from typing import List, Optional, Dict, Any
from enum import Enum


class ReelCleanerStatus(Enum):
    NOMINAL = "nominal"
    WARNING = "warning"
    CRITICAL = "critical"
    OFFLINE = "offline"


@dataclass
class VibrationReading:
    timestamp: float
    x_axis: float
    y_axis: float
    z_axis: float
    rms: float


@dataclass
class ThroughputReading:
    timestamp: float
    kg_per_hour: float


@dataclass
class ReelCleanerState:
    status: ReelCleanerStatus
    vibration_rms: float
    throughput: float
    blockage_probability: float
    last_update: float
    details: Dict[str, Any]


class ReelCleanerSentinel:
    """
    Monitors the reel cleaner in a commercial grain milling facility.
    Detects blockages and vibration anomalies to prevent downstream issues.
    """

    def __init__(self, vibration_threshold: float = 5.0, throughput_min: float = 1000.0):
        self.vibration_threshold = vibration_threshold
        self.throughput_min = throughput_min
        self.vibration_history: List[VibrationReading] = []
        self.throughput_history: List[ThroughputReading] = []
        self.state = ReelCleanerState(
            status=ReelCleanerStatus.OFFLINE,
            vibration_rms=0.0,
            throughput=0.0,
            blockage_probability=0.0,
            last_update=time.time(),
            details={}
        )

    def record_vibration(self, x: float, y: float, z: float) -> None:
        """Record a vibration reading."""
        rms = (x**2 + y**2 + z**2) ** 0.5
        reading = VibrationReading(timestamp=time.time(), x_axis=x, y_axis=y, z_axis=z, rms=rms)
        self.vibration_history.append(reading)
        if len(self.vibration_history) > 100:
            self.vibration_history.pop(0)

    def record_throughput(self, kg_per_hour: float) -> None:
        """Record a throughput reading."""
        reading = ThroughputReading(timestamp=time.time(), kg_per_hour=kg_per_hour)
        self.throughput_history.append(reading)
        if len(self.throughput_history) > 100:
            self.throughput_history.pop(0)

    def analyze(self) -> ReelCleanerState:
        """Analyze current state and update sentinel status."""
        if not self.vibration_history or not self.throughput_history:
            return self.state

        recent_vibrations = self.vibration_history[-10:]
        recent_throughputs = self.throughput_history[-10:]

        avg_vibration = sum(v.rms for v in recent_vibrations) / len(recent_vibrations)
        avg_throughput = sum(t.kg_per_hour for t in recent_throughputs) / len(recent_throughputs)

        # Simple blockage probability heuristic
        blockage_prob = 0.0
        if avg_throughput < self.throughput_min:
            blockage_prob += 0.5
        if avg_vibration > self.vibration_threshold:
            blockage_prob += 0.5

        status = ReelCleanerStatus.NOMINAL
        if blockage_prob > 0.8:
            status = ReelCleanerStatus.CRITICAL
        elif blockage_prob > 0.4:
            status = ReelCleanerStatus.WARNING

        self.state = ReelCleanerState(
            status=status,
            vibration_rms=avg_vibration,
            throughput=avg_throughput,
            blockage_probability=blockage_prob,
            last_update=time.time(),
            details={
                "avg_vibration": avg_vibration,
                "avg_throughput": avg_throughput,
                "threshold_vibration": self.vibration_threshold,
                "min_throughput": self.throughput_min
            }
        )
        return self.state

    def get_state(self) -> ReelCleanerState:
        """Return current state."""
        return self.state


if __name__ == "__main__":
    sentinel = ReelCleanerSentinel(vibration_threshold=5.0, throughput_min=1000.0)

    # Simulate nominal operation
    for _ in range(10):
        sentinel.record_vibration(random.uniform(1.0, 3.0), random.uniform(1.0, 3.0), random.uniform(1.0, 3.0))
        sentinel.record_throughput(random.uniform(1200, 1500))

    state = sentinel.analyze()
    print(f"Nominal State: {state.status}, Vibration: {state.vibration_rms:.2f}, Throughput: {state.throughput:.2f}")

    # Simulate blockage
    for _ in range(10):
        sentinel.record_vibration(random.uniform(6.0, 8.0), random.uniform(6.0, 8.0), random.uniform(6.0, 8.0))
        sentinel.record_throughput(random.uniform(500, 800))

    state = sentinel.analyze()
    print(f"Blockage State: {state.status}, Vibration: {state.vibration_rms:.2f}, Throughput: {state.throughput:.2f}")
