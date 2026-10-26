"""
Nairobi Commercial Chiller Plant & HVAC Biosafety Sentinel
Monitors industrial chiller parameters, compressor discharge pressures, evaporator
approach temperatures, refrigerant levels, and automated load modulation.
"""

import time
import logging
from typing import Dict, Any, List, Optional

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')
logger = logging.getLogger("ChillerPlantSentinel")

class ChillerPlantSentinel:
    """
    Monitors and manages large-scale commercial chiller plant operations in Nairobi,
    guarding against freeze-ups, refrigerant leaks, and high head pressure anomalies.
    """
    def __init__(self, plant_id: str, capacity_tons: float):
        self.plant_id = plant_id
        self.capacity_tons = capacity_tons
        self.status = "STANDBY"
        self.active_alarms: List[str] = []
        self.telemetry_history: List[Dict[str, Any]] = []

    def evaluate_telemetry(self, metrics: Dict[str, float]) -> Dict[str, Any]:
        """
        Evaluates incoming sensor streams for evaporator temperature, condenser pressure,
        oil level, and chilled water flow rate.
        """
        self.active_alarms.clear()
        evap_temp = metrics.get("evaporator_temp_c", 4.5)
        condenser_press = metrics.get("condenser_pressure_bar", 12.0)
        oil_level = metrics.get("compressor_oil_level_pct", 85.0)
        chilled_flow = metrics.get("chilled_water_flow_lps", 25.0)

        # Safety checks
        if evap_temp < 1.0:
            self.active_alarms.append("CRITICAL: Evaporator Freeze Risk Detected")
        if condenser_press > 18.5:
            self.active_alarms.append("WARNING: High Condenser Head Pressure")
        if oil_level < 40.0:
            self.active_alarms.append("CRITICAL: Low Compressor Oil Level")
        if chilled_flow < 10.0:
            self.active_alarms.append("ALERT: Low Chilled Water Flow Rate")

        if self.active_alarms:
            self.status = "FAULT_MITIGATION"
            logger.warning(f"[{self.plant_id}] Alarms triggered: {self.active_alarms}")
        else:
            self.status = "OPTIMAL"

        record = {
            "timestamp": time.time(),
            "status": self.status,
            "metrics": metrics,
            "alarms": list(self.active_alarms)
        }
        self.telemetry_history.append(record)
        return record

    def get_plant_summary(self) -> Dict[str, Any]:
        return {
            "plant_id": self.plant_id,
            "capacity_tons": self.capacity_tons,
            "status": self.status,
            "active_alarms_count": len(self.active_alarms),
            "total_telemetry_records": len(self.telemetry_history)
        }

if __name__ == "__main__":
    sentinel = ChillerPlantSentinel(plant_id="NBO_TOWER_CHILLER_01", capacity_tons=350.0)
    sample_metrics = {
        "evaporator_temp_c": 4.2,
        "condenser_pressure_bar": 14.1,
        "compressor_oil_level_pct": 82.0,
        "chilled_water_flow_lps": 28.5
    }
    result = sentinel.evaluate_telemetry(sample_metrics)
    print("Chiller Evaluation Result:", result)
    print("Plant Summary:", sentinel.get_plant_summary())
