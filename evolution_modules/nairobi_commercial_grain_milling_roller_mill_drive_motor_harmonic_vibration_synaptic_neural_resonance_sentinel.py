"""
Nairobi Commercial Grain Milling Roller Mill Drive Motor Harmonic Vibration Synaptic Neural Resonance Sentinel

Provides advanced spectral vibration analysis, harmonic resonance detection, and predictive
failure mitigation for heavy-duty roller mill drive motors in Nairobi industrial facilities.
"""

import os
import sys
import math
import time
import random
import logging
import json
from typing import Dict, List, Any, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("RollerMillResonanceSentinel")

class RollerMillResonanceSentinel:
    """
    Monitors drive motor vibration harmonics using a lightweight synaptic neural weighting matrix
    to predict mechanical degradation and bearing anomalies before catastrophic failure occurs.
    """

    def __init__(self, machine_id: str = "ROLLER_MILL_ALPHA_01", sample_rate_hz: int = 1000):
        self.machine_id = machine_id
        self.sample_rate_hz = sample_rate_hz
        self.baseline_harmonic_profile: List[float] = [0.05, 0.02, 0.01, 0.005]
        self.synaptic_weights: List[float] = [0.8, 0.6, 0.4, 0.2]
        self.anomaly_threshold: float = 0.75
        logger.info(f"Initialized {self.__class__.__name__} for machine: {self.machine_id}")

    def ingest_vibration_sample(self, raw_spectrum: List[float]) -> Dict[str, Any]:
        """
        Ingests a raw vibration frequency spectrum, computes harmonic deviation via synaptic scoring,
        and returns health telemetry.
        """
        if not raw_spectrum:
            raise ValueError("Empty vibration spectrum received.")

        # Compute dot product against synaptic weights and baseline
        activation_score = 0.0
        for i, val in enumerate(raw_spectrum[:len(self.synaptic_weights)]):
            baseline = self.baseline_harmonic_profile[i] if i < len(self.baseline_harmonic_profile) else 0.01
            delta = abs(val - baseline)
            activation_score += delta * self.synaptic_weights[i]

        # Normalize score between 0.0 and 1.0
        normalized_health_index = max(0.0, min(1.0, 1.0 - (activation_score / 2.0)))
        is_anomaly = (1.0 - normalized_health_index) > self.anomaly_threshold

        telemetry = {
            "machine_id": self.machine_id,
            "timestamp": time.time(),
            "health_index": round(normalized_health_index, 4),
            "anomaly_detected": is_anomaly,
            "harmonic_activation": round(activation_score, 4)
        }

        if is_anomaly:
            logger.warning(f"[ALERT] Harmonic resonance anomaly detected on {self.machine_id}! Health Index: {normalized_health_index}")

        return telemetry

    def calibrate_baseline(self, calibration_batch: List[List[float]]) -> None:
        """
        Recalibrates baseline harmonic profiles from nominal operating conditions.
        """
        if not calibration_batch:
            return
        num_features = len(self.baseline_harmonic_profile)
        accumulated = [0.0] * num_features
        count = len(calibration_batch)

        for sample in calibration_batch:
            for i in range(min(num_features, len(sample))):
                accumulated[i] += sample[i]

        self.baseline_harmonic_profile = [val / count for val in accumulated]
        logger.info(f"Baseline harmonic profile recalibrated for {self.machine_id}.")

if __name__ == "__main__":
    sentinel = RollerMillResonanceSentinel(machine_id="NAIROBI_MILL_BETA_04")
    
    # Simulate nominal baseline data
    nominal_batch = [
        [0.05, 0.02, 0.01, 0.005],
        [0.052, 0.019, 0.011, 0.004]
    ]
    sentinel.calibrate_baseline(nominal_batch)

    # Simulate incoming live spectrum with a developing harmonic anomaly
    test_spectrum = [0.45, 0.30, 0.15, 0.08]
    result = sentinel.ingest_vibration_sample(test_spectrum)
    print(json.dumps(result, indent=2))
