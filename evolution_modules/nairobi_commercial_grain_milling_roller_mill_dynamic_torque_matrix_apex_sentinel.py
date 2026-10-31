"""
Nairobi Commercial Grain Milling Roller Mill Dynamic Torque Matrix Apex Sentinel
Designed for high-precision industrial roller mill monitoring in Nairobi, Kenya.
"""

import time
import math
import logging
from typing import Dict, Any, List, Optional

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')
logger = logging.getLogger("RollerMillApexSentinel")


class RollerMillApexSentinel:
    """
    Monitors, analyzes, and predicts anomalies in commercial grain milling roller assemblies
    by computing a real-time multi-dimensional dynamic torque matrix and thermal harmonic index.
    """

    def __init__(self, mill_id: str, nominal_torque_nm: float = 450.0, max_thermal_delta: float = 35.0):
        self.mill_id = mill_id
        self.nominal_torque_nm = nominal_torque_nm
        self.max_thermal_delta = max_thermal_delta
        self.telemetry_history: List[Dict[str, Any]] = []
        logger.info(f"Apex Sentinel initialized for Mill ID: {self.mill_id} (Nominal Torque: {nominal_torque_nm} Nm)")

    def evaluate_torque_matrix(self, telemetry: Dict[str, float]) -> Dict[str, Any]:
        """
        Evaluates incoming telemetry comprising torque, vibration velocity, acoustic emission,
        and bearing temperature.
        """
        timestamp = time.time()
        actual_torque = telemetry.get("torque_nm", self.nominal_torque_nm)
        vibration_hz = telemetry.get("vibration_hz", 12.5)
        acoustic_db = telemetry.get("acoustic_db", 65.0)
        temperature_c = telemetry.get("temperature_c", 42.0)

        torque_deviation = abs(actual_torque - self.nominal_torque_nm) / self.nominal_torque_nm
        harmonic_index = math.sqrt(vibration_hz * acoustic_db) / 30.0
        thermal_stress = max(0.0, temperature_c - 25.0) / self.max_thermal_delta

        # Apex Risk Score (0.0 to 1.0)
        risk_score = min(1.0, (torque_deviation * 0.4) + (harmonic_index * 0.3) + (thermal_stress * 0.3))

        status = "OPTIMAL"
        if risk_score > 0.75:
            status = "CRITICAL_INTERVENTION_REQUIRED"
        elif risk_score > 0.45:
            status = "ELEVATED_WEAR_WARNING"

        assessment = {
            "timestamp": timestamp,
            "mill_id": self.mill_id,
            "risk_score": round(risk_score, 4),
            "torque_deviation_pct": round(torque_deviation * 100, 2),
            "harmonic_index": round(harmonic_index, 4),
            "thermal_stress_index": round(thermal_stress, 4),
            "status": status
        }

        self.telemetry_history.append(assessment)
        if len(self.telemetry_history) > 1000:
            self.telemetry_history.pop(0)

        if status != "OPTIMAL":
            logger.warning(f"[{self.mill_id}] Status: {status} | Risk Score: {assessment['risk_score']}")
        else:
            logger.info(f"[{self.mill_id}] Status: {status} | Risk Score: {assessment['risk_score']}")

        return assessment

    def get_aggregate_health(self) -> Dict[str, Any]:
        """Computes aggregate health across historical telemetry samples."""
        if not self.telemetry_history:
            return {"sample_count": 0, "average_risk": 0.0}

        avg_risk = sum(item["risk_score"] for item in self.telemetry_history) / len(self.telemetry_history)
        return {
            "sample_count": len(self.telemetry_history),
            "average_risk": round(avg_risk, 4),
            "last_status": self.telemetry_history[-1]["status"]
        }


if __name__ == "__main__":
    sentinel = RollerMillApexSentinel(mill_id="NAI-MILL-ALPHA-01")
    
    # Simulate nominal and anomalous test feeds
    test_feeds = [
        {"torque_nm": 452.1, "vibration_hz": 12.0, "acoustic_db": 64.5, "temperature_c": 41.5},
        {"torque_nm": 489.5, "vibration_hz": 18.2, "acoustic_db": 72.1, "temperature_c": 55.0},
        {"torque_nm": 610.0, "vibration_hz": 28.5, "acoustic_db": 88.0, "temperature_c": 74.2}
    ]

    for feed in test_feeds:
        sentinel.evaluate_torque_matrix(feed)

    print("Aggregate Health Summary:", sentinel.get_aggregate_health())
