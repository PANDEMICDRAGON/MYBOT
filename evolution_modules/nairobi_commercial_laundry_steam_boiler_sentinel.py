import time
import math
import random
import logging
from typing import Dict, List, Optional, Any

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] [SteamBoilerSentinel]: %(message)s')
logger = logging.getLogger(__name__)

class SteamBoilerAnomalyException(Exception):
    """Raised when boiler telemetry indicates critical pressure or thermal anomalies."""
    pass

class NairobiCommercialLaundrySteamBoilerSentinel:
    """
    Autonomous sentinel designed to monitor Nairobi commercial laundry steam boilers.
    Correlates acoustic burner signatures, steam pressure gradients, feedwater flow rates,
    and exhaust temperature harmonics to predict scale fouling, pump cavitation, and pressure spikes.
    """

    def __init__(self, boiler_id: str, operating_pressure_bar: float = 8.5):
        self.boiler_id = boiler_id
        self.target_pressure = operating_pressure_bar
        self.telemetry_history: List[Dict[str, Any]] = []
        self.health_score: float = 100.0
        logger.info(f"SteamBoilerSentinel initialized for {{boiler_id}} at target pressure {{operating_pressure_bar}} bar.")

    def ingest_sensor_reading(self, pressure_bar: float, feedwater_flow_lpm: float, 
                              burner_acoustic_hz: float, exhaust_temp_c: float) -> Dict[str, Any]:
        """Ingests raw boiler sensors, computes harmonic correlation, and updates health index."""
        timestamp = time.time()
        
        # Anomaly detection heuristics
        pressure_delta = abs(pressure_bar - self.target_pressure)
        acoustic_anomaly = abs(burner_acoustic_hz - 120.0) # Nominal burner hum at 120Hz
        thermal_efficiency = exhaust_temp_c / 250.0  # Nominal exhaust ~200-250C
        
        # Compute stress factor
        stress_factor = (pressure_delta * 2.5) + (acoustic_anomaly * 0.05) + max(0.0, (thermal_efficiency - 1.1) * 10)
        self.health_score = max(0.0, min(100.0, self.health_score - (stress_factor * 0.1) + 0.05))

        status = "OPTIMAL"
        if self.health_score < 75.0:
            status = "WARNING"
        if self.health_score < 40.0 or pressure_bar > (self.target_pressure * 1.35):
            status = "CRITICAL"
            logger.warning(f"[{self.boiler_id}] CRITICAL BOILER STATE: Pressure={{pressure_bar}} bar, Health={{self.health_score:.1f}}")

        payload = {
            "timestamp": timestamp,
            "boiler_id": self.boiler_id,
            "pressure_bar": pressure_bar,
            "feedwater_flow_lpm": feedwater_flow_lpm,
            "burner_acoustic_hz": burner_acoustic_hz,
            "exhaust_temp_c": exhaust_temp_c,
            "health_score": self.health_score,
            "status": status
        }

        self.telemetry_history.append(payload)
        if len(self.telemetry_history) > 1000:
            self.telemetry_history.pop(0)

        return payload

    def execute_purge_cycle(self) -> bool:
        """Simulates automated blowdown/purge sequence to clear mineral scaling."""
        logger.info(f"[{self.boiler_id}] Initiating automated blowdown purge cycle...")
        time.sleep(0.05)
        self.health_score = min(100.0, self.health_score + 15.0)
        logger.info(f"[{self.boiler_id}] Blowdown complete. Health score restored to {{self.health_score:.1f}}.")
        return True

    def export_diagnostics(self) -> Dict[str, Any]:
        """Exports operational telemetry summary for Cortana operator review."""
        return {
            "boiler_id": self.boiler_id,
            "current_health": self.health_score,
            "total_telemetry_records": len(self.telemetry_history),
            "last_status": self.telemetry_history[-1]["status"] if self.telemetry_history else "UNKNOWN"
        }

if __name__ == "__main__":
    sentinel = NairobiCommercialLaundrySteamBoilerSentinel(boiler_id="NAI_LAUNDRY_BOILER_04")
    
    # Simulate normal and aberrant telemetry cycles
    for i in range(5):
        p = 8.5 + random.uniform(-0.3, 0.4)
        fw = 15.2 + random.uniform(-1.0, 1.0)
        ac = 120.0 + random.uniform(-2.0, 3.0)
        et = 210.0 + random.uniform(-5.0, 10.0)
        result = sentinel.ingest_sensor_reading(p, fw, ac, et)
        logger.info(f"Test Cycle {{i+1}}: {{result['status']}} | Health: {{result['health_score']:.1f}}")

    # Simulate scale buildup pressure spike
    critical_result = sentinel.ingest_sensor_reading(11.8, 5.1, 145.0, 310.0)
    if critical_result["status"] == "CRITICAL":
        sentinel.execute_purge_cycle()

    diag = sentinel.export_diagnostics()
    logger.info(f"Final Diagnostics: {{diag}}")
