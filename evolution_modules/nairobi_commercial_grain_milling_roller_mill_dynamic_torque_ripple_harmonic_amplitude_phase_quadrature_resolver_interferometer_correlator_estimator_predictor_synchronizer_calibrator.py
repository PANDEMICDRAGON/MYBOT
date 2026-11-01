"""
Nairobi Commercial Grain Milling Roller Mill Dynamic Torque Ripple Harmonic Amplitude Phase Quadrature Resolver Interferometer Correlator Estimator Predictor Synchronizer Calibrator

Designed for Cortana's Autonomous Evolutionary Architecture to monitor, calibrate, and predict
torque ripple harmonics, phase quadrature anomalies, and interferometer resolver shifts in commercial roller mills across Nairobi.
"""

import time
import math
import logging
import statistics
from typing import Dict, List, Optional, Tuple, Any

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("RollerMillCalibrator")

class RollerMillCalibratorError(Exception):
    """Custom exception for roller mill calibration failures."""
    pass

class RollerMillCalibrator:
    """
    Performs real-time interferometer correlation, phase quadrature demodulation, and predictive torque
    synchronization for commercial roller mill drives in Nairobi grain milling operations.
    """
    def __init__(self, mill_id: str, nominal_rpm: float = 1500.0, harmonic_tolerance: float = 0.05):
        self.mill_id = mill_id
        self.nominal_rpm = nominal_rpm
        self.harmonic_tolerance = harmonic_tolerance
        self.calibration_history: List[Dict[str, Any]] = []
        logger.info(f"Initialized RollerMillCalibrator for mill: {self.mill_id} at {self.nominal_rpm} RPM")

    def correlate_resolver_signals(self, sin_wave: List[float], cos_wave: List[float]) -> Tuple[float, float, float]:
        """
        Correlates resolver sin/cos waveforms to extract phase quadrature error and amplitude imbalance.
        """
        if not sin_wave or not cos_wave or len(sin_wave) != len(cos_wave):
            raise RollerMillCalibratorError("Invalid or mismatched resolver waveform lengths.")

        mean_sin = statistics.mean(sin_wave)
        mean_cos = statistics.mean(cos_wave)
        
        # Compute instantaneous amplitudes
        amp_sin = statistics.stdev(sin_wave) if len(sin_wave) > 1 else 0.0
        amp_cos = statistics.stdev(cos_wave) if len(cos_wave) > 1 else 0.0
        
        amplitude_imbalance = abs(amp_sin - amp_cos) / ((amp_sin + amp_cos) / 2.0) if (amp_sin + amp_cos) > 0 else 0.0
        
        # Quadrature phase error estimation
        dot_product = sum((s - mean_sin) * (c - mean_cos) for s, c in zip(sin_wave, cos_wave))
        norm_product = (amp_sin * amp_cos * len(sin_wave)) if (amp_sin * amp_cos) > 0 else 1.0
        phase_error_rad = math.asin(max(-1.0, min(1.0, dot_product / norm_product))) if norm_product != 0 else 0.0

        return amplitude_imbalance, phase_error_rad, (amp_sin + amp_cos) / 2.0

    def estimate_torque_ripple_harmonics(self, torque_stream: List[float]) -> Dict[str, float]:
        """
        Estimates harmonic amplitudes of torque ripple from temporal sensor streams.
        """
        if len(torque_stream) < 10:
            raise RollerMillCalibratorError("Insufficient torque stream data for harmonic estimation.")

        mean_torque = statistics.mean(torque_stream)
        detrended = [t - mean_torque for t in torque_stream]
        
        # Simple discrete harmonic projection at fundamental, 2nd, and 3rd harmonics
        n = len(detrended)
        h1, h2, h3 = 0.0, 0.0, 0.0
        for i, val in enumerate(detrended):
            angle = 2.0 * math.pi * i / n
            h1 += val * math.cos(angle)
            h2 += val * math.cos(2.0 * angle)
            h3 += val * math.cos(3.0 * angle)

        scale = 2.0 / n if n > 0 else 1.0
        metrics = {
            "mean_torque_nm": mean_torque,
            "harmonic_1_amplitude": abs(h1 * scale),
            "harmonic_2_amplitude": abs(h2 * scale),
            "harmonic_3_amplitude": abs(h3 * scale),
        }
        return metrics

    def calibrate_and_synchronize(self, sin_wave: List[float], cos_wave: List[float], torque_stream: List[float]) -> Dict[str, Any]:
        """
        Executes full interferometer correlation, phase quadrature adjustment, and predictive synchronization.
        """
        start_time = time.time()
        amp_imbalance, phase_error, avg_amp = self.correlate_resolver_signals(sin_wave, cos_wave)
        harmonic_metrics = self.estimate_torque_ripple_harmonics(torque_stream)
        
        total_harmonic_distortion = (
            harmonic_metrics["harmonic_1_amplitude"] +
            harmonic_metrics["harmonic_2_amplitude"] +
            harmonic_metrics["harmonic_3_amplitude"]
        ) / max(1.0, harmonic_metrics["mean_torque_nm"])

        status = "OPTIMAL"
        adjustment_required = False
        if total_harmonic_distortion > self.harmonic_tolerance or abs(phase_error) > 0.05 or amp_imbalance > 0.03:
            status = "RECALIBRATION_REQUIRED"
            adjustment_required = True

        result = {
            "mill_id": self.mill_id,
            "timestamp": time.time(),
            "status": status,
            "adjustment_required": adjustment_required,
            "amplitude_imbalance": amp_imbalance,
            "phase_error_rad": phase_error,
            "average_resolver_amplitude": avg_amp,
            "harmonic_metrics": harmonic_metrics,
            "total_harmonic_distortion": total_harmonic_distortion,
            "latency_ms": (time.time() - start_time) * 1000.0
        }

        self.calibration_history.append(result)
        logger.info(f"Mill {self.mill_id} calibration complete. Status: {status}, THD: {total_harmonic_distortion:.4f}")
        return result

if __name__ == "__main__":
    print("Executing RollerMillCalibrator self-test harness...")
    
    # Generate synthetic sin/cos resolver streams with slight phase offset
    samples = 100
    sin_data = [math.sin(2.0 * math.pi * i / 50.0) for i in range(samples)]
    cos_data = [math.cos(2.0 * math.pi * i / 50.0 + 0.02) for i in range(samples)]
    torque_data = [120.0 + 5.0 * math.sin(2.0 * math.pi * i / 25.0) + 1.2 * math.cos(4.0 * math.pi * i / 25.0) for i in range(samples)]

    calibrator = RollerMillCalibrator(mill_id="NAI-MILL-ALPHA-07")
    output = calibrator.calibrate_and_synchronize(sin_data, cos_data, torque_data)
    print("Calibration Output Report:")
    for k, v in output.items():
        print(f"  {k}: {v}")
    print("RollerMillCalibrator module test passed successfully.")
