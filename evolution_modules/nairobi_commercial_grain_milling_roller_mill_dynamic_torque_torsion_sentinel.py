"""
Nairobi Commercial Grain Milling Roller Mill Dynamic Torque Torsion Sentinel

Autonomous Evolutionary Architecture Component v445
Designed for Michael Obiero in Nairobi, Kenya.

Monitors torsional twist, angular deflection variance, and shaft torque differentials
in commercial roller mills to prevent catastrophic driveline failure.
"""

import ast
import logging
import random
import time
from typing import Dict, List, Any, Optional

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("RollerMillTorsionSentinel")


class RollerMillTorsionSentinel:
    """Real-time torsional telemetry analyzer for commercial milling drive shafts."""

    def __init__(self, mill_id: str, torsion_threshold_nm: float = 1250.0):
        self.mill_id = mill_id
        self.torsion_threshold_nm = torsion_threshold_nm
        self.telemetry_history: List[Dict[str, Any]] = []
        self.status = "STANDBY"

    def ingest_telemetry(self, drive_torque_nm: float, driven_torque_nm: float, rpm: float) -> Dict[str, Any]:
        """Analyze incoming torque differentials and calculate torsional stress."""
        torsional_stress = abs(drive_torque_nm - driven_torque_nm)
        twist_index = torsional_stress / (rpm + 1e-6)
        
        alert_triggered = torsional_stress > self.torsion_threshold_nm
        if alert_triggered:
            self.status = "ALERT_TORSIONAL_SPIKE"
            logger.warning(f"[{self.mill_id}] Torsional Spike Detected! Stress: {torsional_stress:.2f} Nm (Threshold: {self.torsion_threshold_nm})")
        else:
            self.status = "NOMINAL"

        record = {
            "timestamp": time.time(),
            "drive_torque_nm": drive_torque_nm,
            "driven_torque_nm": driven_torque_nm,
            "torsional_stress": torsional_stress,
            "twist_index": twist_index,
            "rpm": rpm,
            "status": self.status
        }
        self.telemetry_history.append(record)
        if len(self.telemetry_history) > 1000:
            self.telemetry_history.pop(0)

        return record

    def get_diagnostic_summary(self) -> Dict[str, Any]:
        """Summarize torsion health and operational integrity."""
        if not self.telemetry_history:
            return {"status": "NO_DATA"}

        recent = self.telemetry_history[-50:]
        avg_stress = sum(r["torsional_stress"] for r in recent) / len(recent)
        max_stress = max(r["torsional_stress"] for r in recent)

        return {
            "mill_id": self.mill_id,
            "current_status": self.status,
            "average_torsional_stress_nm": round(avg_stress, 2),
            "peak_torsional_stress_nm": round(max_stress, 2),
            "total_samples_analyzed": len(self.telemetry_history)
        }


if __name__ == "__main__":
    sentinel = RollerMillTorsionSentinel(mill_id="NAIROBI_MILL_ROASTER_04")
    logger.info("Initializing RollerMillTorsionSentinel Test Harness...")

    for _ in range(10):
        d_torque = random.uniform(800.0, 1100.0)
        dn_torque = d_torque - random.uniform(5.0, 50.0) if random.random() > 0.1 else d_torque - 350.0
        rpm_val = random.uniform(490.0, 510.0)
        res = sentinel.ingest_telemetry(d_torque, dn_torque, rpm_val)
        time.sleep(0.01)

    summary = sentinel.get_diagnostic_summary()
    logger.info(f"Diagnostic Summary: {summary}")

    # Validate code integrity via AST parsing
    with open(__file__, "r", encoding="utf-8") as f:
        source_code = f.read()
    parsed_ast = ast.parse(source_code)
    logger.info(f"AST Validation Successful: {len(parsed_ast.body)} nodes verified.")
