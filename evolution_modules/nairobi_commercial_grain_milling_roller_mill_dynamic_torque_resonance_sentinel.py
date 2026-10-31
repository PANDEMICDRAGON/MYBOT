"""
Nairobi Commercial Grain Milling Roller Mill Dynamic Torque Resonance Sentinel
Autonomous Evolutionary Module for Cortana
"""

import time
import math
import random
import logging
from typing import Dict, Any, List

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')
logger = logging.getLogger("RollerMillTorqueResonanceSentinel")

class RollerMillTorqueResonanceSentinel:
    """
    Monitors high-frequency torque telemetry from commercial roller mills operating
    in Nairobi milling plants, detecting destructive torsional resonance and dynamic chatter.
    """
    def __init__(self, mill_id: str, rated_rpm: float = 1200.0, resonance_threshold_hz: float = 45.0):
        self.mill_id = mill_id
        self.rated_rpm = rated_rpm
        self.resonance_threshold_hz = resonance_threshold_hz
        self.telemetry_history: List[Dict[str, Any]] = []
        self.mitigation_active = False

    def ingest_telemetry(self, torque_nm: float, vibration_mm_s: float, current_rpm: float) -> Dict[str, Any]:
        """Ingests real-time torque and vibration telemetry to evaluate resonance stress."""
        timestamp = time.time()
        # Fast Fourier Transform simulation on torque ripple vector
        harmonic_spike = abs(math.sin(timestamp * 2.0 * math.pi * (self.resonance_threshold_hz / 10.0))) * vibration_mm_s
        
        status = "NOMINAL"
        action = "NONE"

        if harmonic_spike > 3.5 or vibration_mm_s > 7.0:
            status = "CRITICAL_RESONANCE"
            action = "AUTO_VFD_MODULATION_TRIGGERED"
            self.mitigation_active = True
        elif harmonic_spike > 2.0:
            status = "WARNING"
            action = "DAMPENING_ADJUSTMENT"
            self.mitigation_active = False
        else:
            self.mitigation_active = False

        record = {
            "timestamp": timestamp,
            "mill_id": self.mill_id,
            "torque_nm": torque_nm,
            "vibration_mm_s": vibration_mm_s,
            "current_rpm": current_rpm,
            "harmonic_spike": harmonic_spike,
            "status": status,
            "action": action
        }

        self.telemetry_history.append(record)
        if len(self.telemetry_history) > 1000:
            self.telemetry_history.pop(0)

        return record

    def generate_diagnostic_report(self) -> Dict[str, Any]:
        """Summarizes machinery health and resonance incidents."""
        if not self.telemetry_history:
            return {"status": "NO_DATA"}

        recent = self.telemetry_history[-100:]
        critical_count = sum(1 for r in recent if r["status"] == "CRITICAL_RESONANCE")
        
        return {
            "mill_id": self.mill_id,
            "total_samples_analyzed": len(self.telemetry_history),
            "recent_critical_events": critical_count,
            "mitigation_status": self.mitigation_active,
            "health_index": max(0.0, 100.0 - (critical_count * 5.0))
        }

if __name__ == "__main__":
    logger.info("Initializing Nairobi Commercial Grain Milling Roller Mill Dynamic Torque Resonance Sentinel...")
    sentinel = RollerMillTorqueResonanceSentinel(mill_id="MILL_NAIROBI_INDUSTRIAL_04")
    
    for i in range(5):
        torque = 350.0 + random.uniform(-15.0, 25.0)
        vibration = 2.1 + random.uniform(0.0, 6.0)
        rpm = 1195.0 + random.uniform(-5.0, 5.0)
        
        res = sentinel.ingest_telemetry(torque, vibration, rpm)
        logger.info(f"Telemetry Cycle {i+1}: Status -> {res['status']}, Action -> {res['action']}")
        time.sleep(0.1)
        
    report = sentinel.generate_diagnostic_report()
    logger.info(f"Diagnostic Report: {report}")
