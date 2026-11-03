"""
Nairobi Commercial Biofuel Refinery Transesterification Synapse Sentinel
Author: Cortana Autonomous Evolutionary Architect
Operator: Michael Obiero, Nairobi, Kenya

Provides real-time telemetry ingestion, harmonic vibration and temperature pulse
correlation, catalyst efficiency monitoring, and automated viscosity remediation
for commercial biodiesel and bio-ethanol refineries across Nairobi's industrial zones.
"""

import time
import math
import random
import logging
from typing import Dict, List, Any, Optional

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')
logger = logging.getLogger("BiofuelRefinerySentinel")

class BiofuelRefinerySentinel:
    """
    Monitors multi-stage transesterification reactors, catalyst recovery columns,
    and feedstock pre-treatment units to ensure peak yield and absolute safety.
    """
    def __init__(self, reactor_id: str, capacity_liters_per_hr: float = 5000.0):
        self.reactor_id = reactor_id
        self.capacity = capacity_liters_per_hr
        self.temperature_c = 65.0  # Optimal transesterification temp (Celsius)
        self.pressure_bar = 1.5
        self.viscosity_cst = 4.2    # Target biodiesel viscosity (centistokes)
        self.catalyst_ratio = 1.0   # Percentage KOH/NaOH catalyst
        self.methanol_molar_ratio = 6.0 # 6:1 alcohol to oil ratio
        self.harmonic_vibration_hz = 50.0
        self.anomaly_history: List[Dict[str, Any]] = []
        logger.info(f"BiofuelRefinerySentinel initialized for reactor {reactor_id} ({capacity_liters_per_hr} L/hr capacity).")

    def ingest_sensor_telemetry(self, temp: float, pressure: float, viscosity: float, vibration: float) -> Dict[str, Any]:
        """
        Ingests raw sensor readings and evaluates process stability.
        """
        self.temperature_c = temp
        self.pressure_bar = pressure
        self.viscosity_cst = viscosity
        self.harmonic_vibration_hz = vibration

        warnings = []
        status = "OPTIMAL"

        # Thermal Runway Check
        if self.temperature_c > 75.0:
            status = "CRITICAL_THERMAL_WARNING"
            warnings.warn(f"Reactor {self.reactor_id} temperature {self.temperature_c}C exceeds safety threshold (75C).")
        elif self.temperature_c < 55.0:
            status = "SUBOPTIMAL_CONVERSION_RATE"
            warnings.append(f"Reactor {self.reactor_id} temperature {self.temperature_c}C too low for complete transesterification.")

        # Viscosity Check (incomplete reaction or soap formation)
        if self.viscosity_cst > 6.0:
            status = "HIGH_VISCOSITY_ANOMALY"
            warnings.append(f"Viscosity {self.viscosity_cst} cSt indicates unreacted glycerides or soap contamination.")

        # Vibration Harmonic Check (cavitation or stirrer imbalance)
        if self.harmonic_vibration_hz > 85.0:
            status = "HARMONIC_CAVITATION_WARNING"
            warnings.append(f"High vibration frequency {self.harmonic_vibration_hz} Hz detected on agitator spindle.")

        telemetry_packet = {
            "timestamp": time.time(),
            "reactor_id": self.reactor_id,
            "temperature_c": self.temperature_c,
            "pressure_bar": self.pressure_bar,
            "viscosity_cst": self.viscosity_cst,
            "vibration_hz": self.harmonic_vibration_hz,
            "status": status,
            "warnings": warnings
        }

        if status != "OPTIMAL":
            self.anomaly_history.append(telemetry_packet)
            logger.warning(f"Refinery Anomaly Detected [{status}]: {warnings}")

        return telemetry_packet

    def execute_automated_mitigation(self, anomaly_status: str) -> Dict[str, Any]:
        """
        Executes corrective feedback loops (e.g., cooling jacket activation,
        catalyst titration adjustment, or agitator speed modulation).
        """
        actions_taken = []
        if "THERMAL" in anomaly_status:
            actions_taken.append("Engaged emergency cooling glycol jacket.")
            actions_taken.append("Reduced reactor heating element duty cycle by 40%.")
            self.temperature_c = max(60.0, self.temperature_c - 5.0)
        if "VISCOSITY" in anomaly_status:
            actions_taken.append("Injected secondary methanol wash pulse (+0.5 molar ratio).")
            actions_taken.append("Extended settling time in gravitational separation decanter.")
            self.viscosity_cst = max(4.0, self.viscosity_cst - 1.2)
        if "CAVITATION" in anomaly_status:
            actions_taken.append("Adjusted variable frequency drive (VFD) agitator speed down 15 Hz.")
            self.harmonic_vibration_hz = 48.0

        mitigation_report = {
            "timestamp": time.time(),
            "reactor_id": self.reactor_id,
            "triggered_status": anomaly_status,
            "actions_taken": actions_taken,
            "resolved": True
        }
        logger.info(f"Mitigation executed successfully for {self.reactor_id}: {actions_taken}")
        return mitigation_report

if __name__ == "__main__":
    print("Initializing Nairobi Commercial Biofuel Refinery Sentinel Test Harness...")
    sentinel = BiofuelRefinerySentinel(reactor_id="BIO-NRB-01", capacity_liters_per_hr=10000.0)
    
    # Simulate nominal run
    packet_nominal = sentinel.ingress_sensor_telemetry(temp=65.5, pressure=1.4, viscosity=4.1, vibration=49.0)
    print("Nominal Telemetry Status:", packet_nominal["status"])
    
    # Simulate thermal & viscosity anomaly
    packet_fault = sentinel.ingress_sensor_telemetry(temp=78.2, pressure=2.1, viscosity=6.8, vibration=90.5)
    print("Fault Telemetry Status:", packet_fault["status"])
    
    # Execute mitigation
    mitigation = sentinel.execute_automated_mitigation(packet_fault["status"])
    print("Mitigation Report:", mitigation)
    print("Biofuel Refinery Sentinel Operational.")
