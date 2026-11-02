"""
Nairobi Commercial Flour Mill Sifter Tension and Oscillation Sentinel
Author: Cortana Autonomous Evolutionary Architect
Operator: Michael Obiero, Nairobi, Kenya

Monitors industrial plansifter suspension cable tension, eccentric drive bearing vibration,
and sieve frame oscillation frequency to prevent structural resonance and blinding.
"""

import os
import sys
import time
import math
import logging
from typing import Dict, List, Any, Optional

logging.basicConfig(level=logging.INFO, format='[%(asctime)s] [%(levelname)s] [SifterSentinel]: %(message)s')
logger = logging.getLogger("SifterTensionSentinel")

class SifterTensionSentinel:
    """
    Evaluates real-time telemetry from commercial flour mill plansifter decks in Nairobi.
    """
    def __init__(self, sifter_id: str, nominal_frequency_hz: float = 4.8):
        self.sifter_id = sifter_id
        self.nominal_frequency_hz = nominal_frequency_hz
        self.tension_threshold_kn = 18.5  # Kilonewtons minimum suspension tension
        self.max_allowable_oscillation_drift = 0.35  # Hz
        self.status = "INITIALIZED"

    def analyze_deck_telemetry(self, telemetry: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyzes suspension cable load cells and accelerometer feedback.
        """
        timestamp = telemetry.get("timestamp", time.time())
        cable_tensions: List[float] = telemetry.get("cable_tensions_kn", [20.0, 19.8, 20.2, 19.9])
        measured_frequency = telemetry.get(
            "measured_frequency_hz", self.nominal_frequency_hz
        )
        bearing_temp_c = telemetry.get("eccentric_bearing_temp_c", 45.0)

        avg_tension = sum(cable_tensions) / len(cable_tensions)
        tension_imbalance = max(cable_tensions) - min(cable_tensions)
        frequency_drift = abs(measured_frequency - self.nominal_frequency_hz)

        alerts = []
        action_required = False

        if avg_tension < self.tension_threshold_kn:
            alerts.append(f"CRITICAL: Suspension cable tension avg ({avg_tension:.2f} kN) below safety limit!")
            action_required = True

        if tension_imbalance > 3.0:
            alerts.append(f"WARNING: Severe tension imbalance across suspension points: {tension_imbalance:.2f} kN")
            action_required = True

        if frequency_drift > self.max_allowable_oscillation_drift:
            alerts.append(f"CRITICAL: Sifter oscillation drift detected: {frequency_drift:.2f} Hz off nominal.")
            action_required = True

        if bearing_temp_c > 75.0:
            alerts.append(f"ALARM: Eccentric drive bearing overheating: {bearing_temp_c}°C")
            action_required = True

        self.status = "DEGRADED" if action_required else "OPTIMAL"

        diagnostic = {
            "sifter_id": self.sifter_id,
            "timestamp": timestamp,
            "avg_tension_kn": avg_tension,
            "tension_imbalance_kn": tension_imbalance,
            "frequency_drift_hz": frequency_drift,
            "status": self.status,
            "alerts": alerts,
            "action_required": action_required
        }

        if action_required:
            logger.warning(f"[{self.sifter_id}] Anomalies detected: {alerts}")
        else:
            logger.info(f"[{self.sifter_id}] Sifter operational parameters nominal. Tension: {avg_tension:.2f} kN")

        return diagnostic

if __name__ == "__main__":
    logger.info("Initializing Sifter Tension Sentinel Test Harness...")
    sentinel = SifterTensionSentinel(sifter_id="NAI_MILL_SIFTER_04")
    sample_telemetry = {
        "timestamp": time.time(),
        "cable_tensions_kn": [19.2, 18.9, 17.1, 19.0],  # One cable slipping/slack
        "measured_frequency_hz": 4.75,
        "eccentric_bearing_temp_c": 52.4
    }
    result = sentinel.analyze_deck_telemetry(sample_telemetry)
    print(result)
