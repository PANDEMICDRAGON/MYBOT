"""Nairobi Commercial Grain Milling Roller Mill Dynamic Torque Ripple Harmonic Amplitude Phase Quadrature Resolver Interferometer Correlator Estimator Predictor Synchronizer Calibrator Module."""

import math
import logging
from typing import Dict, Any, List

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("RollerMillCalibrator")

class RollerMillDynamicCalibrator:
    """Performs real-time quadrature resolver phase calibration and harmonic torque ripple compensation for roller mills."""
    
    def __init__(self, mill_id: str, nominal_rpm: float = 1500.0):
        self.mill_id = mill_id
        self.nominal_rpm = nominal_rpm
        self.phase_offset_rad = 0.0
        self.harmonic_amplitude = 0.0
        logger.info(f"Initialized RollerMillDynamicCalibrator for mill {mill_id} at {nominal_rpm} RPM.")

    def analyze_quadrature_signals(self, sine_wave: List[float], cosine_wave: List[float]) -> Dict[str, float]:
        """Calculates instantaneous phase angle and harmonic amplitude using interferometer-style quadrature correlation."""
        if len(sine_wave) != len(cosine_wave) or not sine_wave:
            raise ValueError("Quadrature signal buffers must be non-empty and of equal length.")
        
        accumulated_phase = 0.0
        accumulated_amplitude = 0.0
        count = len(sine_wave)
        
        for s, c in zip(sine_wave, cosine_wave):
            angle = math.atan2(s, c)
            amplitude = math.hypot(s, c)
            accumulated_phase += angle
            accumulated_amplitude += amplitude
            
        avg_phase = accumulated_phase / count
        avg_amplitude = accumulated_amplitude / count
        
        self.phase_offset_rad = avg_phase
        self.harmonic_amplitude = avg_amplitude
        
        return {
            "estimated_phase_rad": avg_phase,
            "harmonic_amplitude": avg_amplitude,
            "sync_health_score": max(0.0, 1.0 - abs(avg_phase / math.pi))
        }

    def calibrate_and_predict(self, current_torque_ripple: float) -> Dict[str, Any]:
        """Predicts and compensates for torque ripple anomalies based on harmonic phase correction."""
        compensation_factor = math.sin(self.phase_offset_rad) * self.harmonic_amplitude
        adjusted_torque = current_torque_ripple - (compensation_factor * 0.05)
        
        status = "OPTIMAL"
        if abs(adjusted_torque) > 12.5:
            status = "WARNING_HIGH_RIPPLE"
        elif abs(adjusted_torque) < 1.0:
            status = "LOCKED_SYNCHRONIZED"
            
        return {
            "mill_id": self.mill_id,
            "raw_torque_ripple": current_torque_ripple,
            "compensated_torque": adjusted_torque,
            "status": status
        }

if __name__ == "__main__":
    calibrator = RollerMillDynamicCalibrator(mill_id="NAIROBI_MILL_04", nominal_rpm=1485.0)
    sample_sine = [math.sin(i * 0.1) for i in range(50)]
    sample_cosine = [math.cos(i * 0.1) for i in range(50)]
    
    analysis = calibrator.analyze_quadrature_signals(sample_sine, sample_cosine)
    print("Analysis Result:", analysis)
    
    prediction = calibrator.calibrate_and_predict(current_torque_ripple=8.4)
    print("Calibration & Prediction Result:", prediction)
