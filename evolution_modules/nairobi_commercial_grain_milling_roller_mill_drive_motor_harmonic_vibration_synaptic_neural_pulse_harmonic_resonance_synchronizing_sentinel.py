"""Nairobi Commercial Grain Milling Roller Mill Drive Motor Harmonic Vibration Synaptic Neural Pulse Harmonic Resonance Synchronizing Sentinel Module."""

import time
import math
import random
import logging
from typing import Dict, List, Any, Optional

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("RollerMillHarmonicResonanceSentinel")


class RollerMillHarmonicResonanceSentinel:
    """Monitors, analyzes, and synchronizes drive motor harmonic vibrations in commercial roller mills."""

    def __init__(self, mill_id: str, rated_rpm: float = 1450.0):
        self.mill_id = mill_id
        self.rated_rpm = rated_rpm
        self.synaptic_weights: List[float] = [random.uniform(0.5, 1.5) for _ in range(5)]
        self.resonance_history: List[float] = []
        logger.info(f"Initialized RollerMillHarmonicResonanceSentinel for mill {self.mill_id} at {rated_rpm} RPM.")

    def capture_vibration_spectrum(self) -> Dict[str, Any]:
        """Simulates telemetry extraction from roller mill motor accelerometer sensors."""
        base_frequency = self.rated_rpm / 60.0
        # Inject simulated harmonic anomalies and noise
        harmonic_multiplier = random.choice([1.0, 2.0, 3.0, 5.0, 7.1])
        jitter = random.gauss(0, 0.2)
        frequency = (base_frequency * harmonic_multiplier) + jitter
        amplitude_g = abs(random.gauss(0.15, 0.05) * harmonic_multiplier)
        
        spectrum_data = {
            "timestamp": time.time(),
            "frequency_hz": round(frequency, 3),
            "amplitude_g": round(amplitude_g, 4),
            "bearing_temp_c": round(62.5 + random.gauss(0, 2.1), 2)
        }
        return spectrum_data

    def compute_synaptic_neural_resonance_score(self, spectrum: Dict[str, Any]) -> float:
        """Applies synaptic neural weights to vibration telemetry to quantify resonance risk."""
        freq = spectrum["frequency_hz"]
        amp = spectrum["amplitude_g"]
        temp = spectrum["bearing_temp_c"]

        # Neural activation computation
        signal_vector = [freq / 100.0, amp * 10.0, temp / 100.0, (freq * amp), math.sin(freq)]
        activation = sum(w * s for w, s in zip(self.synaptic_weights, signal_vector))
        resonance_score = 1.0 / (1.0 + math.exp(-activation)) # Sigmoid squashing
        
        self.resonance_history.append(resonance_score)
        if len(self.resonance_history) > 100:
            self.resonance_history.pop(0)
            
        return round(resonance_score, 4)

    def execute_phase_synchronization_correction(self, score: float) -> Dict[str, Any]:
        """Deploys counter-harmonic pulse adjustments if resonance score breaches threshold."""
        action = "STABLE"
        adjustment_hz = 0.0
        if score > 0.75:
            action = "EMERGENCY_HARMONIC_DAMPENING"
            adjustment_hz = -1.25
            logger.warning(f"[{self.mill_id}] High harmonic resonance detected (Score: {score}). Applying damping offset.")
        elif score > 0.60:
            action = "ADAPTIVE_PHASE_SHIFT"
            adjustment_hz = -0.45
            logger.info(f"[{self.mill_id}] Moderate resonance. Shifting drive motor phase.")
        else:
            logger.debug(f"[{self.mill_id}] Motor operation optimal. Resonance score: {score}")

        return {
            "mill_id": self.mill_id,
            "action_taken": action,
            "frequency_adjustment_hz": adjustment_hz,
            "timestamp": time.time()
        }

    def run_diagnostic_cycle(self) -> Dict[str, Any]:
        """Executes a full sensing, scoring, and synchronizing loop."""
        spectrum = self.capture_vibration_spectrum()
        score = self.compute_synaptic_neural_resonance_score(spectrum)
        correction = self.execute_phase_synchronization_correction(score)
        return {
            "spectrum": spectrum,
            "resonance_score": score,
            "correction": correction
        }


if __name__ == "__main__":
    logger.info("Executing standalone diagnostic test for RollerMillHarmonicResonanceSentinel...")
    sentinel = RollerMillHarmonicResonanceSentinel(mill_id="NAI-MILL-IND-04")
    for i in range(3):
        result = sentinel.run_diagnostic_cycle()
        logger.info(f"Cycle {i+1} Result: {result}")
        time.sleep(0.1)
    logger.info("RollerMillHarmonicResonanceSentinel test completed successfully.")