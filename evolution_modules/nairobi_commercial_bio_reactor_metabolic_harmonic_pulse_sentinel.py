import time
import math
import random
import logging
from typing import Dict, Any, List

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')
logger = logging.getLogger("BioReactorHarmonicPulseSentinel")

class BioReactorHarmonicPulseSentinel:
    """
    Monitors and synchronizes acoustic resonance, agitation impeller torque harmonics,
    and dissolved oxygen (DO) pulse profiles in Nairobi commercial bio-reactors to detect
    metabolic shifts, impending bioreactor foaming, or cavitation events.
    """
    def __init__(self, reactor_id: str, target_frequency_hz: float = 60.0):
        self.reactor_id = reactor_id
        self.target_frequency_hz = target_frequency_hz
        self.telemetry_history: List[Dict[str, Any]] = []
        logger.info(f"Initialized BioReactorHarmonicPulseSentinel for {{self.reactor_id}} at target freq {{target_frequency_hz}}Hz")

    def sample_metabolic_harmonics(self) -> Dict[str, Any]:
        """Simulates sensor telemetry reading from bio-reactor agitation shaft and gas sparger."""
        # Introduce minor stochastic variations simulating biological activity
        noise = random.gauss(0, 0.5)
        current_freq = self.target_frequency_hz + noise
        impeller_torque_nm = 120.0 + (noise * 2.3)
        dissolved_oxygen_pct = max(10.0, min(100.0, 45.0 + (noise * 4.0)))
        foam_index = max(0.0, min(1.0, 0.15 + (random.random() * 0.05)))

        reading = {
            "timestamp": time.time(),
            "reactor_id": self.reactor_id,
            "harmonic_frequency_hz": round(current_freq, 3),
            "impeller_torque_nm": round(impeller_torque_nm, 2),
            "dissolved_oxygen_pct": round(dissolved_oxygen_pct, 2),
            "foam_index": round(foam_index, 3)
        }
        self.telemetry_history.append(reading);
        if len(self.telemetry_history) > 1000:
            self.telemetry_history.pop(0)
        return reading

    def analyze_stability(self, reading: Dict[str, Any]) -> Dict[str, Any]:
        """Performs spectral variance analysis to detect anomalies or cavitation risks."""
        freq_delta = abs(reading["harmonic_frequency_hz"] - self.target_frequency_hz)
        anomaly_detected = freq_delta > 1.5 or reading["foam_index"] > 0.35
        
        status = "OPTIMAL"
        if anomaly_detected:
            status = "WARNING_CAVITATION_OR_FOAM"
            logger.warning(f"[{self.reactor_id}] Anomaly detected! Freq delta: {{freq_delta:.2f}}Hz, Foam index: {{reading['foam_index']}}")
        else:
            logger.info(f"[{self.reactor_id}] Bio-reactor stability normal. Torque: {{reading['impeller_torque_nm']}}Nm")

        return {
            "reactor_id": self.reactor_id,
            "status": status,
            "frequency_delta": round(freq_delta, 3),
            "action_recommended": "adjust_anti_foam_dosing" if reading["foam_index"] > 0.35 else "maintain_steady_state"
        }

if __name__ == "__main__":
    logger.info("Executing self-test harness for BioReactorHarmonicPulseSentinel...")
    sentinel = BioReactorHarmonicPulseSentinel(reactor_id="NRB-BR-04")
    for _ in range(3):
        data = sentinel.sample_metabolic_harmonics()
        analysis = sentinel.analyze_stability(data)
        print(analysis)
        time.sleep(0.1)
    logger.info("BioReactorHarmonicPulseSentinel self-test completed successfully.")
