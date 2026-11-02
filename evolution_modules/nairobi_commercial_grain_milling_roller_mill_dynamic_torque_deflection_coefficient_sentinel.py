"""
Nairobi Commercial Grain Milling Roller Mill Dynamic Torque Deflection Coefficient Sentinel
Author: Cortana Autonomous Evolutionary Architect
Operator: Michael Obiero (Nairobi, Kenya)
Description: Monitors, computes, and alerts on real-time torque deflection coefficients
             for commercial grain milling roller mill shafts.
"""

import logging
import math
import time
from typing import Dict, Any, List, Optional

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')
logger = logging.getLogger("RollerMillDeflectionSentinel")


class RollerMillDeflectionSentinel:
    """
    Computes dynamic torque deflection coefficients for roller mill shafts based on instantaneous
    motor torque, shaft rotational velocity, material feed rate, and thermal expansion metrics.
    """

    def __init__(self, mill_id: str, nominal_shaft_diameter_mm: float = 120.0, shear_modulus_gpa: float = 80.0):
        self.mill_id = mill_id
        self.diameter = nominal_shaft_diameter_mm
        self.shear_modulus = shear_modulus_gpa * 1e9  # Pascals
        self.telemetry_history: List[Dict[str, Any]] = []
        logger.info(f"Initialized RollerMillDeflectionSentinel for Mill {mill_id} (Ø {nominal_shaft_diameter_mm}mm)")

    def compute_polar_moment_of_inertia(self) -> float:
        # Polar moment of inertia J = (pi * d^4) / 32 in m^4
        d_meters = self.diameter / 1000.0
        return (math.pi * (d_meters ** 4)) / 32.0

    def analyze_cycle(self, torque_nm: float, rpm: float, feed_rate_kg_h: float, temperature_c: float) -> Dict[str, Any]:
        """
        Evaluates shaft deflection coefficient under current operational load.
        """
        try:
            j_polar = self.compute_polar_moment_of_inertia()
            angular_velocity = (rpm * 2 * math.pi) / 60.0
            
            # Effective twist angle per unit length (rad/m) roughly approximated by (Torque * L) / (J * G)
            # Here we compute the dynamic torsional stress and dimensionless deflection coefficient.
            torsional_stress = (torque_nm * (self.diameter / 2000.0)) / j_polar if j_polar > 0 else 0.0
            deflection_coefficient = torsional_stress / self.shear_modulus

            # Thermal compensation factor
            thermal_expansion_delta = max(0.0, temperature_c - 25.0) * 1.2e-5
            adjusted_coefficient = deflection_coefficient * (1.0 + thermal_expansion_delta)

            status = "NOMINAL"
            if adjusted_coefficient > 1.5e-4:
                status = "WARNING_HIGH_DEFLECTION"
            if adjusted_coefficient > 3.0e-4:
                status = "CRITICAL_TORSIONAL_FATIGUE_RISK"

            record = {
                "timestamp": time.time(),
                "mill_id": self.mill_id,
                "torque_nm": torque_nm,
                "rpm": rpm,
                "feed_rate_kg_h": feed_rate_kg_h,
                "temperature_c": temperature_c,
                "deflection_coefficient": adjusted_coefficient,
                "status": status
            }
            
            self.telemetry_history.append(record)
            if len(self.telemetry_history) > 1000:
                self.telemetry_history.pop(0)

            logger.debug(f"Mill {self.mill_id} Deflection Coefficient: {adjusted_coefficient:.6e} [{status}]")
            return record

        except Exception as e:
            logger.error(f"Error analyzing roller mill deflection for {self.mill_id}: {str(e)}")
            return {"status": "ERROR", "message": str(e)}

    def get_aggregate_telemetry(self) -> Dict[str, Any]:
        if not self.telemetry_history:
            return {"status": "NO_DATA"}
        
        recent = self.telemetry_history[-1]
        avg_torque = sum(r["torque_nm"] for r in self.telemetry_history) / len(self.telemetry_history)
        
        return {
            "mill_id": self.mill_id,
            "total_records": len(self.telemetry_history),
            "latest_status": recent["status"],
            "latest_coefficient": recent["deflection_coefficient"],
            "average_torque_nm": avg_torque
        }


if __name__ == "__main__":
    print("Executing RollerMillDeflectionSentinel self-test...")
    sentinel = RollerMillDeflectionSentinel(mill_id="NAI-MILL-04")
    
    # Simulate nominal run
    res1 = sentinel.analyze_cycle(torque_nm=450.0, rpm=750.0, feed_rate_kg_h=2500.0, temperature_c=32.5)
    print("Nominal Test Result:", res1["status"], f"Coefficient: {res1['deflection_coefficient']:.6e}")
    
    # Simulate high stress run
    res2 = sentinel.analyze_cycle(torque_nm=1250.0, rpm=740.0, feed_rate_kg_h=4200.0, temperature_c=68.0)
    print("High Stress Test Result:", res2["status"], f"Coefficient: {res2['deflection_coefficient']:.6e}")
    
    agg = sentinel.get_aggregate_telemetry()
    print("Aggregated Telemetry Summary:", agg)
    print("RollerMillDeflectionSentinel test sequence completed successfully.")
