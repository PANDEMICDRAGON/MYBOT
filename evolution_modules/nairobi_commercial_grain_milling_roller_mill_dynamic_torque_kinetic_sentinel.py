import logging
import time
import statistics
from typing import Dict, List, Any, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("RollerMillKineticSentinel")

class RollerMillKineticSentinel:
    """
    Monitors kinetic energy dissipation and dynamic torque variations in commercial
    grain milling roller mills across Nairobi facilities, preventing catastrophic gear
    box friction anomalies and grain feed jams.
    """
    def __init__(self, mill_id: str, kinetic_threshold: float = 85.0):
        self.mill_id = mill_id
        self.kinetic_threshold = kinetic_threshold
        self.telemetry_history: List[Dict[str, Any]] = []
        self.is_active = True

    def ingest_telemetry(self, timestamp: float, torque_nm: float, rpm: float, vibration_mm_s: float) -> Dict[str, Any]:
        """
        Ingests real-time sensor streams and calculates kinetic energy dissipation index.
        """
        # Kinetic energy factor estimation: 0.5 * I * omega^2 approximated via torque & RPM interaction
        kinetic_index = (torque_nm * rpm) / 9.5488 * (1.0 + (vibration_mm_s * 0.1))
        
        status = "NOMINAL"
        if kinetic_index > self.kinetic_threshold:
            status = "WARNING_HIGH_KINETIC_DISSIPATION"
            logger.warning(f"[{self.mill_id}] High kinetic dissipation detected: {kinetic_index:.2f} (Threshold: {self.kinetic_threshold})")

        record = {
            "timestamp": timestamp,
            "torque_nm": torque_nm,
            "rpm": rpm,
            "vibration_mm_s": vibration_mm_s,
            "kinetic_index": kinetic_index,
            "status": status
        }
        self.telemetry_history.append(record)
        if len(self.telemetry_history) > 1000:
            self.telemetry_history.pop(0)
            
        return record

    def analyze_stability(self) -> Dict[str, Any]:
        """
        Performs statistical aggregation over historical kinetic indices.
        """
        if not self.telemetry_history:
            return {"status": "NO_DATA"}

        indices = [r["kinetic_index"] for r in self.telemetry_history]
        mean_val = statistics.mean(indices)
        stdev_val = statistics.stdev(indices) if len(indices) > 1 else 0.0

        return {
            "mill_id": self.mill_id,
            "samples_analyzed": len(indices),
            "mean_kinetic_index": mean_val,
            "stdev_kinetic_index": stdev_val,
            "anomaly_detected": mean_val > self.kinetic_threshold
        }

if __name__ == "__main__":
    sentinel = RollerMillKineticSentinel(mill_id="NAIROBI_MILL_ALPHA_04")
    current_time = time.time()
    
    # Simulate normal and anomalous runs
    test_data = [
        (current_time, 120.5, 1450.0, 1.2),
        (current_time + 1.0, 122.0, 1452.0, 1.3),
        (current_time + 2.0, 165.4, 1420.0, 4.5),  # Spike
    ]

    for ts, tq, rpm, vib in test_data:
        res = sentinel.ingest_telemetry(ts, tq, rpm, vib)
        logger.info(f"Telemetry Result: {res}")

    summary = sentinel.analyze_stability()
    logger.info(f"Sentinel Stability Summary: {summary}")
