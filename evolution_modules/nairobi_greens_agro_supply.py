"""
Nairobi Urban Rooftop & Greenhouse Hydroponic Nutrients Cold-Chain & Supply Sentinel
Designed for Cortana's Autonomous Evolutionary Architect
Operator: Michael Obiero, Nairobi, Kenya
"""

import json
import logging
import time
from typing import Dict, List, Optional, Any

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')
logger = logging.getLogger("NairobiGreensSentinel")


class HydroponicNutrientEngine:
    """Manages electrical conductivity (EC), pH, and temperature telemetry for urban hydroponics."""

    def __init__(self, target_ec: float = 1.8, target_ph: float = 6.0):
        self.target_ec = target_ec
        self.target_ph = target_ph

    def analyze_solution(self, current_ec: float, current_ph: float, water_temp_c: float) -> Dict[str, Any]:
        actions = []
        status = "OPTIMAL"

        if current_ec < (self.target_ec - 0.3):
            actions.append("Dose Solution A & B: EC low, increase nutrient concentration.")
            status = "ADJUSTMENT_REQUIRED"
        elif current_ec > (self.target_ec + 0.3):
            actions.append("Add Raw Water: EC high, dilute concentration.")
            status = "ADJUSTMENT_REQUIRED"

        if current_ph < 5.5:
            actions.append("Dose pH Up (Potassium Silicate buffer).")
            status = "ADJUSTMENT_REQUIRED"
        elif current_ph > 6.5:
            actions.append("Dose pH Down (Phosphoric acid buffer).")
            status = "ADJUSTMENT_REQUIRED"

        if water_temp_c > 24.0:
            actions.append("Activate Chiller: Water temperature exceeds 24C risk of root pythium.")
            status = "WARNING"

        return {
            "status": status,
            "current_ec": current_ec,
            "current_ph": current_ph,
            "water_temp_c": water_temp_c,
            "recommendations": actions
        }


class ColdChainDispatchLogistics:
    """Tracks harvested leafy greens and fresh herbs dispatch across Nairobi markets (City Market, Parklands, Kilimani)."""

    def __init__(self):
        self.shipments: Dict[str, Dict[str, Any]] = {}

    def create_shipment(self, shipment_id: str, destination: str, produce_type: str, weight_kg: float) -> Dict[str, Any]:
        record = {
            "shipment_id": shipment_id,
            "destination": destination,
            "produce_type": produce_type,
            "weight_kg": weight_kg,
            "status": "DISPATCHED",
            "timestamp": time.time(),
            "telemetry_log": []
        }
        self.shipments[shipment_id] = record
        logger.info(f"Shipment {shipment_id} created for {destination} ({weight_kg}kg {produce_type}).")
        return record

    def log_transit_telemetry(self, shipment_id: str, ambient_temp_c: float, humidity_pct: float) -> Optional[Dict[str, Any]]:
        if shipment_id not in self.shipments:
            logger.error(f"Shipment {shipment_id} not found.")
            return None
        
        alert = None
        if ambient_temp_c > 8.0:
            alert = "COLD_CHAIN_BREACH: Ambient temperature above 8C!"
            logger.warning(f"[{shipment_id}] {alert} Temp: {ambient_temp_c}C")

        log_entry = {
            "time": time.time(),
            "ambient_temp_c": ambient_temp_c,
            "humidity_pct": humidity_pct,
            "alert": alert
        }
        self.shipments[shipment_id]["telemetry_log"].append(log_entry)
        return log_entry


class NairobiGreensSentinelSystem:
    """Unified orchestrator for urban rooftop agriculture and cold-chain distribution."""

    def __init__(self):
        self.hydro_engine = HydroponicNutrientEngine()
        self.logistics = ColdChainDispatchLogistics()

    def execute_diagnostic_cycle(self) -> Dict[str, Any]:
        # Simulated telemetry snapshot from Westlands Rooftop Farm #4
        hydro_check = self.hydro_engine.analyze_solution(current_ec=1.4, current_ph=5.2, water_temp_c=25.2)
        
        # Simulated cold chain tracking
        ship_id = "NRB-GREEN-901"
        self.logistics.create_shipment(ship_id, "Kilimani Organic Hub", "Baby Spinach & Kale", 150.0)
        transit_check = self.logistics.log_transit_telemetry(ship_id, ambient_temp_c=7.5, humidity_pct=82.0)

        return {
            "operator": "Michael Obiero",
            "location": "Nairobi, Kenya",
            "hydroponic_telemetry": hydro_check,
            "dispatch_telemetry": transit_check,
            "system_status": "ACTIVE"
        }


if __name__ == "__main__":
    sentinel = NairobiGreensSentinelSystem()
    report = sentinel.execute_diagnostic_cycle()
    print(json.dumps(report, indent=2))
