import logging
import time
import random
import math
from typing import Dict, Any, List

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("RollerMillTorqueVectorPulseHarmonicSentinel")

class RollerMillTorqueVectorPulseHarmonicSentinel:
    """
    Monitors high-frequency torque vector pulses, harmonic distortion, and phase synchronization
    in Nairobi commercial grain milling roller mill drives. Ensures optimal differential speed
    ratios and prevents catastrophic gear or belt failure under heavy loads.
    """
    def __init__(self, mill_id: str = "NRB-MILL-01") -> None:
        self.mill_id = mill_id
        self.is_monitoring = False
        self.harmonic_threshold = 0.085  # Maximum allowable Total Harmonic Distortion (THD)
        self.pulse_jitter_limit_ms = 1.2
        logger.info(f"Initialized {self.__class__.__name__} for mill unit: {self.mill_id}")

    def analyze_torque_telemetry(self, telemetry: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyzes incoming torque vector telemetry and harmonic metrics.
        """
        vector_amplitude = telemetry.get("vector_amplitude", 1.0)
        harmonic_distortion = telemetry.get("harmonic_distortion", 0.04)
        pulse_jitter = telemetry.get(
            "pulse_jitter_ms", 0.4
        )
        phase_angle_deg = telemetry.get("phase_angle_deg", 0.0)

        # Compute anomaly score
        distortion_excess = max(0.0, harmonic_distortion - self.harmonic_threshold)
        jitter_excess = max(0.0, pulse_jitter - self.pulse_jitter_limit_ms)
        anomaly_score = (distortion_excess * 5.0) + (jitter_excess * 2.0) + abs(math.sin(math.radians(phase_angle_deg))) * 0.1

        status = "NOMINAL"
        action_required = "NONE"

        if anomaly_score > 0.5:
            status = "CRITICAL_HARMONIC_INSTABILITY"
            action_required = "EMERGENCY_DRIVE_INVERTER_MODULATION"
            logger.warning(f"[{self.mill_id}] CRITICAL: Harmonic/Vector anomaly detected! Score: {anomaly_score:.3f}")
        elif anomaly_score > 0.2:
            status = "ELEVATED_PULSE_JITTER"
            action_required = "ADJUST_DYNAMIC_COMPLIANCE"
            logger.info(f"[{self.mill_id}] WARNING: Elevated torque pulse jitter. Score: {anomaly_score:.3f}")
        else:
            logger.debug(f"[{self.mill_id}] Telemetry nominal. Score: {anomaly_score:.3f}")

        return {
            "mill_id": self.mill_id,
            "status": status,
            "anomaly_score": round(anomaly_score, 4),
            "harmonic_distortion": harmonic_distortion,
            "pulse_jitter_ms": pulse_jitter,
            "action_required": action_required,
            "timestamp": time.time()
        }

    def run_diagnostic_sweep(self) -> List[Dict[str, Any]]:
        """
        Simulates a rolling telemetry diagnostic sweep across dual roller stands.
        """
        results = []
        for stand in ["STAND_A_FAST_ROLL", "STAND_B_SLOW_ROLL"]:
            telemetry = {
                "vector_amplitude": random.uniform(0.95, 1.08),
                "harmonic_distortion": random.uniform(0.02, 0.095),
                "pulse_jitter_ms": random.uniform(0.1, 1.5),
                "phase_angle_deg": random.uniform(-15.0, 15.0)
            }
            res = self.analyze_torque_telemetry(telemetry)
            res["stand"] = stand
            results.append(res)
        return results

if __name__ == "__main__":
    sentinel = RollerMillTorqueVectorPulseHarmonicSentinel("NRB-UGALI-MILL-07")
    diagnostic_results = sentinel.run_diagnostic_sweep()
    for res in diagnostic_results:
        logger.info(f"Diagnostic Result: {res}")
