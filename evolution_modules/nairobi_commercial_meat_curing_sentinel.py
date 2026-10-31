"""
Nairobi Commercial Meat Curing & Nitrite-Humidity Sentinel
Autonomous Evolutionary Architecture Module for Cortana

Monitors and regulates commercial meat curing chambers in Nairobi, ensuring exact
relative humidity, temperature, and residual nitrite/pH equilibrium for food safety.
"""

import time
import logging
from typing import Dict, Any, List, Optional

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] [MeatCuringSentinel]: %(message)s')
logger = logging.getLogger("MeatCuringSentinel")

class MeatCuringSentinel:
    """Autonomous sentinel for commercial curing chambers and cold-cut safety."""
    
    def __init__(self, chamber_id: str, target_temp_c: float = 12.5, target_rh_pct: float = 75.0):
        self.chamber_id = chamber_id
        self.target_temp_c = target_temp_c
        self.target_rh_pct = target_rh_pct
        self.telemetry_history: List[Dict[str, Any]] = []
        self.alert_state = False

    def ingest_telemetry(self, current_temp_c: float, current_rh_pct: float, ph_level: float, nitrite_ppm: float) -> Dict[str, Any]:
        """Ingests sensor metrics from the curing chamber and evaluates anomalies."""
        timestamp = time.time()
        status = "OPTIMAL"
        actions: List[str] = []

        temp_delta = current_temp_c - self.target_temp_c
        rh_delta = current_rh_pct - self.target_rh_pct

        if abs(temp_delta) > 2.0:
            status = "WARNING"
            actions.append(f"Adjust cooling/heating coils: delta {temp_delta:+.2f}C")

        if abs(rh_delta) > 5.0:
            status = "WARNING"
            actions.append(f"Modulate humidification/dehumidification dampers: delta {rh_delta:+.2f}%")

        if ph_level < 4.8 or ph_level > 5.8:
            status = "CRITICAL"
            actions.append(f"CRITICAL pH anomaly ({phlet_val := ph_level}): risk of protein breakdown.")
            self.alert_state = True

        if nitrite_ppm < 50.0 or nitrite_ppm > 200.0:
            status = "CRITICAL"
            actions.append(f"CRITICAL Nitrite anomaly ({nitrite_ppm} ppm): outside food safety bounds.")
            self.alert_state = True

        record = {
            "timestamp": timestamp,
            "chamber_id": self.chamber_id,
            "temperature_c": current_temp_c,
            "relative_humidity_pct": current_rh_pct,
            "ph": ph_level,
            "nitrite_ppm": nitrite_ppm,
            "status": status,
            "actions_recommended": actions
        }

        self.telemetry_history.append(record)
        if len(self.telemetry_history) > 1000:
            self.telemetry_history.pop(0)

        logger.info(f"Chamber {self.chamber_id} Evaluated: Status [{status}] | Actions: {len(actions)}")
        return record

    def get_audit_summary(self) -> Dict[str, Any]:
        """Summarizes curing telemetry history."""
        total_readings = len(self.telemetry_history)
        critical_count = sum(1 for r in self.telemetry_history if r["status"] == "CRITICAL")
        return {
            "chamber_id": self.chamber_id,
            "total_readings": total_readings,
            "critical_anomalies": critical_count,
            "alert_active": self.alert_state
        }

if __name__ == "__main__":
    logger.info("Initializing Nairobi Commercial Meat Curing Sentinel Test Harness...")
    sentinel = MeatCuringSentinel(chamber_id="NBO-CURING-ALPHA-01")
    
    # Test normal ingestion
    res1 = sentinel.ingest_telemetry(current_temp_c=12.4, current_rh_pct=74.8, ph_level=5.3, nitrite_ppm=120.0)
    assert res1["status"] == "OPTIMAL"

    # Test anomaly ingestion
    res2 = sentinel.ingest_telemetry(current_temp_c=16.5, current_rh_pct=85.0, ph_level=4.5, nitrite_ppm=30.0)
    assert res2["status"] == "CRITICAL"
    
    summary = sentinel.get_audit_summary()
    logger.info(f"Test Harness Completed Successfully. Audit Summary: {summary}")
