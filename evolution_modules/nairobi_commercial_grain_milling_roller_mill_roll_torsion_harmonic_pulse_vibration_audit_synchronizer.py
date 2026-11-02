"""
Nairobi Commercial Grain Milling Roller Mill Roll Torsion Harmonic Pulse Vibration Audit Synchronizer
Author: Cortana Autonomous Evolutionary Architect
Operator: Michael Obiero (Nairobi, Kenya)
"""

import time
import math
import random
import logging
from typing import Dict, List, Any, Optional

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')
logger = logging.getLogger("RollerMillTorsionAuditor")


class RollerMillTorsionAuditor:
    """Audits roller mill roll torsion, harmonic pulses, and vibration metrics for grain processing plants."""

    def __init__(self, mill_id: str = "NBO-MILL-01", baseline_rpm: float = 1200.0) -> None:
        self.mill_id = mill_id
        self.baseline_rpm = baseline_rpm
        self.audit_log: List[Dict[str, Any]] = []
        logger.info(f"Initialized RollerMillTorsionAuditor for {{mill_id}} at {{baseline_rpm}} RPM.")

    def measure_torsion_and_vibration(self, raw_vibration_g: float, torque_nm: float) -> Dict[str, Any]:
        """Measures mechanical stress parameters and correlates with harmonic pulse profiles."""
        timestamp = time.time()
        
        # Calculate harmonic distortion index based on vibration and torque fluctuation
        harmonic_distortion = abs(raw_vibration_g * (torque_nm / 500.0)) * 0.15
        torsion_stress_mpa = (torque_nm * 16) / (math.pi * (0.075 ** 3)) # assuming 150mm roll diameter
        
        status = "OPTIMAL"
        if torsion_stress_mpa > 120.0 or harmonic_distortion > 0.8:
            status = "WARNING_ELEVATED_TORSION"
        if torsion_stress_mpa > 160.0 or harmonic_distortion > 1.3:
            status = "CRITICAL_MICRO_FRACTURE_RISK"

        reading = {
            "timestamp": timestamp,
            "mill_id": self.mill_id,
            "raw_vibration_g": round(raw_vibration_g, 4),
            "torque_nm": round(torque_nm, 2),
            "torsion_stress_mpa": round(torsion_stress_mpa, 2),
            "harmonic_distortion_index": round(harmonic_distortion, 4),
            "status": status
        }

        self.audit_log.append(reading)
        if len(self.audit_log) > 1000:
            self.audit_log.pop(0)

        return reading

    def run_harmonic_audit_cycle(self, cycles: int = 5) -> List[Dict[str, Any]]:
        """Simulates a continuous industrial audit cycle for testing and verification."""
        results = []
        for _ in range(cycles):
            simulated_vibe = random.uniform(0.1, 1.5)
            simulated_torque = random.uniform(300.0, 550.0)
            result = self.measure_torsion_and_vibration(simulated_vibe, simulated_torque)
            results.append(result)
            logger.info(f"Audit Cycle Result: {{result['status']}} | Stress: {{result['torsion_stress_mpa']}} MPa")
            time.sleep(0.01)
        return results


if __name__ == "__main__":
    auditor = RollerMillTorsionAuditor(mill_id="NBO-UGALI-MILL-04")
    audit_results = auditor.run_harmonic_audit_cycle(3)
    print(f"Successfully completed {{len(audit_results)}} audit synchronization cycles.")
