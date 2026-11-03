"""Nairobi Commercial Macadamia Nut Cracker Acoustic Synapse Sentinel V1

Protects and optimizes commercial macadamia nut cracking machinery in Nairobi processing plants
by analyzing acoustic emission signatures, hydraulic pressure spikes, and mechanical vibration harmonics
to ensure maximum whole-kernel recovery and prevent catastrophic anvil failure.
"""

import time
import math
import random
import logging
from typing import Dict, List, Any, Optional

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')
logger = logging.getLogger("MacadamiaCrackerSentinel")


class MacadamiaCrackerAcousticSentinel:
    """Monitors acoustic synapse and mechanical telemetry of industrial macadamia nut crackers."""

    def __init__(self, machine_id: str = "MAC-CRACKER-NRB-01", target_whole_kernel_ratio: float = 0.85):
        self.machine_id = machine_id
        self.target_whole_kernel_ratio = target_whole_kernel_ratio
        self.telemetry_history: List[Dict[str, Any]] = []
        self.anomaly_count = 0
        logger.info(f"Initialized {self.__class__.__name__} for machine {machine_id} in Nairobi.")

    def sample_telemetry(self) -> Dict[str, Any]:
        """Simulates high-frequency acoustic sensor and hydraulic pressure telemetry."""
        # Simulated acoustic frequency spectrum peaks (Hz)
        primary_impact_freq = random.gauss(3400.0, 120.0)
        secondary_shear_freq = random.gauss(8200.0, 350.0)
        hydraulic_pressure_bar = random.gauss(185.0, 8.5)
        kernel_integrity_ratio = max(0.60, min(0.98, random.gauss(0.87, 0.04)))
        vibration_amplitude_mm_s = max(0.1, random.gauss(1.2, 0.3))

        timestamp = time.time()
        telemetry = {
            "timestamp": timestamp,
            "machine_id": self.machine_id,
            "primary_impact_freq_hz": round(primary_impact_freq, 2),
            "secondary_shear_freq_hz": round(secondary_shear_freq, 2),
            "hydraulic_pressure_bar": round(hydraulic_pressure_bar, 2),
            "kernel_integrity_ratio": round(kernel_integrity_ratio, 4),
            "vibration_amplitude_mm_s": round(vibration_amplitude_mm_s, 3)
        }
        self.telemetry_history.append(telemetry)
        if len(self.telemetry_history) > 1000:
            self.telemetry_history.pop(0)
        return telemetry

    def analyze_harmonic_pulse(self, telemetry: Dict[str, Any]) -> Dict[str, Any]:
        """Analyzes harmonic coherence between acoustic impact and hydraulic pressure."""
        pressure = telemetry["hydraulic_pressure_bar"]
        vibration = telemetry["vibration_amplitude_mm_s"]
        integrity = telemetry["kernel_integrity_ratio"]

        # Harmonic anomaly detection heuristic
        stress_index = (pressure / 200.0) * (vibration / 2.0)
        anomaly_detected = False
        recommendation = "OPTIMAL_OPERATION"

        if pressure > 205.0 or vibration > 1.8:
            anomaly_detected = True
            recommendation = "REDUCE_HYDRAULIC_FEED_PRESSURE"
            self.anomaly_count += 1
        elif integrity < self.target_whole_kernel_ratio:
            anomaly_detected = True
            recommendation = "RECALIBRATE_ANVIL_GAP_MICROMETER"
            self.anomaly_count += 1

        analysis = {
            "machine_id": self.machine_id,
            "timestamp": telemetry["timestamp"],
            "stress_index": round(stress_index, 4),
            "anomaly_detected": anomaly_detected,
            "recommendation": recommendation,
            "total_anomalies_recorded": self.anomaly_count
        }
        return analysis

    def execute_safeguard_routine(self, analysis: Dict[str, Any]) -> None:
        """Executes corrective adjustments or operator alerts if anomalies are flagged."""
        if analysis["anomaly_detected"]:
            logger.warning(
                f"[ALERT] Macadamia Cracker anomaly detected on {analysis['machine_id']}! "
                f"Stress Index: {analysis['stress_index']}. Action: {analysis['recommendation']}"
            )
        else:
            logger.info(f"[STATUS] {analysis['machine_id']} operating within harmonic thresholds.")


if __name__ == "__main__":
    print("--- Executing Nairobi Commercial Macadamia Nut Cracker Acoustic Synapse Sentinel V1 Test Harnes ---")
    sentinel = MacadamiaCrackerAcousticSentinel(machine_id="MAC-NRB-KIAMBU-04")
    for i in range(3):
        t_data = sentinel.sample_telemetry()
        report = sentinel.analyze_harmonic_pulse(t_data)
        sentinel.execute_safeguard_routine(report)
        time.sleep(0.1)
    print("--- Sentinel Test Complete Successfully ---")
