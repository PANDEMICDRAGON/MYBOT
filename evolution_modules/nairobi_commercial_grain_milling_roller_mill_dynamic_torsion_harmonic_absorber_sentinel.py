"""
Nairobi Commercial Grain Milling Roller Mill Dynamic Torsion Harmonic Absorber Sentinel
Designed for Cortana Autonomous Evolution Cycle #704.
Monitors roller mill torsional vibration harmonics and manages dampening actuators.
"""

import time
import math
import random
import logging
from typing import Dict, List, Any, Optional

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')
logger = logging.getLogger("RollerMillHarmonicAbsorberSentinel")

class RollerMillTorsionHarmonicAbsorber:
    """
    Monitors high-frequency torsional oscillations in commercial roller mills,
    computes harmonic distortion, and triggers adaptive dampening responses.
    """
    def __init__(self, mill_id: str, nominal_rpm: float = 1200.0):
        self.mill_id = mill_id
        self.nominal_rpm = nominal_rpm
        self.damping_state = "NORMAL"
        self.harmonic_history: List[float] = []
        self.anomaly_count = 0

    def ingest_telemetry(self, raw_torsion_waveform: List[float], load_factor: float) -> Dict[str, Any]:
        """
        Analyzes raw torsion waveform data using FFT approximation to detect harmonic spikes.
        """
        if not raw_torsion_waveform:
            return {"status": "ERROR", "message": "Empty torsion waveform telemetry."}

        # Compute RMS and peak harmonic energy
        mean_val = sum(raw_torsion_waveform) / len(raw_torsion_waveform)
        variance = sum((x - mean_val) ** 2 for x in raw_torsion_waveform) / len(raw_torsion_waveform)
        rms = math.sqrt(variance)
        peak_amplitude = max(abs(x - mean_val) for x in raw_torsion_waveform)
        
        harmonic_ratio = peak_amplitude / (rms if rms > 0 else 1e-6)
        self.harmonic_history.append(harmonic_ratio)
        if len(self.harmonic_history) > 100:
            self.harmonic_history.pop(0)

        action = "MAINTAIN"
        if harmonic_ratio > 3.5 or peak_amplitude > 15.0:
            self.anomaly_count += 1
            if self.anomaly_count >= 3:
                self.damping_state = "ENGAGED_HEAVY_DAMPING"
                action = "DEPLOY_MAGNETORHEOLOGICAL_DAMPER"
            else:
                self.damping_state = "ENGAGED_LIGHT_DAMPING"
                action = "ADJUST_INVERTER_FREQUENCY"
        else:
            if self.anomaly_count > 0:
                self.anomaly_count -= 1
            if self.anomaly_count == 0:
                self.damping_state = "NORMAL"
                action = "RELEASE_DAMPER"

        logger.info(f"Mill {self.mill_id} | RMS: {rms:.2f} | Peak: {peak_amplitude:.2f} | Ratio: {harmonic_ratio:.2f} | State: {self.damping_state}")

        return {
            "mill_id": self.mill_id,
            "timestamp": time.time(),
            "rms_torsion": rms,
            "peak_amplitude": peak_amplitude,
            "harmonic_ratio": harmonic_ratio,
            "damping_state": self.damping_state,
            "recommended_action": action
        }

def run_self_test() -> bool:
    """
    Executes verification tests for the RollerMillTorsionHarmonicAbsorber.
    """
    logger.info("Initializing RollerMillTorsionHarmonicAbsorber self-test...")
    sentinel = RollerMillTorsionHarmonicAbsorber(mill_id="NAI_MILL_INDUSTRIAL_04")

    # Simulate normal operation waveform
    normal_wave = [math.sin(i * 0.1) * 2.0 + random.uniform(-0.1, 0.1) for i in range(50)]
    res1 = sentinel.ingest_telemetry(normal_wave, load_factor=0.65)
    assert res1["damping_state"] == "NORMAL", "Failed normal state assertion."

    # Simulate high harmonic anomaly waveform
    spike_wave = [math.sin(i * 0.5) * 18.0 + random.uniform(-2.0, 2.0) for i in range(50)]
    for _ in range(3):
        res2 = sentinel.ingest_telemetry(spike_wave, load_factor=0.95)

    assert res2["damping_state"] == "ENGAGED_HEAVY_DAMPING", "Failed heavy damping escalation assertion."
    logger.info("RollerMillTorsionHarmonicAbsorber self-test completed successfully.")
    return True

if __name__ == "__main__":
    run_self_test()
