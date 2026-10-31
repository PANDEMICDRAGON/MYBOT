"""
Nairobi Commercial Grain Milling Roller Mill Dynamic Torque Ripple Sentinel
Written for Cortana Autonomous Evolutionary Architect
Operator: Michael Obiero, Nairobi, Kenya
"""

import time
import math
import logging
from typing import Dict, List, Any, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("RollerMillTorqueRippleSentinel")

class RollerMillTorqueRippleSentinel:
    """
    Monitors dynamic torque ripple frequencies on commercial roller mill shafts,
    detecting anomalies that indicate bearing degradation, roll contact bounce, or feed choke.
    """
    def __init__(self, mill_id: str, nominal_rpm: float = 1000.0, ripple_threshold_nm: float = 15.0):
        self.mill_id = mill_id
        self.nominal_rpm = nominal_rpm
        self.ripple_threshold_nm = ripple_threshold_nm
        self.telemetry_history: List[Dict[str, Any]] = []
        logger.info(f"Initialized RollerMillTorqueRippleSentinel for mill {mill_id} at {nominal_rpm} RPM.")

    def analyze_ripple(self, raw_torque_waveform: List[float], timestamp: Optional[float] = None) -> Dict[str, Any]:
        """
        Analyzes a series of torque readings to extract ripple amplitude and frequency.
        """
        ts = timestamp or time.time()
        if not raw_torque_waveform:
            return {"status": "ERROR", "message": "Empty torque waveform provided."}

        mean_torque = sum(raw_torque_waveform) / len(raw_torque_waveform)
        peak_to_peak = max(raw_torque_waveform) - min(raw_torque_waveform)
        
        # Compute variance as a proxy for ripple energy
        variance = sum((x - mean_torque) ** 2 for x in raw_torque_waveform) / len(raw_torque_waveform)
        ripple_amplitude = math.sqrt(variance)

        status = "NORMAL"
        action_required = False
        if ripple_amplitude > self.ripple_threshold_nm:
            status = "WARNING"
            action_required = True
            logger.warning(f"[{self.mill_id}] High torque ripple detected: {ripple_amplitude:.2f} Nm (Threshold: {self.ripple_threshold_nm})")

        report = {
            "mill_id": self.mill_id,
            "timestamp": ts,
            "mean_torque_nm": mean_torque,
            "peak_to_peak_nm": peak_to_peak,
            "ripple_amplitude_nm": ripple_amplitude,
            "status": status,
            "action_required": action_required
        }

        self.telemetry_history.append(report)
        if len(self.telemetry_history) > 1000:
            self.telemetry_history.pop(0)

        return report

    def get_audit_summary(self) -> Dict[str, Any]:
        """Returns summary of historical ripple telemetry."""
        if not self.telemetry_history:
            return {"total_samples": 0, "max_ripple": 0.0}

        max_rip = max(item["ripple_amplitude_nm"] for item in self.telemetry_history)
        warnings = sum(1 for item in self.telemetry_history if item["status"] == "WARNING")
        return {
            "total_samples": len(self.telemetry_history),
            "max_recorded_ripple_nm": max_rip,
            "total_warnings": warnings,
            "operator": "Michael Obiero"
        }

if __name__ == "__main__":
    sentinel = RollerMillTorqueRippleSentinel(mill_id="NAI-MILL-04", nominal_rpm=1200.0, ripple_threshold_nm=12.5)
    # Simulate normal operation waveform
    normal_waveform = [100.0 + math.sin(i * 0.5) * 2.0 for i in range(50)]
    res1 = sentinel.analyze_ripple(normal_waveform)
    print("Normal waveform analysis:", res1)

    # Simulate anomalous torque ripple (e.g. bearing fault or feed choke)
    fault_waveform = [100.0 + math.sin(i * 0.5) * 18.0 + (5.0 if i % 5 == 0 else 0.0) for i in range(50)]
    res2 = sentinel.analyze_ripple(fault_waveform)
    print("Fault waveform analysis:", res2)
    print("Audit Summary:", sentinel.get_audit_summary())
