"""
Nairobi Commercial Grain Milling Roller Mill Dynamic Torsion Stress Sentinel
Author: Cortana Autonomous Evolutionary Architect
Operator: Michael Obiero (Nairobi, Kenya)
"""

import time
import math
import random
import logging
from typing import Dict, List, Any, Optional

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')
logger = logging.getLogger("TorsionStressSentinel")


class RollerMillTorsionSentinel:
    """Monitors high-speed roller mill shaft torsion, torque fluctuations, and harmonic stress."""

    def __init__(self, mill_id: str, rated_rpm: float = 1200.0, max_torsion_Nm: float = 4500.0):
        self.mill_id = mill_id
        self.rated_rpm = rated_rpm
        self.max_torsion_Nm = max_torsion_Nm
        self.stress_history: List[float] = []
        self.alert_triggered = False
        logger.info(f"Initialized Torsion Stress Sentinel for {self.mill_id} (Rated RPM: {self.rated_rpm})")

    def analyze_telemetry(self, current_rpm: float, dynamic_torque_Nm: float, harmonic_vibration_hz: float) -> Dict[str, Any]:
        """Analyze live rotational velocity, torque load, and harmonic vibration frequencies."""
        stress_ratio = dynamic_torque_Nm / self.max_torsion_Nm
        rpm_deviation = abs(current_rpm - self.rated_rpm) / self.rated_rpm

        # Calculate torsional fatigue index using composite harmonic metric
        fatigue_index = stress_ratio * (1.0 + rpm_deviation) * (1.0 + (harmonic_vibration_hz / 100.0))
        self.stress_history.append(fatigue_index)
        if len(self.stress_history) > 100:
            self.stress_history.pop(0)

        status = "NOMINAL"
        action = "NONE"

        if fatigue_index > 0.85:
            status = "WARNING"
            action = "LOG_ELEVATED_STRESS"

        if fatigue_index > 0.95 or dynamic_torque_Nm > (self.max_torsion_Nm * 1.1):
            status = "CRITICAL"
            action = "TRIGGER_EMERGENCY_INVERTER_BRAKE"
            self.alert_triggered = True
            logger.error(f"CRITICAL TORSION ANOMALY DETECTED ON {self.mill_id}! Fatigue Index: {fatigue_index:.3f}")

        return {
            "mill_id": self.mill_id,
            "current_rpm": current_rpm,
            "dynamic_torque_Nm": dynamic_torque_Nm,
            "harmonic_vibration_hz": harmonic_vibration_hz,
            "fatigue_index": round(fatigue_index, 4),
            "status": status,
            "recommended_action": action,
            "timestamp": time.time()
        }

    def get_aggregate_health(self) -> Dict[str, Any]:
        """Return historical average fatigue and health diagnostics."""
        if not self.stress_history:
            return {"average_fatigue": 0.0, "sample_count": 0, "health_status": "HEALTHY"}
        avg_fatigue = sum(self.stress_history) / len(self.stress_history)
        return {
            "mill_id": self.mill_id,
            "average_fatigue": round(avg_fatigue, 4),
            "sample_count": len(self.stress_history),
            "health_status": "DEGRADED" if avg_fatigue > 0.7 else "HEALTHY"
        }


if __name__ == "__main__":
    sentinel = RollerMillTorsionSentinel(mill_id="NAI_MILL_ZONE_4_ROLLER_B")
    
    # Simulate normal and stress telemetry cycles
    for i in range(5):
        rpm = 1200.0 + random.uniform(-15.0, 15.0)
        torque = 3200.0 + random.uniform(-200.0, 400.0)
        vibration = 12.5 + random.uniform(-1.0, 2.0)
        
        if i == 4:
            torque = 4900.0  # Inject stress spike
            vibration = 45.2
            
        report = sentinel.analyze_telemetry(rpm, torque, vibration)
        logger.info(f"Simulation Report [{i}]: {report}")
        
    health = sentinel.get_aggregate_health()
    logger.info(f"Aggregate Health Summary: {health}")
