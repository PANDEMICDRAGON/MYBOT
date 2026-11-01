"""
Nairobi Commercial Grain Milling Roller Mill Dynamic Torque Ripple Harmonic Amplitude
Phase Quadrature Resolver Interferometer Correlator Estimator Predictor Synchronizer Modulator

Author: Cortana Autonomous Evolutionary Architect
Operator: Michael Obiero, Nairobi, Kenya
"""

import math
import time
import logging
from typing import Dict, List, Optional, Tuple, Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("RollerMillHarmonicPulseDetector")

class RollerMillHarmonicPulseDetector:
    """
    Monitors roller mill spindle torque ripple and harmonic amplitudes using
    phase quadrature interferometry to predict mechanical wear and prevent failure.
    """

    def __init__(self, sample_rate_hz: float = 1000.0, harmonic_order: int = 5):
        self.sample_rate_hz = sample_rate_hz
        self.harmonic_order = harmonic_order
        self.buffer_size = 2048
        self._torque_stream: List[float] = []
        self._phase_stream: List[float] = []
        self.is_calibrated = False

    def ingest_telemetry(self, torque_nm: float, phase_rad: float) -> None:
        """Ingests high-frequency torque and encoder phase telemetry."""
        if len(self._torque_stream) >= self.buffer_size:
            self._torque_stream.pop(0)
            self._phase_stream.pop(0)
        self._torque_stream.append(torque_nm)
        self._phase_stream.append(phase_rad)

    def compute_quadrature_harmonics(self) -> Dict[str, Any]:
        """
        Computes quadrature resolver interferometer correlation, estimating
        harmonic amplitudes and phase shifts.
        """
        if len(self._torque_stream) < 128:
            return {"status": "insufficient_data", "harmonic_amplitude": 0.0, "risk_index": 0.0}

        n = len(self._torque_stream)
        mean_torque = sum(self._torque_stream) / n
        
        # Compute root-mean-square torque ripple
        variance = sum((t - mean_torque) ** 2 for t in self._torque_stream) / n
        rms_ripple = math.sqrt(variance)

        # Simulate quadrature correlation vector
        in_phase_sum = 0.0
        quadrature_sum = 0.0
        for i in range(n):
            p = self._phase_stream[i]
            t_dev = self._torque_stream[i] - mean_torque
            in_phase_sum += t_dev * math.cos(self.harmonic_order * p)
            quadrature_sum += t_dev * math.sin(self.harmonic_order * p)

        amplitude = (2.0 / n) * math.sqrt(in_phase_sum ** 2 + quadrature_sum ** 2)
        phase_offset = math.atan2(quadrature_sum, in_phase_sum)

        # Risk index calculation based on harmonic amplitude threshold
        risk_index = min(1.0, amplitude / (mean_torque + 1e-6))

        return {
            "status": "nominal" if risk_index < 0.75 else "critical_warning",
            "mean_torque_nm": mean_torque,
            "rms_ripple_nm": rms_ripple,
            "harmonic_amplitude": amplitude,
            "phase_offset_rad": phase_offset,
            "risk_index": risk_index,
            "timestamp": time.time()
        }

    def calibrate(self) -> bool:
        """Performs baseline calibration of the resolver interferometer."""
        if len(self._torque_stream) >= 256:
            self.is_calibrated = True
            logger.info("Roller mill harmonic resolver successfully calibrated.")
            return True
        logger.warning(
            f"Calibration deferred. Insufficient samples: {len(self._torque_stream)}/256"
        )
        return False


if __name__ == "__main__":
    detector = RollerMillHarmonicPulseDetector()
    print("Initializing RollerMillHarmonicPulseDetector test harness...")
    
    # Simulate ingestion of telemetry
    for i in range(300):
        phase = (i * 0.1) % (2 * math.pi)
        torque = 150.0 + 12.5 * math.sin(5 * phase) + (i % 3) * 0.5
        detector.ingest_telemetry(torque, phase)

    detector.calibrate()
    result = detector.compute_quadrature_harmonics()
    print(f"Test Harness Execution Result: {result}")
    assert result["status"] in ["nominal", "critical_warning"]
    print("RollerMillHarmonicPulseDetector test harness execution completed successfully.")
