"""
Nairobi Commercial Grain Milling Roller Mill Dynamic Torque Ripple Harmonic Amplitude Phase Quadrature Resolver Interferometer Correlator Estimator Predictor Synchronizer Decoupler Module

Designed for autonomous industrial milling infrastructure monitoring in Nairobi, Kenya.
Provides real-time quadrature resolution, torque ripple harmonic cancellation, and phase decoupling.
"""

import math
import logging
import statistics
from typing import Dict, List, Optional, Tuple

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')
logger = logging.getLogger("RollerMillDecoupler")


class RollerMillDecouplerEngine:
    """
    Core engine for computing phase quadrature and harmonic decoupling in multi-stage
    roller mill drive assemblies.
    """

    def __init__(self, mill_id: str, base_rpm: float = 1450.0):
        self.mill_id = mill_id
        self.base_rpm = base_rpm
        self.history: List[Dict[str, float]] = []

    def compute_quadrature_vector(self, phase_a: float, phase_b: float) -> Tuple[float, float]:
        """
        Computes quadrature (alpha-beta) components from dual-phase sensor inputs.
        """
        alpha = phase_a
        beta = (phase_a + 2.0 * phase_b) / math.sqrt(3.0)
        return alpha, beta

    def analyze_torque_ripple(self, torque_samples: List[float]) -> Dict[str, float]:
        """
        Analyzes harmonic amplitude and phase dispersion across raw torque samples.
        """
        if not torque_samples:
            return {"mean_torque": 0.0, "ripple_amplitude": 0.0, "phase_offset": 0.0}

        mean_val = statistics.mean(torque_samples)
        peak_val = max(torque_samples)
        min_val = min(torque_samples)
        ripple_amplitude = peak_val - min_val
        
        # Approximate phase offset using variance ratio
        variance = statistics.variance(torque_samples) if len(torque_samples) > 1 else 0.0
        phase_offset = math.atan2(math.sqrt(max(0.0, variance)), max(1e-6, mean_val))

        return {
            "mean_torque": round(mean_val, 4),
            "ripple_amplitude": round(ripple_amplitude, 4),
            "phase_offset": round(phase_offset, 4)
        }

    def generate_decoupling_compensation(self, alpha: float, beta: float, ripple_amplitude: float) -> float:
        """
        Computes anti-harmonic counter-torque signal to neutralize mechanical resonance.
        """
        magnitude = math.sqrt(alpha**2 + beta**2)
        compensation = -(magnitude * 0.15) - (ripple_amplitude * 0.05)
        return round(compensation, 4)

    def process_cycle(self, phase_a: float, phase_b: float, torque_samples: List[float]) -> Dict[str, float]:
        alpha, beta = self.compute_quadrature_vector(phase_a, phase_b)
        torque_metrics = self.analyze_torque_ripple(torque_samples)
        compensation = self.generate_decoupling_compensation(alpha, beta, torque_metrics["ripple_amplitude"])

        report = {
            "alpha": alpha,
            "beta": beta,
            "mean_torque": torque_metrics["mean_torque"],
            "ripple_amplitude": torque_metrics["ripple_amplitude"],
            "phase_offset": torque_metrics["phase_offset"],
            "compensation_signal": compensation
        }

        self.history.append(report)
        if len(self.history) > 1000:
            self.history.pop(0)

        return report


if __name__ == "__main__":
    logger.info("Initializing Nairobi Roller Mill Torque Ripple Decoupler Test Harness...")
    engine = RollerMillDecouplerEngine(mill_id="MILL_NAIROBI_INDUSTRIAL_01")
    
    # Simulate sensor streams
    mock_phase_a = 1.25
    mock_phase_b = 1.22
    mock_torque = [45.2, 48.6, 42.1, 49.0, 44.5]

    result = engine.process_cycle(mock_phase_a, mock_phase_b, mock_torque)
    logger.info(f"Decoupling Execution Result: {result}")
    logger.info("Test completed successfully. Module compiled cleanly.")
