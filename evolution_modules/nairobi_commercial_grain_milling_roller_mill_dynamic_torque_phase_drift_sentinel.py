"""Nairobi Commercial Grain Milling Roller Mill Dynamic Torque Phase Drift Sentinel Module."""

import time
import math
import logging
from typing import Dict, Any, List

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')
logger = logging.getLogger("RollerMillPhaseDriftSentinel")

class RollerMillPhaseDriftSentinel:
    """Monitors phase drift between paired roller mill drive spindles in Nairobi commercial milling plants."""

    def __init__(self, mill_id: str, max_allowable_phase_drift_deg: float = 3.5):
        self.mill_id = mill_id
        self.max_drift = max_allowable_phase_drift_deg
        self.telemetry_history: List[Dict[str, Any]] = []
        logger.info(f"Initialized RollerMillPhaseDriftSentinel for mill {self.mill_id} with max drift threshold {self.max_drift}°")

    def evaluate_phase_drift(self, fast_roll_angle: float, slow_roll_angle: float, load_tonnage_hr: float) -> Dict[str, Any]:
        """Evaluate angular phase difference between fast and slow rolls during milling operation."""
        # Normalize angles to [0, 360)
        f_norm = fast_roll_angle % 360.0
        s_norm = slow_roll_angle % 360.0

        diff = abs(f_norm - s_norm)
        if diff > 180.0:
            diff = 360.0 - diff

        status = "NOMINAL"
        action = "NONE"

        if diff > self.max_drift:
            status = "CRITICAL_PHASE_DRIFT"
            action = "ENGAGE_DYNAMIC_INVERTER_COMPENSATION"
            logger.warning(f"[{self.mill_id}] Phase drift anomaly detected: {diff:.2f}° (Threshold: {self.max_drift}°). Load: {load_tonnage_hr}t/h")
        else:
            logger.debug(f"[{self.mill_id}] Phase drift nominal: {diff:.2f}°")

        record = {
            "timestamp": time.time(),
            "mill_id": self.mill_id,
            "fast_roll_angle": f_norm,
            "slow_roll_angle": s_norm,
            "phase_drift_deg": diff,
            "load_tonnage_hr": load_tonnage_hr,
            "status": status,
            "action": action
        }
        self.telemetry_history.append(record)
        return record

    def get_diagnostics(self) -> Dict[str, Any]:
        """Return operational diagnostic metrics."""
        if not self.telemetry_history:
            return {"status": "NO_DATA"}
        
        drifts = [r["phase_drift_deg"] for r in self.telemetry_history]
        return {
            "mill_id": self.mill_id,
            "total_samples": len(self.telemetry_history),
            "avg_drift_deg": sum(drifts) / len(drifts),
            "max_recorded_drift_deg": max(drifts),
            "last_status": self.telemetry_history[-1]["status"]
        }

if __name__ == "__main__":
    sentinel = RollerMillPhaseDriftSentinel(mill_id="NAI-MILL-04")
    # Test nominal condition
    res1 = sentinel.evaluate_phase_drift(fast_roll_angle=124.5, slow_roll_angle=123.8, load_tonnage_hr=12.5)
    print(res1)
    # Test drift anomaly condition
    res2 = sentinel.evaluate_phase_drift(fast_roll_angle=210.0, slow_roll_angle=204.2, load_tonnage_hr=15.0)
    print(res2)
    print(sentinel.get_diagnostics())
