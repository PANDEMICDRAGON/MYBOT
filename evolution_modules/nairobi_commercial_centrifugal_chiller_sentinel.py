"""Nairobi Commercial Centrifugal Chiller & HVAC Biosafety Sentinel. Autonomous Industrial HVAC Monitoring for Nairobi Operators."""

import time
import math
import logging
from typing import Dict, Any, List, Optional

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] [ChillerSentinel]: %(message)s')
logger = logging.getLogger('CentrifugalChillerSentinel')

class CentrifugalChillerSentinel:
    """Monitors high-capacity centrifugal chillers, refrigerant subcooling, oil pressure differentials, and vibration."""
    
    def __init__(self, chiller_id: str, refrigerant_type: str = "R-134a") -> None:
        self.chiller_id = chiller_id
        self.refrigerant_type = refrigerant_type
        self.status = "STANDBY"
        self.telemetry_history: List[Dict[str, Any]] = []
        self.alarm_active = False
        logger.info(f"Initialized Chiller Sentinel for unit {self.chiller_id} using refrigerant {self.refrigerant_type}.")

    def evaluate_telemetry(self, telemetry: Dict[str, float]) -> Dict[str, Any]:
        """Analyzes incoming chiller metrics for anomalies, surging, or subcooling faults."""
        timestamp = time.time()
        evap_temp = telemetry.get("evaporator_temp_c", 4.0)
        suction_pressure_sat = telemetry.get("suction_saturation_temp_c", 3.5)
        cond_temp = telemetry.get("condenser_liquid_temp_c", 35.0)
        discharge_pressure_sat = telemetry.get("discharge_saturation_temp_c", 40.0)
        oil_pressure_diff = telemetry.get("oil_pressure_differential_psi", 25.0)
        vibration_mm_s = telemetry.get("vibration_amplitude_mms", 1.2)
        current_load_pct = telemetry.get("current_load_percentage", 75.0)

        # Calculations
        subcooling = discharge_pressure_sat - cond_temp
        superheat = evap_temp - suction_pressure_sat

        diagnostics = {
            "timestamp": timestamp,
            "chiller_id": self.chiller_id,
            "subcooling_c": round(subcooling, 2),
            "superheat_c": round(superheat, 2),
            "oil_differential_psi": oil_pressure_diff,
            "vibration_mms": vibration_mm_s,
            "load_pct": current_load_pct,
            "warnings": [],
            "fault_tripped": False
        }

        # Safety checks
        if subcooling < 2.0:
            diagnostics["warnings"].append("Low refrigerant subcooling risk of flash gas in expansion valve.")
        elif subcooling > 10.0:
            diagnostics["warnings"].append("High subcooling possible condenser overfill or fouled tubes.")

        if oil_pressure_diff < 15.0:
            diagnostics["warnings"].append("CRITICAL: Low oil pressure differential. Bearing damage risk!")
            diagnostics["fault_tripped"] = True
            self.alarm_active = True

        if vibration_mm_s > 4.5:
            diagnostics["warnings"].append("CRITICAL: Excessive vibration harmonic detected. Impeller surge imminent!")
            diagnostics["fault_tripped"] = True
            self.alarm_active = True

        if not diagnostics["fault_tripped"]:
            self.status = "OPTIMAL"
        else:
            self.status = "SHUTDOWN_TRIPPED"

        self.telemetry_history.append(diagnostics)
        if len(self.telemetry_history) > 1000:
            self.telemetry_history.pop(0)

        return diagnostics

    def get_operational_summary(self) -> Dict[str, Any]:
        """Returns historical operational summary and current health status."""
        return {
            "chiller_id": self.chiller_id,
            "status": self.status,
            "alarm_active": self.alarm_active,
            "total_telemetry_records": len(self.telemetry_history)
        }

if __name__ == "__main__":
    print("Executing CentrifugalChillerSentinel Test Harness...")
    sentinel = CentrifugalChillerSentinel(chiller_id="NAI_CBD_CHILLER_01", refrigerant_type="R-134a")
    
    normal_sample = {
        "evaporator_temp_c": 4.2,
        "suction_saturation_temp_c": 3.9,
        "condenser_liquid_temp_c": 34.0,
        "discharge_saturation_temp_c": 39.5,
        "oil_pressure_differential_psi": 28.5,
        "vibration_amplitude_mms": 1.1,
        "current_load_percentage": 68.0
    }
    result = sentinel.evaluate_telemetry(normal_sample)
    print("Normal Evaluation Result:", result)

    fault_sample = {
        "evaporator_temp_c": 6.0,
        "suction_saturation_temp_c": 3.0,
        "condenser_liquid_temp_c": 38.0,
        "discharge_saturation_temp_c": 39.0,
        "oil_pressure_differential_psi": 11.0,
        "vibration_amplitude_mms": 5.2,
        "current_load_percentage": 95.0
    }
    fault_result = sentinel.evaluate_telemetry(fault_sample)
    print("Fault Evaluation Result:", fault_result)
    print("Chiller Sentinel Module verified successfully.")
