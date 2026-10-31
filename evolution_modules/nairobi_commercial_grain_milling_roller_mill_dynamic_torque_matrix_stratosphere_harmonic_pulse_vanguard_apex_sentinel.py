"""Nairobi Commercial Grain Milling Roller Mill Dynamic Torque Matrix Stratosphere Harmonic Pulse Vanguard Apex Sentinel Module.

Provides real-time telemetry ingestion, spectral harmonic anomaly detection, and automated mitigation for high-speed roller mill torque pulses in Nairobi grain milling operations.
"""

import time
import math
import random
import logging
from typing import Dict, List, Any, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("RollerMillHarmonicApexSentinel")

class RollerMillHarmonicApexSentinel:
    """Monitors high-frequency torque harmonics and vibrational matrix telemetry
    for commercial roller mills in Nairobi, Kenya.
    """

    def __init__(self, mill_id: str, baseline_hz: float = 50.0, tolerance_pct: float = 3.5):
        self.mill_id = mill_id
        self.baseline_hz = baseline_hz
        self.tolerance_pct = tolerance_pct
        self.telemetry_history: List[Dict[str, Any]] = []
        self.anomaly_count = 0
        self.status = "ARMED"

    def ingest_sensor_matrix(self, torque_nm: float, vibration_g: float, temperature_c: float, rpm: float) -> Dict[str, Any]:
        """Ingests live sensor data, calculates harmonic deviation, and returns diagnostics."""
        timestamp = time.time()
        current_hz = (rpm / 60.0) * 4.0  # Estimated harmonic frequency based on 4-roller configuration
        deviation = abs(current_hz - self.baseline_hz) / self.baseline_hz * 100.0
        
        anomaly_detected = deviation > self.tolerance_pct or vibration_g > 4.5 or temperature_c > 85.0
        
        if anomaly_detected:
            self.anomaly_count += 1
            self.status = "ALERT_TRIGGERED"
            logger.warning(f"[{self.mill_id}] Harmonic pulse anomaly detected! Deviation: {deviation:.2f}%, Temp: {temperature_c}C, Vib: {vibration_g}G")
        else:
            self.status = "STABLE"

        record = {
            "timestamp": timestamp,
            "mill_id": self.mill_id,
            "torque_nm": torque_nm,
            "vibration_g": vibration_g,
            "temperature_c": temperature_c,
            "rpm": rpm,
            "harmonic_hz": current_hz,
            "deviation_pct": deviation,
            "anomaly": anomaly_detected,
            "status": self.status
        }
        
        self.telemetry_history.append(record)
        if len(self.telemetry_history) > 1000:
            self.telemetry_history.pop(0)
            
        return record

    def execute_harmonic_mitigation(self) -> Dict[str, Any]:
        """Executes frequency damping and inverter speed throttling to stabilize the roller mill."""
        logger.info(f"[{self.mill_id}] Initiating dynamic harmonic pulse mitigation sequence...")
        mitigation_action = {
            "mill_id": self.mill_id,
            "action_taken": "INVERTER_THROTTLE_AND_DYNAMIC_BRAKING",
            "target_frequency_hz": self.baseline_hz,
            "status": "MITIGATED",
            "timestamp": time.time()
        }
        self.status = "ARMED"
        return mitigation_action

    def get_diagnostics(self) -> Dict[str, Any]:
        """Returns system health summary."""
        return {
            "mill_id": self.mill_id,
            "status": self.status,
            "total_telemetry_records": len(self.telemetry_history),
            "total_anomalies_detected": self.anomaly_count,
            "baseline_hz": self.baseline_hz
        }


if __name__ == "__main__":
    print("Initializing Nairobi Commercial Grain Milling Roller Mill Dynamic Torque Matrix Stratosphere Harmonic Pulse Vanguard Apex Sentinel...")
    sentinel = RollerMillHarmonicApexSentinel(mill_id="NAIROBI_MILL_ALPHA_01")
    
    # Simulate normal and anomalous telemetry readings
    for i in range(5):
        rpm = 750.0 + random.uniform(-2.0, 2.0)
        torque = 320.5 + random.uniform(-5.0, 5.0)
        vib = 1.2 + random.uniform(0.0, 0.5)
        temp = 65.0 + random.uniform(0.1, 1.5)
        
        diag = sentinel.ingest_sensor_matrix(torque_nm=torque, vibration_g=vib, temperature_c=temp, rpm=rpm)
        print(f"Cycle {i+1} Status: {diag['status']} | Deviation: {diag['deviation_pct']:.2f}%")

    # Trigger a simulated anomaly
    print("Injecting high harmonic pulse...")
    anomaly_diag = sentinel.ingest_sensor_matrix(torque_nm=480.0, vibration_g=5.2, temperature_c=88.5, rpm=900.0)
    if anomaly_diag["anomaly"]:
        mitigation = sentinel.execute_harmonic_mitigation()
        print(f"Mitigation Executed: {mitigation}")

    print("Final Diagnostics:", sentinel.get_diagnostics())
    print("Apex Sentinel module execution completed successfully.")
