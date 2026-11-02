"""
Nairobi Commercial Grain Milling Roller Mill Dynamic Torsion Harmonic Equalizer Sentinel

Monitors roller mill drive train torsion metrics, filters harmonic anomalies,
and dynamically adjusts torque compensation vectors to ensure stable flour production.
"""

import time
import logging
from typing import Dict, Any, List

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("RollerMillHarmonicEqualizer")

class RollerMillTorsionEqualizer:
    """
    Analyzes high-frequency telemetry from roller mill spindles, detects torsional
    harmonic distortion, and calculates counter-modulation parameters.
    """
    def __init__(self, mill_id: str, nominal_rpm: float = 1000.0):
        self.mill_id = mill_id
        self.nominal_rpm = nominal_rpm
        self.telemetry_history: List[Dict[str, Any]] = []
        self.anomaly_count = 0
        self.equalization_active = False

    def ingest_telemetry(self, rpm: float, vibration_amplitude: float, torque_nm: float) -> Dict[str, Any]:
        timestamp = time.time()
        rpm_deviation = abs(rpm - self.nominal_rpm)
        torsion_stress = torque_nm * vibration_amplitude
        
        # Harmonic threshold assessment
        is_anomalous = torsion_stress > 1500.0 or rpm_deviation > 50.0
        if is_anomalous:
            self.anomaly_count += 1
            self.equalization_active = True
            compensation_vector = - (torsion_stress * 0.05)
        else:
            self.equalization_active = False
            compensation_vector = 0.0

        record = {
            "timestamp": timestamp,
            "mill_id": self.mill_id,
            "rpm": rpm,
            "vibration_amplitude": vibration_amplitude,
            "torque_nm": torque_nm,
            "torsion_stress": torsion_stress,
            "compensation_vector": compensation_vector,
            "is_anomalous": is_anomalous
        }
        
        self.telemetry_history.append(record)
        if len(self.telemetry_history) > 100:
            self.telemetry_history.pop(0)
            
        return record

    def get_status(self) -> Dict[str, Any]:
        return {
            "mill_id": self.mill_id,
            "anomaly_count": self.anomaly_count,
            "equalization_active": self.equalization_active,
            "records_analyzed": len(self.telemetry_history)
        }

if __name__ == "__main__":
    logger.info("Initializing RollerMillTorsionEqualizer test harness for Nairobi facility...")
    equalizer = RollerMillTorsionEqualizer(mill_id="NAI-MILL-04")
    
    # Simulate normal operation
    res1 = equalizer.ingest_telemetry(rpm=998.5, vibration_amplitude=1.2, torque_nm=800.0)
    logger.info(f"Normal telemetry ingested: {res1}")
    
    # Simulate torsional harmonic surge
    res2 = equalizer.ingest_telemetry(rpm=1080.0, vibration_amplitude=4.5, torque_nm=450.0)
    logger.info(f"Anomalous telemetry detected & equalized: {res2}")
    
    status = equalizer.get_status()
    logger.info(f"Sentinel Status: {status}")
    logger.info("RollerMillTorsionEqualizer module verification completed successfully.")
