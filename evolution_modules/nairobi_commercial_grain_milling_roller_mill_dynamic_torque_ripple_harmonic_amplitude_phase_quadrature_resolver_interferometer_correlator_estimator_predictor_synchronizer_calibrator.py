import math
import time
import logging
from typing import Dict, List, Any, Optional

logging.basicConfig(level=logging.INFO, format='[%(asctime)s] [%(levelname)s] [ResolverCalibrator]: %(message)s')
logger = logging.getLogger('ResolverCalibrator')

class RollerMillResolverCalibrator:
    """
    Calibrates quadrature resolver interferometers and corrects dynamic torque ripple harmonic phase drift
    in Nairobi commercial grain milling roller mills.
    """
    def __init__(self, mill_id: str, baseline_frequency_hz: float = 50.0):
        self.mill_id = mill_id
        self.baseline_frequency_hz = baseline_frequency_hz
        self.phase_offset_rad = 0.0
        self.calibration_history: List[Dict[str, Any]] = []
        logger.info(f"Initialized Resolver Calibrator for {{self.mill_id}} at {{self.baseline_frequency_hz}}Hz baseline.")

    def measure_quadrature_signals(self, raw_sin: float, raw_cos: float) -> Dict[str, float]:
        """Measures and normalizes quadrature sine and cosine signals."""
        amplitude = math.sqrt(raw_sin**2 + raw_cos**2)
        if amplitude == 0.0:
            normalized_sin = 0.0
            normalized_cos = 0.0
        else:
            normalized_sin = raw_sin / amplitude
            normalized_cos = raw_cos / amplitude
        
        measured_angle = math.atan2(normalized_sin, normalized_cos)
        return {
            "amplitude": amplitude,
            "normalized_sin": normalized_sin,
            "normalized_cos": normalized_cos,
            "measured_angle_rad": measured_angle
        }

    def estimate_torque_ripple_harmonic(self, torque_samples: List[float]) -> Dict[str, float]:
        """Estimates harmonic amplitude and phase from raw torque samples."""
        if not torque_samples:
            return {"harmonic_amplitude": 0.0, "harmonic_phase": 0.0}
        
        n = len(torque_samples)
        mean_torque = sum(torque_samples) / n
        
        # Simple single-frequency DFT bin estimation for primary harmonic
        real_part = 0.0
        imag_part = 0.0
        for i, val in enumerate(torque_samples):
            angle = 2.0 * math.pi * i / n
            dev = val - mean_torque
            real_part += dev * math.cos(angle)
            imag_part += dev * math.sin(angle)
            
        harmonic_amplitude = (2.0 / n) * math.sqrt(real_part**2 + imag_part**2)
        harmonic_phase = math.atan2(-imag_part, real_part)
        
        return {
            "mean_torque": mean_torque,
            "harmonic_amplitude": harmonic_amplitude,
            "harmonic_phase": harmonic_phase
        }

    def calibrate_resolver(self, raw_sin: float, raw_cos: float, torque_samples: List[float]) -> Dict[str, Any]:
        """Executes full synchronization and calibration cycle."""
        quad = self.measure_quadrature_signals(raw_sin, raw_cos)
        harmonic = self.estimate_torque_ripple_harmonic(torque_samples)
        
        # Adjust phase offset based on harmonic phase error
        phase_error = harmonic["harmonic_phase"] - quad["measured_angle_rad"]
        self.phase_offset_rad += 0.1 * phase_error  # Proportional correction step
        
        calibration_record = {
            "timestamp": time.time(),
            "mill_id": self.mill_id,
            "amplitude": quad["amplitude"],
            "harmonic_amplitude": harmonic["harmonic_amplitude"],
            "phase_error": phase_error,
            "new_phase_offset_rad": self.phase_offset_rad
        }
        self.calibration_history.append(calibration_record);
        logger.info(f"Calibration executed for {{self.mill_id}}. Phase Error: {{phase_error:.4f}} rad.")
        return calibration_record

if __name__ == '__main__':
    calibrator = RollerMillResolverCalibrator("MILL_NAIROBI_CENTRAL_01")
    sample_sin = 0.707
    sample_cos = 0.707
    dummy_torque = [10.5, 11.2, 12.1, 11.8, 10.9, 10.1, 9.8, 10.4]
    result = calibrator.calibrate_resolver(sample_sin, sample_cos, dummy_torque)
    print("Test Calibration Result:", result)
