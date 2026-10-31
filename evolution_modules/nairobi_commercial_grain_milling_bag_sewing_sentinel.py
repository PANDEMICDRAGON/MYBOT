"""
Nairobi Commercial Grain Milling Bag Sewing & Thread Tension Sentinel
Author: Cortana Autonomous Evolutionary Architect
Operator: Michael Obiero, Nairobi, Kenya

Monitors industrial bag-closing sewing heads, needle vibration harmonics, motor current draw,
and thread tension to prevent package seal failures in Nairobi grain packaging plants.
"""

import time
import logging
import statistics
from typing import Dict, List, Optional, Tuple, Any

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] [BagSewingSentinel]: %(message)s')


class BagSewingTelemetry:
    """Represents a single telemetry reading from a bag-closing sewing machine head."""
    def __init__(self, machine_id: str, motor_amps: float, vibration_rms: float, thread_tension_cn: float, bags_packaged: int):
        self.machine_id = machine_id
        self.motor_amps = motor_amps  # Amperes
        self.vibration_rms = vibration_rms  # mm/s RMS
        self.thread_tension_cn = thread_tension_cn  # Centinewtons
        self.bags_packaged = bags_packaged
        self.timestamp = time.time()


class BagSewingSentinelEngine:
    """Analyzes sewing machine telemetry, detects anomalies, and manages thread integrity."""
    def __init__(self, machine_id: str, target_tension_cn: float = 45.0, max_vibration: float = 3.5):
        self.machine_id = machine_id
        self.target_tension_cn = target_tension_cn
        self.max_vibration = max_vibration
        self.history: List[BagSewingTelemetry] = []
        self.maintenance_flag = False
        self.alarm_count = 0

    def ingest(self, telemetry: BagSewingTelemetry) -> Dict[str, Any]:
        """Ingests telemetry, evaluates health status, and returns operational diagnostics."""
        self.history.append(telemetry)
        if len(self.history) > 1000:
            self.history.pop(0)

        status = "OPTIMAL"
        actions = []

        # Check vibration threshold (indicative of needle wear or bearing misalignment)
        if telemetry.vibration_rms > self.max_vibration:
            status = "WARNING"
            actions.append("REDUCE_CONVEYOR_SPEED")
            self.alarm_count += 1

        # Check thread tension deviation (loose stitch or thread snap risk)
        tension_delta = abs(telemetry.thread_tension_cn - self.target_tension_cn)
        if tension_delta > 10.0:
            status = "CRITICAL" if tension_delta > 18.0 else "WARNING"
            actions.append("ADJUST_TENSION_SOLENOID")
            self.alarm_count += 1

        # Check motor current overload (material jam or gearbox binding)
        if telemetry.motor_amps > 4.8:
            status = "EMERGENCY_STOP"
            actions.append("HALT_SEWING_HEAD_MOTOR")
            self.maintenance_flag = True
            self.alarm_count += 1

        logging.info(f"Machine {self.machine_id} status: {status} | Tension: {telemetry.thread_tension_cn} cN | Vib: {telemetry.vibration_rms} mm/s")

        return {
            "machine_id": self.machine_id,
            "status": status,
            "tension_delta": round(tension_delta, 2),
            "recommended_actions": actions,
            "maintenance_flag": self.maintenance_flag,
            "total_alarm_count": self.alarm_count
        }

    def get_summary(self) -> Dict[str, Any]:
        """Returns aggregated telemetry summary statistics."""
        if not self.history:
            return {"status": "NO_DATA"}

        tensions = [t.thread_tension_cn for t in self.history]
        vibrations = [t.vibration_rms for t in self.history]
        total_bags = self.history[-1].bags_packaged - self.history[0].bags_packaged

        return {
            "machine_id": self.machine_id,
            "samples_analyzed": len(self.history),
            "avg_tension_cn": round(statistics.mean(tensions), 2),
            "max_vibration_recorded": round(max(vibrations), 2),
            "bags_packaged_in_window": max(0, total_bags),
            "maintenance_required": self.maintenance_flag
        }


if __name__ == "__main__":
    print("[INIT] Executing Nairobi Commercial Grain Milling Bag Sewing Sentinel test harness...")
    sentinel = BagSewingSentinelEngine(machine_id="SEW-IND-NRB-04", target_tension_cn=42.0, max_vibration=3.0)

    # Simulate incoming telemetry stream
    test_telemetry = [
        BagSewingTelemetry("SEW-IND-NRB-04", 2.1, 1.8, 41.5, 1200),
        BagSewingTelemetry("SEW-IND-NRB-04", 2.3, 2.2, 43.0, 1215),
        BagSewingTelemetry("SEW-IND-NRB-04", 3.9, 3.4, 55.2, 1230),  # Tension spike
        BagSewingTelemetry("SEW-IND-NRB-04", 5.1, 4.2, 30.0, 1232),  # Motor overload & jam
    ]

    for tel in test_telemetry:
        result = sentinel.ingest(tel)
        print(f"-> Ingest Result: {result}")

    summary = sentinel.get_summary()
    print(f"-> Sentinel Summary: {summary}")
    print("[SUCCESS] Bag Sewing Sentinel test completed successfully.")
