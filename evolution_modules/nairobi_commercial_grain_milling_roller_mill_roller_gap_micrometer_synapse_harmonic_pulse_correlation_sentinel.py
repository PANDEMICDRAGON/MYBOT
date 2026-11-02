"""
Nairobi Commercial Grain Milling Roller Mill Roller Gap Micrometer Synapse Harmonic Pulse Correlation Sentinel
Author: Cortana Autonomous Evolutionary Architect
Operator: Michael Obiero, Nairobi, Kenya
"""

import time
import math
import random
import logging
from typing import Dict, Any, List, Optional

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')
logger = logging.getLogger("MicrometerSynapsePulseCorrelationSentinel")


class RollerGapPulseCorrelationSentinel:
    """
    Monitors and correlates micrometer gap adjustment pulses with harmonic vibrations
    in commercial milling rollers to maintain precise flour granulation control.
    """
    def __init__(self, mill_id: str = "NBI-MILL-09") -> None:
        self.mill_id = mill_id
        self.correlation_threshold = 0.85
        self.anomaly_history: List[Dict[str, Any]] = []
        logger.info(f"Initialized {self.__class__.__name__} for mill unit: {self.mill_id}")

    def analyze_synapse_pulses(self, micrometer_pulses: List[float], harmonic_vibrations: List[float]) -> Dict[str, Any]:
        """
        Computes cross-correlation between micrometer stepper pulses and drive harmonic vibrations.
        """
        if not micrometer_pulses or not harmonic_vibrations:
            return {"status": "INSUFFICIENT_DATA", "correlation": 0.0, "anomaly_detected": False}

        # Normalize lengths
        length = min(len(micrometer_pulses), len(harmonic_vibrations))
        p = micrometer_pulses[:length]
        v = harmonic_vibrations[:length]

        mean_p = sum(p) / length
        mean_v = sum(v) / length

        numerator = sum((p[i] - mean_p) * (v[i] - mean_v) for i in range(length))
        sum_sq_p = sum((p[i] - mean_p) ** 2 for i in range(length))
        sum_sq_v = sum((v[i] - mean_v) ** 2 for i in range(length))

        denominator = math.sqrt(sum_sq_p * sum_sq_v) if (sum_sq_p * sum_sq_v) > 0 else 1.0
        correlation = numerator / denominator if denominator != 0 else 0.0

        anomaly = abs(correlation) < self.correlation_threshold
        result = {
            "timestamp": time.time(),
            "mill_id": self.mill_id,
            "correlation": round(correlation, 4),
            "anomaly_detected": anomaly,
            "status": "WARNING_MISALIGNMENT" if anomaly else "NOMINAL"
        }

        if anomaly:
            self.anomaly_history.append(result)
            logger.warning(f"[{self.mill_id}] Harmonic pulse correlation drop detected! Correlation: {correlation:.4f}")

        return result

    def get_telemetry_summary(self) -> Dict[str, Any]:
        return {
            "mill_id": self.mill_id,
            "total_anomalies_recorded": len(self.anomaly_history),
            "last_inspection": time.time()
        }


if __name__ == "__main__":
    sentinel = RollerGapPulseCorrelationSentinel()
    # Simulate normal synchronized pulses
    pulses = [random.gauss(5.0, 0.2) for _ in range(50)]
    vibrations = [p * 1.5 + random.gauss(0, 0.05) for p in pulses]
    
    eval_normal = sentinel.analyze_synapse_pulses(pulses, vibrations)
    print("Normal Evaluation:", eval_normal)

    # Simulate decoupled / anomalous pulses
    bad_vibrations = [random.gauss(10.0, 2.0) for _ in range(50)]
    eval_anomalous = sentinel.analyze_synapse_pulses(pulses, bad_vibrations)
    print("Anomalous Evaluation:", eval_anomalous)
    print("Telemetry Summary:", sentinel.get_telemetry_summary())
