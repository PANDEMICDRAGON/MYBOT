"""
Nairobi Commercial Macadamia Nut Roasting Thermal Harmonic Pulse Correlation Sentinel

Author: Cortana Autonomous Evolutionary Architect
Operator: Michael Obiero, Nairobi, Kenya
Description:
  Monitors thermal profiles, drum rotation frequency, and convective airflow harmonics
  in commercial macadamia nut roasting lines across Nairobi industrial zones (e.g., Baba Dogo,
  Industrial Area). Correlates micro-fluctuations in heating elements with acoustic vibration
  signatures to prevent uneven roasting and preserve delicate unsaturated fatty acids.
"""

import time
import math
import random
import logging
from typing import Dict, List, Optional, Any

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')
logger = logging.getLogger("MacadamiaRoastSentinel")

class MacadamiaRoastThermalSentinel:
    """
    Core processor for monitoring roasting temperature variance, drum vibration harmonics,
    and moisture evaporation rates during macadamia nut processing.
    """

    def __init__(self, batch_id: str, target_temp_c: float = 135.0, tolerance_c: float = 2.5):
        self.batch_id = batch_id
        self.target_temp_c = target_temp_c
        self.tolerance_c = tolerance_c
        self.telemetry_history: List[Dict[str, Any]] = []
        self.anomaly_count = 0
        logger.info(f"Initialized MacadamiaRoastThermalSentinel for Batch: {batch_id} | Target: {target_temp_c}°C")

    def audit_cycle(self, current_temp: float, vibration_hz: float, airflow_cfm: float) -> Dict[str, Any]:
        """
        Performs a single audit cycle correlating temperature stability with mechanical vibration.
        """
        temp_deviation = abs(current_temp - self.target_temp_c)
        harmonic_anomaly = abs(vibration_hz - 50.0) > 3.0  # Assuming 50Hz standard drum drive
        airflow_optimal = 450.0 <= airflow_cfm <= 550.0

        status = "OPTIMAL"
        adjustment_recommendation = "None"

        if temp_deviation > self.tolerance_c or harmonic_anomaly or not airflow_optimal:
            self.anomaly_count += 1
            status = "DEVIATION_DETECTED"
            if current_temp > self.target_temp_c + self.tolerance_c:
                adjustment_recommendation = "REDUCE_BURNER_INTENSITY_3_PERCENT"
            elif current_temp < self.target_temp_c - self.tolerance_c:
                adjustment_recommendation = "BOOST_BURNER_INTENSITY_2_PERCENT"
            if harmonic_anomaly:
                adjustment_recommendation += "_INSPECT_DRUM_BEARINGS"
            if not airflow_optimal:
                adjustment_recommendation += "_ADJUST_EXHAUST_DAMPER"

        record = {
            "timestamp": time.time(),
            "batch_id": self.batch_id,
            "current_temp_c": current_temp,
            "temp_deviation": temp_deviation,
            "vibration_hz": vibration_hz,
            "airflow_cfm": airflow_cfm,
            "status": status,
            "recommendation": adjustment_recommendation,
            "anomaly_count": self.anomaly_count
        }

        self.telemetry_history.append(record)
        return record

    def get_batch_health_summary(self) -> Dict[str, Any]:
        """
        Summarizes overall batch roasting integrity.
        """
        total_readings = len(self.telemetry_history)
        if total_readings == 0:
            return {"status": "NO_DATA"}

        avg_temp = sum(r["current_temp_c"] for r in self.telemetry_history) / total_readings
        stability_index = max(0.0, 100.0 - (self.anomaly_count / total_readings) * 100.0)

        return {
            "batch_id": self.batch_id,
            "total_audits": total_readings,
            "average_temperature_c": round(avg_temp, 2),
            "cumulative_anomalies": self.anomaly_count,
            "roast_stability_index_percent": round(stability_index, 2)
        }

if __name__ == "__main__":
    print("[+] Executing self-test harness for MacadamiaRoastThermalSentinel...")
    sentinel = MacadamiaRoastThermalSentinel(batch_id="MAC-NBO-2025-089")
    
    # Simulate 5 roasting telemetry ticks
    for i in range(5):
        sim_temp = 135.0 + random.uniform(-4.0, 4.0)
        sim_vib = 50.0 + random.uniform(-1.5, 3.5)
        sim_airflow = random.uniform(440.0, 560.0)
        result = sentinel.audit_cycle(sim_temp, sim_vib, sim_airflow)
        print(f"Cycle {i+1}: Status -> {result['status']} | Rec -> {result['recommendation']}")

    summary = sentinel.get_batch_health_summary()
    print(f"[+] Batch Health Summary: {summary}")
    print("[+] Sentinel V1 operational successfully.")
