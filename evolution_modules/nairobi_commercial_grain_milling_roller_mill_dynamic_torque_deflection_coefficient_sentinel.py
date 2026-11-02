"""Nairobi Commercial Grain Milling Roller Mill Dynamic Torque Deflection Coefficient Sentinel."""

import time
import math
import random
import logging
from typing import Dict, List, Any, Optional

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')
logger = logging.getLogger("RollerMillTorqueDeflectionSentinel")

class RollerMillTorqueDeflectionSentinel:
    """Monitors, analyzes, and mitigates torsional deflection anomalies in commercial roller mill shafts."""

    def __init__(self, mill_id: str, nominal_torque_nm: float = 1250.0, max_deflection_deg: float = 1.45):
        self.mill_id = mill_id
        self.nominal_torque_nm = nominal_torque_nm
        self.max_deflection_deg = max_deflection_deg
        self.deflection_history: List[float] = []
        self.anomaly_count = 0
        self.actuator_feed_gate_position = 100.0  # percentage
        logger.info(f"Initialized RollerMillTorqueDeflectionSentinel for {{self.mill_id}}")

    def sample_telemetry(self, current_torque_nm: float, shaft_speed_rpm: float, bearing_vibration_mm_s: float) -> Dict[str, Any]:
        """Ingests live sensor data, calculates dynamic deflection coefficient, and determines health status."""
        torque_delta = abs(current_torque_nm - self.nominal_torque_nm)
        # Empirical torsional deflection formula: theta = (T * L) / (G * J)
        # Simplified dynamic coefficient calculation relative to nominal baseline
        deflection_coefficient = (torque_delta / self.nominal_torque_nm) * (shaft_speed_rpm / 1000.0)
        estimated_deflection_deg = deflection_coefficient * 1.25 + (bearing_vibration_mm_s * 0.1)

        self.deflection_history.append(estimated_deflection_deg)
        if len(self.deflection_history) > 100:
            self.deflection_history.pop(0)

        status = "OPTIMAL"
        corrective_action = "NONE"

        if estimated_deflection_deg > self.max_deflection_deg:
            status = "CRITICAL_DEFLECTION"
            self.anomaly_count += 1
            # Execute adaptive load shedding via feed gate retraction
            self.actuator_feed_gate_position = max(20.0, self.actuator_feed_gate_position - 15.0)
            corrective_action = f"RETRACT_FEED_GATE_TO_{self.actuator_feed_gate_position:.1f}%"
        elif estimated_deflection_deg > (self.max_deflection_deg * 0.8):
            status = "WARNING"
            self.actuator_feed_gate_position = max(50.0, self.actuator_feed_gate_position - 5.0)
            corrective_action = f"ADJUST_FEED_GATE_TO_{self.actuator_feed_gate_position:.1f}%"
        else:
            if self.actuator_feed_gate_position < 100.0:
                self.actuator_feed_gate_position = min(100.0, self.actuator_feed_gate_position + 2.0)
                corrective_action = f"RESTORE_FEED_GATE_TO_{self.actuator_feed_gate_position:.1f}%"

        telemetry_packet = {
            "mill_id": self.mill_id,
            "timestamp": time.time(),
            "current_torque_nm": current_torque_nm,
            "shaft_speed_rpm": shaft_speed_rpm,
            "bearing_vibration_mm_s": bearing_vibration_mm_s,
            "estimated_deflection_deg": round(estimated_deflection_deg, 4),
            "status": status,
            "actuator_feed_gate_position": round(self.actuator_feed_gate_position, 2),
            "corrective_action": corrective_action,
            "total_anomalies": self.anomaly_count
        }
        return telemetry_packet

    def get_diagnostics(self) -> Dict[str, Any]:
        """Returns aggregate performance and safety diagnostics."""
        avg_deflection = sum(self.deflection_history) / len(self.deflection_history) if self.deflection_history else 0.0
        return {
            "mill_id": self.mill_id,
            "average_deflection_deg": round(avg_deflection, 4),
            "anomaly_count": self.anomaly_count,
            "current_gate_position": self.actuator_feed_gate_position
        }

if __name__ == "__main__":
    sentinel = RollerMillTorqueDeflectionSentinel(mill_id="NAIROBI_MILL_INDUSTRIAL_AREA_04")
    logger.info("Starting Roller Mill Torque Deflection Simulation test run...")
    for step in range(5):
        # Simulate realistic milling load fluctuations
        sim_torque = random.uniform(1100.0, 1450.0)
        sim_speed = random.uniform(980.0, 1020.0)
        sim_vib = random.uniform(0.5, 2.2)
        packet = sentinel.sample_telemetry(sim_torque, sim_speed, sim_vib)
        logger.info(f"Simulation Step {{step+1}}: {{packet}}")
        time.sleep(0.1)
    logger.info(f"Final Diagnostics: {{sentinel.get_diagnostics()}}")
