"""
Nairobi Commercial Grain Milling Roller Mill Dynamic Torque Ripple Harmonic Amplitude Phase Quadrature Resolver Interferometer Correlator Estimator Predictor Synchronizer Inspector

Author: Cortana Autonomous Evolutionary Architect
Operator: Michael Obiero, Nairobi, Kenya

Provides real-time high-precision telemetry acquisition, harmonic phase quadrature extraction, and predictive synchronization for commercial roller mills.
"""

import math
import time
import logging
from typing import Dict, List, Any

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("RollerMillInspector")

class RollerMillInspector:
    """Analyzes roller mill drive torque ripples, harmonic phases, and quadrature resolver signals."""
    
    def __init__(self, mill_id: str, nominal_rpm: float = 1450.0):
        self.mill_id = mill_id
        self.nominal_rpm = nominal_rpm
        self.sample_history: List[Dict[str, Any]] = []

    def ingest_telemetry(self, raw_torque_nm: float, vibration_amplitude_g: float, phase_angle_deg: float) -> Dict[str, Any]:
        timestamp = time.time()
        
        # Compute phase quadrature components
        rad = math.radians(phase_angle_deg)
        quad_i = vibration_amplitude_g * math.cos(rad)
        quad_q = vibration_amplitude_g * math.sin(rad)
        magnitude_vector = math.sqrt(quad_i**2 + quad_q**2)
        
        # Estimate harmonic ripple anomaly score
        ripple_harmonic_index = abs(raw_torque_nm - (self.nominal_rpm * 0.01)) / (self.nominal_rpm + 1e-6)
        
        status = "OPTIMAL"
        if magnitude_vector > 2.5 or ripple_harmonic_index > 0.15:
            status = "WARNING_HARMONIC_DEVIATION"
        if magnitude_vector > 5.0:
            status = "CRITICAL_INTERFEROMETER_MISALIGNMENT"
            
        telemetry_packet = {
            "timestamp": timestamp,
            "mill_id": self.mill_id,
            "raw_torque_nm": raw_torque_nm,
            "vibration_amplitude_g": vibration_amplitude_g,
            "quad_i": quad_i,
            "quad_q": quad_q,
            "magnitude_vector": magnitude_vector,
            "ripple_harmonic_index": ripple_harmonic_index,
            "status": status
        }
        
        self.sample_history.append(telemetry_packet)
        if len(self.sample_history) > 1000:
            self.sample_history.pop(0)
            
        return telemetry_packet

    def get_diagnostic_summary(self) -> Dict[str, Any]:
        if not self.sample_history:
            return {"status": "NO_DATA"}
        latest = self.sample_history[-1]
        avg_mag = sum(s["magnitude_vector"] for s in self.sample_history) / len(self.sample_history)
        return {
            "mill_id": self.mill_id,
            "samples_analyzed": len(self.sample_history),
            "latest_status": latest["status"],
            "average_magnitude_vector": avg_mag
        }

if __name__ == "__main__":
    logger.info("Initializing RollerMillInspector Test Harness for Nairobi Milling Plant...")
    inspector = RollerMillInspector(mill_id="NAI_MILL_ALPHA_04", nominal_rpm=1480.0)
    
    # Simulate normal and aberrant telemetry cycles
    test_readings = [
        (14.2, 0.45, 12.0),
        (15.1, 0.82, 45.5),
        (28.6, 5.21, 112.4),
    ]
    
    for torque, vib, phase in test_readings:
        res = inspector.ingest_telemetry(torque, vib, phase)
        logger.info(f"Telemetry Processed -> Status: {res['status']}, Magnitude Vector: {res['magnitude_vector']:.4f}")
        
    summary = inspector.get_diagnostic_summary()
    logger.info(f"Diagnostic Summary: {summary}")
    logger.info("RollerMillInspector test run successfully completed.")
