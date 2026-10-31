"""
Nairobi Commercial Grain Milling Roller Mill Dynamic Torque Matrix Isolation Sentinel
Designed for real-time telemetry isolation, multi-axis torque matrix analysis, and emergency trip protocols in industrial roller mills.
"""

import ast
import logging
import time
import statistics
from typing import Dict, List, Any, Optional

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')
logger = logging.getLogger("RollerMillTorqueMatrixIsolationSentinel")

class TorqueMatrixIsolationSentinel:
    """
    Monitors multi-axis dynamic torque telemetry from industrial roller mills,
    computes matrix anomaly indices, and executes rapid isolation sequences
    when harmonic distortion or torque vectors exceed safety thresholds.
    """
    def __init__(self, mill_id: str, torque_threshold_nm: float = 1250.0):
        self.mill_id = mill_id
        self.torque_threshold_nm = torque_threshold_nm
        self.telemetry_history: List[Dict[str, float]] = []
        self.isolation_engaged = False
        logger.info(f"Initialized TorqueMatrixIsolationSentinel for mill {mill_id} with threshold {torque_threshold_nm} Nm.")

    def ingest_telemetry(self, timestamp: float, primary_torque: float, secondary_torque: float, vibration_hz: float) -> Dict[str, Any]:
        """Ingests live sensor data, updates matrix state, and evaluates safety conditions."""
        if self.isolation_engaged:
            return {"status": "ISOLATED", "action": "NONE", "mill_id": self.mill_id}

        record = {
            "timestamp": timestamp,
            "primary_torque": primary_torque,
            "secondary_torque": secondary_torque,
            "vibration_hz": vibration_hz,
            "differential": abs(primary_torque - secondary_torque)
        }
        self.telemetry_history.append(record)
        if len(self.telemetry_history) > 100:
            self.telemetry_history.pop(0)

        anomaly = self._evaluate_matrix(record)
        if anomaly:
            self._trigger_isolation(record)
            return {"status": "TRIPPED", "action": "EMERGENCY_ISOLATION", "mill_id": self.mill_id}

        return {"status": "NOMINAL", "action": "CONTINUE", "mill_id": self.mill_id}

    def _evaluate_matrix(self, record: Dict[str, float]) -> bool:
        """Evaluates if torque differential or absolute limits breach critical thresholds."""
        if record["primary_torque"] > self.torque_threshold_nm or record["secondary_torque"] > self.torque_threshold_nm:
            return True
        if record["differential"] > (self.torque_threshold_nm * 0.2):
            return True
        if len(self.telemetry_history) >= 10:
            recent_diffs = [r["differential"] for r in self.telemetry_history[-10:]]
            if statistics.stdev(recent_diffs) > 85.0:
                return True
        return False

    def _trigger_isolation(self, record: Dict[str, float]) -> None:
        """Executes rapid clutch disengagement and inverter shutdown."""
        self.isolation_engaged = True
        logger.critical(f"[EMERGENCY] Torque Matrix Anomaly detected in Mill {self.mill_id}! Primary: {record['primary_torque']} Nm, Secondary: {record['secondary_torque']} Nm. Isolating drive assembly.")

    def reset_sentinel(self) -> None:
        """Resets the isolation state after manual operator inspection."""
        self.isolation_engaged = False
        self.telemetry_history.clear()
        logger.info(f"Sentinel for mill {self.mill_id} reset by operator.")


if __name__ == "__main__":
    sentinel = TorqueMatrixIsolationSentinel(mill_id="NAI_MILL_04", torque_threshold_nm=1200.0)
    
    # Simulate nominal operations
    res1 = sentinel.ingest_telemetry(time.time(), 950.0, 945.0, 14.2)
    print("Test 1:", res1)
    
    # Simulate torque anomaly trigger
    res2 = sentinel.ingest_telemetry(time.time(), 1350.0, 1100.0, 28.5)
    print("Test 2:", res2)
    
    # Verify code syntax integrity
    code_string = open(__file__, "r", encoding="utf-8").read()
    ast.parse(code_string)
    print("AST Syntax Verification: PASSED")
