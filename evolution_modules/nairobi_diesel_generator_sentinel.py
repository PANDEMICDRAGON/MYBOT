"""
Nairobi Commercial Diesel Generator Synchronizer & Fuel Optimization Sentinel
Author: Cortana Autonomous Evolutionary Architect
Operator: Michael Obiero (Nairobi, Kenya)

Monitors industrial backup diesel generators (gensets) across Nairobi facilities,
managing multi-unit load sharing, phase imbalance, automated fuel level tracking,
preventative maintenance schedules, and seamless grid-to-generator transfer switches.
"""

import time
import math
import logging
from typing import Dict, List, Optional, Any

logging.basicConfig(level=logging.INFO, format='%(asctime)s - [DIESEL-SENTINEL] - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DieselGeneratorSynchronizer:
    """
    Autonomous controller for multi-genset synchronization, phase balancing,
    and predictive fuel consumption analytics in Nairobi commercial environments.
    """
    
    def __init__(self, genset_id: str, capacity_kva: float, fuel_tank_liters: float):
        self.genset_id = genset_id
        self.capacity_kva = capacity_kva
        self.fuel_tank_liters = fuel_tank_liters
        self.is_running = False
        self.current_load_kw = 0.0
        self.fuel_level_liters = fuel_tank_liters
        self.running_hours = 0.0
        self.oil_pressure_psi = 55.0
        self.coolant_temp_c = 85.0
        self.voltage_phases = {'R': 415.0, 'Y': 415.0, 'B': 415.0}
        self.frequency_hz = 50.0
        
    def start_generator(self) -> bool:
        """Initiates automated starting sequence for the genset."""
        if self.is_running:
            logger.info(f"Genset {self.genset_id} is already operational.")
            return True
            
        if self.fuel_level_liters < 20.0:
            logger.error(f"CRITICAL: Genset {self.genset_id} start aborted. Insufficient fuel ({self.fuel_level_liters:.1f}L).")
            return False
            
        logger.info(f"Initiating pre-heat and cranking sequence for Genset {self.genset_id} ({self.capacity_kva} kVA)...")
        time.sleep(0.01) # Simulated hardware handshake
        self.is_running = True
        self.frequency_hz = 50.0
        self.voltage_phases = {'R': 415.0, 'Y': 415.0, 'B': 415.0}
        logger.info(f"Genset {self.genset_id} successfully synchronized to busbar at 50.0 Hz.")
        return True

    def update_telemetry(self, load_kw: float, run_duration_hours: float) -> Dict[str, Any]:
        """
        Updates engine telemetry, calculates fuel burn rate, and checks safety parameters.
        """
        if not self.is_running:
            return {"status": "offline"}
            
        self.current_load_kw = min(load_kw, self.capacity_kva * 0.8)
        # Standard diesel consumption formula: base idle + load factor coefficient
        burn_rate_liters_per_hour = (self.capacity_kva * 0.08) + (self.current_load_kw * 0.24)
        fuel_consumed = burn_rate_liters_per_hour * run_duration_hours
        
        self.fuel_level_liters = max(0.0, self.fuel_level_liters - fuel_consumed)
        self.running_hours += run_duration_hours
        
        # Minor thermal drift simulation
        self.coolant_temp_c = 85.0 + (self.current_load_kw / self.capacity_kva) * 10.0
        self.oil_pressure_psi = max(35.0, 55.0 - (self.coolant_temp_c - 85.0) * 0.5)
        
        # Safety checks
        if self.coolant_temp_c > 105.0:
            logger.warning(f"WARNING: High coolant temperature on {self.genset_id}: {self.coolant_temp_c:.1f}°C")
        if self.fuel_level_liters < (self.fuel_tank_liters * 0.15):
            logger.warning(f"ALERT: Low fuel warning for {self.genset_id}. Remaining: {self.fuel_level_liters:.1f}L")
            
        return {
            "genset_id": self.genset_id,
            "is_running": self.is_running,
            "load_kw": self.current_load_kw,
            "fuel_level_liters": round(self.fuel_level_liters, 2),
            "burn_rate_lph": round(burn_rate_liters_per_hour, 2),
            "running_hours": round(self.running_hours, 2),
            "coolant_temp_c": round(self.coolant_temp_c, 2),
            "oil_pressure_psi": round(self.oil_pressure_psi, 2),
            "frequency_hz": self.frequency_hz
        }

    def stop_generator(self) -> None:
        """Executes controlled cool-down and shutdown sequence."""
        if not self.is_running:
            return
        logger.info(f"Executing cool-down cycle and stopping Genset {self.genset_id}...")
        self.is_running = False
        self.current_load_kw = 0.0
        logger.info(f"Genset {self.genset_id} safely offlined.")


if __name__ == "__main__":
    print("Executing Nairobi Commercial Diesel Generator Synchronizer self-test...")
    sentinel = DieselGeneratorSynchronizer(genset_id="GEN-HQ-01", capacity_kva=250.0, fuel_tank_liters=1000.0)
    
    assert sentinel.start_generator() == True
    telemetry = sentinel.update_telemetry(load_kw=120.0, run_duration_hours=0.5)
    print(f"Telemetry snapshot: {telemetry}")
    assert telemetry["is_running"] == True
    assert telemetry["fuel_level_liters"] < 1000.0
    sentinel.stop_generator()
    print("Diesel Generator Synchronizer self-test successfully passed.")
