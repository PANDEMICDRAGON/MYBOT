import time
import math
import logging
from typing import Dict, Any, List, Optional

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')
logger = logging.getLogger("OzoneSterilizationSentinel")

class OzoneSterilizationSentinel:
    """
    Monitors industrial ozone sterilization cycles, ambient safety sensors, and catalyst destruction units
    for commercial facilities in Nairobi, ensuring compliance with environmental safety thresholds.
    """
    
    SAFE_AMBIENT_PPM: float = 0.05
    MAX_CHAMBER_PPM: float = 120.0
    
    def __init__(self, chamber_id: str, capacity_liters: float):
        self.chamber_id = chamber_id
        self.capacity_liters = capacity_liters
        self.is_running = False
        self.current_phase = "STANDBY"
        self.chamber_o3_ppm = 0.0
        self.ambient_o3_ppm = 0.0
        self.catalyst_efficiency = 99.9
        self.chamber_pressure_kpa = 101.3
        self.total_cycles_completed = 0
        logger.info(f"OzoneSterilizationSentinel initialized for Chamber {self.chamber_id} ({self.capacity_liters}L).")

    def start_cycle(self, target_ppm: float, duration_minutes: int) -> Dict[str, Any]:
        """Initiates a timed sterilization cycle with precise generator modulation."""
        if self.is_running:
            raise RuntimeError(f"Chamber {self.chamber_id} is already executing an active cycle.")
        
        self.is_running = True
        self.current_phase = "INJECTION"
        self.chamber_o3_ppm = min(target_ppm, self.MAX_CHAMBER_PPM)
        self.chamber_pressure_kpa = 115.0  # Slightly pressurized during injection
        logger.info(f"[{self.chamber_id}] Cycle started. Target O3: {target_ppm} PPM for {duration_minutes}m.")
        
        return {
            "chamber_id": self.chamber_id,
            "status": "STARTED",
            "target_ppm": self.chamber_o3_ppm,
            "duration_minutes": duration_minutes,
            "timestamp": time.time()
        }

    def monitor_sensors(self, ambient_leak_ppm: float, catalyst_eff: float, pressure_kpa: float) -> Dict[str, Any]:
        """
        Real-time sensor telemetry check. Triggers emergency purge if ambient leakage exceeds safety limits.
        """
        self.ambient_o3_ppm = ambient_leak_ppm
        self.catalyst_efficiency = catalyst_eff
        self.chamber_pressure_kpa = pressure_kpa
        
        alerts = []
        if self.ambient_o3_ppm > self.SAFE_AMBIENT_PPM:
            alerts.append("AMBIENT_OZONE_LEAK_DETECTED")
            self.emergency_purge()
            
        if self.catalyst_efficiency < 95.0:
            alerts.append("CATALYST_DEGRADATION_WARNING")
            
        return {
            "chamber_id": self.chamber_id,
            "is_running": self.is_running,
            "current_phase": self.current_phase,
            "chamber_o3_ppm": self.chamber_o3_ppm,
            "ambient_o3_ppm": self.ambient_o3_ppm,
            "catalyst_efficiency": self.catalyst_efficiency,
            "chamber_pressure_kpa": self.chamber_pressure_kpa,
            "alerts": alerts
        }

    def emergency_purge(self) -> Dict[str, Any]:
        """
        Immediately halts generation and activates emergency vacuum-catalytic destruction exhaust.
        """
        logger.warning(f"[{self.chamber_id}] EMERGENCY PURGE ACTIVATED! Clearing chamber ozone.")
        self.current_phase = "EMERGENCY_PURGE"
        self.chamber_o3_ppm = 0.0
        self.chamber_pressure_kpa = 98.0  # Vacuum pull down
        self.is_running = False
        return {
            "chamber_id": self.chamber_id,
            "status": "PURGED",
            "ambient_ppm": self.ambient_o3_ppm,
            "timestamp": time.time()
        }

    def complete_cycle(self) -> Dict[str, Any]:
        """Completes current cycle successfully and logs metrics."""
        if not self.is_running:
            return {"status": "IDLE"}
            
        self.current_phase = "STANDBY"
        self.is_running = False
        self.chamber_o3_ppm = 0.0
        self.total_cycles_completed += 1
        logger.info(f"[{self.chamber_id}] Cycle completed successfully. Total cycles: {self.total_cycles_completed}")
        return {
            "chamber_id": self.chamber_id,
            "status": "COMPLETED",
            "total_cycles": self.total_cycles_completed,
            "timestamp": time.time()
        }

if __name__ == "__main__":
    print("Initializing Nairobi Commercial Ozone Sterilization Sentinel Test Harness...")
    sentinel = OzoneSterilizationSentinel("OZONE-NBO-01", 2500.0)
    start_res = sentinel.start_cycle(target_ppm=80.0, duration_minutes=45)
    print("Start Result:", start_res)
    
    telemetry = sentinel.monitor_sensors(ambient_leak_ppm=0.02, catalyst_eff=99.5, pressure_kpa=110.0)
    print("Normal Telemetry:", telemetry)
    
    # Simulate leak event
    leak_telemetry = sentinel.monitor_sensors(ambient_leak_ppm=0.08, catalyst_eff=98.0, pressure_kpa=105.0)
    print("Leak Event Telemetry:", leak_telemetry)
    
    print("Sentinel test execution completed successfully.")
