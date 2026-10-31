import logging
import time
import statistics
from typing import Dict, List, Any, Optional

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')
logger = logging.getLogger('TorquePhaseSentinel')

class RollerMillPhaseAnomalyError(Exception):
    """Raised when phase angle deviation exceeds acceptable tolerances."""
    pass

class RollerMillDynamicTorquePhaseSentinel:
    """
    Monitors three-phase motor voltage/current phase angles and torque ripple
    for commercial roller mills in Nairobi grain processing plants.
    """
    def __init__(self, mill_id: str, nominal_frequency_hz: float = 50.0, max_phase_deviation_deg: float = 4.5):
        self.mill_id = mill_id
        self.nominal_frequency_hz = nominal_frequency_hz
        self.max_phase_deviation_deg = max_phase_deviation_deg
        self._phase_history: List[float] = []
        self._anomaly_count = 0
        logger.info(f"Initialized RollerMillDynamicTorquePhaseSentinel for mill {self.mill_id}")

    def ingest_telemetry(self, telemetry: Dict[str, Any]) -> Dict[str, Any]:
        """
        Ingests phase telemetry (voltage vs current phase angle per phase) and checks for anomalies.
        """
        phase_angles = telemetry.get('phase_angles_deg', [])
        if not phase_angles or len(phase_angles) != 3:
            raise ValueError("Telemetry must contain exactly 3 phase angle readings.")

        mean_angle = statistics.mean(phase_angles)
        max_deviation = max(abs(a - mean_angle) for a in phase_angles)
        self._phase_history.append(max_deviation)

        if len(self._phase_history) > 100:
            self._phase_history.pop(0)

        status = "OPTIMAL"
        if max_deviation > self.max_phase_deviation_deg:
            self._anomaly_count += 1
            status = "WARNING_PHASE_ASYMMETRY"
            if max_deviation > (self.max_phase_deviation_deg * 1.5):
                status = "CRITICAL_TORQUE_INSTABILITY"
                logger.error(f"[{self.mill_id}] CRITICAL: Phase deviation {max_deviation:.2f}° exceeds safety limit!")
                raise RollerMillPhaseAnomalyError(f"Phase imbalance detected: {max_deviation:.2f}°")

        return {
            "mill_id": self.mill_id,
            "status": status,
            "max_phase_deviation_deg": round(max_deviation, 3),
            "mean_phase_angle_deg": round(mean_angle, 3),
            "anomaly_count": self._anomaly_count,
            "timestamp": time.time()
        }

    def get_diagnostics(self) -> Dict[str, Any]:
        return {
            "mill_id": self.mill_id,
            "total_samples": len(self._phase_history),
            "anomaly_count": self._anomaly_count,
            "avg_deviation": round(statistics.mean(self._phase_history), 3) if self._phase_history else 0.0
        }

if __main__ == '__main__':
    sentinel = RollerMillDynamicTorquePhaseSentinel(mill_id="MILL-NRB-01")
    test_telemetry = {"phase_angles_deg": [24.1, 25.0, 24.5]}
    result = sentinel.ingest_telemetry(test_telemetry)
    print("Test Result:", result)
