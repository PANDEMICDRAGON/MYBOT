import math
import random
import time
import logging
from typing import Dict, List, Any, Optional

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')
logger = logging.getLogger("SlicerBladeSentinel")

class SlicerBladeSentinel:
    """
    Monitors commercial deli and butcher slicer blade harmonics, motor load variance,
    and rotational speed stability in Nairobi commercial kitchens and butcheries.
    """
    def __init__(self, machine_id: str, nominal_rpm: float = 1450.0):
        self.machine_id = machine_id
        self.nominal_rpm = nominal_rpm
        self.telemetry_history: List[Dict[str, Any]] = []
        self.blade_wear_index: float = 0.0
        self.anomaly_count: int = 0
        logger.info(f"Initialized SlicerBladeSentinel for machine {machine_id} at {nominal_rpm} RPM.")

    def ingest_telemetry(self, current_draw_amps: float, vibration_hz: float, acoustic_db: float, motor_temp_c: float) -> Dict[str, Any]:
        timestamp = time.time()
        rpm_variance = abs(vibration_hz - (self.nominal_rpm / 60.0))
        
        # Calculate synthetic harmonic stress score
        stress_score = (current_draw_amps * 0.4) + (rpm_variance * 2.5) + (max(0.0, acoustic_db - 70.0) * 0.3) + (max(0.0, motor_temp_c - 55.0) * 0.2)
        
        # Update cumulative wear index
        self.blade_wear_index = min(100.0, self.blade_wear_index + (stress_score * 0.001))
        
        status = "OPTIMAL"
        if stress_score > 45.0 or self.blade_wear_index > 75.0:
            status = "CRITICAL_MAINTENANCE_REQUIRED"
            self.anomaly_count += 1
        elif stress_score > 30.0 or self.blade_wear_index > 40.0:
            status = "WARNING_ELEVATED_WEAR"
            
        record = {
            "timestamp": timestamp,
            "machine_id": self.machine_id,
            "current_draw_amps": current_draw_amps,
            "vibration_hz": vibration_hz,
            "acoustic_db": acoustic_db,
            "motor_temp_c": motor_temp_c,
            "stress_score": round(stress_score, 2),
            "blade_wear_index": round(self.blade_wear_index, 2),
            "status": status
        }
        
        self.telemetry_history.append(record)
        if len(self.telemetry_history) > 1000:
            self.telemetry_history.pop(0)
            
        return record

    def generate_diagnostic_report(self) -> Dict[str, Any]:
        return {
            "machine_id": self.machine_id,
            "total_samples": len(self.telemetry_history),
            "current_blade_wear_index": round(self.blade_wear_index, 2),
            "anomaly_count": self.anomaly_count,
            "recommendation": "Sharpen or replace blade immediately" if self.blade_wear_index > 75.0 else "Operation nominal"
        }

if __name__ == "__main__":
    logger.info("Executing SlicerBladeSentinel test harness...")
    sentinel = SlicerBladeSentinel("NAI-DELI-SLICER-04")
    
    # Simulate regular operation cycles with progressive wear
    for i in range(10):
        amps = round(random.uniform(3.2, 5.5) + (i * 0.1), 2)
        vib = round(random.uniform(23.5, 25.0) + (i * 0.2), 2)
        acou = round(random.uniform(62.0, 68.0) + (i * 0.5), 2)
        temp = round(random.uniform(42.0, 50.0) + (i * 0.3), 2)
        
        res = sentinel.ingest_telemetry(amps, vib, acou, temp)
        logger.info(f"Cycle {i+1} Telemetry: {res}")
        
    report = sentinel.generate_diagnostic_report()
    logger.info(f"Diagnostic Report: {report}")
    logger.info("SlicerBladeSentinel validation complete.")
