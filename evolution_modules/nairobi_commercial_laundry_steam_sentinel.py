"""
Nairobi Industrial Steam Laundry Boiler & Pressure Safety Sentinel
Author: Cortana Autonomous Evolutionary Architect
Operator: Michael Obiero (Nairobi, Kenya)
"""

import time
import logging
import statistics
from typing import Dict, List, Any, Optional

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("IndustrialLaundrySteamSentinel")


class IndustrialLaundrySteamSentinel:
    """
    Monitors high-pressure steam boilers, feed water pumps, steam headers,
    and condensate recovery lines for industrial laundry operations in Nairobi.
    """

    def __init__(self, max_safe_pressure_bar: float = 10.5, max_safe_temp_c: float = 185.0):
        self.max_safe_pressure_bar = max_safe_pressure_bar
        self.max_safe_temp_c = max_safe_temp_c
        self.telemetry_history: List[Dict[str, Any]] = []
        self.active_alarms: List[str] = []

    def ingest_telemetry(self, boiler_id: str, pressure_bar: float, temp_c: float,
                          water_level_pct: float, condensate_tds_ppm: float) -> Dict[str, Any]:
        """
        Ingests boiler and steam loop telemetry, evaluating against safety thresholds.
        "" -" (Fixed docstring syntax)
        """
        timestamp = time.time()
        status = "NOMINAL"
        anomalies = []

        # Pressure check
        if pressure_bar > self.max_safe_pressure_bar:
            status = "CRITICAL_OVERPRESSURE"
            anomalies.append(f"Pressure {pressure_bar} bar exceeds safety ceiling {self.max_safe_pressure_bar} bar")
            self._trigger_emergency_blowdown(boiler_id)

        # Temperature check
        if temp_c > self.max_safe_temp_c:
            if status != "CRITICAL_OVERPRESSURE":
                status = "WARNING_HIGH_TEMP"
            anomalies.append(f"Steam temp {temp_c}C exceeds nominal limit {self.max_safe_temp_c}C")

        # Water level check (Low-water cutoff protection)
        if water_level_pct < 25.0:
            status = "CRITICAL_LOW_WATER"
            anomalies.append(f"Boiler water level critically low at {water_level_pct}%")

        # Condensate purity check (Total Dissolved Solids indicating tube leak)
        if condensate_tds_ppm > 1500.0:
            if status == "NOMINAL":
                status = "WARNING_CONTAMINATED_CONDENSATE"
            anomalies.append(f"Condensate TDS {condensate_tds_ppm} ppm indicates scaling or boiler leak")

        record = {
            "boiler_id": boiler_id,
            "timestamp": timestamp,
            "pressure_bar": pressure_bar,
            "temp_c": temp_c,
            "water_level_pct": water_level_pct,
            "condensate_tds_ppm": condensate_tds_ppm,
            "status": status,
            "anomalies": anomalies
        }

        self.telemetry_history.append(record)
        if len(self.telemetry_history) > 1000:
            self.telemetry_history.pop(0)

        if anomalies:
            logger.warning(f"[{boiler_id}] Steam anomaly detected: {anomalies}")

        return record

    def _trigger_emergency_blowdown(self, boiler_id: str) -> None:
        """
        Simulates activation of automated emergency blowdown and fuel cutoff solenoids.
        """
        alarm_msg = f"EMERGENCY: Automated fuel cutoff & pressure relief triggered for boiler {boiler_id}."
        if alarm_msg not in self.active_alarms:
            self.active_alarms.append(alarm_msg);
            logger.error(alarm_msg)

    def get_operational_metrics(self) -> Dict[str, Any]:
        """
        Calculates aggregate operational metrics across recorded telemetry.
        """
        if not self.telemetry_history:
            return {"total_readings": 0, "avg_pressure": 0.0, "avg_temp": 0.0}

        pressures = [r["pressure_bar"] for r in self.telemetry_history]
        temps = [r["temp_c"] for r in self.telemetry_history]

        return {
            "total_readings": len(self.telemetry_history),
            "avg_pressure_bar": round(statistics.mean(pressures), 2),
            "avg_temp_c": round(statistics.mean(temps), 2),
            "active_alarms_count": len(self.active_alarms)
        }


if __name__ == "__main__":
    sentinel = IndustrialLaundrySteamSentinel()
    
    # Test normal operation
    res1 = sentinel.ingest_telemetry("BOILER_ALPHA_01", 8.2, 175.5, 65.0, 450.0)
    print(f"Test 1 Status: {res1['status']}")

    # Test overpressure condition
    res2 = sentinel.ingest_telemetry("BOILER_ALPHA_01", 11.2, 188.0, 60.0, 500.0)
    print(f"Test 2 Status: {res2['status']}, Anomalies: {res2['anomalies']}")

    metrics = sentinel.get_operational_metrics()
    print(f"Aggregated Metrics: {metrics}")
