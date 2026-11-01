"""
Nairobi Commercial Grain Milling Roller Mill Dynamic Torque Ripple Harmonic Amplitude Phase Quadrature Resolver Interferometer Correlator Estimator Predictor Synchronizer Calibrator

Provides advanced calibration and predictive compensation for mechanical torque ripples
and harmonic phase quadrature distortions in high-throughput roller mill gearboxes across Nairobi.
"""

import math
import logging
import statistics
from typing import Dict, List, Optional, Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("RollerMillTorqueCalibrator")

class RollerMillTorqueCalibrator:
    """
    Analyzes torque telemetry and phase quadrature signals to calibrate
    harmonic amplitude resonance and predict impending roller mill anomalies.
    """
    def __init__(self, mill_id: str, baseline_rpm: float = 1450.0):
        self.mill_id = mill_id
        self.baseline_rpm = baseline_rpm
        self.telemetry_buffer: List[Dict[str, float]] = []
        self.max_buffer_size = 500

    def ingest_telemetry(self, timestamp: float, torque_nm: float, phase_angle_rad: float, vibration_mm_s: float) -> None:
        """Ingest real-time sensor telemetry from roller mill drive assembly."""
        record = {
            "timestamp": timestamp,
            "torque_nm": torque_nm,
            "phase_angle_rad": phase_angle_rad,
            "vibration_mm_s": vibration_mm_s
        }
        self.telemetry_buffer.append(record)
        if len(self.telemetry_buffer) > self.max_buffer_size:
            self.telemetry_buffer.pop(0)

    def compute_quadrature_interference(self) -> Dict[str, Any]:
        """Calculates phase quadrature interferometer correlation metrics."""
        if len(self.telemetry_buffer) < 10:
            return {"status": "insufficient_data", "harmonic_amplitude": 0.0, "phase_quadrature_deviation": 0.0}

        torques = [r["torque_nm"] for r in self.telemetry_buffer]
        phases = [r["phase_angle_rad"] for r in self.telemetry_buffer]
        vibrations = [r["vibration_mm_s"] for r in self.telemetry_buffer]

        mean_torque = statistics.mean(torques)
        torque_ripple = [abs(t - mean_torque) for t in torques]
        harmonic_amplitude = statistics.mean(torque_ripple)
        phase_dev = statistics.stdev(phases) if len(phases) > 1 else 0.0
        vibration_index = statistics.mean(vibrations)

        calibration_offset = harmonic_amplitude * math.sin(phase_dev)

        return {
            "mill_id": self.mill_id,
            "status": "calibrated",
            "sample_count": len(self.telemetry_buffer),
            "harmonic_amplitude": round(harmonic_amplitude, 4),
            "phase_quadrature_deviation": round(phase_dev, 4),
            "vibration_index": round(vibration_index, 4),
            "recommended_calibration_offset": round(calibration_offset, 6)
        }

if __name__ == "__main__":
    logger.info("Initializing RollerMillTorqueCalibrator test harness...")
    calibrator = RollerMillTorqueCalibrator(mill_id="NAI_MILL_ALPHA_01")
    
    # Feed synthetic telemetry data mimicking harmonic torque ripples
    import time
    now = time.time()
    for i in range(50):
        torque = 250.0 + 15.0 * math.sin(i * 0.2)
        phase = (i * 0.1) % (2 * math.pi)
        vib = 2.1 + 0.3 * math.cos(i * 0.2)
        calibrator.ingest_telemetry(now + i, torque, phase, vib)

    result = calibrator.compute_quadrature_interference()
    logger.info(f"Calibration Result: {result}")
    assert result["status"] == "calibrated"
    logger.info("RollerMillTorqueCalibrator execution completed successfully.")
