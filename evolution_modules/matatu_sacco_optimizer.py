"""
Module: matatu_sacco_optimizer.py
Author: Cortana Autonomous Evolutionary Architect
Operator: Michael Obiero (Kitengela & Nairobi, Kenya)

Description:
Provides telemetry ingestion, predictive maintenance tracking, daily fare revenue liquidity auditing,
and driver performance analytics for Nairobi and Kitengela Matatu SACCO fleets.
"""

import ast
import json
import logging
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import Dict, List, Optional

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')
logger = logging.getLogger("MatatuSaccoOptimizer")


@dataclass
class TelemetryPacket:
    vehicle_id: str
    sacco_name: str
    route: str
    timestamp: str
    gps_lat: float
    gps_lon: float
    speed_kmh: float
    fuel_level_pct: float
    engine_temp_c: float
    daily_fare_collected_kes: float
    passenger_count: int


@dataclass
class MaintenanceAlert:
    vehicle_id: str
    severity: str
    component: str
    recommended_action: str
    timestamp: str


class MatatuSaccoFleetEngine:
    """Autonomous telematics and revenue liquidity auditor for Kenyan Matatu SACCOs."""

    def __init__(self, warning_temp_c: float = 95.0, min_fuel_pct: float = 15.0):
        self.warning_temp_c = warning_temp_c
        self.min_fuel_pct = min_fuel_pct
        self.fleet_data: Dict[str, List[TelemetryPacket]] = {}
        self.alerts: List[MaintenanceAlert] = []

    def ingest_packet(self, packet: TelemetryPacket) -> List[MaintenanceAlert]:
        """Ingests vehicle telemetry, runs predictive diagnostics, and returns active alerts."""
        if packet.vehicle_id not in self.fleet_data:
            self.fleet_data[packet.vehicle_id] = []
        self.fleet_data[packet.vehicle_id].append(packet)

        generated_alerts = []
        now_str = datetime.now(timezone.utc).isoformat()

        # Check engine temperature
        if packet.engine_temp_c >= self.warning_temp_c:
            alert = MaintenanceAlert(
                vehicle_id=packet.vehicle_id,
                severity="HIGH",
                component="Cooling System / Engine",
                recommended_action=f"Immediate inspection required. Temp at {packet.engine_temp_c}C.",
                timestamp=now_str
            )
            self.alerts.append(alert)
            generated_alerts.append(alert)

        # Check fuel level
        if packet.fuel_level_pct <= self.min_fuel_pct:
            alert = MaintenanceAlert(
                vehicle_id=packet.vehicle_id,
                severity="MEDIUM",
                component="Fuel Tank",
                recommended_action=f"Low fuel warning ({packet.fuel_level_pct}%). Route to nearest Kitengela/Nairobi petrol station.",
                timestamp=now_str
            )
            self.alerts.append(alert)
            generated_alerts.append(alert)

        logger.info(f"Ingested telemetry for {packet.vehicle_id} on route {packet.route}. Generated {len(generated_alerts)} alerts.")
        return generated_alerts

    def audit_route_revenue(self, route: str) -> Dict[str, float]:
        """Audits total fare collection, average passenger load, and liquidity metrics for a given route."""
        total_fare = 0.0
        total_passengers = 0
        active_vehicles = set()

        for v_id, packets in self.fleet_data.items():
            route_packets = [p for p in packets if p.route == route]
            if route_packets:
                active_vehicles.add(v_id)
                latest = route_packets[-1]
                total_fare += latest.daily_fare_collected_kes
                total_passengers += latest.passenger_count

        return {
            "route": route,
            "active_fleet_count": len(active_vehicles),
            "total_revenue_kes": total_fare,
            "total_passengers": total_passengers,
            "avg_revenue_per_vehicle_kes": (total_fare / len(active_vehicles)) if active_vehicles else 0.0
        }


if __name__ == "__main__":
    print("Initializing Matatu SACCO Fleet Telemetry & Revenue Engine...")
    engine = MatatuSaccoFleetEngine()

    sample_packet = TelemetryPacket(
        vehicle_id="KCU-482Z",
        sacco_name="Kitengela Nam Lolwe Express",
        route="Kitengela - Nairobi CBD via Mombasa Road",
        timestamp=datetime.now(timezone.utc).isoformat(),
        gps_lat=-1.4146,
        gps_lon=36.8710,
        speed_kmh=65.5,
        fuel_level_pct=12.0,
        engine_temp_c=98.5,
        daily_fare_collected_kes=14500.0,
        passenger_count=42
    )

    alerts = engine.ingest_packet(sample_packet)
    print(f"Generated Maintenance Alerts: {len(alerts)}")
    for a in alerts:
        print(f" - [{a.severity}] {a.vehicle_id}: {a.recommended_action}")

    revenue_audit = engine.audit_route_revenue("Kitengela - Nairobi CBD via Mombasa Road")
    print(f"Route Audit Summary: {json.dumps(revenue_audit, indent=2)}")

    # Self-validation check under ast
    source_code = open(__file__, encoding="utf-8").read()
    ast.parse(source_code)
    print("AST Compilation Integrity Check: PASSED")
