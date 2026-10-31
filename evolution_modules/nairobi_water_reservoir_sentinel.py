"""Nairobi Commercial Rooftop & Underground Water Reservoir Hydrodynamic Telemetry Sentinel."""

import time
import math
import logging
from typing import Dict, Any, List, Optional

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')
logger = logging.getLogger("WaterReservoirSentinel")

class WaterReservoirSentinel:
    """Monitors dual-reservoir water levels, flow dynamics, and pump health for Nairobi commercial buildings."""

    def __init__(self, reservoir_capacity_liters: float = 20000.0, critical_threshold_pct: float = 15.0):
        self.capacity = reservoir_capacity_liters
        self.critical_threshold = critical_threshold_pct
        self.telemetry_history: List[Dict[str, Any]] = []
        self.pump_state: bool = False  # False = Off, True = Running
        self.fault_flag: bool = False

    def ingest_telemetry(self, current_level_liters: float, inflow_rate_lpm: float, outflow_rate_lpm: float, line_pressure_bar: float) -> Dict[str, Any]:
        """Ingests sensor metrics, evaluates hydrodynamic stability, and triggers safeguards."""
        timestamp = time.time()
        level_pct = (current_level_liters / self.capacity) * 100.0
        net_flow = inflow_rate_lpm - outflow_rate_lpm

        # Anomaly Detection Flags
        dry_run_risk = (current_level_liters <= (self.capacity * (self.critical_threshold / 100.0))) and self.pump_state
        pressure_anomaly = line_pressure_bar < 1.0 or line_pressure_bar > 6.0
        rapid_drainage = outflow_rate_lpm > (inflow_rate_lpm * 3.0) and level_pct < 30.0

        action_taken = "NORMAL"
        if dry_run_risk:
            self.pump_state = False
            self.fault_flag = True
            action_taken = "EMERGENCY_SHUTDOWN: DRY RUN PREVENTED"
            logger.warning(f"[CRITICAL] Water reservoir critically low ({level_pct:.1f}%). Pump forcefully disengaged!")
        elif pressure_anomaly:
            action_taken = "WARNING: ABNORMAL LINE PRESSURE"
            logger.warning(f"[WARNING] Nairobi municipal line pressure anomaly detected: {line_pressure_bar} bar")
        elif rapid_drainage:
            action_taken = "WARNING: RAPID DRAINAGE / POSSIBLE LEAK"
            logger.warning(f"[WARNING] Rapid reservoir depletion detected. Outflow: {outflow_rate_lpm} L/min")

        telemetry_packet = {
            "timestamp": timestamp,
            "level_liters": current_level_liters,
            "level_pct": round(level_pct, 2),
            "inflow_lpm": inflow_rate_lpm,
            "outflow_lpm": outflow_rate_lpm,
            "net_flow_lpm": net_flow,
            "pressure_bar": line_pressure_bar,
            "pump_active": self.pump_state,
            "action": action_taken
        }

        self.telemetry_history.append(telemetry_packet)
        if len(self.telemetry_history) > 1000:
            self.telemetry_history.pop(0)

        return telemetry_packet

    def toggle_pump(self, force_state: Optional[bool] = None) -> bool:
        """Manages pump operational state with safety overrides."""
        if self.fault_flag and force_state is True:
            logger.error("[BLOCKED] Cannot start pump while unresolved fault flag persists.")
            return self.pump_state
        
        if force_state is not None:
            self.pump_state = force_state
            if force_state:
                self.fault_flag = False
        else:
            self.pump_state = not self.pump_state

        logger.info(f"Pump state toggled to: {'RUNNING' if self.pump_state else 'STOPPED'}")
        return self.pump_state

    def get_diagnostics(self) -> Dict[str, Any]:
        """Returns summary telemetry diagnostics."""
        if not self.telemetry_history:
            return {"status": "NO_DATA"}
        
        latest = self.telemetry_history[-1]
        return {
            "capacity_liters": self.capacity,
            "current_level_pct": latest["level_pct"],
            "pump_status": latest["pump_active"],
            "fault_active": self.fault_flag,
            "total_telemetry_records": len(self.telemetry_history)
        }

if __name__ == "__main__":
    print("Initializing Nairobi Water Reservoir Telemetry Sentinel...")
    sentinel = WaterReservoirSentinel(reservoir_capacity_liters=15000.0, critical_threshold_pct=20.0)
    
    # Simulate normal inflow/outflow
    pkt1 = sentinel.ingest_telemetry(12000.0, 50.0, 30.0, 2.5)
    print(f"Telemetry 1: {pkt1}")
    
    # Simulate pump activation
    sentinel.toggle_pump(True)
    
    # Simulate critical dry run event
    pkt2 = sentinel.ingest_telemetry(2500.0, 10.0, 80.0, 1.2)
    print(f"Telemetry 2: {pkt2}")
    
    print("Diagnostics:", sentinel.get_diagnostics())
    print("Water Reservoir Sentinel Module executed successfully.")
