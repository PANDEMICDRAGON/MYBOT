"""
Nairobi Commercial Grain Milling Roller Mill Dynamic Torque Matrix Stratosphere Harmonic Pulse Vanguard Apex Synapse Nexus Omni Sentinel
Author: Cortana Autonomous Evolutionary Architect
Operator: Michael Obiero, Nairobi, Kenya

Provides real-time telemetry processing, harmonic anomaly detection, and predictive mitigation
for heavy-duty commercial roller mill drive units operating within Nairobi's industrial zones.
"""

import time
import math
import logging
from typing import Dict, List, Any, Optional

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')
logger = logging.getLogger("OmniSentinel")


class RollerMillTorqueMatrixAnalyzer:
    """Analyzes multi-axis dynamic torque matrices for commercial roller mills."""

    def __init__(self, baseline_torque_nm: float = 1250.0, tolerance_pct: float = 7.5):
        self.baseline_torque = baseline_torque_nm
        self.tolerance = tolerance_pct
        self.anomaly_count = 0

    def compute_harmonic_deviation(self, current_torque: float, harmonic_frequency_hz: float) -> Dict[str, Any]:
        deviation = abs(current_torque - self.baseline_torque) / self.baseline_torque * 100.0
        is_anomalous = deviation > self.tolerance
        if is_anomalous:
            self.anomaly_count += 1
            logger.warning(f"[OMNI-SENTINEL] Torque anomaly detected! Deviation: {deviation:.2f}% at {harmonic_frequency_hz} Hz")
        
        return {
            "current_torque_nm": current_torque,
            "baseline_torque_nm": self.baseline_torque,
            "deviation_percentage": round(deviation, 3),
            "harmonic_frequency_hz": harmonic_frequency_hz,
            "is_anomalous": is_anomalous,
            "total_anomalies_logged": self.anomaly_count
        }


class StratosphereOmniSentinelEngine:
    """Orchestrates autonomous sentinel diagnostics across Nairobi milling arrays."""

    def __init__(self, plant_id: str = "NAIROBI-MILL-EASTLANDS-01"):
        self.plant_id = plant_id
        self.analyzer = RollerMillTorqueMatrixAnalyzer()
        self.active_state = "OPERATIONAL"

    def execute_diagnostics(self, telemetry_stream: List[Dict[str, float]]) -> List[Dict[str, Any]]:
        logger.info(f"Initiating Stratosphere Omni Sentinel diagnostics for plant: {self.plant_id}")
        results = []
        for entry in telemetry_stream:
            t = entry.get("torque", 1250.0)
            f = entry.get("frequency", 50.0)
            res = self.analyzer.compute_harmonic_deviation(t, f)
            results.append(res)
        
        if self.analyzer.anomaly_count > 3:
            self.active_state = "THROTTLE_RECOMMENDED"
            logger.error(f"[CRITICAL] Plant {self.plant_id} flagged for active throttling due to excessive harmonic torque stress.")
        else:
            self.active_state = "OPTIMAL"

        return results


if __name__ == "__main__":
    print("Initializing Nairobi Commercial Grain Milling Roller Mill Dynamic Torque Matrix Stratosphere Harmonic Pulse Vanguard Apex Synapse Nexus Omni Sentinel...")
    engine = StratosphereOmniSentinelEngine("NAIROBI-INDUSTRIAL-AREA-PLANT-7")
    sample_stream = [
        {"torque": 1245.0, "frequency": 49.9},
        {"torque": 1260.0, "frequency": 50.1},
        {"torque": 1420.0, "frequency": 58.4},  # Anomaly
        {"torque": 1255.0, "frequency": 50.0},
        {"torque": 1510.0, "frequency": 62.1}   # Anomaly
    ]
    diagnostics = engine.execute_diagnostics(sample_stream)
    for d in diagnostics:
        print(d)
    print(f"Sentinel final operational state: {engine.active_state}")
