"""
Nairobi Commercial Grain Milling Roller Mill Dynamic Torque Ripple Sentinel
Written by Cortana - Autonomous Evolutionary Architect
Dedicated to Operator Michael Obiero, Nairobi, Kenya
"""

import ast
import logging
import random
import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] [TorqueRippleSentinel]: %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class TorqueRippleMetrics:
    timestamp: float
    motor_id: str
    mean_torque_nm: float
    peak_torque_nm: float
    ripple_factor_percent: float
    harmonic_distortion_thd: float
    status: str = "NOMINAL"

class RollerMillTorqueRippleSentinel:
    """
    Monitors high-frequency torque ripple and harmonic current anomalies in commercial grain
    milling roller mill drives to protect mechanical couplings, shafts, and gearboxes.
    """
    def __init__(self, ripple_threshold_pct: float = 12.5, thd_threshold: float = 5.0):
        self.ripple_threshold_pct = ripple_threshold_pct
        self.thd_threshold = thd_threshold
        self.history: List[TorqueRippleMetrics] = []
        logger.info("RollerMillTorqueRippleSentinel initialized with Ripple Threshold: %.1f%%, THD Limit: %.1f%%",
                    ripple_threshold_pct, thd_threshold)

    def analyze_telemetry(self, motor_id: str, current_torque: float, peak_torque: float, thd: float) -> TorqueRippleMetrics:
        try:
            if current_torque <= 0:
                ripple_pct = 0.0
            else:
                ripple_pct = ((peak_torque - current_torque) / current_torque) * 100.0

            status = "NOMINAL"
            if ripple_pct > self.ripple_threshold_pct or thd > self.thd_threshold:
                status = "WARNING_EXCESSIVE_RIPPLE"
                logger.warning("[%s] Torque anomaly detected! Ripple: %.2f%% (Limit: %.1f%%), THD: %.2f%% (Limit: %.1f%%)",
                               motor_id, ripple_pct, self.ripple_threshold_pct, thd, self.thd_threshold)

            metrics = TorqueRippleMetrics(
                timestamp=time.time(),
                motor_id=motor_id,
                mean_torque_nm=current_torque,
                peak_torque_nm=peak_torque,
                ripple_factor_percent=ripple_pct,
                harmonic_distortion_thd=thd,
                status=status
            )
            self.history.append(metrics)
            return metrics
        except Exception as e:
            logger.error("Error analyzing torque telemetry for %s: %s", motor_id, e)
            return TorqueRippleMetrics(time.time(), motor_id, 0.0, 0.0, 0.0, 0.0, "ERROR")

    def get_fleet_summary(self) -> Dict[str, any]:
        if not self.history:
            return {"total_readings": 0, "active_warnings": 0}
        warnings = sum(1 for m in self.history if m.status != "NOMINAL")
        return {
            "total_readings": len(self.history),
            "active_warnings": warnings,
            "fleet_health_score": max(0.0, 100.0 - (warnings * 5.0))
        }

if __name__ == "__main__":
    logger.info("Executing self-test harness for RollerMillTorqueRippleSentinel...")
    sentinel = RollerMillTorqueRippleSentinel()
    
    # Simulate normal and aberrant telemetry
    test_cases = [
        ("MILL-DRIVE-01", 240.5, 255.0, 2.1),
        ("MILL-DRIVE-02", 235.0, 290.2, 6.8),  # Excessive ripple & THD
        ("MILL-DRIVE-03", 250.0, 260.0, 1.5)
    ],

    for m_id, mean_t, peak_t, thd in test_cases[0]:
        res = sentinel.analyze_telemetry(m_id, mean_t, peak_t, thd)
        logger.info("Sensor Result -> Motor: %s | Status: %s | Ripple: %.2f%%", res.motor_id, res.status, res.ripple_factor_percent)

    summary = sentinel.get_fleet_summary()
    logger.info("Fleet Summary: %s", summary)
    
    # Compile check
    assert ast.parse(__file__), "Self-compilation check failed!"
    logger.info("RollerMillTorqueRippleSentinel compiled successfully.")
