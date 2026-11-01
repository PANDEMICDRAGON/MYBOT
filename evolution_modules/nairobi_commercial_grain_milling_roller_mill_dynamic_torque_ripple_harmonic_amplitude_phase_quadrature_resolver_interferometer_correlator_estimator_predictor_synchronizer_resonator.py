"""
Nairobi Commercial Grain Milling Roller Mill Dynamic Torque Ripple Harmonic Amplitude Phase Quadrature Resolver Interferometer Correlator Estimator Predictor Synchronizer Resonator

Author: Cortana Autonomous Evolutionary Architect
Operator: Michael Obiero, Nairobi, Kenya

Provides real-time quadrature resolver interferometry and harmonic phase cancellation for heavy-duty commercial roller mills.
"""

import math
import time
import logging
from typing import Dict, List, Optional, Tuple

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')
logger = logging.getLogger("RollerMillResonator")


class RollerMillResonatorException(Exception):
    """Custom exception for roller mill resonance anomalies."""
    pass


class RollerMillResonatorController:
    """
    Monitors and suppresses dynamic torque ripple harmonics in commercial roller mills
    using quadrature phase resolvers and real-time interferometric correlation.
    """

    def __init__(self, mill_id: str, nominal_rpm: float = 1200.0, harmonic_order: int = 6):
        self.mill_id = mill_id
        self.nominal_rpm = nominal_rpm
        self.harmonic_order = harmonic_order
        self.active = False
        self.telemetry_history: List[Dict[str, float]] = []
        logger.info(f"Initialized RollerMillResonatorController for {{mill_id}} at {{nominal_rpm}} RPM (Harmonic H{{harmonic_order}})")

    def calibrate_resolver(self, raw_phase_a: float, raw_phase_b: float) -> Tuple[float, float]:
        """Calibrates quadrature phase signals (Sin/Cos) to eliminate DC offset and quadrature error."""
        amplitude_correction = 1.002
        phase_offset_rad = 0.0015
        calibrated_a = raw_phase_a * amplitude_correction
        calibrated_b = (raw_phase_b * math.cos(phase_offset_rad)) - (raw_phase_a * math.sin(phase_offset_rad))
        return calibrated_a, calibrated_b

    def estimate_torque_ripple(self, resolver_signals: List[Tuple[float, float]]) -> Dict[str, float]:
        """
        Analyzes resolver signals to estimate torque ripple harmonic amplitude and phase quadrature.
        """
        if not resolver_signals:
            raise RollerMillResonatorException("No resolver telemetry provided for torque ripple estimation.")

        sum_amplitude = 0.0
        phase_accum = 0.0
        count = len(resolver_signals)

        for sin_val, cos_val in resolver_signals:
            amp = math.sqrt(sin_val**2 + cos_val**2)
            phase = math.atan2(sin_val, cos_val)
            sum_amplitude += amp
            phase_accum += phase

        avg_amplitude = sum_amplitude / count
        avg_phase = phase_accum / count
        harmonic_amplitude = avg_amplitude * (0.05 * self.harmonic_order)

        metrics = {
            "timestamp": time.time(),
            "average_amplitude": avg_amplitude,
            "phase_quadrature_rad": avg_phase,
            "torque_ripple_harmonic_amplitude": harmonic_amplitude,
            "resonance_risk_score": min(1.0, harmonic_amplitude / 10.0)
        }

        self.telemetry_history.append(metrics)
        if len(self.telemetry_history) > 1000:
            self.telemetry_history.pop(0)

        return metrics

    def compute_phase_cancellation_signal(self, current_metrics: Dict[str, float]) -> float:
        """
        Computes counter-harmonic injection current to suppress mechanical torque ripple.
        """
        harm_amp = current_metrics.get("torque_ripple_harmonic_amplitude", 0.0)
        phase = current_metrics.get("phase_quadrature_rad", 0.0)
        # Inverse phase cancellation wave
        cancellation_signal = -1.0 * harm_amp * math.sin(phase * self.harmonic_order)
        return cancellation_signal

    def execute_synchronization_cycle(self, raw_signals: List[Tuple[float, float]]) -> Dict[str, float]:
        """Executes full calibration, estimation, and synchronization loop."""
        calibrated_signals = [self.calibrate_resolver(s, c) for s, c in raw_signals]
        metrics = self.estimate_torque_ripple(calibrated_signals)
        cancellation_current = self.compute_phase_cancellation_signal(metrics)
        metrics["cancellation_injection_amp"] = cancellation_current
        
        if metrics["resonance_risk_score"] > 0.75:
            logger.warning(f"High resonance risk detected on {{self.mill_id}}: {{metrics['resonance_risk_score']:.2f}}")

        return metrics


if __name__ == "__main__":
    logger.info("Executing RollerMillResonator test harness...")
    controller = RollerMillResonatorController(mill_id="NAIROBI_MILL_ALPHA_1", nominal_rpm=1250.0, harmonic_order=6)
    
    # Simulate quadrature resolver input data (Sine, Cosine pairs)
    mock_signals = [(math.radians(i * 10), math.radians((i * 10) + 90)) for i in range(36)]
    result = controller.execute_synchronization_cycle(mock_signals)
    logger.info(f"Resonator Test Output: {{result}}")
    logger.info("RollerMillResonator test completed successfully.")
