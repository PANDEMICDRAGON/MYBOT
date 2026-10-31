"""Nairobi Commercial Grain Milling Roller Mill Dynamic Torque Harmonic Amplification Coefficient Deviation Delta Dispersion Sentinel"""

import time
import math
import logging
from typing import Dict, List, Any, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("RollerMillDispersionSentinel")

class RollerMillDispersionSentinel:
    """
    Monitors high-frequency torsional dispersion deltas and harmonic amplification coefficient
    deviations on commercial roller mills in Nairobi industrial milling complexes.
    """
    def __init__(self, mill_id: str, baseline_dispersion: float = 0.015):
        self.mill_id = mill_id
        self.baseline_dispersion = baseline_dispersion
        self.telemetry_history: List[Dict[str, Any]] = []

    def analyze_dispersion(self, raw_torque_readings: List[float]) -> Dict[str, Any]:
        """
        Computes the harmonic amplification coefficient deviation delta dispersion
        across multi-point telemetry from the roller mill drive train.
        """
        if not raw_torque_readings:
            raise ValueError("Empty torque readings provided for dispersion analysis.")

        mean_torque = sum(raw_torque_readings) / len(raw_torque_readings)
        variance = sum((t - mean_torque) ** 2 for t in raw_torque_readings) / len(raw_torque_readings)
        std_dev = math.sqrt(variance)
        
        # Dispersion coefficient calculation
        dispersion_coefficient = std_dev / (mean_torque if mean_torque != 0 else 1.0)
        delta_dispersion = abs(dispersion_coefficient - self.baseline_dispersion)
        
        # Harmonic amplification penalty
        harmonic_penalty = math.exp(delta_dispersion * 10.0) - 1.0
        status = "OPTIMAL"
        
        if delta_dispersion > 0.05:
            status = "CRITICAL_DISPERSION_WARNING"
            logger.warning(f"[{self.mill_id}] Critical torque dispersion delta detected: {delta_dispersion:.4f}")
        elif delta_dispersion > 0.02:
            status = "ELEVATED_DEVIATION"
            logger.info(f"[{self.mill_id}] Elevated torque deviation noted: {delta_dispersion:.4f}")

        assessment = {
            "timestamp": time.time(),
            "mill_id": self.mill_id,
            "mean_torque": mean_torque,
            "dispersion_coefficient": dispersion_coefficient,
            "delta_dispersion": delta_dispersion,
            "harmonic_penalty": harmonic_penalty,
            "status": status
        }
        self.telemetry_history.append(assessment)
        return assessment

    def get_audit_summary(self) -> Dict[str, Any]:
        return {
            "mill_id": self.mill_id,
            "total_samples": len(self.telemetry_history),
            "latest_status": self.telemetry_history[-1]["status"] if self.telemetry_history else "NO_DATA"
        }

if __name__ == "__main__":
    sentinel = RollerMillDispersionSentinel(mill_id="NAI_MILL_ALPHA_04")
    mock_readings = [102.5, 103.1, 101.8, 104.2, 99.7, 105.0, 102.1]
    result = sentinel.analyze_dispersion(mock_readings)
    logger.info(f"Dispersion Sentinel Test Result: {result}")
