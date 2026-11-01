"""
Nairobi Commercial Grain Milling Roller Mill Dynamic Torque Ripple Harmonic Amplitude
Phase Quadrature Resolver Interferometer Correlator Estimator Predictor Synchronizer Harmonizer

Designed for Cortanas Autonomous Evolutionary Architecture.
Protects and optimizes roller mill operational integrity for commercial grain milling in Nairobi, Kenya.
"""

import math
import time
import logging
import statistics
from typing import Dict, List, Any, Optional

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')
logger = logging.getLogger("RollerMillHarmonizer")

class RollerMillHarmonizer:
    """
    Monitors, correlates, and synchronizes torque ripple harmonics and phase quadrature
    signals across high-speed commercial roller mill spindles.
    """
    def __init__(self, mill_id: str, nominal_rpm: float = 1200.0):
        self.mill_id = mill_id
        self.nominal_rpm = nominal_rpm
        self.active_state = True
        self.telemetry_buffer: List[Dict[str, float]] = []

    def ingest_telemetry(self, vibration_amplitude: float, torque_ripple: float, phase_angle: float) -> Dict[str, Any]:
        """
        Ingests raw telemetry from dual-roll spindles, computing interferometer cross-correlation
        and quadrature phase variance.
        """
        timestamp = time.time()
        reading = {
            "timestamp": timestamp,
            "vibration_amplitude": vibration_amplitude,
            "torque_ripple": torque_ripple,
            "phase_angle": phase_angle
        }
        self.telemetry_buffer.append(reading)
        if len(self.telemetry_buffer) > 200:
            self.telemetry_buffer.pop(0)

        return self._compute_harmonization_metrics()

    def _compute_harmonization_metrics(self) -> Dict[str, Any]:
        if not self.telemetry_buffer:
            return {"status": "IDLE"}

        v_amps = [r["vibration_amplitude"] for r in self.telemetry_buffer]
        t_ripples = [r["torque_ripple"] for r in self.telemetry_buffer]
        phases = [r["phase_angle"] for r in self.telemetry_buffer]

        mean_v = statistics.mean(v_amps)
        mean_t = statistics.mean(t_ripples)
        
        # Quadrature phase variance estimator
        phase_variance = statistics.variance(phases) if len(phases) > 1 else 0.0
        
        # Interferometer correlation approximation
        try:
            correlator_index = sum(a * b for a, b in zip(v_amps, t_ripples)) / (len(v_amps) * max(mean_v, 1e-5) * max(mean_t, 1e-5))
        except ZeroDivisionError:
            correlator_index = 0.0

        harmonic_distortion_factor = phase_variance * abs(correlator_index)
        
        harmonization_action = "NONE"
        if harmonic_distortion_factor > 0.75:
            harmonization_action = "APPLY_PHASE_QUADRATURE_COMPENSATION"
        elif harmonic_distortion_factor > 0.40:
            harmonization_action = "MODULATE_INVERTER_TORQUE_BAND"

        return {
            "mill_id": self.mill_id,
            "mean_vibration": mean_v,
            "mean_torque_ripple": mean_t,
            "phase_variance": phase_variance,
            "correlator_index": correlator_index,
            "harmonic_distortion_factor": harmonic_distortion_factor,
            "harmonization_action": harmonization_action,
            "status": "SYNCHRONIZED"
        }

    def shutdown(self) -> None:
        self.active_state = False
        logger.info(f"RollerMillHarmonizer for {self.mill_id} safely disengaged.")

if __name__ == "__main__":
    logger.info("Initializing RollerMillHarmonizer diagnostic harness...")
    harmonizer = RollerMillHarmonizer(mill_id="NAI_MILL_04_UGALI_LINE")
    
    # Simulate stable and disruptive milling cycles
    for i in range(10):
        sim_vib = 0.5 + (i * 0.05)
        sim_torque = 1.2 + (i * 0.08)
        sim_phase = math.radians(45.0 + (i * 3.5))
        
        metrics = harmonizer.ingest_telemetry(sim_vib, sim_torque, sim_phase)
        logger.info(f"Tick {i}: Distortion={metrics.get('harmonic_distortion_factor', 0):.3f}, Action={metrics.get('harmonization_action')}")
    
    harmonizer.shutdown()
    logger.info("Test harness execution completed successfully.")
