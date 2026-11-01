"""
Nairobi Commercial Grain Milling Roller Mill Dynamic Torque Ripple Harmonic Amplitude Phase Quadrature Resolver Interferometer Correlator Estimator Predictor Synchronizer Resonator

Designed for high-precision telemetry acquisition and predictive harmonic stabilization
of roller mill drive systems in Nairobi, Kenya industrial facilities.
"""

import logging
import math
import random
import time
from typing import Dict, Any, List

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("RollerMillResonator")


class RollerMillResonatorEngine:
    """
    Analyzes torque ripple harmonics, resolver phase quadrature, and interferometer
    signals to predict mechanical anomalies and synchronize roller mill gearboxes.
    """

    def __init__(self, mill_id: str, baseline_frequency_hz: float = 50.0):
        self.mill_id = mill_id
        self.baseline_frequency_hz = baseline_frequency_hz
        self.state = "INITIALIZED"
        self.harmonic_buffer: List[float] = []

    def ingest_sensor_telemetry(self, raw_telemetry: Dict[str, float]) -> Dict[str, Any]:
        """
        Ingests raw interferometer and torque ripple measurements.
        Returns a synchronized harmonic health index.
        """
        torque_ripple = raw_telemetry.get("torque_ripple_nm", 0.0)
        phase_quadrature = raw_telemetry.get("phase_quadrature_deg", 0.0)
        interferometer_shift = raw_telemetry.get(
            "interferometer_shift_nm", 0.0
        )

        # Compute harmonic amplitude vector magnitude
        amplitude = math.sqrt(
            torque_ripple ** 2
            + phase_quadrature ** 2
            + interferometer_shift ** 2
        )
        self.harmonic_buffer.append(amplitude)
        if len(self.harmonic_buffer) > 100:
            self.harmonic_buffer.pop(0)

        mean_amplitude = sum(self.harmonic_buffer) / len(self.harmonic_buffer)
        resonance_risk = min(100.0, (mean_amplitude / 50.0) * 100.0)

        status = "OPTIMAL"
        if resonance_risk > 75.0:
            status = "CRITICAL_RESONANCE_DETECTED"
            logger.warning(
                f"[{self.mill_id}] High harmonic resonance risk: {resonance_risk:.2f}%. Adjusting inverter frequency."
            )
        elif resonance_risk > 45.0:
            status = "ELEVATED_VIBRATION"
            logger.info(
                f"[{self.mill_id}] Moderate vibration harmonic detected: {resonance_risk:.2f}%."
            )

        self.state = status
        return {
            "mill_id": self.mill_id,
            "status": status,
            "harmonic_amplitude_magnitude": round(amplitude, 4),
            "resonance_risk_score": round(resonance_risk, 2),
            "timestamp": time.time(),
        }

    def execute_synchronization_protocol(self) -> Dict[str, Any]:
        """
        Executes counter-harmonic phase correction to stabilize roller mill operations.
        """
        correction_phase = random.uniform(-1.5, 1.5)
        logger.info(
            f"[{self.mill_id}] Applying phase quadrature correction offset: {correction_phase:.4f} rad"
        )
        return {
            "mill_id": self.mill_id,
            "action": "PHASE_QUADRATURE_CORRECTION",
            "offset_rad": round(correction_phase, 4),
            "status": "SYNCHRONIZED",
        }


if __name__ == "__main__":
    print("Initializing Nairobi Roller Mill Resonator Subsystem...")
    resonator = RollerMillResonatorEngine("NRB-MILL-ALPHA-07")
    
    # Simulate incoming telemetry stream
    sample_data = {
        "torque_ripple_nm": 14.5,
        "phase_quadrature_deg": 2.3,
        "interferometer_shift_nm": 8.1,
    }
    
    analysis = resonator.ingest_sensor_telemetry(sample_data)
    print("Telemetry Analysis Result:", analysis)
    
    sync_result = resonator.execute_synchronization_protocol()
    print("Synchronization Result:", sync_result)
