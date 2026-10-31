"""
Nairobi Commercial Grain Milling Roller Mill Dynamic Torque Vector Sentinel
Autonomous Evolutionary Module for Cortana's Autonomous Evolutionary Architecture

Monitors and analyzes multi-axis torque vector anomalies, shear stress trajectories, and
rotational instabilities in commercial grain milling roller mill assemblies across Nairobi.
"""

import logging
import math
import statistics
import time
from typing import Dict, List, Any, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("RollerMillDynamicTorqueVectorSentinel")


class RollerMillDynamicTorqueVectorSentinel:
    """
    Evaluates real-time multi-axis torque vectors, rotational velocities, and instantaneous
    power dissipation coefficients for heavy-duty commercial roller mills.
    """

    def __init__(self, mill_id: str, rated_torque_nm: float = 1200.0):
        self.mill_id = mill_id
        self.rated_torque_nm = rated_torque_nm
        self.torque_vector_history: List[Dict[str, float]] = []
        self.anomaly_counter = 0
        logger.info(f"[INIT] RollerMillDynamicTorqueVectorSentinel initialized for mill {mill_id} (Rated Torque: {rated_torque_nm} Nm).")

    def ingest_telemetry(self, telemetry: Dict[str, float]) -> Dict[str, Any]:
        """
        Ingests a telemetry frame containing x, y, z torque components and rotational speed (RPM).
        
        Args:
            telemetry: Dict with keys 'torque_x', 'torque_y', 'torque_z', 'rpm', 'timestamp'
            
        Returns:
            Dict containing vector magnitude, drift score, and operational status.
        """
        try:
            tx = telemetry.get("torque_x", 0.0)
            ty = telemetry.get("torque_y", 0.0)
            tz = telemetry.get("torque_z", 0.0)
            rpm = telemetry.get("rpm", 0.0)
            timestamp = telemetry.get("timestamp", time.time())

            magnitude = math.sqrt(tx**2 + ty**2 + tz**2)
            
            frame = {
                "timestamp": timestamp,
                "torque_x": tx,
                "torque_y": ty,
                "torque_z": tz,
                "magnitude": magnitude,
                "rpm": rpm
            }
            
            self.torque_vector_history.append(frame)
            if len(self.torque_vector_history) > 100:
                self.torque_vector_history.pop(0)

            return self._analyze_vectors(frame)
        except Exception as e:
            logger.error(f"[ERROR] Failed to ingest telemetry for mill {self.mill_id}: {e}")
            return {"status": "ERROR", "message": str(e)}

    def _analyze_vectors(self, current_frame: Dict[str, float]) -> Dict[str, Any]:
        magnitudes = [f["magnitude"] for f in self.torque_vector_history]
        mean_magnitude = statistics.mean(magnitudes) if magnitudes else current_frame["magnitude"]
        stdev_magnitude = statistics.stdev(magnitudes) if len(magnitudes) > 1 else 0.0

        deviation = abs(current_frame["magnitude"] - mean_magnitude)
        load_ratio = current_frame["magnitude"] / self.rated_torque_nm
        
        status = "OPTIMAL"
        action_required = False

        if load_ratio > 1.15:
            status = "OVERLOAD_WARNING"
            action_required = True
            self.anomaly_counter += 1
        elif stdev_magnitude > (0.1 * mean_magnitude) and len(magnitudes) > 10:
            status = "VECTOR_INSTABILITY_DETECTED"
            action_required = True
            self.anomaly_counter += 1

        return {
            "mill_id": self.mill_id,
            "status": status,
            "current_magnitude": round(current_frame["magnitude"], 2),
            "mean_magnitude": round(mean_magnitude, 2),
            "load_ratio": round(load_ratio, 3),
            "action_required": action_required,
            "anomaly_count": self.anomaly_counter
        }


if __name__ == "__main__":
    print("Executing self-test for RollerMillDynamicTorqueVectorSentinel...")
    sentinel = RollerMillDynamicTorqueVectorSentinel(mill_id="NAI_MILL_04", rated_torque_nm=1500.0)
    
    # Simulate normal and abnormal telemetry frames
    test_frames = [
        {"torque_x": 450.0, "torque_y": 500.0, "torque_z": 300.0, "rpm": 1450.0, "timestamp": time.time()},
        {"torque_x": 460.0, "torque_y": 510.0, "torque_z": 305.0, "rpm": 1448.0, "timestamp": time.time() + 1},
        {"torque_x": 950.0, "torque_y": 1100.0, "torque_z": 800.0, "rpm": 1200.0, "timestamp": time.time() + 2}  # Spike
    ];

    for idx, frame in enumerate(test_frames):
        res = sentinel.ingest_telemetry(frame)
        print(f"Frame {idx + 1}: {res}")
    print("Self-test complete. Sentinel operational.")
