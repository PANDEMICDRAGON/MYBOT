import logging
import time
import statistics
from typing import Dict, List, Any, Optional

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - [%(filename)s] - %(message)s')
logger = logging.getLogger('GrainMillingPurifierSentinel')

class GrainPurifierAnomalyException(Exception):
    """Raised when purifier metrics breach operational thresholds."""
    pass

class GrainPurifierSentinel:
    """
    Monitors commercial semolina purifiers in grain milling plants.
    Ensures proper deck oscillation, suction pressure, and feed distribution.
    """
    def __init__(self, purifier_id: str, target_suction_pa: float = 850.0, target_oscillation_hz: float = 7.5):
        self.purifier_id = purifier_id
        self.target_suction_pa = target_suction_pa
        self.target_oscillation_hz = target_oscillation_hz
        self.suction_history: List[float] = []
        self.oscillation_history: List[float] = []
        self.tailings_load_history: List[float] = []
        logger.info(f"Initialized GrainPurifierSentinel for unit: {self.purifier_id}")

    def ingest_telemetry(self, suction_pa: float, oscillation_hz: float, tailings_kg_hr: float) -> Dict[str, Any]:
        """
        Ingests real-time telemetry from purifier sensors and evaluates health.
        "" - suction_pa: Air suction pressure under the sieve decks.
        - oscillation_hz: Mechanical reciprocating frequency of the deck.
        - tailings_kg_hr: Mass flow of coarse tailings recirculated or rejected.
        """
        self.suction_history.append(suction_pa)
        self.oscillation_history.append(oscillation_hz)
        self.tailings_load_history.append(tailings_kg_hr)

        # Keep last 50 readings
        if len(self.suction_history) > 50:
            self.suction_history.pop(0)
            self.oscillation_history.pop(0)
            self.tailings_load_history.pop(0)

        # Diagnostics
        suction_delta = abs(suction_pa - self.target_suction_pa)
        oscillation_delta = abs(oscillation_hz - self.target_oscillation_hz)

        status = "OPTIMAL"
        warnings = []

        if suction_delta > 120.0:
            warnings.warn(f"Suction pressure deviation high: {suction_pa} Pa (Target: {self.target_suction_pa})")
            status = "WARNING"

        if oscillation_delta > 1.0:
            warnings.warn(f"Deck oscillation frequency erratic: {oscillation_hz} Hz (Target: {self.target_oscillation_hz})")
            status = "WARNING"

        if tailings_kg_hr > 250.0:
            warnings.warn(f"Tailings overload detected: {tailings_kg_hr} kg/hr. Check feed gate.")
            status = "CRITICAL"

        if status == "CRITICAL":
            logger.error(f"[{self.purifier_id}] Critical purifier fault detected. Action required.")

        return {
            "purifier_id": self.purifier_id,
            "timestamp": time.time(),
            "status": status,
            "suction_pa": suction_pa,
            "oscillation_hz": oscillation_hz,
            "tailings_kg_hr": tailings_kg_hr,
            "warnings": warnings
        }

    def get_summary(self) -> Dict[str, Any]:
        """Returns aggregated statistical health metrics."""
        if not self.suction_history:
            return {"status": "NO_DATA"}

        return {
            "purifier_id": self.purifier_id,
            "avg_suction_pa": statistics.mean(self.suction_history),
            "avg_oscillation_hz": statistics.mean(self.oscillation_history),
            "avg_tailings_kg_hr": statistics.mean(self.tailings_load_history),
            "samples_recorded": len(self.suction_history)
        }

if __name__ == "__main__":
    print("Executing GrainPurifierSentinel Test Harness...")
    sentinel = GrainPurifierSentinel(purifier_id="PURIFIER-03-NAIROBI")
    
    # Simulate normal and aberrant telemetry
    telemetry_samples = [
        (845.2, 7.5, 45.0),
        (852.0, 7.4, 50.0),
        (710.0, 6.2, 280.0),  # Should trigger warnings/critical
        (849.1, 7.5, 48.0)
    ]

    for s, o, t in telemetry_samples:
        res = sentinel.ingest_telemetry(s, o, t)
        print(f"Telemetry Result: {res['status']} | Warnings: {res['warnings']}")

    summary = sentinel.get_summary()
    print(f"Purifier Summary: {summary}")
    print("GrainPurifierSentinel test execution complete.")
