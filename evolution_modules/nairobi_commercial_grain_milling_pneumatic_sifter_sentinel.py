"""
Nairobi Commercial Grain Milling Pneumatic Sifter Sentinel
Module for real-time monitoring and anomaly detection of pneumatic sifting units
in industrial flour and grain processing plants across Nairobi, Kenya.
"""

import time
import math
import random
import logging
from typing import Dict, Any, List, Optional

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] [PneumaticSifterSentinel]: %(message)s')
logger = logging.getLogger('PneumaticSifterSentinel')

class PneumaticSifterSentinel:
    """
    Monitors pneumatic pressure, sifter screen tension, airflow velocity,
    and particle sizing efficiency for commercial grain milling lines.
    """
    def __init__(self, sifter_id: str = "PS-NBO-01"):
        self.sifter_id = sifter_id
        self.is_active = False
        self.metrics_history: List[Dict[str, Any]] = []
        logger.info(f"PneumaticSifterSentinel initialized for unit {self.sifter_id}")

    def start_monitoring(self) -> None:
        """Activate telemetry collection and safety protocols."""
        self.is_active = True
        logger.info(f"Sentinel active on pneumatic sifter {self.sifter_id}")

    def sample_telemetry(self) -> Dict[str, float]:
        """Simulate or capture live sensor readings from the pneumatic sifter."""
        # Normal operating parameters with slight stochastic variance
        delta_p = round(random.gauss(1.25, 0.05), 3)       # kPa pressure drop across screen
        airflow_mps = round(random.gauss(18.5, 0.8), 2)    # meters per second
        vibration_hz = round(random.gauss(49.8, 0.3), 2)   # screen oscillation frequency
        reject_rate = round(random.gauss(2.1, 0.15), 2)    # percentage of oversize/reject particles
        
        telemetry = {
            "timestamp": time.time(),
            "delta_pressure_kpa": delta_p,
            "airflow_velocity_mps": airflow_mps,
            "vibration_frequency_hz": vibration_hz,
            "reject_rate_pct": reject_rate
        }
        self.metrics_history.append(telemetry)
        if len(self.metrics_history) > 1000:
            self.metrics_history.pop(0)
        return telemetry

    def evaluate_health(self, telemetry: Dict[str, float]) -> Dict[str, Any]:
        """Analyze telemetry for blinding, choking, or pressure anomalies."""
        alerts = []
        status = "OPTIMAL"

        # Check for screen blinding (high pressure drop)
        if telemetry["delta_pressure_kpa"] > 1.50:
            alerts.append("WARNING: High pressure drop detected across sifter screen (potential blinding).")
            status = "DEGRADED"
        elif telemetry["delta_pressure_kpa"] < 0.90:
            alerts.append("WARNING: Low pressure drop detected (possible screen tear or air leak).")
            status = "DEGRADED"

        # Check airflow velocity
        if telemetry["airflow_velocity_mps"] < 15.0:
            alerts.append("CRITICAL: Airflow velocity insufficient for pneumatic lift and separation.")
            status = "CRITICAL"

        # Check vibration frequency stability
        if abs(telemetry["vibration_frequency_hz"] - 50.0) > 1.5:
            alerts.append("WARNING: Sifter oscillation frequency drift detected.")
            if status != "CRITICAL":
                status = "WARNING"

        return {
            "sifter_id": self.sifter_id,
            "status": status,
            "alerts": alerts,
            "metrics": telemetry
        }

    def execute_safety_purge(self) -> bool:
        """Trigger pneumatic reverse-pulse clean cycle to clear blocked mesh screen."""
        logger.warning(f"Executing emergency pneumatic reverse-pulse purge on {self.sifter_id}...")
        time.sleep(0.1) # Simulate hardware actuator latency
        logger.info(f"Purge cycle completed successfully for {self.sifter_id}.")
        return True

if __name__ == "__main__":
    sentinel = PneumaticSifterSentinel("PS-NBO-ALPHA")
    sentinel.start_monitoring()
    sample = sentinel.sample_telemetry()
    assessment = sentinel.evaluate_health(sample)
    logger.info(f"Initial Health Assessment: {assessment}")
    if assessment["status"] != "OPTIMAL":
        sentinel.execute_safety_purge()
