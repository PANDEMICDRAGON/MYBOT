"""Nairobi Commercial Grain Milling Roller Mill Dynamic Torque Ripple Harmonic Amplitude Phase Quadrature Resolver Interferometer Correlator Estimator Predictor Synchronizer Investigator Module."""

import math
import time
from typing import Dict, Any, List

class RollerMillInterferometricInvestigator:
    """Investigates and correlates dynamic torque ripple harmonics in commercial roller mills."""

    def __init__(self, mill_id: str, base_frequency_hz: float = 50.0) -> None:
        self.mill_id = mill_id
        self.base_frequency_hz = base_frequency_hz
        self.sample_count = 0

    def analyze_quadrature_phase(self, raw_torque_samples: List[float]) -> Dict[str, Any]:
        self.sample_count += len(raw_torque_samples)
        if not raw_torque_samples:
            return {"status": "insufficient_data", "harmonic_distortion_percent": 0.0}

        mean_torque = sum(raw_torque_samples) / len(raw_torque_samples)
        variance = sum((t - mean_torque) ** 2 for t in raw_torque_samples) / len(raw_torque_samples)
        std_dev = math.sqrt(variance)

        # Interferometric quadrature estimation
        in_phase_component = sum(t * math.cos(i * 0.1) for i, t in enumerate(raw_torque_samples))
        quadrature_component = sum(t * math.sin(i * 0.1) for i, t in enumerate(raw_torque_samples))
        phase_angle = math.atan2(quadrature_component, in_phase_component if in_phase_component != 0 else 1e-6)
        amplitude = math.hypot(in_phase_component, quadrature_component) / len(raw_torque_samples)

        distortion_index = (std_dev / (abs(mean_torque) + 1e-6)) * 100.0

        return {
            "mill_id": self.mill_id,
            "timestamp": time.time(),
            "mean_torque_nm": mean_torque,
            "torque_ripple_amplitude": amplitude,
            "quadrature_phase_rad": phase_angle,
            "harmonic_distortion_percent": distortion_index,
            "investigation_status": "OPTIMAL" if distortion_index < 15.0 else "RESONANCE_WARNING"
        }

if __name__ == "__main__":
    investigator = RollerMillInterferometricInvestigator("MILL-NAI-01")
    mock_samples = [100.5 + 5.0 * math.sin(i * 0.2) + 2.0 * math.cos(i * 0.5) for i in range(100)]
    report = investigator.analyze_quadrature_phase(mock_samples)
    print(f"[EXECUTION SUCCESS] Roller Mill Interferometer Report: {report}")
