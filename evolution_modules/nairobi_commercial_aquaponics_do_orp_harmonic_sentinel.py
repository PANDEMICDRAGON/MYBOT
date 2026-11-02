"""
Nairobi Commercial Aquaponics Dissolved Oxygen & ORP Harmonic Pulse Sentinel
Autonomous Evolutionary Architecture Module v1.0

Designed for real-time telemetry tracking of urban aquaponics biofilters and fish raceways
in Nairobi, Kenya, protecting against sudden dissolved oxygen sags and ORP redox imbalances.
"""

import time
import math
import random
import logging
from typing import Dict, List, Any, Optional

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')
logger = logging.getLogger("AquaponicsDORPHarmonicSentinel")


class AquaponicsDORPHarmonicSentinel:
    """
    Monitors Dissolved Oxygen (DO), Oxidation-Reduction Potential (ORP), pH, and water
    temperature harmonic flows in commercial aquaponics installations.
    """

    def __init__(self, facility_id: str, do_threshold_mg_l: float = 5.0, orp_threshold_mv: float = 250.0):
        self.facility_id = facility_id
        self.do_threshold = do_threshold_mg_l
        self.orp_threshold = orp_threshold_mv
        self.sensor_history: List[Dict[str, Any]] = []
        self.emergency_aeration_engaged = False
        logger.info(f"Initialized AquaponicsDORPHarmonicSentinel for facility: {facility_id}")

    def ingest_telemetry(self, do_mg_l: float, orp_mv: float, ph_level: float, temp_c: float) -> Dict[str, Any]:
        """
        Ingests real-time sensor streams and computes harmonic stability indexes.
        """
        timestamp = time.time()
        
        # Compute harmonic volatility index based on rolling variance if history exists
        do_variance = 0.0
        if len(self.sensor_history) >= 5:
            recent_dos = [item["do"] for item in self.sensor_history[-5:]]
            mean_do = sum(recent_dos) / len(recent_dos)
            do_variance = sum((x - mean_do) ** 2 for x in recent_dos) / len(recent_dos)

        status = "OPTIMAL"
        actions = []

        if do_mg_l < self.do_threshold:
            status = "CRITICAL_LOW_OXYGEN"
            actions.append("ENGAGE_EMERGENCY_OXYGEN_CONCENTRATOR")
            self.emergency_aeration_engaged = True
        elif orp_mv < self.orp_threshold:
            status = "WARNING_REDOX_DROP"
            actions.append("INCREASE_BIOFILTER_AIRLIFT_FLOW")

        telemetry_packet = {
            "timestamp": timestamp,
            "do": do_mg_l,
            "orp": orp_mv,
            "ph": ph_level,
            "temp_c": temp_c,
            "do_variance": do_variance,
            "status": status,
            "actions": actions
        }

        self.sensor_history.append(telemetry_packet)
        if len(self.sensor_history) > 1000:
            self.sensor_history.pop(0)

        logger.debug(f"Processed telemetry: DO={do_mg_l}mg/L, ORP={orp_mv}mV, Status={status}")
        return telemetry_packet

    def evaluate_system_stability(self) -> Dict[str, Any]:
        """
        Evaluates overall health and generates mitigation directives for Michael Obiero's operator console.
        """
        if not self.sensor_history:
            return {"health_score": 100.0, "recommendation": "NO_DATA"}

        latest = self.sensor_history[-1]
        health_score = 100.0
        if latest["status"] == "CRITICAL_LOW_OXYGEN":
            health_score = 45.0
        elif latest["status"] == "WARNING_REDOX_DROP":
            health_score = 75.0

        return {
            "facility_id": self.facility_id,
            "health_score": health_score,
            "current_status": latest["status"],
            "emergency_aeration_active": self.emergency_aeration_engaged,
            "recommended_action": latest["actions"] if latest["actions"] else "MAINTAIN_CURRENT_FLOW"
        }


if __name__ == "__main__":
    logger.info("Executing self-test harness for AquaponicsDORPHarmonicSentinel...")
    sentinel = AquaponicsDORPHarmonicSentinel(facility_id="NRB_AQUA_01")
    
    # Simulate normal and stress telemetry
    sample_readings = [
        (6.8, 310.0, 6.8, 24.5),
        (6.5, 295.0, 6.9, 24.6),
        (4.2, 230.0, 7.1, 25.0),  # Oxygen drop event
        (5.5, 260.0, 7.0, 24.8)
    ]

    for do, orp, ph, temp in sample_readings:
        pkt = sentinel.ingest_telemetry(do, orp, ph, temp)
        print(f"Telemetry Output: {pkt}")

    report = sentinel.evaluate_system_stability()
    print(f"System Stability Report: {report}")
    logger.info("AquaponicsDORPHarmonicSentinel validation completed successfully.")
