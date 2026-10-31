import time
import logging
import threading
from typing import Dict, Any, List, Optional

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')
logger = logging.getLogger("MillStoneSentinel")

class MillStoneSentinel:
    """
    Monitors commercial grain milling machinery (stone mills & Buchanan roller gaps)
    in Nairobi industrial zones (e.g., Industrial Area, Gikomba, or Kawangware mills)
    to prevent stone glazing, friction overheating, and roller gap misalignment.
    """
    def __init__(self, mill_id: str, mill_type: str = "stone", max_temp_c: float = 78.0, max_vibration_mm_s: float = 4.5):
        self.mill_id = mill_id
        self.mill_type = mill_type.lower()
        self.max_temp_c = max_temp_c
        self.max_vibration_mm_s = max_vibration_mm_s
        self.running = False
        self._lock = threading.Lock()
        self.metrics_history: List[Dict[str, Any]] = []
        self.status = "STANDBY"
        logger.info(f"Initialized MillStoneSentinel for [{self.mill_id}] of type [{self.mill_type}]")

    def evaluate_telemetry(self, bearing_temp_c: float, vibration_mm_s: float, motor_current_amps: float, gap_clearance_mm: float) -> Dict[str, Any]:
        """
        Evaluates real-time sensor telemetry against safety thresholds.
        Returns a prescriptive mitigation dictionary.
        """
        with self._lock:
            alerts = []
            mitigations = []
            severity = "NORMAL"

            if bearing_temp_c > self.max_temp_c:
                severity = "WARNING"
                alerts.append(f"High bearing/stone temperature detected: {bearing_temp_c}C (Limit: {self.max_temp_c}C)")
                mitigations.append("Increase cooling airflow / drip-feed water flow if applicable; check lubrication.")

            if vibration_mm_s > self.max_vibration_mm_s:
                severity = "CRITICAL" if severity == "WARNING" else "WARNING"
                alerts.append(f"Excessive vibration amplitude: {vibration_mm_s} mm/s (Limit: {self.max_vibration_mm_s} mm/s)")
                mitigations.append("Check roller alignment / stone dressing balance for uneven contact.")

            if self.mill_type == "buchanan" and gap_clearance_mm < 0.15:
                severity = "CRITICAL"
                alerts.append(f"Buchanan roller gap dangerously tight: {gap_clearance_mm} mm risk of metal-on-metal contact!")
                mitigations.append("Auto-retract roller hydraulic actuators by 0.05mm immediately.")

            record = {
                "timestamp": time.time(),
                "bearing_temp_c": bearing_temp_c,
                "vibration_mm_s": vibration_mm_s,
                "motor_current_amps": motor_current_amps,
                "gap_clearance_mm": gap_clearance_mm,
                "severity": severity,
                "alerts": alerts
            }
            self.metrics_history.append(record)
            if len(self.metrics_history) > 1000:
                self.metrics_history.pop(0)

            self.status = severity
            return {
                "mill_id": self.mill_id,
                "status": severity,
                "alerts": alerts,
                "mitigations": mitigations,
                "timestamp": record["timestamp"]
            }

    def get_diagnostics(self) -> Dict[str, Any]:
        with self._lock:
            return {
                "mill_id": self.mill_id,
                "mill_type": self.mill_type,
                "status": self.status,
                "total_readings": len(self.metrics_history)
            }

if __name__ == "__main__":
    print("Executing local verification test for MillStoneSentinel...")
    sentinel = MillStoneSentinel(mill_id="NAI-IND-MILL-04", mill_type="buchanan", max_temp_c=75.0, max_vibration_mm_s=4.0)
    
    # Test normal operation
    res1 = sentinel.evaluate_telemetry(bearing_temp_c=65.2, vibration_mm_s=2.1, motor_current_amps=42.5, gap_clearance_mm=0.35)
    assert res1["status"] == "NORMAL"
    
    # Test anomalous tight gap
    res2 = sentinel.evaluate_telemetry(bearing_temp_c=79.1, vibration_mm_s=5.2, motor_current_amps=58.0, gap_clearance_mm=0.10)
    assert res2["status"] == "CRITICAL"
    assert len(res2["alerts"]) > 0
    
    print(f"Test passed successfully! Diagnostics: {sentinel.get_diagnostics()}")
