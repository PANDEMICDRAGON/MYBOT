"""Nairobi Commercial Grain Milling Roller Mill Dynamic Torsion Harmonic Amplitude Equilibrium Sentinel"""

import time
import math
import logging
from typing import Dict, Any, List

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("RollerMillHarmonicEquilibriumSentinel")

class RollerMillHarmonicEquilibriumSentinel:
    """Monitors roller mill drive shafts for harmonic torsion anomalies and maintains operational equilibrium."""
    
    def __init__(self, mill_id: str, sample_rate_hz: float = 100.0, harmonic_threshold: float = 4.5):
        self.mill_id = mill_id
        self.sample_rate_hz = sample_rate_hz
        self.harmonic_threshold = harmonic_threshold
        self.telemetry_history: List[Dict[str, float]] = []
        logger.info(f"Initialized Equilibrium Sentinel for Mill ID: {self.mill_id}")

    def measure_torsion_amplitude(self, raw_torque_signal: List[float]) -> Dict[str, Any]:
        """Calculates harmonic amplitude and checks equilibrium status."""
        if not raw_torque_signal:
            return {"status": "IDLE", "amplitude": 0.0, "equilibrium_factor": 1.0}
        
        mean_torque = sum(raw_torque_signal) / len(raw_torque_signal)
        variance = sum((x - mean_torque) ** 2 for x in raw_torque_signal) / len(raw_torque_signal)
        std_dev = math.sqrt(variance)
        
        # Simulated harmonic amplitude index
        harmonic_amplitude = std_dev / (abs(mean_torque) + 1e-6) * 10.0
        equilibrium_factor = max(0.0, 1.0 - (harmonic_amplitude / self.harmonic_threshold))
        
        status = "STABLE"
        if harmonic_amplitude > self.harmonic_threshold:
            status = "WARNING_RESONANCE_DETECTED"
        elif harmonic_amplitude > (self.harmonic_threshold * 1.5):
            status = "CRITICAL_TORSION_SPIKE"
            
        result = {
            "timestamp": time.time(),
            "mill_id": self.mill_id,
            "mean_torque": mean_torque,
            "harmonic_amplitude": harmonic_amplitude,
            "equilibrium_factor": equilibrium_factor,
            "status": status
        }
        self.telemetry_history.append(result)
        return result

    def attenuate_harmonic_feedback(self, status: str) -> str:
        """Executes countermeasures if resonance threatens mill rollers."""
        if status == "CRITICAL_TORSION_SPIKE":
            logger.critical(f"[{self.mill_id}] CRITICAL RESONANCE! Engaging dynamic inverter frequency offset.")
            return "INVERTER_MODULATION_APPLIED"
        elif status == "WARNING_RESONANCE_DETECTED":
            logger.warning(f"[{self.mill_id}] Warning harmonic elevation. Adjusting feed gate damper.")
            return "FEED_GATE_ADJUSTED"
        return "SYSTEM_NOMINAL"

if __name__ == "__main__":
    sentinel = RollerMillHarmonicEquilibriumSentinel(mill_id="NAIROBI_MILL_ALPHA_04")
    simulated_signal = [102.5, 98.1, 105.4, 91.2, 110.8, 89.5, 104.2]
    metrics = sentinel.measure_torsion_amplitude(simulated_signal)
    print("Metrics Output:", metrics)
    action = sentinel.attenuate_harmonic_feedback(metrics["status"])
    print("Mitigation Action:", action)
