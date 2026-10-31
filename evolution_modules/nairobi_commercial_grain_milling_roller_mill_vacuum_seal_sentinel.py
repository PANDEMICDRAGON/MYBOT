"""Nairobi Commercial Grain Milling Roller Mill Vacuum Seal Sentinel Module.

Monitors negative pressure differentials, gasket integrity, and air suction 
metrics on commercial roller mill housings in Nairobi grain processing facilities.
"""

import time
import math
import logging
from typing import Dict, Any, List, Optional

logging.basicConfig(level=logging.INFO, format='[%(asctime)s] [%(levelname)s] [VacuumSealSentinel]: %(message)s')
logger = logging.getLogger("RollerMillVacuumSealSentinel")

class RollerMillVacuumSealSentinel:
    """Continuously tracks vacuum pressure sensors on roller mill suction hoods,
    detecting seal degradation, filter blinding, or aspiration drop-offs.
    """
    def __init__(self, mill_id: str, nominal_vacuum_pa: float = 450.0, tolerance_pa: float = 75.0):
        self.mill_id = mill_id
        self.nominal_vacuum_pa = nominal_vacuum_pa
        self.tolerance_pa = tolerance_pa
        self.telemetry_history: List[Dict[str, Any]] = []
        logger.info(f"Initialized Vacuum Seal Sentinel for Mill {self.mill_id} | Target Vacuum: {nominal_vacuum_pa} Pa")

    def evaluate_seal_integrity(self, current_vacuum_pa: float, differential_pressure_pa: float, ambient_temp_c: float) -> Dict[str, Any]:
        """Evaluates current vacuum pressure against nominal threshold and detects leaks."""
        deviation = current_vacuum_pa - self.nominal_vacuum_pa
        abs_deviation = abs(deviation)
        
        status = "OPTIMAL"
        action_required = False
        risk_score = min(100.0, (abs_deviation / self.tolerance_pa) * 50.0)

        if current_vacuum_pa < (self.nominal_vacuum_pa - self.tolerance_pa):
            status = "SEAL_DEGRADATION_OR_AIR_LEAK"
            action_required = True
            logger.warning(f"[{self.mill_id}] Vacuum drop detected! Current: {current_vacuum_pa} Pa (Nominal: {self.nominal_vacuum_pa} Pa)")
        elif current_vacuum_pa > (self.nominal_vacuum_pa + self.tolerance_pa):
            status = "FILTER_BLINDING_OR_OVER_SUCTION"
            action_required = True
            logger.warning(f"[{self.mill_id}] High suction pressure detected! Current: {current_vacuum_pa} Pa")

        telemetry = {
            "timestamp": time.time(),
            "mill_id": self.mill_id,
            "current_vacuum_pa": current_vacuum_pa,
            "differential_pressure_pa": differential_pressure_pa,
            "ambient_temp_c": ambient_temp_c,
            "deviation_pa": deviation,
            "risk_score": round(risk_score, 2),
            "status": status,
            "action_required": action_required
        }
        
        self.telemetry_history.append(telemetry)
        if len(self.telemetry_history) > 1000:
            self.telemetry_history.pop(0)
            
        return telemetry

    def generate_diagnostic_summary(self) -> Dict[str, Any]:
        """Summarizes recent vacuum health metrics."""
        if not self.telemetry_history:
            return {"status": "NO_DATA"}
            
        recent = self.telemetry_history[-1]
        avg_risk = sum(t["risk_score"] for t in self.telemetry_history) / len(self.telemetry_history)
        
        return {
            "mill_id": self.mill_id,
            "total_samples": len(self.telemetry_history),
            "latest_status": recent["status"],
            "latest_vacuum_pa": recent["current_vacuum_pa"],
            "average_risk_score": round(avg_risk, 2)
        }

if __name__ == "__main__":
    print("[+] Executing RollerMillVacuumSealSentinel Self-Test Diagnostic...")
    sentinel = RollerMillVacuumSealSentinel(mill_id="NAI-MILL-04")
    
    # Test normal operation
    res1 = sentinel.evaluate_seal_integrity(448.0, 25.0, 24.5)
    assert res1["status"] == "OPTIMAL", "Expected optimal status"
    
    # Test leak condition
    res2 = sentinel.evaluate_seal_integrity(360.0, 10.0, 26.0)
    assert res2["status"] == "SEAL_DEGRADATION_OR_AIR_LEAK", "Expected seal degradation status"
    
    summary = sentinel.generate_diagnostic_summary()
    print(f"[+] Diagnostic Summary: {summary}")
    print("[+] RollerMillVacuumSealSentinel self-test passed successfully.")
