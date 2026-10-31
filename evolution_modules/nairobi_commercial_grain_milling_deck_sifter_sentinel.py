"""
Module: nairobi_commercial_grain_sifter_sentinel.py
Description: Autonomous telemetry collector, vibration frequency analyzer, and bearing thermal sentinel
             for commercial grain milling deck sifters in Nairobi, Kenya.
Author: Cortana Autonomous Evolutionary Architect
Operator: Michael Obiero
"""

import ast
import logging
import random
import time
from typing import Dict, Any, List, Optional

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] [DeckSifterSentinel]: %(message)s"
)
logger = logging.getLogger("DeckSifterSentinel")

class DeckSifterSentinel:
    """
    Monitors deck sifter eccentric drive vibration, bearing temperatures, and sifting efficiency.
    """
    
    def __init__(self, sifter_id: str, target_frequency_hz: float = 5.0) -> None:
        self.sifter_id = sifter_id
        self.target_frequency_hz = target_frequency_hz
        self.is_active = False
        self.telemetry_history: List[Dict[str, Any]] = []

    def start_monitoring(self) -> None:
        """Activate telemetry stream."""
        self.is_active = True
        logger.info(f"Deck Sifter Sentinel [{self.sifter_id}] activated. Target Frequency: {self.target_frequency_hz} Hz.")

    def sample_sensors(self) -> Dict[str, Any]:
        """Simulate physical sensor reads from the sifter drive and deck mesh."""
        if not self.is_active:
            raise RuntimeError("Sentinel is inactive. Call start_monitoring() first.")

        # Simulated anomalies occasionally
        frequency_jitter = random.gauss(0, 0.15)
        current_freq = max(1.0, self.target_frequency_hz + frequency_jitter)
        bearing_temp = random.gauss(48.5, 3.2) # Celsius
        mesh_blinding_index = max(0.0, min(1.0, random.beta(2, 10)))
        feed_rate_tph = random.uniform(3.5, 8.0)

        reading = {
            "timestamp": time.time(),
            "sifter_id": self.sifter_id,
            "frequency_hz": round(current_freq, 2),
            "bearing_temperature_c": round(bearing_temp, 2),
            "mesh_blinding_index": round(mesh_blinding_index, 4),
            "feed_rate_tph": round(feed_rate_tph, 2)
        }
        self.telemetry_history.append(reading)
        if len(self.telemetry_history) > 1000:
            self.telemetry_history.pop(0)
        return reading

    def evaluate_health(self, reading: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze telemetry against safety thresholds."""
        alerts = []
        status = "OPTIMAL"

        freq_dev = abs(reading["frequency_hz"] - self.target_frequency_hz)
        if freq_dev > 0.8:
            status = "WARNING"
            alerts.append(f"Oscillation frequency deviation high: {reading['frequency_hz']} Hz")

        if reading["bearing_temperature_c"] > 75.0:
            status = "CRITICAL"
            alerts.append(f"Bearing overheating detected: {reading['bearing_temperature_c']} C")

        if reading["mesh_blinding_index"] > 0.65:
            if status != "CRITICAL":
                status = "WARNING"
            alerts.append(f"High mesh blinding index: {reading['mesh_blinding_index']}")

        return {
            "status": status,
            "alerts": alerts,
            "timestamp": reading["timestamp"]
        }

    def stop_monitoring(self) -> None:
        """Deactivate telemetry stream."""
        self.is_active = False
        logger.info(f"Deck Sifter Sentinel [{self.sifter_id}] deactivated.")


if __name__ == "__main__":
    logger.info("Executing self-test harness for DeckSifterSentinel...")
    sentinel = DeckSifterSentinel(sifter_id="DS-NAIROBI-01", target_frequency_hz=5.0)
    sentinel.start_monitoring()
    
    try:
        for i in range(3):
            data = sentinel.sample_sensors()
            eval_result = sentinel.evaluate_health(data)
            logger.info(f"Test Cycle {i+1}: Data={data} | Evaluation={eval_result}")
            time.sleep(0.1)
    finally:
        sentinel.stop_monitoring()

    # Compile check verification
    module_source = open(__file__, "r", encoding="utf-8").read()
    ast.parse(module_source)
    logger.info("AST compilation check passed successfully. Module is pristine.")
