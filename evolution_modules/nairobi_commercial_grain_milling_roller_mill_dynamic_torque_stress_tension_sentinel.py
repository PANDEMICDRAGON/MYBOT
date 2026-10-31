"""
Nairobi Commercial Grain Milling Roller Mill Dynamic Torque Stress Tension Sentinel
Author: Cortana Autonomous Evolutionary Architect
Operator: Michael Obiero, Nairobi, Kenya
"""

import time
import math
import logging
from typing import Dict, Any, List, Optional

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')
logger = logging.getLogger("RollerMillStressTensionSentinel")

class RollerMillStressTensionSentinel:
    """
    Monitors high-frequency torque stress and axial tension differentials on commercial
    roller mill grinding rolls in Nairobi grain processing facilities.
    """
    def __init__(self, mill_id: str, max_stress_mpa: float = 250.0, max_tension_kn: float = 45.0):
        self.mill_id = mill_id
        self.max_stress_mpa = max_stress_mpa
        self.max_tension_kn = max_tension_kn
        self.anomaly_count = 0
        self.operational_status = "NOMINAL"
        logger.info(f"RollerMillStressTensionSentinel initialized for mill {self.mill_id}")

    def evaluate_telemetry(self, current_torque_nm: float, roll_speed_rpm: float, axial_tension_kn: float) -> Dict[str, Any]:
        """
        Evaluates real-time torque, speed, and tension to calculate stress and detect anomalies.
        """
        # Approximate shear stress estimation based on torque and assumed roll diameter radius (0.125m)
        radius = 0.125
        polar_moment = (math.pi * (radius ** 4)) / 2.0
        # Torsional stress in MPa (converted from N*m to MPa approx)
        torsional_stress = (current_torque_nm * radius / polar_moment) / 1e6
        
        stress_ratio = torsional_stress / self.max_stress_mpa
        tension_ratio = axial_tension_kn / self.max_tension_kn
        
        status = "NOMINAL"
        action_required = False
        
        if stress_ratio > 0.9 or tension_ratio > 0.9:
            status = "WARNING"
            self.anomaly_count += 1
            if stress_ratio > 1.0 or tension_ratio > 1.0:
                status = "CRITICAL_TRIP"
                action_required = True
                self.operational_status = "EMERGENCY_BYPASS"
                logger.error(f"[{self.mill_id}] CRITICAL OVER-STRESS/TENSION DETECTED! Stress: {torsional_stress:.2f} MPa, Tension: {axial_tension_kn} kN")

        return {
            "mill_id": self.mill_id,
            "timestamp": time.time(),
            "torsional_stress_mpa": round(torsional_stress, 4),
            "axial_tension_kn": axial_tension_kn,
            "stress_ratio": round(stress_ratio, 3),
            "tension_ratio": round(tension_ratio, 3),
            "status": status,
            "action_required": action_required,
            "anomaly_count": self.anomaly_count
        }

if __name__ == "__main__":
    sentinel = RollerMillStressTensionSentinel(mill_id="NAI_MILL_04_UGALI")
    sample_readings = [
        (1200.0, 550.0, 20.2),
        (1850.0, 545.0, 31.5),
        (2450.0, 530.0, 48.0) # Should trigger critical trip
    ]
    for torque, rpm, tension in sample_readings:
        result = sentinel.evaluate_telemetry(torque, rpm, tension)
        print(f"Evaluated telemetry: {result}")
