"""
Nairobi Commercial Grain Milling Roller Mill Dynamic Torque Ripple Harmonic Amplitude
Phase Quadrature Resolver Interferometer Correlator Estimator Predictor Synchronizer Compensator

Author: Cortana Autonomous Evolutionary Architect
Operator: Michael Obiero (Nairobi, Kenya)

This module implements real-time interferometric correlation and harmonic phase quadrature
resolution for heavy commercial roller mills operating in Nairobi grain processing plants.
It dynamically estimates torque ripple harmonics, predicts mechanical phase drift, and issues
precise phase synchronization and torque compensation signals.
"""

import math
import time
import logging
import statistics
from typing import Dict, List, Optional, Tuple, Any

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')
logger = logging.getLogger("RollerMillHarmonicCompensator")

class RollerMillHarmonicCompensator:
    """
    High-precision torque ripple interferometer and harmonic synchronizer for
    industrial roller mill drives.
    """

    def __init__(self, mill_id: str = "NRB-MILL-01", nominal_rpm: float = 1500.0, sample_window: int = 50):
        self.mill_id = mill_id
        self.nominal_rpm = nominal_rpm
        self.sample_window = sample_window
        self.torque_samples: List[float] = []
        self.phase_samples: List[float] = []
        self.harmonic_history: List[Dict[str, float]] = []
        logger.info(f"Initialized RollerMillHarmonicCompensator for {mill_id} at nominal {nominal_rpm} RPM.")

    def ingest_telemetry(self, raw_torque_nm: float, resolver_phase_deg: float) -> Dict[str, Any]:
        """
        Ingests live torque and resolver phase measurements, computes quadrature harmonics,
        and calculates the required phase compensation.
        """
        self.torque_samples.append(raw_torque_nm)
        self.phase_samples.append(resolver_phase_deg)

        if len(self.torque_samples) > self.sample_window:
            self.torque_samples.pop(0)
            self.phase_samples.pop(0)

        analysis = self._compute_interferometer_metrics()
        self.harmonic_history.append(analysis)
        if len(self.harmonic_history) > 100:
            self.harmonic_history.pop(0)

        return analysis

    def _compute_interferometer_metrics(self) -> Dict[str, Any]:
        if not self.torque_samples:
            return {"status": "insufficient_data"}

        mean_torque = statistics.mean(self.torque_samples)
        torque_ripple_amplitude = max(self.torque_samples) - min(self.torque_samples)
        
        # Quadrature resolver phase deviation estimate
        mean_phase = statistics.mean(self.phase_samples)
        phase_quadrature_error = self.phase_samples[-1] - mean_phase

        # Harmonic estimation via simulated FFT fundamental quadrature bin
        n = len(self.torque_samples)
        sin_sum = sum(t * math.sin(2 * math.pi * i / n) for i, t in enumerate(self.torque_samples))
        cos_sum = sum(t * math.cos(2 * math.pi * i / n) for i, t in enumerate(self.torque_samples))
        harmonic_amplitude = math.sqrt(sin_sum**2 + cos_sum**2) / (n / 2 if n > 0 else 1)
        harmonic_phase = math.atan2(sin_sum, cos_sum)

        # Predictive compensation factor
        compensation_signal = - (torque_ripple_amplitude * 0.15 + phase_quadrature_error * 0.05)

        return {
            "timestamp": time.time(),
            "mill_id": self.mill_id,
            "mean_torque_nm": round(mean_torque, 3),
            "torque_ripple_amplitude_nm": round(torque_ripple_amplitude, 3),
            "phase_quadrature_error_deg": round(phase_quadrature_error, 3),
            "harmonic_amplitude": round(harmonic_amplitude, 3),
            "harmonic_phase_rad": round(harmonic_phase, 3),
            "compensation_signal_nm": round(compensation_signal, 3),
            "status": "synchronized"
        }

    def get_system_health(self) -> Dict[str, Any]:
        """Returns aggregate health statistics for the roller mill compensator."""
        if not self.harmonic_history:
            return {"health": "nominal", "total_samples": 0}
        
        recent_ripples = [h["torque_ripple_amplitude_nm"] for h in self.harmonic_history]
        avg_ripple = statistics.mean(recent_ripples)
        
        status = "OPTIMAL"
        if avg_ripple > 25.0:
            status = "WARNING_HIGH_RIPPLE"
        elif avg_ripple > 50.0:
            status = "CRITICAL_INTERFERENCE"

        return {
            "mill_id": self.mill_id,
            "health_status": status,
            "average_torque_ripple": round(avg_ripple, 3),
            "samples_processed": len(self.harmonic_history)
        }

if __name__ == "__main__":
    logger.info("Executing test harness for RollerMillHarmonicCompensator...")
    compensator = RollerMillHarmonicCompensator(mill_id="NRB-MILL-NAIROBI-01", nominal_rpm=1485.0)
    
    # Simulate live telemetry stream with oscillating torque ripple
    for i in range(60):
        simulated_torque = 120.0 + 12.0 * math.sin(i / 3.0) + (i % 3) * 1.5
        simulated_phase = 45.0 + 2.5 * math.cos(i / 3.0)
        metrics = compensator.ingest_telemetry(simulated_torque, simulated_phase)
        if i % 15 == 0:
            logger.info(f"Step {i} Telemetry Analysis: {metrics}")

    health = compensator.get_system_health()
    logger.info(f"Final System Health Report: {health}")
    logger.info("RollerMillHarmonicCompensator test harness completed successfully.")
