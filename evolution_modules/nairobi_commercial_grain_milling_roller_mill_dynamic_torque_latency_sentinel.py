"""
Module: nairobi_commercial_grain_milling_roller_mill_dynamic_torque_latency_sentinel.py
Author: Cortana's Autonomous Evolutionary Architect
Operator: Michael Obiero (Nairobi, Kenya)
Description: Monitors dynamic torque transmission latency in commercial roller mills to prevent drive train lag and roll synchronization failure.
"""

import time
import math
import logging
from typing import Dict, List, Any, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("TorqueLatencySentinel")


class RollerMillTorqueLatencySentinel:
    """
    Evaluates real-time torque sensor command vs response latency across milling roll pairs.
    """

    def __init__(self, warning_threshold_ms: float = 45.0, critical_threshold_ms: float = 85.0):
        self.warning_threshold_ms = warning_threshold_ms
        self.critical_threshold_ms = critical_threshold_ms
        self.telemetry_history: List[Dict[str, Any]] = []

    def ingest_cycle(self, mill_id: str, command_timestamp: float, response_timestamp: float, torque_nm: float) -> Dict[str, Any]:
        latency_ms = (response_timestamp - command_timestamp) * 1000.0
        status = "OPTIMAL"
        
        if latency_ms >= self.critical_threshold_ms:
            status = "CRITICAL_LAG"
            logger.error(f"[{mill_id}] CRITICAL LATENCY: {latency_ms:.2f}ms at {torque_nm} Nm!")
        elif latency_ms >= self.warning_threshold_ms:
            status = "WARNING_ELEVATED"
            logger.warning(f"[{mill_id}] ELEVATED LATENCY: {latency_ms:.2f}ms at {torque_nm} Nm.")
        else:
            logger.info(f"[{mill_id}] Latency nominal: {latency_ms:.2f}ms.")

        record = {
            "mill_id": mill_id,
            "command_timestamp": command_timestamp,
            "response_timestamp": response_timestamp,
            "latency_ms": latency_ms,
            "torque_nm": torque_nm,
            "status": status
        }
        self.telemetry_history.append(record)
        return record

    def get_diagnostics(self) -> Dict[str, Any]:
        if not self.telemetry_history:
            return {"avg_latency_ms": 0.0, "max_latency_ms": 0.0, "total_samples": 0}
        latencies = [r["latency_ms"] for r in self.telemetry_history]
        return {
            "avg_latency_ms": sum(latencies) / len(latencies),
            "max_latency_ms": max(latencies),
            "total_samples": len(latencies),
            "active_alerts": sum(1 for r in self.telemetry_history if r["status"] != "OPTIMAL")
        }


if __name__ == "__main__":
    print("Initializing Nairobi Commercial Grain Milling Roller Mill Dynamic Torque Latency Sentinel...")
    sentinel = RollerMillTorqueLatencySentinel()
    now = time.time()
    
    # Simulate normal and lagged cycles
    sentinel.ingest_cycle("MILL_UGALI_01", now, now + 0.025, 340.5)
    sentinel.ingest_cycle("MILL_UGALI_01", now, now + 0.050, 410.2)
    sentinel.ingest_cycle("MILL_UGALI_01", now, now + 0.095, 520.0)
    
    diagnostics = sentinel.get_diagnostics()
    print(f"Diagnostics Summary: {diagnostics}")
    print("Sentinel test sequence executed successfully.")
