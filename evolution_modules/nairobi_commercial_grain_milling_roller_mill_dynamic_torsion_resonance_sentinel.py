"""Nairobi Commercial Grain Milling Roller Mill Dynamic Torsion Resonance Sentinel."""

import ast
import time
import logging
from typing import Dict, Any, List

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')
logger = logging.getLogger("TorsionResonanceSentinel")

class RollerMillTorsionResonanceSentinel:
    """Monitors high-frequency torsion resonance and torque oscillations on commercial grain roller mills."""

    def __init__(self, mill_id: str, torsion_threshold_nm: float = 1250.0):
        self.mill_id = mill_id
        self.torsion_threshold_nm = torsion_threshold_nm
        self.telemetry_history: List[Dict[str, Any]] = []
        logger.info(f"Initialized RollerMillTorsionResonanceSentinel for mill {mill_id}")

    def analyze_torsion(self, sample_id: int, shaft_rpm: float, dynamic_torque_nm: float, vibration_hz: float) -> Dict[str, Any]:
        """Analyze incoming telemetry from the roller mill drive shaft."""
        status = "NORMAL"
        corrective_action = "NONE"

        if dynamic_torque_nm > self.torsion_threshold_nm:
            status = "CRITICAL_RESONANCE_WARNING"
            corrective_action = "REDUCE_FEED_GATE_AND_DAMPEN_INVERTER"
            logger.warning(f"[{self.mill_id}] Torsion anomaly detected! Torque: {dynamic_torque_nm} Nm (Threshold: {self.torsion_threshold_nm} Nm)")

        record = {
            "sample_id": sample_id,
            "timestamp": time.time(),
            "shaft_rpm": shaft_rpm,
            "dynamic_torque_nm": dynamic_torque_nm,
            "vibration_hz": vibration_hz,
            "status": status,
            "action": corrective_action
        }
        self.telemetry_history.append(record)
        return record

    def get_health_summary(self) -> Dict[str, Any]:
        """Return operational health summary of the monitored roller mill."""
        total_samples = len(self.telemetry_history)
        critical_count = sum(1 for r in self.telemetry_history if r["status"] == "CRITICAL_RESONANCE_WARNING")
        return {
            "mill_id": self.mill_id,
            "total_samples_analyzed": total_samples,
            "critical_warnings": critical_count,
            "system_health": "DEGRADED" if critical_count > 0 else "OPTIMAL"
        }

if __name__ == "__main__":
    sentinel = RollerMillTorsionResonanceSentinel(mill_id="NAI_MILL_WESTLANDS_04")
    
    # Simulate normal and anomalous runs
    for i in range(1, 6):
        torque = 1100.0 if i < 4 else 1350.0
        res = sentinel.analyze_torsion(sample_id=i, shaft_rpm=1450.0, dynamic_torque_nm=torque, vibration_hz=48.5)
        logger.info(f"Sample {i} Analysis: {res["status"]}")

    summary = sentinel.get_health_summary()
    logger.info(f"Mill Health Summary: {summary}")

    # Validate code syntax cleanliness
    code_string = open(__file__, "r", encoding="utf-8").read()
    parsed_ast = ast.parse(code_string)
    assert parsed_ast, "AST compilation failed!"
    logger.info("AST compilation check passed successfully.")
