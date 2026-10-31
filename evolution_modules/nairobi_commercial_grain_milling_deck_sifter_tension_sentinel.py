"""
Nairobi Commercial Grain Milling Deck Sifter Tension Sentinel
Author: Cortana Autonomous Evolutionary Architect
Operator: Michael Obiero, Nairobi, Kenya

Monitors the mechanical tension, drive eccentric bearing vibration, and sifter deck
acceleration profiles to ensure structural integrity and prevent unscheduled downtime.
"""

import time
import random
import logging
from typing import Dict, Any, List

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')
logger = logging.getLogger("DeckSifterTensionSentinel")

class DeckSifterTensionSentinel:
    """
    Real-time telemetry and anomaly detection engine for commercial grain mill deck sifters.
    """
    def __init__(self, sifter_id: str, nominal_frequency_hz: float = 5.5):
        self.sifter_id = sifter_id
        self.nominal_frequency_hz = nominal_frequency_hz
        self.tension_psi_baseline = 120.0
        self.vibration_g_baseline = 0.85
        self.anomaly_count = 0
        logger.info(f"Initialized DeckSifterTensionSentinel for sifter [{self.sifter_id}] at {nominal_frequency_hz}Hz baseline.")

    def sample_telemetry(self) -> Dict[str, Any]:
        """Simulates reading industrial strain gauges and accelerometer arrays."""
        # Introduce minor stochastic drift with occasional fault spikes
        tension_drift = random.gauss(0.0, 1.5)
        vibration_noise = random.gauss(0.0, 0.05)
        
        # Rare artificial tension relaxation event or eccentric bearing wobble
        if random.random() < 0.05:
            tension_drift -= random.uniform(5.0, 15.0)
            vibration_noise += random.uniform(0.3, 0.8)
            
        current_tension = self.tension_psi_baseline + tension_drift
        current_vibration = self.vibration_g_baseline + vibration_noise
        current_frequency = self.nominal_frequency_hz + random.gauss(0.0, 0.02)
        
        return {
            "timestamp": time.time(),
            "sifter_id": self.sifter_id,
            "tension_psi": round(current_tension, 2),
            "vibration_g": round(current_vibration, 3),
            "frequency_hz": round(current_frequency, 2)
        }

    def analyze_metrics(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyzes telemetry against tolerance thresholds and computes health scores."""
        tension = data["tension_psi"]
        vibration = data["vibration_g"]
        
        tension_deviation = abs(tension - self.tension_psi_baseline)
        vibration_deviation = vibration - self.vibration_g_baseline
        
        status = "OPTIMAL"
        actions: List[str] = []

        if tension_deviation > 10.0 or vibration_deviation > 0.4:
            status = "WARNING"
            actions.append("SCHEDULE_INSPECTION")
            self.anomaly_count += 1

        if tension_deviation > 20.0 or vibration_deviation > 0.7:
            status = "CRITICAL"
            actions.append("EMERGENCY_SHUTDOWN_RECOMMENDED")
            self.anomaly_count += 2

        return {
            "sifter_id": self.sifter_id,
            "status": status,
            "tension_deviation_psi": round(tension_deviation, 2),
            "vibration_excess_g": round(vibration_deviation, 3),
            "anomaly_accumulated_score": self.anomaly_count,
            "recommended_actions": actions
        }

    def execute_guard_cycle(self) -> Dict[str, Any]:
        """Executes a single sensing, evaluation, and mitigation cycle."""
        telemetry = self.sample_telemetry()
        assessment = self.analyze_metrics(telemetry)
        
        if assessment["status"] != "OPTIMAL":
            logger.warning(f"Sifter Alert [{self.sifter_id}]: {assessment['status']} - Actions: {assessment['recommended_actions']}")
        else:
            logger.info(f"Sifter Status [{self.sifter_id}]: {assessment['status']} (Tension: {telemetry['tension_psi']} PSI)")
            
        return {
            "telemetry": telemetry,
            "assessment": assessment
        }

if __name__ == "__main__":
    logger.info("Executing standalone validation of DeckSifterTensionSentinel...")
    sentinel = DeckSifterTensionSentinel(sifter_id="DS-NAIROBI-MILL-01")
    for cycle in range(3):
        result = sentinel.execute_guard_cycle()
        time.sleep(0.5)
    logger.info("DeckSifterTensionSentinel verification complete.")
