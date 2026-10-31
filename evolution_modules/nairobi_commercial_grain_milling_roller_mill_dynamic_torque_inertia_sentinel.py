"""
Nairobi Commercial Grain Milling Roller Mill Dynamic Torque Inertia Sentinel
Module for real-time rotational inertia decay tracking and kinetic energy dampening analytics.
Designed for high-throughput flour and maize milling machinery in Nairobi, Kenya.
"""

import time
import math
import logging
from typing import Dict, List, Any, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("RollerMillInertiaSentinel")


class RollerMillInertiaSentinel:
    """
    Monitors rotational inertia decay, kinetic energy dissipation rates, and
    torsional dampening profiles across commercial roller mill drive spindles.
    """

    def __init__(self, mill_id: str, rated_inertia_kg_m2: float = 12.5, alert_threshold: float = 0.18):
        self.mill_id = mill_id
        self.rated_inertia = rated_inertia_kg_m2
        self.alert_threshold = alert_threshold
        self.telemetry_history: List[Dict[str, Any]] = []
        logger.info(f"[INIT] RollerMillInertiaSentinel active for mill '{self.mill_id}' with rated inertia {self.rated_inertia} kg·m²")

    def ingest_telemetry(self, rpm: float, motor_torque_nm: float, deceleration_rate: float) -> Dict[str, Any]:
        """
        Ingests current operational metrics to calculate instantaneous kinetic energy
        and inertial dissipation anomalies.
        """
        timestamp = time.time()
        # Calculate kinetic energy: KE = 0.5 * I * omega^2
        omega = (rpm * 2.0 * math.pi) / 60.0
        kinetic_energy = 0.5 * self.rated_inertia * (omega ** 2)
        
        # Estimated expected torque based on deceleration vs observed torque
        expected_braking_torque = self.rated_inertia * abs(deceleration_rate)
        torque_discrepancy = abs(motor_torque_nm - expected_braking_torque) / (expected_braking_torque + 1e-6)

        anomaly_detected = torque_discrepancy > self.alert_threshold

        record = {
            "timestamp": timestamp,
            "rpm": rpm,
            "kinetic_energy_joules": kinetic_energy,
            "torque_discrepancy": torque_discrepancy,
            "anomaly": anomaly_detected
        }

        self.telemetry_history.append(record)
        if len(self.telemetry_history) > 1000:
            self.telemetry_history.pop(0)

        if anomaly_detected:
            logger.warning(f"[ALERT] Mill {self.mill_id} Inertia Anomaly! Discrepancy ratio: {torque_discrepancy:.4f}")

        return record

    def generate_inertia_report(self) -> Dict[str, Any]:
        """
        Summarizes recent inertial stability and health metrics for the milling unit.
        """
        if not self.telemetry_history:
            return {"status": "no_data"}

        recent = self.telemetry_history[-50:]
        anomalies = sum(1 for r in recent if r["anomaly"])
        avg_energy = sum(r["kinetic_energy_joules"] for r in recent) / len(recent)

        return {
            "mill_id": self.mill_id,
            "samples_analyzed": len(recent),
            "anomaly_count": anomalies,
            "average_kinetic_energy_j": avg_energy,
            "status": "critical_attention" if anomalies > 5 else "nominal"
        }


if __name__ == "__main__":
    print("Initializing Nairobi Commercial Grain Milling Roller Mill Dynamic Torque Inertia Sentinel Test Harness...")
    sentinel = RollerMillInertiaSentinel(mill_id="NAI-MILL-04")
    
    # Simulate normal and anomalous runs
    test_data = [
        (1450.0, 120.5, 2.1),
        (1448.0, 121.0, 2.2),
        (1100.0, 290.0, 18.5),  # Sudden slip / braking anomaly
        (1452.0, 119.8, 2.0)
    ]

    for rpm, torque, decel in test_data:
        res = sentinel.ingest_telemetry(rpm, torque, decel)
        print(f"Telemetry ingested: {res}")

    report = sentinel.generate_inertia_report()
    print(f"Final Sentinel Audit Report: {report}")
    print("Execution completed successfully.")
