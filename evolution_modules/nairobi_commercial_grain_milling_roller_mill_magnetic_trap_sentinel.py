"""
Nairobi Commercial Grain Milling Roller Mill Magnetic Trap Sentinel

Monitors magnetic trap retention efficiency, ferrous contamination accumulation,
flux density degradation, and flush trigger status for roller mill feed streams in
Nairobi commercial milling facilities.
"""

import time
import logging
from typing import Dict, Any, List, Optional

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')
logger = logging.getLogger("RollerMillMagneticTrapSentinel")


class RollerMillMagneticTrapSentinel:
    """
    Real-time telemetry monitor for permanent and electromagnetic trap assemblies
    protecting roller mills from tramp metal damage.
    """

    def __init__(self, mill_id: str, threshold_gauss: float = 4500.0, max_ferrous_load_grams: float = 150.0):
        self.mill_id = mill_id
        self.threshold_gauss = threshold_gauss
        self.max_ferrous_load_grams = max_ferrous_load_grams
        self.is_active = True
        self.alert_history: List[Dict[str, Any]] = []

    def inspect_trap(self, current_gauss: float, collected_ferrous_grams: float, trap_temperature_c: float) -> Dict[str, Any]:
        """
        Inspects magnetic trap health and contamination load.
        """
        if not self.is_active:
            return {"status": "INACTIVE", "mill_id": self.mill_id}

        status = "OPTIMAL"
        actions = []

        # Check magnetic flux density (demagnetization check)
        if current_gauss < self.threshold_gauss:
            status = "WARNING"
            actions.append("MAGNETIC_FLUX_DEGRADATION_DETECTED: Schedule magnet re-magnetization or replacement.")

        # Check collected tramp iron mass
        if collected_ferrous_grams >= self.max_ferrous_load_grams:
            status = "CRITICAL"
            actions.append("TRAP_SATURATION_WARNING: Immediate magnetic purge/flush required to prevent overflow into roller nip.")

        # Check thermal status (overheating in electromagnets)
        if trap_temperature_c > 65.0:
            status = "CRITICAL"
            actions.append("ELECTROMAGNET_THERMAL_OVERLOAD: Risk of coil insulation breakdown. Check cooling.")

        assessment = {
            "timestamp": time.time(),
            "mill_id": self.mill_id,
            "current_gauss": current_gauss,
            "collected_ferrous_grams": collected_ferrous_grams,
            "trap_temperature_c": trap_temperature_c,
            "status": status,
            "recommended_actions": actions
        }

        if status != "OPTIMAL":
            self.alert_history.append(assessment)
            logger.warning(f"[{self.mill_id}] Magnetic Trap Alert: {status} | Actions: {actions}")
        else:
            logger.info(f"[{self.mill_id}] Magnetic Trap operating nominally at {current_gauss} Gauss.")

        return assessment

    def get_audit_trail(self) -> List[Dict[str, Any]]:
        return self.alert_history


if __name__ == "__main__":
    print("Initializing Nairobi Commercial Grain Milling Roller Mill Magnetic Trap Sentinel Test...")
    sentinel = RollerMillMagneticTrapSentinel(mill_id="NAIROBI_MILL_ALPHA_03")
    
    # Test normal condition
    res1 = sentinel.inspect_trap(current_gauss=4800.0, collected_ferrous_grams=25.0, trap_temperature_c=35.0)
    assert res1["status"] == "OPTIMAL"

    # Test saturation condition
    res2 = sentinel.inspect_trap(current_gauss=4600.0, collected_ferrous_grams=160.0, trap_temperature_c=40.0)
    assert res2["status"] == "CRITICAL"

    print("Roller Mill Magnetic Trap Sentinel verification completed successfully.")
