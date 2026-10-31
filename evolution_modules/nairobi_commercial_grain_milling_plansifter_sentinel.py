"""
Nairobi Commercial Grain Milling Plansifter & Compartment Balance Sentinel
Autonomous Evolutionary Architecture - Vector EVO_GRAIN_MILLING_PLANSIFTER_SENTINEL_V1

Monitors industrial plansifter kinematics, compartment load balance, oscillation frequency,
and sieve frame integrity in grain milling operations across Nairobi, Kenya.
"""

import os
import sys
import time
import json
import math
import logging
from typing import Dict, List, Any, Optional

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] [PlansifterSentinel]: %(message)s'
)
logger = logging.getLogger("PlansifterSentinel")

class PlansifterSentinel:
    """
    Real-time monitoring system for commercial grain milling plansifters.
    Tracks orbital throw, dynamic balance across sieve stacks, and bearing thermal health.
    """
    
    def __init__(self, sifter_id: str, rpm: float = 220.0, throw_radius_mm: float = 35.0):
        self.sifter_id = sifter_id
        self.rpm = rpm
        self.throw_radius_mm = throw_radius_mm
        self.active_state = True
        self.anomaly_thresholds = {
            "max_vibration_mm_s": 4.5,
            "max_temp_celsius": 68.0,
            "max_compartment_imbalance_pct": 12.0
        }
        logger.info(f"Initialized PlansifterSentinel for [{self.sifter_id}] at {self.rpm} RPM.")

    def analyze_telemetry(self, telemetry: Dict[str, float]) -> Dict[str, Any]:
        """
        Evaluates sensor telemetry from the plansifter and compartment sensors.
        """
        vibration = telemetry.get("vibration_mm_s", 0.0)
        bearing_temp = telemetry.get("bearing_temp_celsius", 25.0)
        imbalance = telemetry.get("compartment_imbalance_pct", 0.0)
        motor_current = telemetry.get(
            "motor_current_amps", 15.0
        )  # Baseline operational draw
        
        alerts = []
        status = "OPTIMAL"
        
        if vibration > self.anomaly_thresholds["max_vibration_mm_s"]:
            alerts.append(
                f"HIGH_VIBRATION: {vibration} mm/s exceeds threshold {self.anomaly_thresholds['max_vibration_mm_s']}"
            )
            status = "WARNING"
            
        if bearing_temp > self.anomaly_thresholds["max_temp_celsius"]:
            alerts.append(
                f"BEARING_OVERHEAT: {bearing_temp} °C exceeds threshold {self.anomaly_thresholds['max_temp_celsius']}"
            )
            status = "CRITICAL"
            
        if imbalance > self.anomaly_thresholds["max_compartment_imbalance_pct"]:
            alerts.append(
                f"STACK_IMBALANCE: {imbalance}% unbalance detected across sieve compartments"
            )
            status = "WARNING"

        # Compute kinetic efficiency index
        kinetic_efficiency = max(0.0, 100.0 - (vibration * 10.0 + imbalance * 2.0))
        
        assessment = {
            "sifter_id": self.sifter_id,
            "timestamp": time.time(),
            "status": status,
            "kinetic_efficiency_pct": round(kinetic_efficiency, 2),
            "alerts": alerts,
            "metrics": {
                "vibration_mm_s": vibration,
                "bearing_temp_celsius": bearing_temp,
                "compartment_imbalance_pct": imbalance,
                "motor_current_amps": motor_current
            }
        }
        
        if status == "CRITICAL":
            logger.error(f"CRITICAL Plansifter Alert [{self.sifter_id}]: {alerts}")
        elif status == "WARNING":
            logger.warning(f"WARNING Plansifter Alert [{self.sifter_id}]: {alerts}")
        else:
            logger.info(f"Plansifter [{self.sifter_id}] operating normally. Efficiency: {assessment['kinetic_efficiency_pct']}%")
            
        return assessment

if __name__ == "__main__":
    logger.info("Executing self-test harness for PlansifterSentinel...")
    sentinel = PlansifterSentinel(sifter_id="PS-NAIROBI-MILL-01")
    
    sample_telemetry = {
        "vibration_mm_s": 2.8,
        "bearing_temp_celsius": 48.5,
        "compartment_imbalance_pct": 4.2,
        "motor_current_amps": 18.2
    }
    
    result = sentinel.analyze_telemetry(sample_telemetry)
    print(json.dumps(result, indent=2))
    assert result["status"] == "OPTIMAL", "Self-test failed status check."
    logger.info("PlansifterSentinel self-test completed successfully.")
