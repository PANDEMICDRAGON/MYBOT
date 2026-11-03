import time
import math
import random
import logging
from typing import Dict, List, Any, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("InductionCooktopSentinel")

class InductionCooktopSentinel:
    """
    Monitors industrial induction cooktop current draws, voltage phases, high-frequency
    inverter switching ripples, and thermal telemetry. Correlates harmonic anomalies
    to prevent IGBT bridge failure and optimize power factor under fluctuating Nairobi grid conditions.
    """
    def __init__(self, unit_id: str, rated_power_kw: float = 15.0):
        self.unit_id = unit_id
        self.rated_power_kw = rated_power_kw
        self.telemetry_history: List[Dict[str, Any]] = []
        self.active_protection_tripped = False

    def ingest_telemetry(self, voltage: float, current: float, frequency_hz: float,
                         igbt_temp_c: float, thd_percent: float) -> Dict[str, Any]:
        """
        Ingests real-time power telemetry and computes harmonic health and thermal risk.
        """
        timestamp = time.time()
        apparent_power = (voltage * current) / 1000.0 # kVA
        
        # Harmonic anomaly factor based on Total Harmonic Distortion (THD) & temperature
        thermal_stress = max(0.0, (igbt_temp_c - 65.0) / 35.0)
        harmonic_risk = thd_percent / 15.0
        composite_risk_score = min(1.0, (thermal_stress * 0.6) + (harmonic_risk * 0.4))

        status = "NOMINAL"
        if composite_risk_score > 0.85 or igbt_temp_c > 92.0:
            status = "CRITICAL_THERMAL_OVERLOAD"
            self.active_protection_tripped = True
        elif composite_risk_score > 0.6 or thd_percent > 12.0:
            status = "WARNING_HARMONIC_DEGRADATION"

        record = {
            "timestamp": timestamp,
            "unit_id": self.unit_id,
            "voltage": voltage,
            "current": current,
            "apparent_power_kva": apparent_power,
            "igbt_temp_c": igbt_temp_c,
            "thd_percent": thd_percent,
            "composite_risk_score": composite_risk_score,
            "status": status
        }

        self.telemetry_history.append(record)
        if len(self.telemetry_history) > 1000:
            self.telemetry_history.pop(0)

        return record

    def calculate_phase_balance_index(self, phase_currents: List[float]) -> float:
        """
        Evaluates 3-phase current imbalance common in commercial kitchen arrays.
        """
        if not phase_currents or len(phase_currents) != 3:
            return 0.0
        mean_current = sum(phase_currents) / 3.0
        if mean_current == 0.0:
            return 0.0
        max_deviation = max(abs(c - mean_current) for c in phase_currents)
        return float(max_deviation / mean_current)

    def generate_mitigation_directive(self) -> str:
        if self.active_protection_tripped:
            return "EMERGENCY_THROTTLE: Reduce induction inverter PWM duty cycle by 50% and engage auxiliary cooling fans."
        return "SYSTEM_STABLE: Power phase harmonics within acceptable Nairobi grid operational bounds."

if __name__ == "__main__":
    sentinel = InductionCooktopSentinel(unit_id="NAI_KITCHEN_IND_01", rated_power_kw=20.0)
    
    # Simulate normal and stress telemetry ingestion
    test_readings = [
        (240.0, 45.2, 50.0, 58.5, 3.2),
        (238.5, 52.1, 50.1, 72.0, 7.8),
        (230.0, 78.4, 49.8, 94.2, 14.5)
    ]
    
    for v, c, f, temp, thd in test_readings:
        res = sentinel.ingest_telemetry(v, c, f, temp, thd)
        logger.info(f"Telemetry Evaluated: {res['status']} | Risk: {res['composite_risk_score']:.2f}")
    
    imbalance = sentinel.calculate_phase_balance_index([45.2, 48.0, 42.1])
    logger.info(f"Phase Imbalance Index: {imbalance:.4f}")
    logger.info(sentinel.generate_mitigation_directive())
