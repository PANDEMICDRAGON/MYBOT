"""
Nairobi Commercial Grain Milling Roller Mill Dynamic Torque Pulse Dampening Sentinel

Proactively monitors high-frequency torque pulsing and harmonic resonance on roller
mill drive assemblies in Nairobi commercial grain mills, executing real-time dampening
compensation protocols to protect mechanical integrity.
"""

import time
import math
import logging
from typing import Dict, List, Any

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')
logger = logging.getLogger("RollerMillTorquePulseDampeningSentinel")

class RollerMillTorquePulseDampeningSentinel:
    """
    Monitors high-speed roller mill shaft torque pulses, evaluates harmonic distortion,
    and applies adaptive dampening profiles.
    """
    def __init__(self, mill_id: str, rated_torque_nm: float = 450.0):
        self.mill_id = mill_id
        self.rated_torque_nm = rated_torque_nm
        self.pulse_history: List[float] = []
        self.dampening_active = False
        logger.info(f"Initialized RollerMillTorquePulseDampeningSentinel for {{self.mill_id}} with {rated_torque_nm} Nm rating.")

    def ingest_torque_pulse(self, torque_sample: float, frequency_hz: float) -> Dict[str, Any]:
        """
        Ingests a torque sample, detects pulse anomalies, and determines dampening status.
        """
        self.pulse_history.append(torque_sample)
        if len(self.pulse_history) > 100:
            self.pulse_history.pop(0)

        deviation = abs(torque_sample - self.rated_torque_nm)
        pulse_ratio = deviation / self.rated_torque_nm

        # Threshold for high-frequency torque pulse intervention
        requires_dampening = pulse_ratio > 0.18 or frequency_hz > 120.0
        self.dampening_active = requires_dampening

        compensation_nm = 0.0
        if requires_dampening:
            compensation_nm = (torque_sample - self.rated_torque_nm) * 0.35
            logger.warning(f"[{self.mill_id}] Torque pulse anomaly detected! Sample: {torque_sample} Nm at {frequency_hz} Hz. Applying dampening compensation: {compensation_nm:.2f} Nm")

        return {
            "mill_id": self.mill_id,
            "torque_sample": torque_sample,
            "frequency_hz": frequency_hz,
            "deviation": deviation,
            "pulse_ratio": pulse_ratio,
            "dampening_active": self.dampening_active,
            "compensation_nm": compensation_nm,
            "timestamp": time.time()
        }

    def get_status(self) -> Dict[str, Any]:
        avg_torque = sum(self.pulse_history) / len(self.pulse_history) if self.pulse_history else 0.0
        return {
            "mill_id": self.mill_id,
            "average_recent_torque": avg_torque,
            "dampening_active": self.dampening_active,
            "samples_recorded": len(self.pulse_history)
        }

if __name__ == "__main__":
    sentinel = RollerMillTorquePulseDampeningSentinel(mill_id="MILL_NAIROBI_CENTRAL_04")
    
    # Simulate normal and pulsing torque readings
    test_readings = [
        (452.0, 50.0),
        (448.5, 52.0),
        (580.0, 135.5),  # Trigger pulse dampening
        (460.0, 51.0)
    ];

    for t_sample, f_hz in test_readings:
        result = sentinel.ingest_torque_pulse(t_sample, f_hz)
        logger.info(f"Test Result: {result}")

    print(f"Final Sentinel Status: {sentinel.get_status()}")
