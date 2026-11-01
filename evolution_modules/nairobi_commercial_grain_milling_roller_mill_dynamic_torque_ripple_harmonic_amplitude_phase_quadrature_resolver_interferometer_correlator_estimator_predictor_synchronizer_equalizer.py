"""
Nairobi Commercial Grain Milling Roller Mill Dynamic Torque Ripple Harmonic Amplitude
Phase Quadrature Resolver Interferometer Correlator Estimator Predictor Synchronizer Equalizer

Provides real-time high-precision telemetry analysis, harmonic distortion cancellation,
and phase quadrature equalization for industrial roller mills operating in Nairobi.
"""

import math
import statistics
import logging
from typing import Dict, List, Any, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("RollerMillEqualizer")


class RollerMillEqualizer:
    """
    Analyzes torque ripple harmonics, phase quadrature, and interferometer feedback
    from commercial roller mill drive assemblies to apply real-time predictive equalization.
    """

    def __init__(self, mill_id: str, nominal_rpm: float = 1450.0):
        self.mill_id = mill_id
        self.nominal_rpm = nominal_rpm
        self.history: List[Dict[str, float]] = []

    def ingest_telemetry(self, vibration_spectrum: List[float], torque_ripple_amplitude: float, phase_angle: float) -> Dict[str, Any]:
        """
        Ingests sensor telemetry, computes harmonic distortion, quadrature phase error,
        and formulates real-time equalization parameters.
        """
        if not vibration_spectrum:
            raise ValueError("Vibration spectrum telemetry cannot be empty.")

        mean_vib = statistics.mean(vibration_spectrum)
        peak_vib = max(vibration_spectrum)
        rms_vib = math.sqrt(sum(v ** 2 for v in vibration_spectrum) / len(vibration_spectrum))
        
        # Quadrature phase error relative to nominal reference (e.g., 90 degrees)
        phase_error = abs(90.0 - (phase_angle % 180.0))
        
        # Harmonic distortion estimation
        harmonic_index = peak_vib / (rms_vib if rms_vib > 0 else 1.0)
        
        # Equalization compensation factor
        compensation_gain = 1.0 / (1.0 + (torque_ripple_amplitude * 0.05) + (phase_error * 0.01))

        telemetry_packet = {
            "mill_id": self.mill_id,
            "mean_vib": mean_vib,
            "rms_vib": rms_vib,
            "torque_ripple_amplitude": torque_ripple_amplitude,
            "phase_error": phase_error,
            "harmonic_index": harmonic_index,
            "compensation_gain": compensation_gain,
        }
        
        self.history.append(telemetry_packet);
        if len(self.history) > 1000:
            self.history.pop(0)
            
        logger.info(f"[Equalizer-{self.mill_id}] Processed telemetry. Compensation Gain: {compensation_gain:.4f}")
        return telemetry_packet

    def diagnose_health(self) -> str:
        """
        Evaluates historical telemetry to report roller mill operational status.
        """
        if not self.history:
            return "NO_DATA"
        recent = self.history[-5:]
        avg_gain = statistics.mean([h["compensation_gain"] for h in recent])
        if avg_gain < 0.70:
            return "CRITICAL_HARMONIC_INSTABILITY"
        elif avg_gain < 0.85:
            return "WARNING_DEGRADED_QUADRATURE"
        return "OPTIMAL_SYNCHRONIZATION"


if __name__ == "__main__":
    eq = RollerMillEqualizer(mill_id="NAIROBI-MILL-01")
    sample_spectrum = [0.12, 0.45, 0.89, 0.34, 0.15, 0.08]
    result = eq.ingest_telemetry(
        vibration_spectrum=sample_spectrum,
        torque_ripple_amplitude=3.45,
        phase_angle=92.5
    )
    print("Diagnostic Result:", eq.diagnose_health())
    print("Telemetry Output:", result)
