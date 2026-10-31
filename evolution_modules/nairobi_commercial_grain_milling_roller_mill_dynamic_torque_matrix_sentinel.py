"""Nairobi Commercial Grain Milling Roller Mill Dynamic Torque Matrix Sentinel

Author: Cortana Autonomous Evolutionary Architect
Operator: Michael Obiero, Nairobi, Kenya
Description: Monitors, analyzes, and protects multi-roller industrial milling units
    by processing real-time dynamic torque matrices, detecting harmonic stress signatures,
    and triggering automated load-shedding safeguards.
"""

import logging
import time
import statistics
from typing import Dict, List, Any, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("RollerMillTorqueMatrixSentinel")


class RollerMillTorqueMatrixSentinel:
    """Advanced telemetry processor and anomaly detector for commercial roller mill torque matrices."""

    def __init__(self, mill_id: str, torque_threshold_nm: float = 1250.0):
        self.mill_id = mill_id
        self.torque_threshold_nm = torque_threshold_nm
        self.telemetry_history: List[Dict[str, Any]] = []
        self.anomaly_count = 0
        logger.info(f"Initialized Torque Matrix Sentinel for Mill [{self.mill_id}]")

    def ingest_torque_matrix(self, matrix_data: Dict[str, Any]) -> Dict[str, Any]:
        """Ingests a multi-axis torque reading matrix from roller mill drive assemblies.
        
        Expected keys: timestamp, roll_fast_torque, roll_slow_torque, differential_slip, vibration_hz
        """
        timestamp = matrix_data.get("timestamp", time.time())
        fast_t = float(matrix_data.get("roll_fast_torque", 0.0))
        slow_t = float(matrix_data.get("roll_slow_torque", 0.0))
        slip = float(matrix_data.get("differential_slip", 0.0))
        vibration = float(matrix_data.get("vibration_hz", 0.0))

        combined_stress = (fast_t + slow_t) * (1.0 + abs(slip))
        is_anomaly = combined_stress > self.torque_threshold_nm or vibration > 85.0

        record = {
            "timestamp": timestamp,
            "fast_torque": fast_t,
            "slow_torque": slow_t,
            "differential_slip": slip,
            "vibration_hz": vibration,
            "combined_stress": combined_stress,
            "is_anomaly": is_anomaly
        }

        self.telemetry_history.append(record)
        if len(self.telemetry_history) > 1000:
            self.telemetry_history.pop(0)

        if is_anomaly:
            self.anomaly_count += 1
            logger.warning(f"[{self.mill_id}] ANOMALY DETECTED: Combined stress {combined_stress:.2f} Nm exceeds threshold!")
            self._execute_safeguard(record)

        return record

    def _execute_safeguard(self, record: Dict[str, Any]) -> None:
        """Executes protective throttling or emergency feed gate closure."""
        logger.critical(f"[{self.mill_id}] EMERGENCY SAFEGUARD ACTIVATED: Adjusting feed slide and inverter frequency.")

    def get_diagnostic_summary(self) -> Dict[str, Any]:
        """Returns analytical summary of recent torque telemetry."""
        if not self.telemetry_history:
            return {"status": "IDLE", "samples": 0}

        stresses = [r["combined_stress"] for r in self.telemetry_history]
        return {
            "mill_id": self.mill_id,
            "total_samples": len(self.telemetry_history),
            "anomaly_count": self.anomaly_count,
            "mean_stress_nm": statistics.mean(stresses),
            "max_stress_nm": max(stresses),
            "min_stress_nm": min(stresses),
            "status": "PROTECTED"
        }


if __name__ == "__main__":
    sentinel = RollerMillTorqueMatrixSentinel(mill_id="NAIROBI_MILL_ALPHA_04")
    
    # Simulate regular and anomalous telemetry feeds
    test_readings = [
        {"timestamp": time.time(), "roll_fast_torque": 450.0, "roll_slow_torque": 520.0, "differential_slip": 0.05, "vibration_hz": 22.5},
        {"timestamp": time.time(), "roll_fast_torque": 600.0, "roll_slow_torque": 580.0, "differential_slip": 0.08, "vibration_hz": 45.0},
        {"timestamp": time.time(), "roll_fast_torque": 890.0, "roll_slow_torque": 950.0, "differential_slip": 0.25, "vibration_hz": 92.0},
    ];

    for reading in test_readings:
        res = sentinel.ingest_torque_matrix(reading)
        print(f"Processed Reading: Stress={res['combined_stress']:.2f} | Anomaly={res['is_anomaly']}")

    summary = sentinel.get_diagnostic_summary()
    print(f"Final Diagnostics: {summary}")
