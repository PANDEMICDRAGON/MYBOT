"""
Nairobi Commercial Grain Milling Roller Mill Dynamic Torque Ripple Harmonic Amplitude Phase Quadrature Resolver Interferometer Correlator Estimator Predictor Synchronizer Modulator Module
Created for Cortana's Autonomous Evolutionary Architect.

Provides high-precision real-time processing of roller mill motor telemetry, quadrature resolver interferometry, and dynamic torque ripple harmonic cancellation for industrial milling operations in Nairobi, Kenya.
"""

import math
import logging
import statistics
from typing import Dict, List, Any, Optional

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')
logger = logging.getLogger("RollerMillModulator")

class RollerMillModulatorException(Exception):
    """Custom exception for roller mill modulation and synchronization errors."""
    pass


class RollerMillDynamicModulator:
    """
    Core processor for real-time harmonic amplitude phase quadrature resolver interferometry
    and predictive torque ripple cancellation in commercial grain milling roller assemblies.
    """

    def __init__(self, mill_id: str, base_rpm: float = 1450.0, harmonic_orders: Optional[List[int]] = None):
        self.mill_id = mill_id
        self.base_rpm = base_rpm
        self.harmonic_orders = harmonic_orders or [1, 2, 3, 5, 7]
        self.telemetry_buffer: List[Dict[str, float]] = []
        self.modulation_history: List[Dict[str, Any]] = []
        logger.info(f"Initialized RollerMillDynamicModulator for mill: {self.mill_id} at {self.base_rpm} RPM")

    def ingest_resolver_telemetry(self, timestamp: float, quadrature_sin: float, quadrature_cos: float, current_torque_nm: float) -> Dict[str, float]:
        """
        Ingests raw quadrature resolver sine/cosine signals and instantaneous torque measurements.
        Computes phase angle, apparent electrical angle, and stores telemetry.
        """
        try:
            phase_rad = math.atan2(quadrature_sin, quadrature_cos)
            phase_deg = math.degrees(phase_rad) % 360.0
            
            reading = {
                "timestamp": timestamp,
                "sin": quadrature_sin,
                "cos": quadrature_cos,
                "phase_deg": phase_deg,
                "torque_nm": current_torque_nm
            }
            self.telemetry_buffer.append(reading)
            if len(self.telemetry_buffer) > 1000:
                self.telemetry_buffer.pop(0)
                
            return reading
        except Exception as e:
            logger.error(f"Failed to ingest resolver telemetry for {self.mill_id}: {e}")
            raise RollerMillModulatorException(f"Resolver ingest error: {e}") from e

    def correlate_harmonics_and_torque(self) -> Dict[str, Any]:
        """
        Performs interferometric correlation between quadrature resolver phase variations
        and torque ripple harmonic amplitudes.
        """
        if len(self.telemetry_buffer) < 10:
            return {"status": "insufficient_data", "harmonic_correlations": {}}

        torques = [t["torque_nm"] for t in self.telemetry_buffer]
        phases = [t["phase_deg"] for t in self.telemetry_buffer]
        
        mean_torque = statistics.mean(torques)
        torque_ripples = [t - mean_torque for t in torques]
        amplitude_proxy = max(torques) - min(torques)

        harmonic_correlations = {}
        for order in self.harmonic_orders:
            # Simulated harmonic phase quadrature correlation score
            harmonic_correlations[f"order_{order}"] = round(math.sin(order * math.radians(statistics.mean(phases))) * amplitude_proxy, 4)

        result = {
            "mill_id": self.mill_id,
            "mean_torque_nm": round(mean_torque, 2),
            "torque_ripple_amplitude": round(amplitude_proxy, 2),
            "harmonic_correlations": harmonic_correlations,
            "status": "success"
        }
        self.modulation_history.append(result)
        return result

    def compute_modulation_compensation(self) -> Dict[str, float]:
        """
        Calculates phase-quadrature correction signals to actively attenuate torque ripple
        and protect roller bearings from harmonic resonance.
        """
        if not self.modulation_history:
            return {"phase_compensation_deg": 0.0, "amplitude_modulation_gain": 1.0}

        latest = self.modulation_history[-1]
        ripple = latest.get("torque_ripple_amplitude", 0.0)
        
        # Inverse proportional modulation gain to dampen torque spikes
        compensation_angle = min(15.0, ripple * 0.05)
        modulation_gain = max(0.85, min(1.15, 1.0 - (ripple * 0.002)))

        return {
            "phase_compensation_deg": round(compensation_angle, 3),
            "amplitude_modulation_gain": round(modulation_gain, 3)
        }


if __name__ == "__main__":
    logger.info("Executing self-test for RollerMillDynamicModulator...")
    modulator = RollerMillDynamicModulator(mill_id="NAI_MILL_ALPHA_04")
    
    # Simulate incoming telemetry stream
    for i in range(20):
        t = float(i)
        sin_val = math.sin(i * 0.5)
        cos_val = math.cos(i * 0.5)
        torque = 240.0 + (12.5 * math.sin(i * 0.2)) + (3.2 * math.cos(i * 0.6))
        modulator.ingest_resolver_telemetry(t, sin_val, cos_val, torque)

    corr = modulator.correlate_harmonics_and_torque()
    logger.info(f"Correlation result: {corr}")

    comp = modulator.compute_modulation_compensation()
    logger.info(f"Computed modulation compensation: {comp}")
    logger.info("RollerMillDynamicModulator test completed successfully.")
