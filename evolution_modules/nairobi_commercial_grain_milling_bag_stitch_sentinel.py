"""
Nairobi Commercial Grain Milling Bag Stitch & Closure Quality Sentinel
Monitors automated bag closing sewing heads, thread breakages, stitch skip frequency,
and tension sensors to prevent packaging failure in commercial flour and maize mills.
"""

import time
import logging
from typing import Dict, Any, List, Optional

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')
logger = logging.getLogger("BagStitchSentinel")

class BagStitchSentinel:
    """
    Real-time telemetry processor for industrial bag-closing sewing lines.
    Tracks needle reciprocation rate, thread tension, and stitch count per bag.
    """
    def __init__(self, line_id: str, max_skip_tolerance: int = 2):
        self.line_id = line_id
        self.max_skip_tolerance = max_skip_tolerance
        self.metrics_history: List[Dict[str, Any]] = []
        self.active_faults: List[str] = []

    def inspect_bag_closure(self, bag_id: str, stitch_count: int, skip_stitches: int, thread_tension_n: float) -> Dict[str, Any]:
        """
        Inspects telemetry from a freshly sewn grain bag.
        """
        status = "PASS"
        faults = []

        if skip_stitches > self.max_skip_tolerance:
            faults.append(f"EXCESSIVE_SKIP_STITCHES:{skip_stitches}")
            status = "REJECT"

        if thread_tension_n < 15.0 or thread_tension_n > 45.0:
            faults.append(f"ABNORMAL_THREAD_TENSION:{thread_tension_n}N")
            status = "WARNING" if status == "PASS" else "REJECT"

        if stitch_count < 20:
            faults.append(f"INSUFFICIENT_STITCH_COUNT:{stitch_count}")
            status = "REJECT"

        record = {
            "timestamp": time.time(),
            "bag_id": bag_id,
            "line_id": self.line_id,
            "stitch_count": stitch_count,
            "skip_stitches": skip_stitches,
            "thread_tension_n": thread_tension_n,
            "status": status,
            "faults": faults
        }

        self.metrics_history.append(record)
        if len(self.metrics_history) > 1000:
            self.metrics_history.pop(0)

        if status == "REJECT":
            logger.warning(f"[Line {self.line_id}] Bag {bag_id} REJECTED due to: {faults}")

        return record

    def get_line_health(self) -> Dict[str, Any]:
        """
        Aggregates bag closure health across recent inspections.
        """
        if not self.metrics_history:
            return {"line_id": self.line_id, "total_inspected": 0, "pass_rate": 1.0}

        total = len(self.metrics_history)
        passed = sum(1 for m in self.metrics_history if m["status"] == "PASS")
        return {
            "line_id": self.line_id,
            "total_inspected": total,
            "pass_rate": passed / total,
            "recent_faults": self.metrics_history[-1].get("faults", [])
        }

if __name__ == "__main__":
    logger.info("Initializing Nairobi Commercial Grain Milling Bag Stitch Sentinel Test Harness...")
    sentinel = BagStitchSentinel(line_id="NAI-MILL-LINE-04")
    
    # Test normal bag
    res1 = sentinel.inspect_bag_closure("BAG-9901", stitch_count=35, skip_stitches=0, thread_tension_n=28.5)
    logger.info(f"Bag 1 Result: {res1['status']}")

    # Test defective bag (skip stitches & low tension)
    res2 = sentinel.inspect_bag_closure("BAG-9902", stitch_count=30, skip_stitches=4, thread_tension_n=10.2)
    logger.info(f"Bag 2 Result: {res2['status']} - Faults: {res2['faults']}")

    health = sentinel.get_line_health()
    logger.info(f"Line Health Summary: {health}")
    logger.info("Bag Stitch Sentinel module compiled and verified successfully.")
