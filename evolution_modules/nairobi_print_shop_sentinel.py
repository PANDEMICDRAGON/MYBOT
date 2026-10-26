"""
Nairobi Commercial Print Shop & UV Curing Biosafety Sentinel
Designed to monitor print shop operations in Nairobi, Kenya.
Handles UV lamp degradation, VOC exhaust safety, pneumatic cutter pressure,
and thermal emergency cutoffs.
"""

import time
import logging
from typing import Dict, Any, List, Optional

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')
logger = logging.getLogger("PrintShopSentinel")

class PrintShopSentinel:
    def __init__(self, shop_id: str, uv_threshold_mw_cm2: float = 75.0, max_voc_ppm: float = 50.0):
        self.shop_id = shop_id
        self.uv_threshold = uv_threshold_mw_cm2
        self.max_voc_ppm = max_voc_ppm
        self.equipment_status: Dict[str, Dict[str, Any]] = {}
        logger.info(f"Initialized PrintShopSentinel for shop: {self.shop_id}")

    def register_equipment(self, equipment_id: str, equipment_type: str) -> None:
        """Register a printing press, UV drier, or cutter unit."""
        self.equipment_status[equipment_id] = {
            "type": equipment_type,
            "status": "ACTIVE",
            "uv_intensity_mw_cm2": 100.0,
            "voc_ppm": 10.0,
            "pneumatic_psi": 120.0,
            "temperature_c": 35.0,
            "last_serviced": time.time()
        }
        logger.info(f"Registered equipment {equipment_id} ({equipment_type}) in {self.shop_id}")

    def ingest_telemetry(self, equipment_id: str, telemetry: Dict[str, float]) -> Dict[str, Any]:
        """
        Ingest sensor telemetry for UV lamps, VOCs, pneumatic pressure, and temperature.
        Returns safety actions if thresholds are breached.
        """
        if equipment_id not in self.equipment_status:
            raise ValueError(f"Equipment {equipment_id} not registered.")

        eq = self.equipment_status[equipment_id]
        eq.update(telemetry)

        alerts: List[str] = []
        action_required = "NONE"

        # Check UV Curing Lamp degradation
        if eq["type"] == "UV_DRYER" and eq.get("uv_intensity_mw_cm2", 100.0) < self.uv_threshold:
            alerts.append(f"UV Lamp degradation detected: {eq['uv_intensity_mw_cm2']} mW/cm² < {self.uv_threshold}")
            action_required = "SCHEDULE_UV_BULB_REPLACEMENT"

        # Check VOC Exhaust safety
        if eq.get("voc_ppm", 0.0) > self.max_voc_ppm:
            alerts.append(f"High solvent VOC concentration: {eq['voc_ppm']} ppm > {self.max_voc_ppm} ppm")
            action_required = "EMERGENCY_VENTILATION_BOOST"

        # Check Pneumatic Pressure (e.g., guillotine cutters)
        if eq.get("pneumatic_psi", 120.0) < 90.0:
            alerts.append(f"Low pneumatic pressure: {eq['pneumatic_psi']} PSI (Risk of incomplete cut)")
            if action_required == "NONE":
                action_required = "PAUSE_FEEDER"

        # Check Thermal runaway
        if eq.get("temperature_c", 35.0) > 75.0:
            alerts.append(f"Critical temperature overheat: {eq['temperature_c']}°C")
            action_required = "IMMEDIATE_THERMAL_SHUTDOWN"
            eq["status"] = "EMERGENCY_SHUTDOWN"

        return {
            "equipment_id": equipment_id,
            "timestamp": time.time(),
            "status": eq["status"],
            "alerts": alerts,
            "action_required": action_required
        }

if __name__ == "__main__":
    sentinel = PrintShopSentinel("INDUSTRIAL_AREA_PRESS_01")
    sentinel.register_equipment("HEIDELBERG_SM_01", "OFFSET_PRESS")
    sentinel.register_equipment("UV_DRYER_02", "UV_DRYER")

    # Test normal ingestion
    res1 = sentinel.ingest_telemetry("UV_DRYER_02", {"uv_intensity_mw_cm2": 85.0, "voc_ppm": 15.0, "temperature_c": 40.0})
    print("Telemetry 1 Result:", res1)

    # Test hazardous VOC ingestion
    res2 = sentinel.ingest_telemetry("HEIDELBERG_SM_01", {"voc_ppm": 65.0, "pneumatic_psi": 110.0, "temperature_c": 45.0})
    print("Telemetry 2 Result:", res2)

    # Test thermal emergency ingestion
    res3 = sentinel.ingest_telemetry("UV_DRYER_02", {"uv_intensity_mw_cm2": 60.0, "voc_ppm": 20.0, "temperature_c": 82.0})
    print(
        "Telemetry 3 Result:", res3)
