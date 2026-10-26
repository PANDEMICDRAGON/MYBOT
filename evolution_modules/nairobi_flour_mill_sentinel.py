"""
Nairobi Commercial Flour Milling & Grain Dust Explosion Biosafety Sentinel
Autonomous Evolutionary Architecture Module #136
Designed for Cortana in Nairobi, Kenya

Monitors mill silo sensors, particulate density (mg/m3), static charge buildup, and
initiates pneumatic suppression and nitrogen blanketing protocols to prevent dust explosions.
"""

import time
import math
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] (FlourMillSentinel): %(message)s')
logger = logging.getLogger("NairobiFlourMillSentinel")

@dataclass
class SiloTelemetry:
    silo_id: str
    grain_type: str  # e.g., 'wheat', 'maize'
    particulate_mg_m3: float  # PM concentration
    static_charge_volts: float  # Electrostatic potential
    temperature_celsius: float
    humidity_percent: float
    pressure_differential_pa: float
    spark_detector_tripped: bool
    timestamp: float = field(default_factory=time.time)

class FlourMillBiosafetySentinel:
    def __init__(self, 
                 max_particulate_threshold: float = 60.0,
                 max_static_volts: float = 1200.0,
                 max_temp_celsius: float = 48.0,
                 min_humidity_percent: float = 30.0):
        self.max_particulate = max_particulate_threshold
        self.max_static = max_static_volts
        self.max_temp = max_temp_celsius
        self.min_humidity = min_humidity_percent
        self.incident_logs: List[Dict[str, Any]] = []
        logger.info("Initialized Nairobi Commercial Flour Milling Biosafety Sentinel.")

    def evaluate_silo_safety(self, telemetry: SiloTelemetry) -> Dict[str, Any]:
        """
        Evaluates silo telemetry against explosion risk parameters.
        Returns required mitigation actions.
        """
        risk_score = 0.0
        triggers = []

        # 1. Particulate density evaluation (Explosive lower limit check)
        if telemetry.particulate_mg_m3 >= self.max_particulate:
            part_ratio = telemetry.particulate_mg_m3 / self.max_particulate
            risk_score += min(50.0, part_ratio * 25.0)
            triggers.append(f"HIGH_PARTICULATE_DENSITY_{telemetry.particulate_mg_m3}mg/m3")

        # 2. Static electricity gradient
        if abs(telemetry.static_charge_volts) >= self.max_static:
            risk_score += 30.0
            triggers.append(f"ELEVATED_STATIC_POTENTIAL_{telemetry.static_charge_volts}V")

        # 3. Temperature & Dryness (Spontaneous heating risk)
        if telemetry.temperature_celsius >= self.max_temp or telemetry.humidity_percent <= self.min_humidity:
            risk_score += 20.0
            triggers.append(f"THERMAL_DRYNESS_ANOMALY_T:{telemetry.temperature_celsius}C_H:{telemetry.humidity_percent}%")

        # 4. Immediate physical spark detection
        if telemetry.spark_detector_tripped:
            risk_score = 100.0
            triggers.insert(0, "CRITICAL_SPARK_DETECTED_IN_CHUTE")

        risk_score = min(100.0, risk_score)
        action = self._determine_mitigation_action(risk_score, triggers)

        assessment = {
            "silo_id": telemetry.silo_id,
            "grain_type": telemetry.grain_type,
            "risk_score": risk_score,
            "triggers": triggers,
            "action_command": action,
            "timestamp": telemetry.timestamp
        }

        if risk_score > 40.0:
            self.incident_logs.append(assessment)
            logger.warning(f"SILO ALERT [{telemetry.silo_id}]: Risk Score {risk_score:.1f}% | Actions: {action}")

        return assessment

    def _determine_mitigation_action(self, risk_score: float, triggers: List[str]) -> str:
        if risk_score >= 90.0 or any("SPARK" in t for t in triggers):
            return "EMERGENCY_SHUTDOWN_AND_NITROGEN_BLANKET"
        elif risk_score >= 70.0:
            return "ACTIVATE_PNEUMATIC_MIST_SUPPRESSION_AND_HALT_ELEVATORS"
        elif risk_score >= 40.0:
            return "INCREASE_BAG_HOUSE_EXHAUST_SPEED_AND_GROUND_STATIC"
        return "NOMINAL_OPERATION"

    def get_audit_summary(self) -> Dict[str, Any]:
        return {
            "total_incidents_logged": len(self.incident_logs),
            "sentinel_status": "ACTIVE_MONITORING",
            "location": "Nairobi Industrial Area / Baba Dogo Hub"
        }

if __name__ == "__main__":
    sentinel = FlourMillBiosafetySentinel()
    sample_telemetry = SiloTelemetry(
        silo_id="SILO-NBO-04",
        grain_type="maize",
        particulate_mg_m3=75.5,
        static_charge_volts=1450.0,
        temperature_celsius=49.0,
        humidity_percent=26.5,
        pressure_differential_pa=120.0,
        spark_detector_tripped=False
    );
    result = sentinel.evaluate_silo_safety(sample_telemetry)
    print("Test Evaluation Result:", result)
    print("Audit Summary:", sentinel.get_audit_summary())
