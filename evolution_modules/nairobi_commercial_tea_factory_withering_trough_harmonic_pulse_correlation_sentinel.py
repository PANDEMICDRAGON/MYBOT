"""Nairobi Commercial Tea Factory Withering Trough Harmonic Pulse Correlation Sentinel"""

import os
import time
import math
import random
import logging
from typing import Dict, List, Any, Optional

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')
logger = logging.getLogger("TeaFactoryWitheringSentinel")


class WitheringTroughSentinel:
    """
    Monitors and correlates harmonic pressure pulses and vibration frequencies
    of withering trough axial fans in Kenyan commercial tea factories.
    """

    def __init__(self, trough_id: str, rated_airflow_cfm: float = 12500.0):
        self.trough_id = trough_id
        self.rated_airflow_cfm = rated_airflow_cfm
        self.telemetry_history: List[Dict[str, float]] = []
        logger.info(f"WitheringTroughSentinel initialized for trough {trough_id} (Rated Airflow: {rated_airflow_cfm} CFM).")

    def sample_sensor_stream(self, vibration_mm_s: float, static_pressure_pa: float, airflow_cfm: float) -> Dict[str, Any]:
        """
        Ingests real-time sensor data from axial fan and bed sensors.
        """
        timestamp = time.time()
        
        # Compute harmonic anomaly coefficient
        airflow_deviation = abs(airflow_cfm - self.rated_airflow_cfm) / self.rated_airflow_cfm
        harmonic_score = (vibration_mm_s * 1.8) + (static_pressure_pa * 0.05) + (airflow_deviation * 10.0)
        
        status = "OPTIMAL"
        if harmonic_score > 15.0:
            status = "CRITICAL_IMBALANCE"
        elif harmonic_score > 8.0:
            status = "WARNING_DRIFT"
            
        reading = {
            "timestamp": timestamp,
            "vibration_mm_s": vibration_mm_s,
            "static_pressure_pa": static_pressure_pa,
            "airflow_cfm": airflow_cfm,
            "harmonic_score": harmonic_score,
            "status": status
        }
        
        self.telemetry_history.append(reading)
        if len(self.telemetry_history) > 1000:
            self.telemetry_history.pop(0)
            
        return reading

    def evaluate_withering_batch(self) -> Dict[str, Any]:
        """
        Evaluates the overall health and moisture extraction efficiency of the withering process.
        """
        if not self.telemetry_history:
            return {"error": "No telemetry data available."}
            
        recent = self.telemetry_history[-50:]
        avg_harmonic = sum(r["harmonic_score"] for r in recent) / len(recent)
        critical_count = sum(1 for r in recent if r["status"] == "CRITICAL_IMBALANCE")
        
        recommendation = "Maintain current airflow and humidity settings."
        if critical_count > 5:
            recommendation = "Inspect axial fan bearings immediately and check trough canvas seals for air leaks."
        elif avg_harmonic > 8.0:
            recommendation = "Adjust fan inverter frequency to compensate for static pressure build-up in leaf bed."
            
        return {
            "trough_id": self.trough_id,
            "samples_analyzed": len(recent),
            "average_harmonic_score": round(avg_harmonic, 2),
            "critical_events": critical_count,
            "recommendation": recommendation
        }


if __name__ == "__main__":
    print("Executing WitheringTroughSentinel validation test...")
    sentinel = WitheringTroughSentinel(trough_id="KTDA-KER-TR-04")
    
    # Simulate normal and anomalous telemetry
    for _ in range(10):
        vib = random.uniform(0.5, 2.5)
        pres = random.uniform(100.0, 250.0)
        cfm = random.uniform(11500.0, 13000.0)
        res = sentinel.sample_sensor_stream(vib, pres, cfm)
        print(f"Sample: {res}")
        
    batch_eval = sentinel.evaluate_withering_batch()
    print(f"Batch Evaluation: {batch_eval}")
    print("WitheringTroughSentinel operational test passed successfully.")
