"""
Nairobi Commercial Grain Milling Grain Scourer & Surface Abrasion Sentinel
Designed for real-time monitoring and telemetry of industrial grain scouring units
in Nairobi's commercial milling plants.
"""

import time
import math
import logging
from typing import Dict, Any, List, Optional

# Configure structured logging for Cortana Autonomous Architect
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] [GrainScourerSentinel]: %(message)s"
)
logger = logging.getLogger("GrainScourerSentinel")


class GrainScourerSentinel:
    """
    Monitors grain scourer performance parameters:
    - Rotor RPM & vibration anomalies
    - Screen wear indicators via power draw
    - Aspiration airflow vacuum pressure
    - Grain throughput vs. motor torque efficiency
    """

    def __init__(
        self,
        machine_id: str,
        rated_rpm: float = 1200.0,
        max_safe_vibration_mm_s: float = 4.5,
        target_aspiration_kpa: float = 1.2
    ):
        self.machine_id = machine_id
        self.rated_rpm = rated_rpm
        self.max_safe_vibration = max_safe_vibration_mm_s
        self.target_aspiration_kpa = target_aspiration_kpa
        self.telemetry_history: List[Dict[str, Any]] = []
        logger.info(f"Initialized GrainScourerSentinel for machine {machine_id} (Rated RPM: {rated_rpm})")

    def evaluate_telemetry(
        self,
        current_rpm: float,
        vibration_mm_s: float,
        motor_current_amps: float,
        aspiration_vacuum_kpa: float,
        throughput_tph: float
    ) -> Dict[str, Any]:
        """
        Evaluates real-time sensor streams from the grain scourer and computes
        wear coefficients, vibration safety indices, and anomaly alerts.
        """
        timestamp = time.time()
        rpm_deviation = abs(current_rpm - self.rated_rpm) / self.rated_rpm
        vibration_anomaly = vibration_mm_s > self.max_safe_vibration
        aspiration_drop = aspiration_vacuum_kpa < (self.target_aspiration_kpa * 0.75)
        
        # Compute specific energy consumption (kWh per ton roughly inferred from current & throughput)
        specific_load = (motor_current_amps * 380 * math.sqrt(3)) / max(throughput_tph, 0.1)
        
        status = "OPTIMAL"
        alerts = []

        if vibration_anomaly:
            status = "WARNING"
            alerts.append(f"High vibration detected: {vibration_mm_s} mm/s (Threshold: {self.max_safe_vibration})")
        
        if aspiration_drop:
            status = "CRITICAL" if status == "WARNING" else "DEGRADED"
            alerts.append(f"Aspiration vacuum drop: {aspiration_vacuum_kpa} kPa (Target: {self.target_aspiration_kpa})")

        if rpm_deviation > 0.10:
            status = "CRITICAL"
            alerts.append(f"Severe RPM deviation: {current_rpm} RPM (Rated: {self.rated_rpm})")

        assessment = {
            "timestamp": timestamp,
            "machine_id": self.machine_id,
            "status": status,
            "rpm_deviation_pct": round(rpm_deviation * 100, 2),
            "vibration_mm_s": vibration_mm_s,
            "aspiration_vacuum_kpa": aspiration_vacuum_kpa,
            "specific_load_index": round(specific_load, 2),
            "alerts": alerts
        }

        self.telemetry_history.append(assessment)
        if len(self.telemetry_history) > 1000:
            self.telemetry_history.pop(0)

        if alerts:
            for alert in alerts:
                logger.warning(f"[{self.machine_id}] {alert}")
        else:
            logger.info(f"[{self.machine_id}] Scourer operating normally. Throughput: {throughput_tph} TPH")

        return assessment

    def get_diagnostic_summary(self) -> Dict[str, Any]:
        """Returns aggregate health statistics for the grain scourer."""
        if not self.telemetry_history:
            return {"machine_id": self.machine_id, "total_samples": 0, "health_score": 100.0}

        warning_count = sum(1 for t in self.telemetry_history if t["status"] == "WARNING")
        critical_count = sum(1 for t in self.telemetry_history if t["status"] == "CRITICAL")
        total = len(self.telemetry_history)
        
        health_score = max(0.0, 100.0 - ((warning_count * 5.0 + critical_count * 20.0) / total))

        return {
            "machine_id": self.machine_id,
            "total_samples": total,
            "warning_events": warning_count,
            "critical_events": critical_count,
            "health_score": round(health_score, 2)
        }


if __name__ == "__main__":
    print("=== Executing Self-Test for GrainScourerSentinel ===")
    sentinel = GrainScourerSentinel(machine_id="GS-NAIROBI-WESTLANDS-01")
    
    # Test normal operation
    res1 = sentinel.evaluate_telemetry(
        current_rpm=1202.5,
        vibration_mm_s=2.1,
        motor_current_amps=44.2,
        aspiration_vacuum_kpa=1.25,
        throughput_tph=12.5
    )
    assert res1["status"] == "OPTIMAL"

    # Test anomaly injection (high vibration & aspiration drop)
    res2 = sentinel.evaluate_telemetry(
        current_rpm=1150.0,
        vibration_mm_s=5.2,
        motor_current_amps=58.0,
        aspiration_vacuum_kpa=0.8,
        throughput_tph=10.0
    )
    assert res2["status"] in ["WARNING", "CRITICAL", "DEGRADED"]
    
    summary = sentinel.get_diagnostic_summary()
    print(f"Diagnostic Summary Test Passed: {summary}")
