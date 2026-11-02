"""
Nairobi Commercial Grain Milling Roller Mill Dynamic Torsion Harmonic Amplitude
Equilibrium Modulation Sentinel

Monitors torsional vibration, harmonic distortion, and shaft torque fluctuations
in commercial grain roller mills across Nairobi, applying real-time dynamic
equilibrium modulation to prevent mechanical failure and optimize milling precision.
"""

import time
import math
import random
import logging
from typing import Dict, Any, List, Optional

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')
logger = logging.getLogger("TorsionHarmonicEquilibriumSentinel")

class TorsionHarmonicEquilibriumSentinel:
    """
    Analyzes torsional vibration spectra and harmonic amplitude equilibrium in roller mills,
    modulating inverter excitation frequencies to dampen destructive resonant nodes.
    """

    def __init__(self, mill_id: str, rated_rpm: float = 1450.0, base_torque_nm: float = 350.0):
        self.mill_id = mill_id
        self.rated_rpm = rated_rpm
        self.base_torque_nm = base_torque_nm
        self.resonance_threshold_amplitude = 4.2  # mm/s RMS torsional velocity
        self.active_modulation_engaged = False
        self.harmonic_history: List[float] = []
        logger.info(f"Initialized TorsionHarmonicEquilibriumSentinel for Mill [{self.mill_id}]")

    def sample_telemetry(self) -> Dict[str, float]:
        """Simulates telemetry extraction from roller mill torsional strain gauges & shaft encoders."""
        rpm_jitter = random.gauss(0.0, 1.5)
        current_rpm = self.rated_rpm + rpm_jitter
        
        torque_ripple = random.gauss(0.0, 12.5)
        # Inject periodic resonant spike occasionally
        resonant_spike = 8.5 if random.random() < 0.15 else 0.0
        current_torque = self.base_torque_nm + torque_ripple + (resonant_spike * 15.0)
        
        torsional_amplitude = abs(torque_ripple / 10.0) + resonant_spike
        
        return {
            "timestamp": time.time(),
            "rpm": round(current_rpm, 2),
            "torque_nm": round(current_torque, 2),
            "torsional_amplitude_rms": round(torsional_amplitude, 3)
        }

    def evaluate_equilibrium(self, telemetry: Dict[str, float]) -> Dict[str, Any]:
        """
        Evaluates whether torsional harmonic amplitude exceeds safe equilibrium limits.
        Calculates phase counter-modulation offset if resonance is detected.
        """
        amp = telemetry["torsional_amplitude_rms"]
        self.harmonic_history.append(amp)
        if len(self.harmonic_history) > 100:
            self.harmonic_history.pop(0)

        status = "STABLE"
        modulation_offset = 0.0

        if amp > self.resonance_threshold_amplitude:
            self.active_modulation_engaged = True
            status = "RESONANCE_WARNING_MODULATING"
            # Generate anti-phase torque correction factor (-15% to -35% compensation)
            modulation_offset = round(-0.25 * (amp - self.resonance_threshold_amplitude), 4)
            logger.warning(f"[{self.mill_id}] Torsional resonance detected! Amp: {amp} mm/s > Threshold {self.resonance_threshold_amplitude}. Applying counter-modulation: {modulation_offset}")
        else:
            if self.active_modulation_engaged:
                logger.info(f"[{self.mill_id}] Torsional amplitude stabilized at {amp} mm/s. Disengaging active modulation.")
                self.active_modulation_engaged = False

        return {
            "mill_id": self.mill_id,
            "status": status,
            "torsional_amplitude_rms": amp,
            "modulation_offset_hz": modulation_offset,
            "active_modulation_engaged": self.active_modulation_engaged
        }

    def run_sentinel_cycle(self) -> Dict[str, Any]:
        """Executes a full diagnostic and modulation loop iteration."""
        raw_data = self.sample_telemetry()
        assessment = self.evaluate_equilibrium(raw_data)
        return assessment

if __name__ == "__main__":
    print("--- Starting Torsion Harmonic Equilibrium Sentinel Diagnostic Test ---")
    sentinel = TorsionHarmonicEquilibriumSentinel(mill_id="NAI-MILL-ALPHA-04")
    for cycle in range(5):
        result = sentinel.run_sentinel_cycle()
        print(f"Cycle {cycle + 1}: {result}")
        time.sleep(0.1)
    print("--- Sentinel Diagnostic Test Completed Successfully ---")
