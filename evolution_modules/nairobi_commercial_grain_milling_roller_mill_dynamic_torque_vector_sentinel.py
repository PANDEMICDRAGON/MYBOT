"""
Nairobi Commercial Grain Milling Roller Mill Dynamic Torque Vector Sentinel
Autonomous Evolutionary Architecture Module #446

Monitors multi-axis torque vector trajectories on commercial roller mills
in Nairobi, Kenya, ensuring optimal grain reduction ratios and preventing
catastrophic spindle fracture.
"""

import time
import math
import logging
from typing import Dict, List, Any, Optional

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - [%(name)s] %(message)s')
logger = logging.getLogger("RollerMillTorqueVectorSentinel")


class RollerMillVectorAnomaly:
    """Represents a detected torque vector anomaly on roller mill spindles."""
    def __init__(self, mill_id: str, vector_magnitude: float, angle_deg: float, severity: str):
        self.timestamp = time.time()
        self.mill_id = mill_id
        self.vector_magnitude = vector_magnitude
        self.angle_deg = angle_deg
        self.severity = severity

    def to_dict(self) -> Dict[str, Any]:
        return {
            "timestamp": self.timestamp,
            "mill_id": self.mill_id,
            "vector_magnitude": self.vector_magnitude,
            "angle_deg": self.angle_deg,
            "severity": self.severity
        }


class RollerMillTorqueVectorSentinel:
    """
    Computes 2D torque vector components (axial vs tangential) from dual-drive
    roller mill sensors to detect asymmetrical grain feeding or roller skewing.
    """
    def __init__(self, magnitude_threshold: float = 85.0, angle_drift_limit: float = 12.5):
        self.magnitude_threshold = magnitude_threshold
        self.angle_drift_limit = angle_drift_limit
        self.anomalies: List[RollerMillVectorAnomaly] = []

    def analyze_torque_vector(self, mill_id: str, axial_torque: float, tangential_torque: float) -> Optional[RollerMillVectorAnomaly]:
        """
        Calculates resultant torque vector magnitude and directional angle.
        Triggers an anomaly if thresholds are breached.
        """
        magnitude = math.sqrt(axial_torque ** 2 + tangential_torque ** 2)
        angle_rad = math.atan2(tangential_torque, axial_torque if axial_torque != 0 else 1e-6)
        angle_deg = math.degrees(angle_rad)

        severity = "NORMAL"
        if magnitude > self.magnitude_threshold:
            severity = "CRITICAL_OVERLOAD"
        elif abs(angle_deg) > self.angle_drift_limit:
            severity = "WARNING_SKEW_DRIFT"

        if severity != "NORMAL":
            anomaly = RollerMillVectorAnomaly(mill_id, magnitude, angle_deg, severity)
            self.anomalies.append(anomaly)
            logger.warning(f"[VECTOR_BREACH] Mill {mill_id} -> Magnitude: {magnitude:.2f}Nm, Angle: {angle_deg:.2f}°, Severity: {severity}")
            return anomaly

        return None

    def get_recent_anomalies(self) -> List[Dict[str, Any]]:
        return [a.to_dict() for a in self.anomalies]


if __name__ == "__main__":
    sentinel = RollerMillTorqueVectorSentinel(magnitude_threshold=80.0, angle_drift_limit=10.0)
    
    # Simulate normal operation
    sentinel.analyze_torque_vector("MILL_INDUSTRIAL_AREA_01", 45.2, 5.1)
    
    # Simulate skew drift anomaly
    sentinel.analyze_torque_vector(
        mill_id="MILL_INDUSTRIAL_AREA_02",
        axial_torque=50.0,
        tangential_torque=25.0  # Causes excessive angle drift
    )
    
    # Simulate critical overload
    sentinel.analyze_torque_vector(
        mill_id="MILL_INDUSTRIAL_AREA_03",
        axial_torque=85.0,
        tangential_torque=40.0
    )
    
    print(f"Total Vector Anomalies Logged: {len(sentinel.get_recent_anomalies())}")
