import time
import logging
import statistics
from typing import Dict, List, Any, Optional

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')
logger = logging.getLogger("SolarCanopySentinel")

class SolarCanopyHarmonicSentinel:
    """
    Monitors commercial solar canopy micro-inverter harmonic frequencies, thermal stress,
    and string current imbalances across Nairobi microgrid installations.
    """
    def __init__(self, canopy_id: str, rated_capacity_kw: float):
        self.canopy_id = canopy_id
        self.rated_capacity_kw = rated_capacity_kw
        self.telemetry_history: List[Dict[str, Any]] = []
        self.anomaly_count = 0
        logger.info(f"Initialized SolarCanopyHarmonicSentinel for {self.canopy_id} ({self.rated_capacity_kw} kW)")

    def ingest_telemetry(self, string_currents: List[float], voltages: List[float], harmonic_thd: float, temperature_c: float) -> Dict[str, Any]:
        timestamp = time.time()
        mean_current = statistics.mean(string_currents) if string_currents else 0.0
        current_imbalance = max([abs(c - mean_current) for c in string_currents]) if string_currents else 0.0
        avg_voltage = statistics.mean(voltages) if voltages else 0.0
        
        # Harmonic resonance and degradation heuristics
        status = "OPTIMAL"
        remediation = "None"

        if harmonic_thd > 5.0:
            status = "WARNING_HIGH_THD"
            remediation = "Initiate micro-inverter phase realignment and filter capacitor inspection."
            self.anomaly_count += 1

        if current_imbalance > (mean_current * 0.15):
            status = "WARNING_STRING_MISMATCH"
            remediation = "Inspect string connectors for dust deposition or partial shading (Nairobi dust profile)."
            self.anomaly_count += 1

        if temperature_c > 65.0:
            status = "THERMAL_THROTTLE"
            remediation = "Engage canopy passive cooling airflow or adjust MPPT sweep frequency."
            self.anomaly_count += 1

        record = {
            "timestamp": timestamp,
            "canopy_id": self.canopy_id,
            "mean_current": mean_current,
            "current_imbalance": current_imbalance,
            "avg_voltage": avg_voltage,
            "harmonic_thd": harmonic_thd,
            "temperature_c": temperature_c,
            "status": status,
            "remediation": remediation
        }

        self.telemetry_history.append(record)
        if len(self.telemetry_history) > 1000:
            self.telemetry_history.pop(0)

        return record

    def get_system_health(self) -> Dict[str, Any]:
        total_records = len(self.telemetry_history)
        latest = self.telemetry_history[-1] if total_records > 0 else None
        return {
            "canopy_id": self.canopy_id,
            "total_telemetry_packets": total_records,
            "total_anomalies_detected": self.anomaly_count,
            "latest_status": latest
        }

if __name__ == "__main__":
    logger.info("Executing test harness for Nairobi Commercial Solar Canopy Sentinel...")
    sentinel = SolarCanopyHarmonicSentinel(canopy_id="NAI_IND_SOLAR_04", rated_capacity_kw=250.0)
    
    # Simulate nominal ingestion
    report_1 = sentinel.ingest_telemetry([45.2, 45.0, 44.8, 45.1], [380.5, 381.0, 380.2], 2.1, 42.5)
    logger.info(f"Report 1: {report_1['status']}")
    
    # Simulate thermal & harmonic anomaly
    report_2 = sentinel.ingest_telemetry([45.2, 32.1, 44.8, 45.1], [370.0, 371.0, 369.5], 6.8, 68.2)
    logger.info(f"Report 2: {report_2['status']} -> {report_2['remediation']}")
    
    health = sentinel.get_system_health()
    logger.info(f"Canopy Health Summary: {health}")
    logger.info("Solar Canopy Harmonic Pulse Sentinel execution completed successfully.")
