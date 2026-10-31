import logging
import time
import statistics
from typing import Dict, List, Any, Optional

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')
logger = logging.getLogger("RollerMillApexSynapseSentinel")

class RollerMillApexSynapseSentinel:
    """
    Monitors high-frequency telemetry from commercial roller mills, analyzing dynamic
    torque matrices, harmonic distortions, and roll gap variances to execute real-time
    adaptive damping and predictive anomaly isolation for Nairobi grain processing plants.
    """
    def __init__(self, mill_id: str, torque_threshold: float = 85.0, harmonic_limit: float = 5.0):
        self.mill_id = mill_id
        self.torque_threshold = torque_threshold
        self.harmonic_limit = harmonic_limit
        self.telemetry_history: List[Dict[str, float]] = []
        logger.info(f"Initialized Apex Synapse Sentinel for Mill: {self.mill_id}")

    def ingest_telemetry(self, torque_nm: float, vibration_hz: float, harmonic_distortion_pct: float, roll_gap_mm: float) -> Dict[str, Any]:
        timestamp = time.time()
        record = {
            "timestamp": timestamp,
            "torque_nm": torque_nm,
            "vibration_hz": vibration_hz,
            "harmonic_distortion_pct": harmonic_distortion_pct,
            "roll_gap_mm": roll_gap_mm
        }
        self.telemetry_history.append(record)
        if len(self.telemetry_history) > 1000:
            self.telemetry_history.pop(0)
        return self._evaluate_matrix(record)

    def _evaluate_matrix(self, current: Dict[str, float]) -> Dict[str, Any]:
        status = "OPTIMAL"
        actions = []

        if current["torque_nm"] > self.torque_threshold:
            status = "WARNING"
            actions.append("ADJUST_INVERTER_TORQUE_LIMIT")

        if current["harmonic_distortion_pct"] > self.harmonic_limit:
            status = "CRITICAL"
            actions.append("ENGAGE_HARMONIC_DAMPING_FILTER")

        recent_torques = [r["torque_nm"] for r in self.telemetry_history[-10:]]
        torque_jitter = statistics.stdev(recent_torques) if len(recent_torques) > 1 else 0.0

        if torque_jitter > 4.5:
            status = "CRITICAL"
            actions.append("TRIGGER_ROLL_GAP_SYNCHRONIZATION")

        assessment = {
            "mill_id": self.mill_id,
            "status": status,
            "torque_jitter": round(torque_jitter, 3),
            "recommended_actions": actions,
            "timestamp": current["timestamp"]
        }
        
        if status != "OPTIMAL":
            logger.warning(f"Anomaly detected in {self.mill_id}: {assessment}")
        else:
            logger.debug(f"Mill {self.mill_id} operating within nominal parameters.")

        return assessment

    def generate_health_report(self) -> Dict[str, Any]:
        if not self.telemetry_history:
            return {"mill_id": self.mill_id, "status": "NO_DATA"}
        
        torques = [r["torque_nm"] for r in self.telemetry_history]
        return {
            "mill_id": self.mill_id,
            "total_samples": len(self.telemetry_history),
            "mean_torque_nm": round(statistics.mean(torques), 2),
            "max_torque_nm": round(max(torques), 2),
            "min_torque_nm": round(min(torques), 2)
        }

if __name__ == "__main__":
    sentinel = RollerMillApexSynapseSentinel(mill_id="NAI_MILL_ALPHA_01")
    # Simulate normal and aberrant telemetry ingestion
    metrics = [
        (72.4, 14.2, 1.2, 0.45),
        (75.1, 14.5, 1.5, 0.45),
        (88.9, 18.0, 5.8, 0.42),
        (91.2, 22.1, 6.4, 0.40)
    ]
    for t, v, h, g in metrics:
        res = sentinel.ingest_telemetry(t, v, h, g)
        print(res)
    print(sentinel.generate_health_report())
