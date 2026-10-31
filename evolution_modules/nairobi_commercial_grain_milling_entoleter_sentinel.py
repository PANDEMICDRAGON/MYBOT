"""
Nairobi Commercial Grain Milling Entoleter & Insect Scourer Sentinel

Monitors high-speed impact entoleters, pin mills, and grain scourers in 
commercial flour milling operations (e.g., Nairobi Industrial Area grain mills).
Ensures complete physical destruction of hidden insect pests (weevils, beetles, eggs),
detects rotor pin breakage, housing vibration anomalies, and differential pressure drops
in dust extraction systems to prevent infestation in distributed packaged flour.
"""

import math
import time
import logging
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Tuple

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("EntoleterScourerSentinel")


@dataclass
class EntoleterTelemetry:
    timestamp: float
    unit_id: str
    rotor_rpm: float            # Nominal ~2800-3500 RPM
    vibration_mm_s: float       # Nominal < 4.5 mm/s
    casing_temp_c: float        # Nominal 30 - 65 C
    diff_pressure_kpa: float    # Air extraction differential: 0.8 - 2.5 kPa
    pin_wear_metric: float      # Normalized 0.0 (new) to 1.0 (worn out)
    acoustic_db: float          # Noise level: 82 - 98 dB


@dataclass
class ScourerStatus:
    unit_id: str
    timestamp: float
    is_operational: bool
    pest_destruction_rate_pct: float
    pin_damage_detected: bool
    vibration_severity: str     # "NOMINAL", "ELEVATED", "CRITICAL"
    air_aspiration_ok: bool
    maintenance_required: bool
    action_directives: List[str]


class EntoleterScourerSentinel:
    """
    Sentinel system for monitoring entoleter impact infestation destroyers 
    and grain scouring machines in commercial milling facilities.
    """

    MIN_RPM_THRESHOLD = 2600.0      # Minimum RPM for 99.9% pest egg destruction
    MAX_VIBRATION_WARNING = 4.5    # mm/s RMS
    MAX_VIBRATION_CRITICAL = 7.1   # mm/s RMS
    MAX_CASING_TEMP = 75.0         # Celsius
    MIN_DIFF_PRESSURE = 0.5        # kPa (dust collection active)

    def __init__(self, facility_id: str = "NBI_IND_MILL_01"):
        self.facility_id = facility_id
        self.history: Dict[str, List[EntoleterTelemetry]] = {}
        logger.info("EntoleterScourerSentinel initialized for facility %s", self.facility_id)

    def calculate_pest_destruction(self, rpm: float, pin_wear: float) -> float:
        """
        Calculates mechanical impact destruction rate of insect eggs/larvae 
        based on centrifugal impact velocity (proportional to RPM) and pin integrity.
        """
        if rpm < 1000.0:
            return 0.0
        
        # Kinetic energy scales with RPM squared
        base_efficiency = min(100.0, (rpm / 3200.0) ** 2 * 99.9)
        # Pin wear reduces impact efficiency
        wear_penalty = pin_wear * 15.0
        
        destruction_rate = max(0.0, min(100.0, base_efficiency - wear_penalty))
        return round(destruction_rate, 2)

    def process_telemetry(self, telemetry: EntoleterTelemetry) -> ScourerStatus:
        """
        Analyzes entoleter and scourer telemetry to ensure biosecurity, 
        detect pin breakage/out-of-balance rotors, and enforce preventative maintenance.
        """
        if telemetry.unit_id not in self.history:
            self.history[telemetry.unit_id] = []
        self.history[telemetry.unit_id].append(telemetry)

        # Retain last 100 readings
        if len(self.history[telemetry.unit_id]) > 100:
            self.history[telemetry.unit_id].pop(0)

        directives: List[str] = []
        
        # Calculate pest impact efficacy
        pest_rate = self.calculate_pest_destruction(telemetry.rotor_rpm, telemetry.pin_wear_metric)
        if pest_rate < 98.0:
            directives.append("WARN: Pest destruction efficacy below 98%. Increase rotor speed or replace worn impact pins.")

        # Evaluate Vibration
        vib_severity = "NOMINAL"
        if telemetry.vibration_mm_s >= self.MAX_VIBRATION_CRITICAL:
            vib_severity = "CRITICAL"
            directives.append("ALERT: Critical rotor unbalance detected! Immediate emergency shutdown recommended to prevent casing rupture.")
        elif telemetry.vibration_mm_s >= self.MAX_VIBRATION_WARNING:
            vib_severity = "ELEVATED"
            directives.append("WARN: Elevated vibration detected. Inspect rotor balance and pin erosion.")

        # Detect potential broken pin (high frequency acoustic spike with high vibration)
        pin_damage = False
        if telemetry.vibration_mm_s > 5.0 and telemetry.acoustic_db > 96.0:
            pin_damage = True
            directives.append("CRITICAL: Acoustic signature matches missing/broken impact pin.")

        # Evaluate Air Aspiration
        air_ok = telemetry.diff_pressure_kpa >= self.MIN_DIFF_PRESSURE
        if not air_ok:
            directives.append("WARN: Dust extraction differential pressure low. Risk of scourer choke or husk buildup.")

        # Evaluate Temperature
        if telemetry.casing_temp_c > self.MAX_CASING_TEMP:
            directives.append("ALERT: Bearing/casing over-temperature detected. Verify lubrication.")

        maint_required = (vib_severity == "CRITICAL" or pin_damage or telemetry.pin_wear_metric > 0.85 or not air_ok)
        is_operational = (telemetry.rotor_rpm >= self.MIN_RPM_THRESHOLD) and (vib_severity != "CRITICAL")

        status = ScourerStatus(
            unit_id=telemetry.unit_id,
            timestamp=telemetry.timestamp,
            is_operational=is_operational,
            pest_destruction_rate_pct=pest_rate,
            pin_damage_detected=pin_damage,
            vibration_severity=vib_severity,
            air_aspiration_ok=air_ok,
            maintenance_required=maint_required,
            action_directives=directives
        )

        logger.info("Processed unit %s: Operational=%s, DestructRate=%.1f%%, Vib=%s",
                    telemetry.unit_id, is_operational, pest_rate, vib_severity)

        return status


