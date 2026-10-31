import ast
import logging
import math
import time
from typing import Dict, List, Any

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')
logger = logging.getLogger("RollerMillTorqueVectorSentinel")

class RollerMillTorqueVectorSentinel:
    """
    Monitors and modulates dynamic torque vectors in commercial grain milling roller mills
    across industrial operations in Nairobi, Kenya.
    """
    def __init__(self, mill_id: str, rated_kw: float = 75.0):
        self.mill_id = mill_id
        self.rated_kw = rated_kw
        self.vector_history: List[Dict[str, Any]] = []
        logger.info(f"Initialized RollerMillTorqueVectorSentinel for mill {mill_id} ({rated_kw} kW).")

    def analyze_torque_vector(self, axial_torque: float, radial_torque: float, torsional_vibration: float) -> Dict[str, Any]:
        """
        Analyzes multi-axis torque components and computes vector magnitude and phase angle.
        """
        magnitude = math.sqrt(axial_torque ** 2 + radial_torque ** 2)
        phase_angle = math.degrees(math.atan2(radial_torque, axial_torque))
        
        # Dynamic anomaly threshold based on rated power scaling
        threshold = self.rated_kw * 1.35
        status = "OPTIMAL"
        adjustment_action = "NONE"

        if magnitude > threshold or torsional_vibration > 4.5:
            status = "CRITICAL_SHEAR_WARNING"
            adjustment_action = "REDUCE_FEED_GATE_VALVE_15_PERCENT"
            logger.warning(f"[{self.mill_id}] Torque vector anomaly detected! Magnitude: {magnitude:.2f} kNm, Vibration: { torsional_vibration }")
        elif magnitude > self.rated_kw * 1.15:
            status = "ELEVATED"
            adjustment_action = "OPTIMIZE_INVERTER_FREQUENCY"

        record = {
            "timestamp": time.time(),
            "axial_torque": axial_torque,
            "radial_torque": radial_torque,
            "torsional_vibration": torsional_vibration,
            "vector_magnitude": magnitude,
            "phase_angle": phase_angle,
            "status": status,
            "action": adjustment_action
        }
        self.vector_history.append(record)
        return record

    def get_telemetry_summary(self) -> Dict[str, Any]:
        if not self.vector_history:
            return {"status": "NO_DATA"}
        latest = self.vector_history[-1]
        return {
            "mill_id": self.mill_id,
            "total_readings": len(self.vector_history),
            "latest_status": latest["status"],
            "latest_magnitude": latest["vector_magnitude"]
        }

if __name__ == "__main__":
    sentinel = RollerMillTorqueVectorSentinel(mill_id="NAI_MILL_04", rated_kw=90.0)
    telemetry = sentinel.analyze_torque_vector(axial_torque=85.5, radial_torque=22.1, torsional_vibration=2.1)
    print(f"Execution Test Telemetry: {telemetry}")
    code_text = open(__file__, "r").read()
    ast.parse(code_text)
    print("AST validation passed successfully.")
