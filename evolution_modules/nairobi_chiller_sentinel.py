"""
Module: nairobi_chiller_sentinel.py
Author: Cortana, Autonomous Evolutionary Architect
Operator: Michael Obiero (Nairobi, Kenya)

Description:
Monitors industrial water chillers and HVAC cooling loops in Nairobi commercial installations.
Tracks approach temperatures, refrigerant pressures, oil sump levels, and cooling tower biosafety
metrics to prevent operational failure and optimize thermodynamic efficiency.
"""

import logging
import time
from typing import Dict, Any, List

logging.basicConfig(level=logging.INFO, format='%(asctime)s - [CHILLER-SENTINEL] - %(levelname)s - %(message)s')
logger = logging.getLogger("NairobiChillerSentinel")


class ChillerBiosafetySentinel:
    """Real-time sensor telemetry processor for commercial water chillers and HVAC cooling circuits."""

    def __init__(self, chiller_id: str, refrigerant_type: str = "R-134a") -> None:
        self.chiller_id = chiller_id
        self.refrigerant_type = refrigerant_type
        self.anomaly_history: List[Dict[str, Any]] = []

    def evaluate_telemetry(self, telemetry: Dict[str, float]) -> Dict[str, Any]:
        """
        Evaluates incoming sensor telemetry against thermodynamic and biosafety thresholds.
        Expected keys: evaporator_temp_c, condenser_temp_c, approach_temp_c, refrigerant_pressure_psi,
        oil_pressure_psi, cooling_tower_chlorine_ppm, vibration_mm_s.
        """
        alerts: List[str] = []
        status = "OPTIMAL"

        evap_t = telemetry.get("evaporator_temp_c", 4.5)
        cond_t = telemetry.get(
            "condenser_temp_c", 35.0)
        approach = telemetry.get("approach_temp_c", 2.0)
        ref_press = telemetry.get("refrigerant_pressure_psi", 140.0)
        oil_press = telemetry.get("oil_pressure_psi", 45.0)
        chlorine = telemetry.get("cooling_tower_chlorine_ppm", 1.2)
        vibration = telemetry.get("vibration_mm_s", 1.0)

        # Approach temperature check (scaling fouling factor or tube scaling)
        if approach > 4.5:
            alerts.append(f"HIGH_APPROACH_TEMP: {approach}C indicates potential tube scaling or fouling.")
            status = "WARNING"

        # Refrigerant pressure anomaly (potential leak or overcharge)
        if ref_press < 110.0 or ref_press > 185.0:
            alerts.append(f"REFRIGERANT_PRESSURE_ANOMALY: {ref_press} PSI outside safe envelope for {self.refrigerant_type}.")
            status = "CRITICAL"

        # Compressor oil differential pressure check
        if oil_press < 30.0:
            alerts.append(f"LOW_OIL_PRESSURE: {oil_press} PSI. Risk of compressor bearing seizure.")
            status = "CRITICAL"

        # Cooling tower biological hazard check (Legionella risk mitigation)
        if chlorine < 0.5:
            alerts.append(f"BIOCIDE_DEFICIT: Cooling tower chlorine at {chlorine} PPM. Legionella risk elevated.")
            status = "CRITICAL"

        # Mechanical vibration check
        if vibration > 3.5:
            alerts.append(f"EXCESSIVE_VIBRATION: {vibration} mm/s indicates mechanical imbalance or cavitation.")
            status = "WARNING" if status != "CRITICAL" else "CRITICAL"

        evaluation_result = {
            "chiller_id": self.chiller_id,
            "timestamp": time.time(),
            "status": status,
            "alerts": alerts,
            "metrics_analyzed": telemetry
        }

        if status != "OPTIMAL":
            self.anomaly_history.append(evaluation_result)
            logger.warning(f"Chiller {self.chiller_id} status: {status} | Alerts: {alerts}")
        else:
            logger.info(f"Chiller {self.chiller_id} operating within normal parameters.")

        return evaluation_result


if __name__ == "__main__":
    print("Initializing Nairobi Commercial Chiller & Cold-Water HVAC Biosafety Sentinel...")
    sentinel = ChillerBiosafetySentinel(chiller_id="CHILLER-CBD-04", refrigerant_type="R-134a")

    # Test normal telemetry
    normal_telemetry = {
        "evaporator_temp_c": 4.2,
        "condenser_temp_c": 32.5,
        "approach_temp_c": 1.8,
        "refrigerant_pressure_psi": 145.0,
        "oil_pressure_psi": 50.0,
        "cooling_tower_chlorine_ppm": 1.5,
        "vibration_mm_s": 0.8
    }
    sentinel.evaluate_telemetry(normal_telemetry)

    # Test anomalous telemetry (biocide deficit and high approach temp)
    stressed_telemetry = {
        "evaporator_temp_c": 7.0,
        "condenser_temp_c": 42.0,
        "approach_temp_c": 5.2,
        "refrigerant_pressure_psi": 195.0,
        "oil_pressure_psi": 25.0,
        "cooling_tower_chlorine_ppm": 0.2,
        "vibration_mm_s": 4.1
    }
    sentinel.evaluate_telemetry(stressed_telemetry)
    print("Chiller Biosafety Sentinel test cycle completed successfully.")