def test_entoleter_sentinel():
    sentinel = EntoleterScourerSentinel("NBI_INDUSTRIAL_AREA_MILL_1")

    # Test Nominal Telemetry
    nominal_telemetry = EntoleterTelemetry(
        timestamp=time.time(),
        unit_id="ENTOLETER_LINE_A",
        rotor_rpm=3150.0,
        vibration_mm_s=2.1,
        casing_temp_c=42.0,
        diff_pressure_kpa=1.4,
        pin_wear_metric=0.1,
        acoustic_db=85.5
    )
    res_nominal = sentinel.process_telemetry(nominal_telemetry)
    assert res_nominal.is_operational is True
    assert res_nominal.pest_destruction_rate_pct > 98.0
    assert res_nominal.vibration_severity == "NOMINAL"
    assert len(res_nominal.action_directives) == 0

    # Test Fault Telemetry (Broken Pin & Low Pressure)
    fault_telemetry = EntoleterTelemetry(
        timestamp=time.time(),
        unit_id="ENTOLETER_LINE_A",
        rotor_rpm=2400.0,
        vibration_mm_s=7.8,
        casing_temp_c=78.0,
        diff_pressure_kpa=0.3,
        pin_wear_metric=0.9,
        acoustic_db=98.5
    )
    res_fault = sentinel.process_telemetry(fault_telemetry)
    assert res_fault.is_operational is False
    assert res_fault.pin_damage_detected is True
    assert res_fault.vibration_severity == "CRITICAL"
    assert res_fault.maintenance_required is True
    assert len(res_fault.action_directives) >= 3

    print("EntoleterScourerSentinel self-test PASSED successfully.")


if __name__ == "__main__":
    test_entoleter_sentinel()
