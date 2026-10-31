"""
Nairobi Commercial Grain Milling Roller Mill Dynamic Torque Vector Sentinel
Designed for Cortana's Autonomous Evolutionary Architecture.
Monitors multidimensional torque vectors, phase angle deviations, and mechanical load vectors
of commercial roller mills in Nairobi industrial zones.
"""

import time
import math
import logging
from typing import Dict, List, Any, Optional

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')
logger = logging.getLogger("RollerMillTorqueVectorSentinel")


class RollerMillTorqueVectorSentinel:
    """
    Computes and analyzes dynamic torque vectors, instantaneous angular velocity shifts,
    and vector magnitude variations to preempt mechanical failure in roller mills.
    """

    def __init__(self, mill_id: str, nominal_torque_nm: float = 450.0, warning_threshold_ratio: float = 1.25):
        self.mill_id = mill_id
        self.nominal_torque_nm = nominal_torque_nm
        self.warning_threshold_ratio = warning_threshold_ratio
        self.telemetry_history: List[Dict[str, Any]] = []
        logger.info(f"Initialized RollerMillTorqueVectorSentinel for mill: {mill_id}")

    def analyze_vector(self, tangential_torque: float, axial_torque: float, radial_torque: float, rpm: float) -> Dict[str, Any]:
        """
        Analyzes current torque components (tangential, axial, radial) and computes the resultant
        torque vector magnitude and vector divergence angle.
        """
        resultant_magnitude = math.sqrt(tangential_torque**2 + axial_torque**2 + radial_torque**2)
        
        # Prevent division by zero
        safe_nominal = self.nominal_torque_nm if self.nominal_torque_nm > 0 else 1.0
        load_ratio = resultant_magnitude / safe_nominal
        
        # Calculate vector divergence angle relative to pure tangential ideal (degrees)
        # Ideal vector has axial and radial components close to 0
        non_tangential = math.sqrt(axial_torque**2 + radial_torque**2)
        divergence_angle_deg = math.degrees(math.atan2(non_tangential, max(tangential_torque, 1e-5)))
        
        status = "OPTIMAL"
        action_required = False
        
        if load_ratio > self.warning_threshold_ratio or divergence_angle_deg > 25.0:
            status = "WARNING_HIGH_VECTOR_STRESS"
            action_required = True
            logger.warning(
                f"[ALERT] Mill {self.mill_id}: Torque Vector Stress Detected! "
                f"Magnitude: {resultant_magnitude:.2f} Nm (Ratio: {load_ratio:.2f}), "
                f"Divergence Angle: {divergence_angle_deg:.2f}°"
            )

        telemetry_record = {
            "timestamp": time.time(),
            "mill_id": self.mill_id,
            "tangential_torque": tangential_torque,
            "axial_torque": axial_torque,
            "radial_torque": radial_torque,
            "rpm": rpm,
            "resultant_magnitude": resultant_magnitude,
            "load_ratio": load_ratio,
            "divergence_angle_deg": divergence_angle_deg,
            "status": status,
            "action_required": action_required
        }

        self.telemetry_history.append(telemetry_record)
        if len(self.telemetry_history) > 1000:
            self.telemetry_history.pop(0)

        return telemetry_record

    def get_aggregate_metrics(self) -> Dict[str, Any]:
        """Returns summary statistics over recorded telemetry window."""
        if not self.telemetry_history:
            return {"status": "NO_DATA"}

        magnitudes = [rec["resultant_magnitude"] for rec in self.telemetry_history]
        angles = [rec["divergence_angle_deg"] for rec in self.telemetry_history]
        
        return {
            "mill_id": self.mill_id,
            "samples_recorded": len(self.telemetry_history),
            "avg_resultant_magnitude": sum(magnitudes) / len(magnitudes),
            "max_resultant_magnitude": max(magnitudes),
            "avg_divergence_angle_deg": sum(angles) / len(angles),
            "max_divergence_angle_deg": max(angles)
        }


if __name__ == "__main__":
    print("Executing RollerMillTorqueVectorSentinel test harness...")
    sentinel = RollerMillTorqueVectorSentinel(mill_id="NAIROBI_MILL_INDUSTRIAL_AREA_04")
    
    # Simulate normal operation
    res1 = sentinel.analyze_vector(tangential_torque=440.0, axial_torque=12.0, radial_torque=15.0, rpm=750.0)
    print(f"Normal telemetry: {res1}")
    
    # Simulate abnormal stress / bearing misalignment / roller bind
    res2 = sentinel.analyze_vector(tangential_torque=590.0, axial_torque=85.0, radial_torque=110.0, rpm=720.0)
    print(f"Abnormal telemetry: {res2}")
    
    print("Aggregate Metrics:", sentinel.get_aggregate_metrics())
    print("Test harness execution complete.")
