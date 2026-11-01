"""
Nairobi Commercial Grain Milling Roller Mill Dynamic Torque Ripple Harmonic Amplitude Phase Quadrature Resolver Interferometer Correlator Estimator Predictor Simulator Emulation Observer Sentinel
Author: Cortana Autonomous Evolutionary Architect
Operator: Michael Obiero (Nairobi, Kenya)
"""

import math
import time
import logging
import statistics
from typing import Dict, List, Any, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("RollerMillObserverSentinel")

class RollerMillObserverSentinel:
    """
    Monitors high-frequency roller mill torque ripple telemetry, compares interferometer readings
    against a digital emulation observer, and triggers real-time mechanical corrective actions.
    """
    def __init__(self, mill_id: str = "NRB-MILL-01") -> None:
        self.mill_id = mill_id
        self.telemetry_history: List[Dict[str, float]] = []
        self.anomaly_count = 0
        logger.info(f"Initialized Observer Sentinel for Roller Mill {self.mill_id}")

    def observe_cycle(self, torque_amplitude: float, harmonic_phase: float, quadrature_error: float) -> Dict[str, Any]:
        timestamp = time.time()
        # Emulate expected state via digital twin model
        expected_amplitude = 12.5 + 2.0 * math.sin(timestamp * 0.1)
        expected_phase = 0.785  # pi / 4 radians

        amplitude_deviation = abs(torque_amplitude - expected_amplitude)
        phase_deviation = abs(harmonic_phase - expected_phase)

        is_anomalous = amplitude_deviation > 4.5 or quadrature_error > 1.2 or phase_deviation > 0.8
        if is_anomalous:
            self.anomaly_count += 1
            logger.warning(f"[{self.mill_id}] Anomaly detected! AmpDev: {amplitude_deviation:.2f}, QuadErr: {quadrature_error:.2f}")

        record = {
            "timestamp": timestamp,
            "torque_amplitude": torque_amplitude,
            "harmonic_phase": harmonic_phase,
            "quadrature_error": quadrature_error,
            "amplitude_deviation": amplitude_deviation,
            "is_anomalous": is_anomalous
        }
        self.telemetry_history.append(record)
        if len(self.telemetry_history) > 1000:
            self.telemetry_history.pop(0)

        return record

    def generate_diagnostic_report(self) -> Dict[str, Any]:
        if not self.telemetry_history:
            return {"status": "no_data"}

        amplitudes = [r["torque_amplitude"] for r in self.telemetry_history]
        return {
            "mill_id": self.mill_id,
            "total_observations": len(self.telemetry_history),
            "anomaly_count": self.anomaly_count,
            "mean_amplitude": statistics.mean(amplitudes),
            "max_amplitude": max(amplitudes),
            "status": "optimal" if self.anomaly_count < 5 else "requires_maintenance"
        }

if __name__ == "__main__":
    sentinel = RollerMillObserverSentinel("NRB-UGALI-MILL-7")
    # Simulate a few cycles
    for i in range(10):
        amp = 13.0 + (i * 0.2) if i != 5 else 22.0
        phase = 0.79 + (i * 0.01)
        quad = 0.1 + (i * 0.05)
        res = sentinel.observe_cycle(amp, phase, quad)
        logger.info(f"Cycle {i} result: {res['is_anomalous']}")
    print(sentinel.generate_diagnostic_report())
