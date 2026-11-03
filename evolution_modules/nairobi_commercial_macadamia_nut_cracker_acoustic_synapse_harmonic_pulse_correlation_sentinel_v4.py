"""Nairobi Commercial Macadamia Nut Cracker Acoustic Synapse Harmonic Pulse Correlation Sentinel V4

Designed for real-time acoustic telemetry monitoring of industrial macadamia nut cracking
machinery in Nairobi, Kenya. Protects mechanical actuators, optimizes kernel yield,
and prevents whole-nut crushing via advanced harmonic pulse correlation.
"""

import time
import math
import random
import logging
from typing import Dict, List, Any

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')
logger = logging.getLogger("MacadamiaSentinelV4")


class MacadamiaNutCrackerAcousticSentinel:
    """Monitors acoustic impedance, impact resonance, and pneumatic pressure in real-time."""

    def __init__(self, machine_id: str = "MAC-CRACKER-NRB-04") -> None:
        self.machine_id = machine_id
        self.baseline_frequency_hz: float = 1420.5
        self.tolerance_pct: float = 3.5
        self.anomaly_counter: int = 0
        self.is_active: bool = False

    def start_monitoring(self) -> None:
        """Activates the acoustic pulse correlation sensor grid."""
        self.is_active = True
        logger.info(f"[{self.machine_id}] Acoustic Synapse Sentinel V4 activated for Nairobi facility.")

    def sample_acoustic_resonance(self) -> Dict[str, Any]:
        """Simulates high-frequency acoustic sampling of cracking impact."""
        if not self.is_active:
            raise RuntimeError("Sentinel is not active. Call start_monitoring() first.")
        
        # Introduce minor stochastic variance mimicking raw nut hardness distribution
        jitter = random.gauss(0.0, 15.0)
        current_freq = self.baseline_frequency_hz + jitter
        
        deviation = abs(current_freq - self.baseline_frequency_hz) / self.baseline_frequency_hz * 100.0
        anomaly_detected = deviation > self.tolerance_pct
        
        if anomaly_detected:
            self.anomaly_counter += 1
            logger.warning(f"[{self.machine_id}] Acoustic anomaly detected! Freq: {current_freq:.2f}Hz (Deviation: {deviation:.2f}%)")

        return {
            "machine_id": self.machine_id,
            "timestamp": time.time(),
            "measured_frequency_hz": round(current_freq, 2),
            "deviation_percent": round(deviation, 2),
            "anomaly": anomaly_detected,
            "total_anomalies": self.anomaly_counter
        }

    def calibrate_pneumatic_valve(self, telemetry: Dict[str, Any]) -> str:
        """Dynamically adjusts pneumatic ram pressure based on acoustic telemetry feedback."""
        if telemetry["anomaly"]:
            if telemetry["measured_frequency_hz"] > self.baseline_frequency_hz:
                logger.info(f"[{self.machine_id}] Adjusting valve: Decreasing pneumatic pressure to prevent shell shattering.")
                return "DECREASE_PRESSURE"
            else:
                logger.info(f"[{self.machine_id}] Adjusting valve: Increasing pneumatic pressure to ensure complete shell fracture.")
                return "INCREASE_PRESSURE"
        return "OPTIMAL"


if __name__ == "__main__":
    sentinel = MacadamiaNutCrackerAcousticSentinel()
    sentinel.start_monitoring()
    
    for cycle in range(5):
        telemetry_data = sentinel.sample_acoustic_resonance()
        action = sentinel.calibrate_pneumatic_valve(telemetry_data)
        logger.info(f"Cycle {cycle+1} Result: Action -> {action}")
        time.sleep(0.1)
