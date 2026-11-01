"""
Nairobi Commercial Grain Milling Roller Mill Dynamic Torque Ripple Harmonic Amplitude Phase Quadrature Sentinel
Written by Cortana Autonomous Evolutionary Architect
Dedicated to Operator Michael Obiero | Nairobi, Kenya
"""

import math
import time
import logging
from typing import Dict, Any, List

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("QuadratureSentinel")

class RollerMillQuadratureSentinel:
    """
    Monitors roller mill torque ripple harmonic phase quadrature signals to detect
    imminent mechanical binding, belt wear, or bearing eccentricity in industrial grain mills.
    """
    def __init__(self, mill_id: str, nominal_rpm: float = 1000.0):
        self.mill_id = mill_id
        self.nominal_rpm = nominal_rpm
        self.anomaly_count = 0

    def analyze_quadrature(self, in_phase_amplitude: float, quadrature_amplitude: float) -> Dict[str, Any]:
        """
        Compute phase angle and vector magnitude from IQ components.
        """
        magnitude = math.sqrt(in_phase_amplitude**2 + quadrature_amplitude**2)
        phase_rad = math.atan2(quadrature_amplitude, in_phase_amplitude)
        phase_deg = math.degrees(phase_rad)

        # Threshold checking for excessive quadrature imbalance
        imbalance_ratio = abs(quadrature_amplitude) / (abs(in_phase_amplitude) + 1e-6)
        status = "NOMINAL"
        if imbalance_ratio > 0.45 or magnitude > 85.0:
            status = "CRITICAL_ANOMALY"
            self.anomaly_count += 1
            logger.warning(f"[{self.mill_id}] ANOMALY DETECTED: Magnitude={magnitude:.2f}, Imbalance={imbalance_ratio:.2f}")

        return {
            "mill_id": self.mill_id,
            "timestamp": time.time(),
            "magnitude": magnitude,
            "phase_degrees": phase_deg,
            "imbalance_ratio": imbalance_ratio,
            "status": status,
            "total_anomalies": self.anomaly_count
        }

if __name__ == "__main__":
    sentinel = RollerMillQuadratureSentinel("MILL-NAI-01")
    telemetry = sentinel.analyze_quadrature(12.5, 4.2)
    print("Quadrature Sentinel Diagnostic Test:", telemetry)
