"""
Nairobi Commercial Grain Milling Roller Mill Dynamic Harmonic Vibration Absorber Sentinel

Monitors roller mill vibration spectra, calculates harmonic frequencies, adjusts dynamic
absorber counter-masses, and preempts structural resonance failures in Nairobi grain mills.
"""

import logging
import time
import random
from typing import Dict, Any, List

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("RollerMillHarmonicAbsorberSentinel")


class RollerMillVibrationAbsorberSentinel:
    """
    Autonomous sentinel for detecting harmful harmonic vibration frequencies in roller mills
    and modulating dynamic damping mechanisms.
    """
    def __init__(self, mill_id: str, baseline_frequency_hz: float = 50.0):
        self.mill_id = mill_id
        self.baseline_frequency_hz = baseline_frequency_hz
        self.active_dampening_factor: float = 1.0
        self.resonance_alerts: List[Dict[str, Any]] = []

    def sample_vibration_spectrum(self) -> Dict[str, float]:
        """Simulate vibration sensor telemetry reading from the roller mill bearings."""
        # Introduce occasional resonance spikes to simulate load variations
        frequency_offset = random.uniform(-2.5, 3.5)
        if random.random() < 0.15:
            frequency_offset += random.uniform(15.0, 25.0)

        current_freq = self.baseline_frequency_hz + frequency_offset
        amplitude_g = random.uniform(0.1, 0.8) + (1.5 if abs(current_freq - self.baseline_frequency_hz) > 12.0 else 0.0)
        
        return {
            "frequency_hz": round(current_freq, 2),
            "amplitude_g": round(amplitude_g, 3),
            "timestamp": time.time()
        }

    def evaluate_harmonics(self, telemetry: Dict[str, float]) -> Dict[str, Any]:
        """Evaluate vibration telemetry against safety thresholds and calculate damper adjustment."""
        freq = telemetry["frequency_hz"]
        amp = telemetry["amplitude_g"]
        
        deviation = abs(freq - self.baseline_frequency_hz)
        status = "NOMINAL"
        action_taken = "NONE"

        if amp > 1.2 or deviation > 15.0:
            status = "CRITICAL_RESONANCE"
            self.active_dampening_factor = min(2.5, self.active_dampening_factor + 0.5)
            action_taken = "ENGAGE_TUNED_MASS_DAMPER"
            self.resonance_alerts.append({
                "timestamp": telemetry["timestamp"],
                "frequency": freq,
                "amplitude": amp
            })
        elif amp > 0.8 or deviation > 8.0:
            status = "WARNING"
            self.active_dampening_factor = min(1.8, self.active_dampening_factor + 0.2)
            action_taken = "ADJUST_COUNTER_MASS"
        else:
            status = "OPTIMAL"
            self.active_dampening_factor = max(1.0, self.active_dampening_factor - 0.1)
            action_taken = "MAINTAIN_STEADY_STATE"

        return {
            "mill_id": self.mill_id,
            "status": status,
            "dampening_factor": round(self.active_dampening_factor, 2),
            "action_taken": action_taken,
            "telemetry": telemetry
        }

    def run_diagnostic_cycle(self, iterations: int = 5) -> List[Dict[str, Any]]:
        """Execute a continuous diagnostic sequence for operational verification."""
        results = []
        logger.info(f"Starting Roller Mill Harmonic Sentinel diagnostics for {{self.mill_id}}...")
        for _ in range(iterations):
            telemetry = self.sample_vibration_spectrum()
            evaluation = self.evaluate_harmonics(telemetry)
            results.append(evaluation)
            logger.info(f"Mill Status: {{evaluation['status']}} | Dampening: {{evaluation['dampening_factor']}}x | Action: {{evaluation['action_taken']}}")
            time.sleep(0.1)
        return results


if __name__ == "__main__":
    sentinel = RollerMillVibrationAbsorberSentinel(mill_id="NAIROBI_MILL_LINE_03")
    diagnostic_results = sentinel.run_diagnostic_cycle(3)
    print(f"Completed {{len(diagnostic_results)}} vibration absorber telemetry cycles successfully.")
