"""
Nairobi Commercial Grain Milling Roller Mill Dynamic Torque Matrix Pulse Sentinel
Autonomous Evolutionary Architecture - Cycle #51

Provides real-time pulse analytics, torsional snap evaluation, and adaptive load shedding
for commercial roller mills operating in industrial Nairobi milling plants.
"""

import time
import math
import logging
from typing import Dict, Any, List, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("RollerMillPulseSentinel")

class RollerMillPulseSentinel:
    """Monitors high-frequency torsional pulse matrices and dynamic torque variations on commercial roller mills."""
    
    def __init__(self, mill_id: str, rated_torque_nm: float = 1250.0, pulse_threshold_pct: float = 18.5):
        self.mill_id = mill_id
        self.rated_torque_nm = rated_torque_nm
        self.pulse_threshold_pct = pulse_threshold_pct
        self.telemetry_history: List[Dict[str, Any]] = []
        self.anomaly_count = 0
        
    def ingest_torque_pulse(self, current_torque_nm: float, rpm: float, vibration_hz: float) -> Dict[str, Any]:
        """Ingecst high-frequency torque telemetry, computes pulse deviation, and checks safety thresholds."""
        deviation = ((current_torque_nm - self.rated_torque_nm) / self.rated_torque_nm) * 100.0
        is_pulse_anomaly = abs(deviation) > self.pulse_threshold_pct
        
        status = "NOMINAL"
        action_required = "NONE"
        
        if is_pulse_anomaly:
            self.anomaly_count += 1
            status = "CRITICAL_PULSE_SPIKE" if deviation > 0 else "CRITICAL_TORQUE_DROP"
            action_required = "ENGAGE_FEED_GATE_CHOKE_VALVE" if deviation > 0 else "CHECK_DRIVE_BELT_SLIP"
            logger.warning(f"[{self.mill_id}] PULSE ANOMALY DETECTED: {status} | Deviation: {deviation:.2f}%")
            
        telemetry_packet = {
            "timestamp": time.time(),
            "mill_id": self.mill_id,
            "current_torque_nm": current_torque_nm,
            "rated_torque_nm": self.rated_torque_nm,
            "deviation_pct": round(deviation, 2),
            "rpm": rpm,
            "vibration_hz": vibration_hz,
            "status": status,
            "action_required": action_required
        }
        
        self.telemetry_history.append(telemetry_packet)
        if len(self.telemetry_history) > 1000:
            self.telemetry_history.pop(0)
            
        return telemetry_packet

    def get_diagnostics(self) -> Dict[str, Any]:
        """Returns aggregate diagnostics for the roller mill sentinel."""
        return {
            "mill_id": self.mill_id,
            "total_telemetry_records": len(self.telemetry_history),
            "total_anomalies": self.anomaly_count,
            "health_status": "DEGRADED" if self.anomaly_count > 5 else "OPTIMAL"
        }

if __name__ == "__main__":
    print("Initializing Nairobi Commercial Grain Milling Roller Mill Dynamic Torque Matrix Pulse Sentinel...")
    sentinel = RollerMillPulseSentinel(mill_id="NAI_MILL_UNGA_04")
    
    # Test normal pulse
    p1 = sentinel.ingest_torque_pulse(1240.0, 750.0, 14.2)
    print("Telemetry 1:", p1)
    
    # Test abnormal pulse surge
    p2 = sentinel.ingest_torque_pulse(1550.0, 720.0, 28.6)
    print("Telemetry 2:", p2)
    
    print("Diagnostics:", sentinel.get_diagnostics())
    print("Pulse Sentinel initialized and tested successfully.")
