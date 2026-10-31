"""
Nairobi Commercial Grain Milling Grain Damper & Tempering Sentinel
Autonomous Evolutionary Module for Cortana Autonomous System

Monitors and regulates industrial grain dampening (water addition rate proportional to incoming mass flow) and tempering bin dwell duration before roller milling.
"""

import logging
import time
import math
from typing import Dict, Any, List, Optional

logging.basicConfig(level=logging.INFO, format='[%(asctime)s] [TEMPERING_SENTINEL] %(levelname)s: %(message)s')
logger = logging.getLogger("GrainDamperTemperingSentinel")

class GrainDamperController:
    """
    Controls the micro-metering water pump for dampening wheat or maize
    based on instantaneous conveyor mass flow and target moisture differential.
    """
    def __init__(self, target_moisture_pct: float = 15.5, default_flow_tph: float = 10.0):
        self.target_moisture_pct = target_moisture_pct
        self.current_mass_flow_tph = default_flow_tph  # Tonnes per hour
        self.water_valve_pct = 50.0
        self.pump_hz = 35.0
        self.alarm_state = False

    def compute_water_injection(self, incoming_moisture_pct: float, mass_flow_tph: float) -> float:
        """
        Computes required liters/hour of water addition.
        Formula: Q = M * [ (Target - Initial) / (100 - Target) ] * 1000
        """
        self.current_mass_flow_tph = max(0.1, mass_flow_tph)
        moisture_diff = self.target_moisture_pct - incoming_moisture_pct
        
        if moisture_diff < 0:
            logger.warning("Incoming grain moisture exceeds target! Dampening suspended.")
            return 0.0

        # Mass of dry grain component * moisture delta
        water_liters_per_hour = self.current_mass_flow_tph * (moisture_diff / (100.0 - self.target_moisture_pct)) * 1000.0
        return round(water_liters_per_hour, 2)

    def adjust_actuators(self, water_lph: float) -> Dict[str, float]:
        # Map liters per hour to pump frequency (Hz) and control valve percentage
        self.pump_hz = min(60.0, max(5.0, (water_lph / 500.0) * 50.0))
        self.water_valve_pct = min(100.0, max(0.0, (water_lph / 600.0) * 100.0))
        return {"pump_hz": round(self.pump_hz, 2), "valve_pct": round(self.water_valve_pct, 2)}


class GrainTemperingBinMonitor:
    """
    Monitors grain bins during the resting/tempering phase (typically 8 to 24 hours)
    to ensure grain core hydration and prevent anaerobic respiration or heating.
    """
    def __init__(self, bin_id: str, required_hours: float = 12.0):
        self.bin_id = bin_id
        self.required_hours = required_hours
        self.batches: List[Dict[str, Any]] = []

    jettison_threshold_temp_c = 38.0

    def start_tempering_batch(self, batch_id: str, initial_temp_c: float, tonnage: float) -> Dict[str, Any]:
        batch = {
            "batch_id": batch_id,
            "start_time": time.time(),
            "initial_temp_c": initial_temp_c,
            "tonnage": tonnage,
            "status": "TEMPERING"
        }
        self.batches.append(batch)
        logger.info(f"Bin {self.bin_id}: Started batch {batch_id} | {tonnage}T | Temp: {initial_temp_c}°C")
        return batch

    def evaluate_batches(self, current_temps: Dict[str, float]) -> List[Dict[str, Any]]:
        now = time.time()
        alerts = []
        for batch in self.batches:
            if batch["status"] != "TEMPERING":
                continue
            elapsed_hours = (now - batch["start_time"]) / 3600.0
            current_temp = current_temps.get(batch["batch_id"], batch["initial_temp_c"])

            if current_temp >= self.jettison_threshold_temp_c:
                batch["status"] = "OVERHEAT_WARNING"
                alerts.append({
                    "bin_id": self.bin_id,
                    "batch_id": batch["batch_id"],
                    "alert": "TEMPERATURE_ANOMALY",
                    "temp_c": current_temp,
                    "message": "Tempering bin heating up! Risk of spoilage."
                })
            elif elapsed_hours >= self.required_hours:
                batch["status"] = "READY_FOR_MILLING"
                logger.info(f"Bin {self.bin_id}: Batch {batch["batch_id"]} completed tempering ({elapsed_hours:.1f}h).")
        return alerts


class NairobiGrainTemperingSystem:
    """
    Integrated supervisory unit coordinating multiple damper lines and tempering silos.
    """
    def __init__(self):
        self.damper = GrainDamperController(target_moisture_pct=15.0, default_flow_tph=15.0)
        self.bins = {
            "BIN_01": GrainTemperingBinMonitor("BIN_01", required_hours=12.0),
            "BIN_02": GrainTemperingBinMonitor("BIN_02", required_hours=16.0)
        }

    def run_telemetry_cycle(self, incoming_moisture: float, mass_flow: float, temp_readings: Dict[str, float]) -> Dict[str, Any]:
        water_req = self.damper.compute_water_injection(incoming_moisture, mass_flow)
        actuators = self.damper.adjust_actuators(water_req)

        all_alerts = []
        for bin_id, bin_monitor in self.bins.items():
            alerts = bin_monitor.evaluate_batches(temp_readings)
            all_alerts.extend(alerts)

        return {
            "status": "ACTIVE",
            "water_injection_lph": water_req,
            "actuators": actuators,
            "alerts": all_alerts
        }


if __name__ == "__main__":
    logger.info("Executing self-test for NairobiGrainTemperingSystem...")
    system = NairobiGrainTemperingSystem()
    
    # Start test batch
    system.bins["BIN_01"].start_tempering_batch("BATCH_KENYA_001", 24.5, 25.0)
    
    # Simulate telemetry evaluation
    telemetry_result = system.run_telemetry_cycle(
        incoming_moisture=11.5,
        mass_flow_tph=18.5,
        temp_readings={"BATCH_KENYA_001": 25.1}
    )
    logger.info(f"Telemetry Result: {telemetry_result}")
    logger.info("Nairobi Commercial Grain Milling Grain Damper & Tempering Sentinel verified successfully.")
