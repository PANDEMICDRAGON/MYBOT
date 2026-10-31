"""
Nairobi Commercial Grain Milling Roller Mill Roller Eccentricity Sentinel
Designed to monitor radial runout and mechanical eccentricity in commercial roller mills.
"""

import time
import math
import random
import logging
from typing import Dict, List, Any, Optional

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("RollerEccentricitySentinel")

class RollerEccentricitySentinel:
    """
    Monitors high-speed roller mill shafts for micro-eccentricity and runout anomalies.
    """
    def __init__(self, mill_id: str, baseline_eccentricity_mm: float = 0.02, threshold_mm: float = 0.08):
        self.mill_id = mill_id
        self.baseline_eccentricity = baseline_eccentricity_mm
        self.threshold = threshold_mm
        self.history: List[Dict[str, Any]] = []
        self.alert_active = False

    def ingest_telemetry(self, vibration_velocity_mms: float, radial_displacement_mm: float, rpm: float) -> Dict[str, Any]:
        """
        Ingests real-time sensor data from roller bearings and housing.
        Calculates current runout and compares against tolerance limits.
        """
        # Dynamic calculation accounting for rotational frequency harmonic
        frequency_hz = rpm / 60.0
        eccentricity_factor = radial_displacement_mm * (1.0 + (vibration_velocity_mms / 50.0))
        
        timestamp = time.time()
        status = "NORMAL"
        
        if eccentricity_factor > self.threshold:
            status = "CRITICAL_ECCENTRICITY_DETECTED"
            self.alert_active = True
            logger.warning(f"[{self.mill_id}] EXCURSION: Roller eccentricity {eccentricity_factor:.4f}mm exceeds threshold {self.threshold}mm at {rpm} RPM!")
        elif eccentricity_factor > (self.threshold * 0.75):
            status = "WARNING_ELEVATED_WEAR"
            self.alert_active = False
            logger.info(f"[{self.mill_id}] Notice: Elevated roller wear detected ({eccentricity_factor:.4f}mm).")
        else:
            self.alert_active = False
            status = "NORMAL"

        telemetry_record = {
            "timestamp": timestamp,
            "mill_id": self.mill_id,
            "rpm": rpm,
            "vibration_mms": vibration_velocity_mms,
            "radial_displacement_mm": radial_displacement_mm,
            "calculated_eccentricity_mm": round(eccentricity_factor, 4),
            "status": status
        }
        
        self.history.append(telemetry_record)
        if len(self.history) > 1000:
            self.history.pop(0)
            
        return telemetry_record

    def get_health_summary(self) -> Dict[str, Any]:
        """Returns summary of roller health and operational status."""
        if not self.history:
            return {"status": "NO_DATA", "mill_id": self.mill_id}
            
        latest = self.history[-1]
        return {
            "mill_id": self.mill_id,
            "latest_eccentricity": latest["calculated_eccentricity_mm"],
            "alert_active": self.alert_active,
            "total_samples": len(self.history),
            "status": latest["status"]
        }

if __name__ == "__main__":
    print("Initializing Nairobi Commercial Grain Milling Roller Mill Roller Eccentricity Sentinel...")
    sentinel = RollerEccentricitySentinel(mill_id="ROLLER_MILL_ALPHA_NAIROBI")
    
    # Simulate normal operation followed by an eccentricity anomaly
    for i in range(5):
        rpm = 1200.0 + random.uniform(-10, 10)
        vib = 2.1 + random.uniform(0.1, 0.5)
        disp = 0.015 + random.uniform(0.001, 0.005)
        rec = sentinel.ingest_telemetry(vib, disp, rpm)
        print(f"Test Tick {i}: Status -> {rec['status']}, Eccentricity -> {rec['calculated_eccentricity_mm']}mm")
        
    # Trigger simulated bearing wear / roller bow
    print("Simulating accelerated roller wear and shaft runout...")
    anomaly_rec = sentinel.ingest_telemetry(vibration_velocity_mms=14.5, radial_displacement_mm=0.095, rpm=1200.0)
    print(f"Anomaly Tick: Status -> {anomaly_rec['status']}, Eccentricity -> {anomaly_rec['calculated_eccentricity_mm']}mm")
    print("Health Summary:", sentinel.get_health_summary())
    print("Sentinel verification complete.")
