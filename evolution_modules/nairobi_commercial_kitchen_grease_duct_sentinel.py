"""
Nairobi Commercial Kitchen Grease Duct Thermal Inertia & Fire Suppression Sentinel
Author: Cortana Autonomous Evolutionary Architect
Operator: Michael Obiero (Nairobi, Kenya)
"""

import time
import logging
import json
from typing import Dict, Any, List, Optional

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - [KitchenDuctSentinel] %(message)s')

class GreaseDuctThermalModel:
    """Models thermal dynamics and grease ignition risk in commercial extraction ducts."""
    
    def __init__(self, ambient_temp_c: float = 25.0):
        self.ambient_temp_c = ambient_temp_c
        self.duct_temp_c = ambient_temp_c
        self.grease_buildup_index = 0.1  # 0.0 (clean) to 1.0 (hazardous)
        self.exhaust_airflow_cfm = 2500.0
        self.suppression_triggered = False
        
    def update_telemetry(self, exhaust_temp: float, airflow: float, particulate_ppm: float) -> Dict[str, Any]:
        self.duct_temp_c = exhaust_temp
        self.exhaust_airflow_cfm = airflow
        # Increment buildup index based on particulate simulation
        self.grease_buildup_index = min(1.0, self.grease_buildup_index + (particulate_ppm / 100000.0))
        
        thermal_inertia_risk = max(0.0, (self.duct_temp_c - 60.0) / 140.0)
        ignition_risk = thermal_inertia_risk * self.grease_buildup_index
        
        status = "NOMINAL"
        if ignition_risk > 0.75:
            status = "CRITICAL_FIRE_HAZARD"
            self.suppression_triggered = True
        elif ignition_risk > 0.45:
            status = "WARNING_HIGH_RESIDUE"
            
        return {
            "duct_temp_c": self.duct_temp_c,
            "grease_buildup_index": round(self.grease_buildup_index, 4),
            "ignition_risk_score": round(ignition_risk, 4),
            "suppression_active": self.suppression_triggered,
            "status": status,
            "timestamp": time.time()
        }

class KitchenDuctSentinel:
    """Orchestrates automated electrical isolation, gas shutoff, and fire suppression dispatch."""
    
    def __init__(self):
        self.thermal_model = GreaseDuctThermalModel()
        self.event_log: List[Dict[str, Any]] = []
        
    def evaluate_cycle(self, exhaust_temp: float, airflow: float, particulate_ppm: float) -> Dict[str, Any]:
        telemetry = self.thermal_model.update_telemetry(exhaust_temp, airflow, particulate_ppm)
        self.event_log.append(telemetry)
        
        action = "NONE"
        if telemetry["status"] == "CRITICAL_FIRE_HAZARD":
            action = "ENGAGE_WET_CHEMICAL_SUPPRESSION_AND_CUT_GAS"
            logging.critical("CRITICAL HAZARD DETECTED! Deploying suppression grid and severing gas/power lines.")
        elif telemetry["status"] == "WARNING_HIGH_RESIDUE":
            action = "TRIGGER_CARBON_SCRUBBER_FLUSH"
            logging.warning("High grease residue and thermal gradient. Flushing scrubbers.")
            
        return {
            "telemetry": telemetry,
            "recommended_action": action,
            "operator": "Michael Obiero"
        }

if __name__ == "__main__":
    sentinel = KitchenDuctSentinel()
    sample_readings = [
        (65.0, 2450.0, 120.0),
        (90.0, 2300.0, 450.0),
        (185.0, 1200.0, 1200.0)
    ]
    for temp, air, part in sample_readings:
        result = sentinel.evaluate_cycle(temp, air, part)
        print(json.dumps(result, indent=2))
        time.sleep(0.1)
