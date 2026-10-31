"""
Nairobi Commercial Grain Milling Bag Sewing & Closure Sentinel

Monitors high-speed bag stitching heads, thread tension, cutter actuation,
and skip-stitch optical sensors in Nairobi commercial grain milling plants.
"""

import time
import logging
from typing import Dict, Any, List

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("BagSewingSentinel")

class BagSewingSentinel:
    def __init__(self, machine_id: str, max_thread_tension_n: float = 45.0):
        self.machine_id = machine_id
        self.max_thread_tension_n = max_thread_tension_n
        self.total_bags_stitched = 0
        self.stitch_errors_detected = 0
        self.operational_status = "IDLE"

    def inspect_bag_closure(self, telemetry: Dict[str, Any]) -> Dict[str, Any]:
        """Analyzes telemetry from the bag closing and sewing head."""
        tension = telemetry.get("thread_tension_n", 25.0)
        rpm = telemetry.get("sewing_head_rpm", 1800.0)
        skip_stitch = telemetry.get("skip_stitch_detected", False)
        cutter_active = telemetry.get("thread_cutter_actuated", True)

        alerts: List[str] = []
        status = "OPTIMAL"

        if tension > self.max_thread_tension_n:
            alerts.append(f"HIGH_THREAD_TENSION: {tension}N exceeds limit {self.max_thread_tension_n}N")
            status = "WARNING"
        elif tension < 10.0:
            alerts.append(f"LOW_THREAD_TENSION: {tension}N indicates potential thread breakage")
            status = "CRITICAL"

        if skip_stitch:
            alerts.append("SKIP_STITCH_OPTICAL_FAULT: Defective seal detected on bag hem")
            status = "CRITICAL"
            self.stitch_errors_detected += 1

        if not cutter_active and telemetry.get("bag_passed", False):
            alerts.append("CUTTER_FAILURE: Thread tail not severed after bag exit")
            status = "WARNING"

        self.total_bags_stitched += 1
        self.operational_status = status

        return {
            "machine_id": self.machine_id,
            "status": status,
            "rpm": rpm,
            "tension": tension,
            "alerts": alerts,
            "total_bags_stitched": self.total_bags_stitched,
            "stitch_errors_detected": self.stitch_errors_detected,
            "timestamp": time.time()
        }

if __name__ == "__main__":
    logger.info("Initializing Nairobi Commercial Grain Milling Bag Sewing & Closure Sentinel...")
    sentinel = BagSewingSentinel(machine_id="SEW-LINE-04")
    sample_telemetry = {
        "thread_tension_n": 28.5,
        "sewing_head_rpm": 1850.0,
        "skip_stitch_detected": False,
        "thread_cutter_actuated": True,
        "bag_passed": True
    }
    report = sentinel.inspect_bag_closure(sample_telemetry)
    logger.info(f"Diagnostic Report: {report}")
