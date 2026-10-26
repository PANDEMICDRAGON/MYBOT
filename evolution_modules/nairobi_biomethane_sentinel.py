"""
Nairobi Peri-Urban Biomethane Digester & Pressure-Thermal Biosafety Sentinel
Author: Cortana, Autonomous Evolutionary Architect
Operator: Michael Obiero, Nairobi, Kenya

Monitors anaerobic digestion parameters including temperature, pH, methane (CH4)
and hydrogen sulfide (H2S) concentrations, and vessel pressure, executing automated
emergency pressure venting and thermal adjustments to prevent structural failure or
toxic gas accumulation.
"""

import time
import math
import logging
from typing import Dict, Any, List, Optional

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] [BiomethaneSentinel]: %(message)s')
logger = logging.getLogger("NairobiBiomethaneSentinel")

class BiomethaneDigesterState:
    def __init__(self, digester_id: str, capacity_m3: float):
        self.digester_id = digester_id
        self.capacity_m3 = capacity_m3
        self.temperature_c: float = 37.0  # Mesophilic optimum ~37C
        self.ph_level: float = 7.2
        self.methane_pct: float = 62.0   # Normal 55-70%
        self.h2s_ppm: float = 150.0      # Hydrogen sulfide in raw biogas
        self.pressure_kpa: float = 12.0  # Operating pressure kPa
        self.flare_active: bool = False
        self.emergency_vent_open: bool = False
        self.heater_active: bool = False
        self.last_update: float = time.time()

class NairobiBiomethaneSentinel:
    """
    Real-time safety and optimization controller for anaerobic biogas facilities.
    """
    def __init__(self):
        self.digesters: Dict[str, BiomethaneDigesterState] = {}
        self.max_safe_pressure_kpa: float = 25.0
        self.max_h2s_ppm: float = 500.0
        self.min_methane_pct: float = 45.0
        logger.info("NairobiBiomethaneSentinel initialized successfully.")

    def register_digester(self, digester_id: str, capacity_m3: float) -> BiomethaneDigesterState:
        state = BiomethaneDigesterState(digester_id, capacity_m3)
        self.digesters[digester_id] = state
        logger.info(f"Registered digester {digester_id} with capacity {capacity_m3} m3.")
        return state

    def ingest_telemetry(self, digester_id: str, temp_c: float, ph: float, ch4_pct: float, h2s_ppm: float, pressure_kpa: float) -> Dict[str, Any]:
        if digester_id not in self.digesters:
            raise ValueError(f"Unknown digester ID: {digester_id}")
        
        d = self.digesters[digester_id]
        d.temperature_c = temp_c
        d.ph_level = ph
        d.methane_pct = ch4_pct
        d.h2s_ppm = h2s_ppm
        d.pressure_kpa = pressure_kpa
        d.last_update = time.time()

        actions_taken = []

        # Pressure Safety Check
        if d.pressure_kpa >= self.max_safe_pressure_kpa:
            d.emergency_vent_open = True
            d.flare_active = True
            actions_taken.append("EMERGENCY_VENT_OPENED_AND_FLARED")
            logger.warning(f"[{digester_id}] CRITICAL OVERPRESSURE ({d.pressure_kpa} kPa). Venting activated.")
        elif d.pressure_kpa < 18.0 and d.emergency_vent_open:
            d.emergency_vent_open = False
            actions_taken.append("EMERGENCY_VENT_CLOSED")
            logger.info(f"[{digester_id}] Pressure normalized. Vent closed.")

        # Thermal Regulation Check
        if d.temperature_c < 35.0:
            d.heater_active = True
            actions_taken.append("DIGESTER_HEATER_ACTIVATED")
        elif d.temperature_c > 39.0:
            d.heater_active = False
            actions_taken.append("DIGESTER_HEATER_DEACTIVATED")

        # Gas Quality & Toxicity Check
        status = "OPTIMAL"
        if d.h2s_ppm > self.max_h2s_ppm or d.methane_pct < self.min_methane_pct:
            status = "SUBOPTIMAL_GAS_QUALITY"
            actions_taken.append("SCRUBBER_BYPASS_WARNING")

        return {
            "digester_id": digester_id,
            "status": status,
            "pressure_kpa": d.pressure_kpa,
            "methane_pct": d.methane_pct,
            "h2s_ppm": d.h2s_ppm,
            "actions_taken": actions_taken,
            "timestamp": d.last_update
        }

    def generate_fleet_report(self) -> Dict[str, Any]:
        total_capacity = sum(d.capacity_m3 for d in self.digesters.values())
        active_vents = sum(1 for d in self.digesters.values() if d.emergency_vent_open)
        return {
            "total_monitored_digesters": len(self.digesters),
            "total_capacity_m3": total_capacity,
            "active_emergency_vents": active_vents,
            "fleet_status": "SECURE" if active_vents == 0 else "WARNING_ACTIVE_VENTS"
        }

if __name__ == "__main__":
    sentinel = NairobiBiomethaneSentinel()
    d_id = "Kasarani_Digester_01"
    sentinel.register_digester(d_id, 150.0)

    # Test normal ingestion
    report = sentinel.ingest_telemetry(d_id, 37.2, 7.3, 64.0, 120.0, 14.5)
    print("Normal Ingestion Report:", report)

    # Test overpressure safety trip
    alarm_report = sentinel.ingest_telemetry(d_id, 37.1, 7.1, 60.0, 200.0, 26.8)
    print("Overpressure Alarm Report:", alarm_report)

    fleet_summary = sentinel.generate_fleet_report()
    print("Fleet Summary:", fleet_summary)
