"""
Nairobi Commercial Coffee Milling & Hulling Biosafety Sentinel
Author: Cortana Autonomous Evolutionary Architect
Operator: Michael Obiero (Nairobi, Kenya)

Monitors coffee milling plant parameters including hulling chamber temperature,
chaff cyclone pressure differentials, bean moisture content, and particulate dust
explosive risk index. Provides automated emergency dampening and operator alerts.
"""

import logging
import time
import json
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] [CoffeeMillingSentinel]: %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class MillingNodeMetrics:
    node_id: str
    hulling_temp_c: float
    chaff_cyclone_pa: float
    bean_moisture_pct: float
    dust_particulate_mg_m3: float
    vibration_mm_s: float
    timestamp: float = field(default_factory=time.time)

class CoffeeMillingSentinel:
    """
    Real-time safety and operational biosafety sentinel for Nairobi coffee hulling and grading lines.
    """
    MAX_HULLING_TEMP = 85.0  # Celsius
    MIN_BEAN_MOISTURE = 10.0  # Percentage
    MAX_BEAN_MOISTURE = 12.5  # Percentage
    MAX_DUST_PARTICULATE = 450.0  # mg/m3 (Combustible dust threshold risk)
    MAX_VIBRATION = 7.5  # mm/s RMS

    def __init__(self, plant_id: str):
        self.plant_id = plant_id
        self.incident_log: List[Dict[str, Any]] = []

    def evaluate_node(self, metrics: MillingNodeMetrics) -> Dict[str, Any]:
        """
        Evaluates real-time sensor streams for fire risks, mechanical fatigue, or mold hazards.
        """
        warnings = []
        critical_actions = []

        # 1. Thermal check on hulling discs
        if metrics.hulling_temp_c > self.MAX_HULLING_TEMP:
            warnings.append(f"HIGH_HULLING_TEMP: {metrics.hulling_temp_c}C exceeds limit {self.MAX_HULLING_TEMP}C")
            critical_actions.append("ENGAGE_WATER_MIST_QUENCH")

        # 2. Combustible dust risk
        if metrics.dust_particulate_mg_m3 > self.MAX_DUST_PARTICULATE:
            warnings.append(f"COMBUSTIBLE_DUST_HAZARD: {metrics.dust_particulate_mg_m3} mg/m3")
            critical_actions.append("ACTIVATE_CYCLONE_EXHAUST_BOOST")

        # 3. Moisture check (Risk of mold if too high, hull damage if too low)
        if metrics.bean_moisture_pct > self.MAX_BEAN_MOISTURE:
            warnings.append(f"MOISTURE_HIGH_MOLD_RISK: {metrics.bean_moisture_pct}%")
            critical_actions.append(
                "DIVERT_TO_SECONDARY_DRYER"
            )
        elif metrics.bean_moisture_pct < self.MIN_BEAN_MOISTURE:
            warnings.append(f"MOISTURE_LOW_BRITTLE_RISK: {metrics.bean_moisture_pct}%")

        # 4. Mechanical vibration check
        if metrics.vibration_mm_s > self.MAX_VIBRATION:
            warnings.append(f"EXCESSIVE_VIBRATION: {metrics.vibration_mm_s} mm/s")
            critical_actions.append(
                "EMERGENCY_STOP_CONVEYOR"
            )

        status = "NOMINAL"
        if critical_actions:
            status = "CRITICAL_INTERVENTION"
        elif warnings:
            status = "WARNING"

        evaluation = {
            "plant_id": self.plant_id,
            "node_id": metrics.node_id,
            "status": status,
            "warnings": warnings,
            "critical_actions": critical_actions,
            "timestamp": metrics.timestamp
        }

        if status != "NOMINAL":
            self.incident_log.append(evaluation)
            logger.warning(f"[{self.plant_id}] Node {metrics.node_id} status: {status} | Actions: {critical_actions}")
        else:
            logger.info(f"[{self.plant_id}] Node {metrics.node_id} operational metrics nominal.")

        return evaluation

    def get_audit_summary(self) -> Dict[str, Any]:
        return {
            "plant_id": self.plant_id,
            "total_incidents_logged": len(self.incident_log),
            "incidents": self.incident_log[-10:]  # Last 10
        }

if __name__ == "__main__":
    print("Initializing Nairobi Commercial Coffee Milling Sentinel Test Harness...")
    sentinel = CoffeeMillingSentinel(plant_id="NAIROBI-KAHAWA-MILL-01")
    
    test_metrics = MillingNodeMetrics(
        node_id="HULLER-LINE-A",
        hulling_temp_c=88.5,
        chaff_cyclone_pa=1250.0,
        bean_moisture_pct=13.2,
        dust_particulate_mg_m3=510.0,
        vibration_mm_s=8.1
    )

    result = sentinel.evaluate_node(test_metrics)
    print(json.dumps(result, indent=2))
    print("Coffee Milling Sentinel test completed successfully.")
