import math
import time
import logging
from typing import Dict, Any, List

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("RollerMillTorqueValidator")

class RollerMillTorqueHarmonicValidator:
    """
    Monitors, correlates, and predicts harmonic torque ripple phase quadrature resolver interferometry
    for heavy-duty roller mills in Nairobi commercial grain milling facilities.
    """
    def __init__(self, mill_id: str, nominal_rpm: float = 1500.0):
        self.mill_id = mill_id
        self.nominal_rpm = nominal_rpm
        self.sample_buffer: List[Dict[str, float]] = []

    def ingest_telemetry(self, torque_nm: float, resolver_phase_deg: float, vibration_mm_s: float) -> Dict[str, Any]:
        timestamp = time.time()
        sample = {
            "timestamp": timestamp,
            "torque_nm": torque_nm,
            "resolver_phase_deg": resolver_phase_deg,
            "vibration_mm_s": vibration_mm_s
        }
        self.sample_buffer.append(sample)
        if len(self.sample_buffer) > 100:
            self.sample_buffer.pop(0)
            
        return self._analyze_harmonics()

    def _analyze_harmonics(self) -> Dict[str, Any]:
        if not self.sample_buffer:
            return {"status": "insufficient_data"}

        recent = self.sample_buffer[-1]
        torque = recent["torque_nm"]
        phase = recent["resolver_phase_deg"]
        vibration = recent["vibration_mm_s"]

        # Synthetic quadrature interferometry correlation metric
        harmonic_amplitude = abs(torque * math.sin(math.radians(phase))) * 0.05
        quadrature_error = math.cos(math.radians(phase)) * vibration

        status = "OPTIMAL"
        if harmonic_amplitude > 12.5 or abs(quadrature_error) > 3.0:
            status = "WARNING_HARMONIC_DEVIATION"

        return {
            "mill_id": self.mill_id,
            "harmonic_amplitude_est": round(harmonic_amplitude, 4),
            "quadrature_error_est": round(quadrature_error, 4),
            "status": status,
            "timestamp": recent["timestamp"]
        }

if __name__ == "__main__":
    validator = RollerMillTorqueHarmonicValidator(mill_id="NAIROBI_MILL_ALPHA_01")
    result = validator.ingest_telemetry(torque_nm=245.8, resolver_phase_deg=45.2, vibration_mm_s=1.2)
    logger.info(f"Autonomous Validation Test Result: {result}")
