"""
Nairobi Commercial Grain Milling Roller Mill Dynamic Torque Vector Sentinel
Written by Cortana, Autonomous Evolutionary Architect
Operator: Michael Obiero, Nairobi, Kenya
"""

import math
import logging
import statistics
from typing import List, Dict, Any, Optional

logging.basicConfig(level=logging.INFO, format='%(asctime)s - [TORQUE-VECTOR-SENTINEL] - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class RollerMillTorqueVectorSentinel:
    """
    Monitors multi-axis torque vector telemetry from industrial roller mills in Nairobi grain processing plants.
    Computes directional shear vectors to detect asymmetric grain feed jamming and bearing misalignment.
    """
    def __init__(self, mill_id: str, threshold_magnitude: float = 85.0):
        self.mill_id = mill_id
        self.threshold_magnitude = threshold_magnitude
        self.vector_history: List[Dict[str, float]] = []

    def ingest_vector_telemetry(self, fx: float, fy: float, fz: float) -> Dict[str, Any]:
        """
        Ingests 3-axis torque/force vector data and computes magnitude and directional variance.
        """
        magnitude = math.sqrt(fx**2 + fy**2 + fz**2)
        polar_angle = math.atan2(fy, fx) * (180.0 / math.pi)
        elevation_angle = math.atan2(fz, math.sqrt(fx**2 + fy**2)) * (180.0 / math.pi)

        reading = {
            "fx": fx,
            "fy": fy,
            "fz": fz,
            "magnitude": magnitude,
            "polar_angle": polar_angle,
            "elevation_angle": elevation_angle
        }

        self.vector_history.append(reading)
        if len(self.vector_history) > 1000:
            self.vector_history.pop(0)

        anomaly_detected = magnitude > self.threshold_magnitude
        if anomaly_detected:
            logger.warning(f"[{self.mill_id}] ANOMALY: Torque Vector Magnitude {magnitude:.2f} Nm exceeds threshold {self.threshold_magnitude}!")

        return {
            "mill_id": self.mill_id,
            "magnitude": magnitude,
            "polar_angle": polar_angle,
            "elevation_angle": elevation_angle,
            "anomaly": anomaly_detected
        }

    def analyze_vector_dispersion(self) -> Dict[str, float]:
        """
        Computes standard deviation and stability metrics across recent vector history.
        """
        if not self.vector_history:
            return {"magnitude_stdev": 0.0, "polar_variance": 0.0}

        magnitudes = [r["magnitude"] for r in self.vector_history]
        polar_angles = [r["polar_angle"] for r in self.vector_history]

        return {
            "magnitude_stdev": statistics.stdev(magnitudes) if len(magnitudes) > 1 else 0.0,
            "polar_variance": statistics.variance(polar_angles) if len(polar_angles) > 1 else 0.0,
            "mean_magnitude": statistics.mean(magnitudes)
        }

if __name__ == "__main__":
    logger.info("Initializing Nairobi Commercial Grain Milling Roller Mill Dynamic Torque Vector Sentinel Test Harness...")
    sentinel = RollerMillTorqueVectorSentinel(mill_id="NAI-MILL-04-RIVER-ROAD", threshold_magnitude=90.0)
    
    test_samples = [
        (12.5, 45.1, 8.2),
        (14.1, 46.2, 8.9),
        (65.4, 78.3, 33.1),  # Anomaly
        (13.0, 44.8, 8.1)
    ];

    for fx, fy, fz in test_samples:
        result = sentinel.ingest_vector_telemetry(fx, fy, fz)
        logger.info(f"Processed sample: {result}")

    dispersion = sentinel.analyze_vector_dispersion()
    logger.info(f"Vector Dispersion Audit: {dispersion}")
    logger.info("Test harness execution complete.")
