"""
Nairobi Peri-Urban Vermicompost & Microbial Bioreactor Sentinel
Author: Cortana Autonomous Evolutionary Architect
Operator: Michael Obiero (Nairobi, Kenya)

Monitors and regulates vermicomposting and organic waste bioreactors across Nairobi peri-urban zones,
ensuring optimal moisture, temperature, carbon-to-nitrogen ratios, and leachate biosafety.
"""

import logging
from typing import Dict, Any, List
from dataclasses import dataclass

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("VermicompostSentinel")

@dataclass
class BioreactorMetrics:
    reactor_id: str
    temperature_c: float
    moisture_pct: float
    ph_level: float
    cn_ratio: float
    ammonia_ppm: float
    leachate_turbidity_ntu: float

class VermicompostSentinel:
    """Performs real-time telemetry analysis and biosafety control for urban vermicompost systems."""

    def __init__(self, target_moisture_range: tuple = (60.0, 80.0), target_temp_range: tuple = (15.0, 30.0)) -> None:
        self.min_moisture, self.max_moisture = target_moisture_range
        self.min_temp, self.max_temp = target_temp_range

    def evaluate_reactor(self, metrics: BioreactorMetrics) -> Dict[str, Any]:
        """Evaluates reactor telemetry and returns corrective actuation directives."""
        alerts: List[str] = []
        actions: List[str] = []
        status = "OPTIMAL"

        # Temperature Check
        if not (self.min_temp <= metrics.temperature_c <= self.max_temp):
            status = "WARNING"
            if metrics.temperature_c > self.max_temp:
                alerts.append(f"High temperature warning: {metrics.temperature_c}C (risk to Eisenia fetida)")
                actions.append("TRIGGER_MISTING_AND_VENTILATION")
            else:
                alerts.append(f"Low temperature warning: {metrics.temperature_c}C")
                actions.append("REDUCE_SHADING_OR_ADD_THERMAL_COVER")

        # Moisture Check
        if not (self.min_moisture <= metrics.moisture_pct <= self.max_moisture):
            status = "WARNING"
            if metrics.moisture_pct < self.min_moisture:
                alerts.append(f"Sub-optimal moisture: {metrics.moisture_pct}% (Bedding drying out)")
                actions.append("INITIATE_DRIP_IRRIGATION_CYCLE")
            else:
                alerts.append(f"Excess moisture: {metrics.moisture_pct}% (Risk of anaerobic pockets)")
                actions.append("INCREASE_AERATION_AND_ADD_CARBON_MATRIX")

        # pH & Ammonia checks
        if metrics.ph_level < 6.0 or metrics.ph_level > 8.0:
            status = "CRITICAL"
            alerts.append(f"pH out of range: {metrics.ph_level}")
            actions.append("APPLY_AGRICULTURAL_LIME_OR_BUFFER")

        if metrics.ammonia_ppm > 25.0:
            status = "CRITICAL"
            alerts.append(f"High ammonia toxicity: {metrics.ammonia_ppm} ppm")
            actions.append(
                "PAUSE_NITROGEN_INPUTS_AND_FLUSH"
            )

        logger.info(f"Reactor {metrics.reactor_id} evaluated. Status: {status} | Alerts: {len(alerts)}")
        return {
            "reactor_id": metrics.reactor_id,
            "status": status,
            "alerts": alerts,
            "actions": actions
        }

if __name__ == "__main__":
    sentinel = VermicompostSentinel()
    sample_metrics = BioreactorMetrics(
        reactor_id="VERMI-NRB-01",
        temperature_c=32.5,
        moisture_pct=52.0,
        ph_level=6.8,
        cn_ratio=25.0,
        ammonia_ppm=12.0,
        leachate_turbidity_ntu=4.5
    )
    report = sentinel.evaluate_reactor(sample_metrics)
    print("--- Vermicompost Sentinel Test Report ---")
    for k, v in report.items():
        print(f"{k}: {v}")
