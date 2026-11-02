"""Nairobi Commercial Grain Milling Roller Mill Dynamic Torsion Harmonic Damping Sentinel"""

import time
import math
import random
import logging
from typing import Dict, List, Any

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')
logger = logging.getLogger("RollerMillTorsionHarmonicSentinel")

class RollerMillTorsionHarmonicDampingSentinel:
    """
    Monitors high-frequency torsional oscillations and harmonic damping coefficients on commercial
    grain milling roller mill drive shafts in Nairobi mills to prevent shaft snapping and gear wear.
    """
    
    def __init__(self, mill_id: str = "NAI-MILL-01", baseline_damping_ratio: float = 0.15):
        self.mill_id = mill_id
        self.baseline_damping_ratio = baseline_damping_ratio
        self.anomaly_threshold = 0.30
        self.telemetry_history: List[Dict[str, Any]] = []

    def analyze_torsion_spectrum(self, rpm: float, torque_nm: float, vibration_spectrum: List[float]) -> Dict[str, Any]:
        """
        Analyzes torsional harmonic frequencies against baseline damping ratios.
        """
        # Calculate peak harmonic amplitude from vibration spectrum proxy
        peak_amplitude = max(vibration_spectrum) if vibration_spectrum else 0.0
        mean_amplitude = sum(vibration_spectrum) / len(vibration_spectrum) if vibration_spectrum else 0.0
        
        # Simulated damping ratio degradation factor under load
        load_factor = torque_nm / 1500.0
        current_damping_ratio = max(0.01, self.baseline_damping_ratio * (1.0 - (load_factor * 0.15) - (peak_amplitude * 0.05)))
        
        harmonic_stress_index = (peak_amplitude / (mean_amplitude + 1e-6)) * (rpm / 1000.0)
        
        is_anomaly = harmonic_stress_index > self.anomaly_threshold or current_damping_ratio < 0.08

        telemetry = {
            "timestamp": time.time(),
            "mill_id": self.mill_id,
            "rpm": rpm,
            "torque_nm": torque_nm,
            "damping_ratio": round(current_damping_ratio, 4),
            "harmonic_stress_index": round(harmonic_stress_index, 4),
            "status": "CRITICAL_DAMPING_FAILURE" if is_anomaly else "NOMINAL"
        }

        self.telemetry_history.append(telemetry)
        if len(self.telemetry_history) > 100:
            self.telemetry_history.pop(0)

        if is_anomaly:
            logger.warning(f"[{self.mill_id}] Torsional Harmonic Damping Anomaly Detected! Index: {harmonic_stress_index:.3f}, Damping: {current_damping_ratio:.3f}")
        else:
            logger.info(f"[{self.mill_id}] Roller mill torsion nominal. Damping: {current_damping_ratio:.3f}")

        return telemetry

    def execute_countermeasure(self, telemetry: Dict[str, Any]) -> Dict[str, str]:
        """
        Applies automated inverter frequency adjustment to bypass resonant harmonic frequencies.
        """
        if telemetry["status"] == "CRITICAL_DAMPING_FAILURE":
            adjustment_hz = random.uniform(-2.5, 2.5)
            logger.critical(f"[{self.mill_id}] AUTOMATED COUNTERMEASURE: Shifting drive inverter frequency by {adjustment_hz:+.2f} Hz to detune torsional resonance.")
            return {
                "action": "INVERTER_FREQUENCY_SHIFT",
                "status": "EXECUTED",
                "adjustment_hz": str(round(adjustment_hz, 2))
            }
        return {"action": "NONE", "status": "STANDBY"}

if __name__ == "__main__":
    sentinel = RollerMillTorsionHarmonicDampingSentinel(mill_id="NAI-UGALI-MILL-7")
    simulated_spectrum = [random.uniform(0.1, 0.9) for _ in range(16)]
    simulated_spectrum[5] = 2.8 # Inject harmonic spike
    
    telemetry = sentinel.analyze_torsion_spectrum(rpm=1450.0, torque_nm=1120.5, vibration_spectrum=simulated_spectrum)
    action = sentinel.execute_countermeasure(telemetry)
    print("Test Execution Complete:", telemetry, action)
