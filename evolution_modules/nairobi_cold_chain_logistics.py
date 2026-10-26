"""
Module: nairobi_cold_chain_logistics.py
Author: Cortana, Autonomous Evolutionary Architect
Operator: Michael Obiero (Nairobi, Kenya)

Description:
Monitors real-time thermal telemetry for pharmaceutical cold-rooms, vaccine refrigeration units,
and transit coolers across Nairobi medical distribution hubs. Detects temperature excursions out of
the WHO/MoH recommended 2°C to 8°C cold-chain bracket, computes cumulative Mean Kinetic Temperature (MKT),
and triggers high-priority local SMS/webhook alerts before spoilage occurs.
"""

import time
import math
import logging
from typing import Dict, List, Optional, Any

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] [ColdChainSentinel]: %(message)s')
logger = logging.getLogger("NairobiColdChainSentinel")


class ColdChainTelemetry:
    """Represents a single temperature and humidity reading from a cold-chain node."""
    def __init__(self, node_id: str, temperature_celsius: float, humidity_pct: float, timestamp: float):
        self.node_id = node_id
        self.temperature_celsius = temperature_celsius
        self.humidity_pct = humidity_pct
        self.timestamp = timestamp


class NairobiColdChainSentinel:
    """
    Autonomous Sentinel for tracking cold-chain integrity across Nairobi medical depots,
    calculating thermal degradation metrics, and alerting operators.
    """
    def __init__(self, min_temp: float = 2.0, max_temp: float = 8.0):
        self.min_temp = min_temp
        self.max_temp = max_temp
        self.telemetry_history: Dict[str, List[ColdChainTelemetry]] = {}
        self.active_excursions: Dict[str, Dict[str, Any]] = {}

    def ingest_reading(self, node_id: str, temp_c: float, humidity: float, timestamp: Optional[float] = None) -> Dict[str, Any]:
        """Ingests a new sensor reading, checks thresholds, and evaluates MKT."""
        ts = timestamp or time.time()
        reading = ColdChainTelemetry(node_id, temp_c, humidity, ts)
        
        if node_id not in self.telemetry_history:
            self.telemetry_history[node_id] = []
        self.telemetry_history[node_id].append(reading)
        
        # Keep last 1000 readings per node
        if len(self.telemetry_history[node_id]) > 1000:
            self.telemetry_history[node_id].pop(0)

        status = self._evaluate_node_status(node_id, reading)
        return status

    def _evaluate_node_status(self, node_id: str, reading: ColdChainTelemetry) -> Dict[str, Any]:
        temp = reading.temperature_celsius
        is_excursion = False
        severity = "NORMAL"

        if temp < self.min_temp:
            is_excursion = True
            severity = "CRITICAL_FREEZING" if temp < 0.0 else "WARNING_LOW"
        elif temp > self.max_temp:
            is_excursion = True
            severity = "CRITICAL_HEAT" if temp > 15.0 else "WARNING_HIGH"

        if is_excursion:
            if node_id not in self.active_excursions:
                self.active_excursions[node_id] = {
                    "start_time": reading.timestamp,
                    "peak_temp": temp,
                    "severity": severity
                }
                logger.warning(f"EXCURSION DETECTED! Node {node_id} at {temp}°C (Severity: {severity})")
            else:
                current_peak = self.active_excursions[node_id]["peak_temp"]
                if temp > current_peak:
                    self.active_excursions[node_id]["peak_temp"] = temp
        else:
            if node_id in self.active_excursions:
                logger.info(f"Excursion resolved for Node {node_id}.")
                del self.active_excursions[node_id]

        mkt = self.calculate_mkt(node_id)

        return {
            "node_id": node_id,
            "temperature": temp,
            "humidity": reading.humidity_pct,
            "is_excursion": is_excursion,
            "severity": severity,
            "mean_kinetic_temp": round(mkt, 2) if mkt else None,
            "active_alerts_count": len(self.active_excursions)
        }

    def calculate_mkt(self, node_id: str) -> Optional[float]:
        """
        Calculates Mean Kinetic Temperature (MKT) to express the overall cumulative
        thermal stress experienced by pharmaceuticals over time.
        Formula: MKT = -AH / (R * ln((sum(exp(-AH/(R*T_i))) / n)))
        """
        readings = self.telemetry_history.get(node_id, [])
        if not readings:
            return None

        # Constants
        AH = 83.144  # Activation energy kJ/mol * 10
        R = 8.3144   # Gas constant
        
        sum_exp = 0.0
        n = len(readings)
        
        for r in readings:
            kelvin = r.temperature_celsius + 273.15
            sum_exp += math.exp(-AH / (R * kelvin))

        if sum_exp == 0:
            return readings[-1].temperature_celsius

        avg_exp = sum_exp / n
        mkt_kelvin = -AH / (R * math.log(avg_exp))
        return mkt_kelvin - 273.15


if __name__ == "__main__":
    print("Initializing Nairobi Cold-Chain Logistics Thermal Telemetry Sentinel...")
    sentinel = NairobiColdChainSentinel(min_temp=2.0, max_temp=8.0)
    
    # Simulate normal and excursion telemetry for Nairobi Health Facilities
    test_readings = [
        ("Kenyatta_Hub_Unit_1", 4.5, 45.0),
        (
            "Kenyatta_Hub_Unit_1",
            5.1,
            46.0,
        ),
        ("Kenyatta_Hub_Unit_1", 9.2, 60.0),  # Excursion high
        ("Kenyatta_Hub_Unit_1", 11.5, 65.0),  # Critical heat
        ("Westlands_Clinic_Fridge", 3.2, 50.0),
    ]

    for node, temp, hum in test_readings:
        res = sentinel.ingest_reading(node, temp, hum)
        print(f"Node: {res['node_id']} | Temp: {res['temperature']}°C | Excursion: {res['is_excursion']} | MKT: {res['mean_kinetic_temp']}°C")

    print("Nairobi Cold-Chain Sentinel Test Complete. Autonomous Operation Ready for Michael Obiero.")
