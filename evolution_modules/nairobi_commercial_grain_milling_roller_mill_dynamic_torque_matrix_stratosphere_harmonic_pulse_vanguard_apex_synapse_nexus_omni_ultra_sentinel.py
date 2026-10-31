"""
Nairobi Commercial Grain Milling Roller Mill Dynamic Torque Matrix Stratosphere Harmonic Pulse Vanguard Apex Synapse Nexus Omni Ultra Sentinel
Designed to safeguard industrial milling hardware in Nairobi, Kenya.
"""

import os
import time
import math
import logging
import json
from typing import Dict, Any, List, Optional

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')
logger = logging.getLogger("RollerMillOmniUltraSentinel")

class RollerMillOmniUltraSentinel:
    """
    Monitors high-frequency torsional oscillations, stratospheric load vectors,
    and harmonic resonance profiles of industrial roller mills.
    """
    def __init__(self, mill_id: str, baseline_torque_nm: float = 1250.0):
        self.mill_id = mill_id
        self.baseline_torque_nm = baseline_torque_nm
        self.telemetry_history: List[Dict[str, Any]] = []
        self.is_active = True
        logger.info(f"Initialized RollerMillOmniUltraSentinel for Mill ID: {self.mill_id}")

    def ingest_telemetry(self, current_torque: float, vibration_hz: float, bearing_temp_c: float) -> Dict[str, Any]:
        """
        Ingests real-time sensor telemetry and computes harmonic variance and anomaly scores.
        """
        timestamp = time.time()
        torque_delta = abs(current_torque - self.baseline_torque_nm)
        harmonic_pulse_index = (torque_delta / self.baseline_torque_nm) * (vibration_hz / 50.0)
        
        status = "NOMINAL"
        action_required = False
        
        if harmonic_pulse_index > 0.35 or bearing_temp_c > 85.0:
            status = "CRITICAL_HARMONIC_ANOMALY"
            action_required = True
            logger.warning(f"[{self.mill_id}] CRITICAL THREAT DETECTED: Pulse Index={harmonic_pulse_index:.4f}, Temp={bearing_temp_c}C")
        elif harmonic_pulse_index > 0.20 or bearing_temp_c > 75.0:
            status = "ELEVATED_WARNING"
            logger.info(f"[{self.mill_id}] Elevated wear pattern detected. Pulse Index={harmonic_pulse_index:.4f}")

        record = {
            "timestamp": timestamp,
            "mill_id": self.mill_id,
            "current_torque": current_torque,
            "vibration_hz": vibration_hz,
            "bearing_temp_c": bearing_temp_c,
            "harmonic_pulse_index": harmonic_pulse_index,
            "status": status,
            "action_required": action_required
        }
        self.telemetry_history.append(record)
        return record

    def generate_diagnostic_report(self) -> str:
        """
        Generates a structured JSON diagnostic summary of recent operational cycles.
        """
        summary = {
            "mill_id": self.mill_id,
            "total_samples": len(self.telemetry_history),
            "system_status": "SECURE" if self.is_active else "OFFLINE",
            "latest_telemetry": self.telemetry_history[-1] if self.telemetry_history else None
        }
        return json.dumps(summary, indent=2)

if __name__ == "__main__":
    logger.info("Executing self-test harness for RollerMillOmniUltraSentinel...")
    sentinel = RollerMillOmniUltraSentinel(mill_id="MILL-NAIROBI-EAST-01")
    
    # Simulate normal operation
    res1 = sentinel.ingest_telemetry(current_torque=1255.2, vibration_hz=49.8, bearing_temp_c=65.4)
    assert res1["status"] == "NOMINAL"
    
    # Simulate stress anomaly
    res2 = sentinel.ingest_telemetry(current_torque=1850.0, vibration_hz=88.5, bearing_temp_c=89.1)
    assert res2["action_required"] is True
    
    report = sentinel.generate_diagnostic_report()
    logger.info(f"Diagnostic Report Generated successfully:\n{report}")
    logger.info("RollerMillOmniUltraSentinel self-test complete. System fully operational.")
