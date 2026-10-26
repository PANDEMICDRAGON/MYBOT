"""
Nairobi Fresh Produce Cold-Chain & Solar Micro-Cold-Storage Logistics Sentinel
Author: Cortana Autonomous Evolutionary Architect
Operator: Michael Obiero, Nairobi, Kenya

Provides real-time IoT thermal telemetry tracking for solar-powered cold rooms in
Nairobi markets, predictive thermal excursion alerts, and automated micro-lease billing.
"""

import logging
import json
import time
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field

logging.basicConfig(level=logging.INFO, format='[%(asctime)s] [NBI-COLD-STORAGE] [%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class ColdRoomTelemetry:
    room_id: str
    market_location: str
    current_temp_celsius: float
    target_temp_celsius: float
    battery_voltage: float
    solar_input_amps: float
    occupancy_crates: int
    timestamp: float = field(default_factory=time.time)

class NairobiColdStorageSentinel:
    """Monitors solar cold-chain facilities in Nairobi markets to prevent spoilage of fresh produce."""

    CRITICAL_TEMP_THRESHOLD_C: float = 8.0
    MAX_BATTERY_DEPTH_DISCHARGE: float = 11.2

    def __init__(self, pricing_per_crate_kes: float = 50.0):
        self.pricing_per_crate_kes = pricing_per_crate_kes
        self.telemetry_history: List[ColdRoomTelemetry] = []
        self.active_alerts: Dict[str, str] = {}

    def ingest_telemetry(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Ingests telemetry payload from cold room IoT gateway and evaluates system health."""
        try:
            telemetry = ColdRoomTelemetry(
                room_id=data["room_id"],
                market_location=data["market_location"],
                current_temp_celsius=float(data["current_temp_celsius"]),
                target_temp_celsius=float(data["target_temp_celsius"]),
                battery_voltage=float(data["battery_voltage"]),
                solar_input_amps=float(data["solar_input_amps"]),
                occupancy_crates=int(data["occupancy_crates"])
            )
            self.telemetry_history.append(telemetry)
            return self._evaluate_conditions(telemetry)
        except (KeyError, ValueError) as e:
            logger.error(f"Malformed telemetry payload: {e}")
            return {"status": "error", "message": str(e)}

    def _evaluate_conditions(self, telemetry: ColdRoomTelemetry) -> Dict[str, Any]:
        alerts = []
        status = "OPTIMAL"

        # Thermal Excursion Check
        if telemetry.current_temp_celsius > self.CRITICAL_TEMP_THRESHOLD_C:
            status = "CRITICAL_THERMAL_EXCURSION"
            msg = f"WARNING: Cold room {teleymetry_room_id := telemetry.room_id} at {telemetry.market_location} is breaching safe threshold! Temp: {telemetry.current_temp_celsius}°C"
            logger.warning(msg)
            self.active_alerts[telemetry.room_id] = msg
            alerts.append(msg)
        else:
            if telemetry.room_id in self.active_alerts:
                del self.active_alerts[telemetry.room_id]

        # Power / Battery Check
        if telemetry.battery_voltage < self.MAX_BATTERY_DEPTH_DISCHARGE:
            status = "POWER_CRITICAL"
            msg = f"CRITICAL: Solar battery voltage low ({telemetry.battery_voltage}V) at {telemetry.market_location}."
            logger.error(msg)
            alerts.append(msg)

        # Micro-lease revenue computation
        projected_daily_revenue_kes = telemetry.occupancy_crates * self.pricing_per_crate_kes

        return {
            "room_id": telemetry.room_id,
            "market": telemetry.market_location,
            "status": status,
            "current_temp": telemetry.current_temp_celsius,
            "projected_daily_revenue_kes": projected_daily_revenue_kes,
            "active_alerts": alerts
        }

if __name__ == "__main__":
    sentinel = NairobiColdStorageSentinel()
    sample_payload = {
        "room_id": "CR-WAKULIMA-01",
        "market_location": "Wakulima Market, Nairobi",
        "current_temp_celsius": 9.5,
        "target_temp_celsius": 4.0,
        "battery_voltage": 12.4,
        "solar_input_amps": 14.2,
        "occupancy_crates": 120
    }
    result = sentinel.ingest_telemetry(sample_payload)
    print(json.dumps(result, indent=2))
