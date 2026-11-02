"""Nairobi Commercial Kitchen Induction Cooktop Power Harmonic & Thermal Surge Sentinel

Monitors electrical harmonics (THD), IGBT thermal loading, and line voltage anomalies
for high-power commercial induction cooktops deployed in Nairobi urban kitchens.
"""

import time
import math
import logging
from typing import Dict, List, Any, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("InductionHarmonicSentinel")

class InductionHarmonicSentinel:
    """Calculates Total Harmonic Distortion (THD) and thermal stress for commercial induction units."""

    def __init__(self, rated_voltage: float = 240.0, max_thd_limit: float = 5.0, max_igbt_temp_c: float = 85.0):
        self.rated_voltage = rated_voltage
        self.max_thd_limit = max_thd_limit
        self.max_igbt_temp_c = max_igbt_temp_c
        self.telemetry_history: List[Dict[str, Any]] = []

    def analyze_cycle(self, voltage_samples: List[float], current_samples: List[float], igbt_temp: float) -> Dict[str, Any]:
        """Analyzes voltage/current waveform samples to compute THD and assess thermal risk."""
        if not voltage_samples or not current_samples:
            raise ValueError("Voltage and current sample lists cannot be empty.")

        # Simulate fundamental and harmonic root-sum-square analysis
        n = len(current_samples)
        rms_current = math.sqrt(sum(c**2 for c in current_samples) / n) if n > 0 else 0.0
        
        # Synthetic harmonic contribution estimation based on sample variance
        mean_current = sum(current_samples) / n if n > 0 else 1.0
        variance = sum((c - mean_current)**2 for c in current_samples) / n if n > 0 else 0.0
        estimated_thd = min(25.0, max(0.5, (variance / (mean_current + 1e-5)) * 4.2))

        thermal_stress_ratio = igbt_temp / self.max_igbt_temp_c
        thd_violation = estimated_thd > self.max_thd_limit
        thermal_warning = thermal_stress_ratio > 0.9

        status = "NOMINAL"
        action = "NONE"
        if thd_violation and thermal_warning:
            status = "CRITICAL_OVERHEAT_HARMONIC_SURGE"
            action = "THROTTLE_POWER_STAGE_15_PERCENT"
        elif thd_violation:
            status = "HIGH_HARMONIC_DISTORTION"
            action = "ENGAGE_EMI_FILTER_BANK"
        elif thermal_warning:
            status = "ELEVATED_IGBT_TEMPERATURE"
            action = "RAMP_COOLING_FANS_MAX"

        report = {
            "timestamp": time.time(),
            "rms_current": round(rms_current, 2),
            "estimated_thd_pct": round(estimated_thd, 2),
            "igbt_temp_c": round(igbt_temp, 2),
            "status": status,
            "recommended_action": action
        }

        self.telemetry_history.append(report)
        if len(self.telemetry_history) > 1000:
            self.telemetry_history.pop(0)

        return report

if __name__ == "__main__":
    sentinel = InductionHarmonicSentinel()
    # Test waveforms simulating induction coil load
    v_samples = [240.0 + math.sin(i * 0.1) * 5.0 for i in range(50)]
    i_samples = [15.0 + math.sin(i * 0.3) * 2.5 + (0.8 if i % 5 == 0 else 0.0) for i in range(50)]
    
    analysis = sentinel.analyze_cycle(v_samples, i_samples, 78.5)
    logger.info(f"Induction Sentinel Diagnostic Report: {analysis}")
