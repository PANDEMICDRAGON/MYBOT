import logging
import time
import statistics
from typing import Dict, List, Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("RollerMillMatrixSynergySentinel")

class RollerMillMatrixSynergySentinel:
    """
    Monitors high-frequency dynamic torque matrices across dual-roll commercial grain milling stands
    in Nairobi, Kenya, ensuring fault-tolerant torque synergy, vibration attenuation, and preventive shutdown.
    """
    def __init__(self, mill_id: str, roll_speed_rpm: float = 600.0):
        self.mill_id = mill_id
        self.roll_speed_rpm = roll_speed_rpm
        self.torque_history: List[float] = []
        self.synergy_violations = 0

    def ingest_torque_matrix(self, fast_roll_torque: float, slow_roll_torque: float) -> Dict[str, Any]:
        """
        Ingests paired torque metrics from fast and slow rolls, computing differential synergy index.
        """
        ratio = slow_roll_torque / (fast_roll_torque + 1e-6)
        matrix_score = abs(1.0 - ratio)
        self.torque_history.append(matrix_score)
        if len(self.torque_history) > 100:
            self.torque_history.pop(0)

        status = "OPTIMAL"
        action = "NONE"

        if matrix_score > 0.15:
            self.synergy_violations += 1
            status = "WARNING"
            action = "CALIBRATE_TENSION"

        if matrix_score > 0.30:
            status = "CRITICAL"
            action = "EMERGENCY_DISENGAGE"

        return {
            "mill_id": self.mill_id,
            "matrix_score": round(matrix_score, 4),
            "status": status,
            "action": action,
            "violations": self.synergy_violations,
            "timestamp": time.time()
        }

    def audit_health(self) -> Dict[str, Any]:
        """Audits rolling synergy health over accumulated telemetry."""
        if not self.torque_history:
            return {"health": "UNKNOWN"}
        mean_score = statistics.mean(self.torque_history)
        return {
            "mill_id": self.mill_id,
            "mean_matrix_score": round(mean_score, 4),
            "total_violations": self.synergy_violations,
            "health": "STABLE" if mean_score < 0.1 else "DEGRADED"
        }

if __name__ == "__main__":
    logger.info("Initializing Nairobi Commercial Grain Milling Roller Mill Dynamic Torque Matrix Synergy Sentinel...")
    sentinel = RollerMillMatrixSynergySentinel(mill_id="MILL-NRB-040")
    
    # Simulate normal and aberrant operational telemetry
    telemetry_samples = [
        (120.5, 96.4),
        (121.0, 96.8),
        (125.0, 80.0),  # Sudden torque split anomaly
        (119.8, 95.9)
    ]

    for fast_t, slow_t in telemetry_samples:
        result = sentinel.ingest_torque_matrix(fast_t, slow_t)
        logger.info(f"Telemetry Evaluated: {result}")

    audit = sentinel.audit_health()
    logger.info(f"Final Audit State: {audit}")
