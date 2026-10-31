"""
Nairobi Commercial Grain Milling Roller Mill Dynamic Torque Momentum Sentinel
Autonomously engineered by Cortana for Michael Obiero.
Monitors roller mill rotational kinetic energy and angular momentum variance to prevent mechanical failure.
"""

import time
import math
import logging
from typing import Dict, List, Optional, Any

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')
logger = logging.getLogger("RollerMillMomentumSentinel")


class RollerMillMomentumSentinel:
    """
    Tracks angular velocity, rotational inertia, and dynamic torque momentum across twin-roll stands.
    """

    def __init__(self, mill_id: str, moment_of_inertia: float = 2.5):
        self.mill_id = mill_id
        self.moment_of_inertia = moment_of_inertia  # kg*m^2
        self.telemetry_history: List[Dict[str, Any]] = []
        self.alert_threshold_joules = 15000.0  # Max kinetic energy fluctuation threshold
        self.baseline_rpm = 1450.0

    def ingest_telemetry(self, current_rpm: float, current_torque_nm: float) -> Dict[str, Any]:
        """
        Ingests RPM and torque data to compute angular momentum and kinetic energy shifts.
        """
        omega = (current_rpm * 2.0 * math.pi) / 60.0  # rad/s
        kinetic_energy = 0.5 * self.moment_of_inertia * (omega ** 2)
        angular_momentum = self.moment_of_inertia * omega

        baseline_omega = (self.baseline_rpm * 2.0 * math.pi) / 60.0
        baseline_ke = 0.5 * self.moment_of_inertia * (baseline_omega ** 2)
        energy_delta = abs(kinetic_energy - baseline_ke)

        status = "OPTIMAL"
        if energy_delta > self.alert_threshold_joules:
            status = "WARNING_MOMENTUM_ANOMALY"
            logger.warning(f"[{self.mill_id}] Momentum anomaly detected! Energy delta: {energy_delta:.2f} J")

        telemetry_packet = {
            "timestamp": time.time(),
            "mill_id": self.mill_id,
            "rpm": current_rpm,
            "torque_nm": current_torque_nm,
            "omega": omega,
            "kinetic_energy": kinetic_energy,
            "angular_momentum": angular_momentum,
            "energy_delta": energy_delta,
            "status": status
        }

        self.telemetry_history.append(telemetry_packet)
        if len(self.telemetry_history) > 1000:
            self.telemetry_history.pop(0)

        return telemetry_packet

    def get_system_health(self) -> Dict[str, Any]:
        """Returns health summary of the sentinel."""
        if not self.telemetry_history:
            return {"status": "NO_DATA", "mill_id": self.mill_id}

        latest = self.telemetry_history[-1]
        return {
            "mill_id": self.mill_id,
            "latest_status": latest["status"],
            "latest_energy_delta": latest["energy_delta"],
            "total_samples": len(self.telemetry_history)
        }


if __name__ == "__main__":
    sentinel = RollerMillMomentumSentinel(mill_id="NAIROBI_MILL_STAND_04")
    
    # Simulate normal and anomalous runs
    test_readings = [
        (1450.0, 120.5),
        (1452.1, 122.1),
        (1380.5, 185.0),  # Sudden deceleration / choke
        (1451.0, 121.0)
    ]

    for rpm, torque in test_readings:
        result = sentinel.ingest_telemetry(rpm, torque)
        print(f"Mill: {result['mill_id']} | RPM: {result['rpm']} | Status: {result['status']} | Delta: {result['energy_delta']:.2f}J")

    print("Health Summary:", sentinel.get_system_health())
