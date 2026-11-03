import time
import logging
import statistics
from typing import Dict, List, Any, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("GuillotineHydraulicSentinel")

class GuillotineHydraulicSentinel:
    """
    Monitors hydraulic pressure impulses and acoustic resonance patterns during
    commercial paper guillotine clamp and cutting cycles in Nairobi stationery plants.
    """
    def __init__(self, machine_id: str, pressure_threshold_bar: float = 210.0):
        self.machine_id = machine_id
        self.pressure_threshold_bar = pressure_threshold_bar
        self.telemetry_history: List[Dict[str, Any]] = []
        self.anomaly_count = 0

    def ingest_cycle_metrics(self, cycle_id: str, peak_pressure_bar: float, vibration_hz: float, valve_response_ms: float) -> Dict[str, Any]:
        """
        Ingests metrics for a single guillotine cutting stroke and evaluates mechanical health.
        """
        timestamp = time.time()
        is_anomalous = False
        warnings = []

        if peak_pressure_bar > self.pressure_threshold_bar:
            is_anomalous = True
            warnings.append(f"Over-pressure detected: {peak_pressure_bar} bar (Limit: {self.pressure_threshold_bar})")

        if valve_response_ms > 120.0:
            is_anomalous = True
            warnings.append(f"Solenoid valve lag detected: {valve_response_ms} ms")

        if vibration_hz < 40.0 or vibration_hz > 95.0:
            is_anomalous = True
            warnings.append(f"Abnormal harmonic vibration frequency: {vibration_hz} Hz")

        if is_anomalous:
            self.anomaly_count += 1
            logger.warning(f"[{self.machine_id}] ANOMALOUS CYCLE {cycle_id}: {warnings}")
        else:
            logger.info(f"[{self.machine_id}] Cycle {cycle_id} nominal. Pressure: {peak_pressure_bar}bar, Vib: {vibration_hz}Hz")

        record = {
            "timestamp": timestamp,
            "cycle_id": cycle_id,
            "peak_pressure_bar": peak_pressure_bar,
            "vibration_hz": vibration_hz,
            "valve_response_ms": valve_response_ms,
            "is_anomalous": is_anomalous,
            "warnings": warnings
        }
        self.telemetry_history.append(record)
        return record

    def generate_health_audit(self) -> Dict[str, Any]:
        """
        Generates an aggregate diagnostic report for maintenance dispatch.
        """
        if not self.telemetry_history:
            return {"status": "no_data"}

        pressures = [r["peak_pressure_bar"] for r in self.telemetry_history]
        vibrations = [r["vibration_hz"] for r in self.telemetry_history]
        valve_latencies = [r["valve_response_ms"] for r in self.telemetry_history]

        return {
            "machine_id": self.machine_id,
            "total_cycles_monitored": len(self.telemetry_history),
            "anomaly_count": self.anomaly_count,
            "avg_pressure_bar": statistics.mean(pressures),
            "max_pressure_bar": max(pressures),
            "avg_vibration_hz": statistics.mean(vibrations),
            "avg_valve_response_ms": statistics.mean(valve_latencies),
            "system_integrity": "DEGRADED" if self.anomaly_count > 2 else "OPTIMAL"
        }

if __name__ == "__main__":
    sentinel = GuillotineHydraulicSentinel(machine_id="NBI-PRINT-GUILLOTINE-04")
    sentinel.ingest_cycle_metrics("CYC-1001", 195.5, 65.2, 85.0)
    sentinel.ingest_cycle_metrics("CYC-1002", 218.0, 32.1, 135.5)
    sentinel.ingest_cycle_metrics("CYC-1003", 198.0, 64.8, 88.2)
    audit = sentinel.generate_health_audit()
    print("Hydraulic Audit Result:", audit)
