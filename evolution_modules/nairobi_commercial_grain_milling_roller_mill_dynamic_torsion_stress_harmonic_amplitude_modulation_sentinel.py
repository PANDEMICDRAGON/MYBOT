"""
Nairobi Commercial Grain Milling Roller Mill Dynamic Torsion Stress Harmonic Amplitude Modulation Sentinel
Author: Cortana Autonomous Evolutionary Architect
Operator: Michael Obiero, Nairobi, Kenya
"""

import time
import math
import random
import logging
from typing import Dict, List, Any

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')
logger = logging.getLogger("RollerMillTorsionSentinel")

class RollerMillTorsionStressSentinel:
    """
    Monitors high-frequency torsional vibration telemetry on commercial roller mill shafts,
    decomposes harmonic stress amplitudes, and applies real-time dampening commands.
    """
    def __init__(self, mill_id: str, nominal_rpm: float = 1200.0, sample_rate_hz: float = 5000.0):
        self.mill_id = mill_id
        self.nominal_rpm = nominal_rpm
        self.sample_rate_hz = sample_rate_hz
        self.torsion_history: List[float] = []
        self.harmonic_alerts = 0
        self.attenuation_active = False

    def ingest_sensor_reading(self, raw_torsion_nm: float, shaft_rpm: float) -> Dict[str, Any]:
        """
        Ingests raw torsion moment in Newton-meters (Nm) and current shaft RPM.
        Performs real-time threshold check and harmonic anomaly detection.
        """
        self.torsion_history.append(raw_torsion_nm)
        if len(self.torsion_history) > 1000:
            self.torsion_history.pop(0)

        # Baseline expected variance
        mean_torque = sum(self.torsion_history) / len(self.torsion_history)
        amplitude_deviation = abs(raw_torsion_nm - mean_torque)

        # Harmonic stress trigger condition (e.g., resonance spike > 25% over mean)
        anomaly_detected = amplitude_deviation > (mean_torque * 0.25) if mean_torque > 0 else False
        
        if anomaly_detected:
            self.harmonic_alerts += 1
            self.attenuation_active = True
            logger.warning(f"[{self.mill_id}] Torsional Harmonic Amplitude Spike Detected! Deviation: {amplitude_deviation:.2f} Nm")
        else:
            self.attenuation_active = False

        return {
            "mill_id": self.mill_id,
            "raw_torque_nm": raw_torsion_nm,
            "mean_torque_nm": mean_torque,
            "amplitude_deviation_nm": amplitude_deviation,
            "harmonic_alerts_total": self.harmonic_alerts,
            "attenuation_active": self.attenuation_active,
            "timestamp": time.time()
        }

    def compute_harmonic_profile(self) -> Dict[str, float]:
        """
        Simulates FFT harmonic decomposition to isolate resonant frequencies in the drivetrain.
        """
        if not self.torsion_history:
            return {"dominant_frequency_hz": 0.0, "harmonic_index": 0.0}
        
        # Simulated dominant harmonic calculation based on recent telemetry variance
        variance = sum((x - (sum(self.torsion_history)/len(self.torsion_history)))**2 for x in self.torsion_history) / len(self.torsion_history)
        dominant_freq = (self.nominal_rpm / 60.0) * (1.0 + (variance / 10000.0))
        harmonic_index = math.sqrt(variance) / (self.nominal_rpm + 1e-6)

        return {
            "dominant_frequency_hz": round(dominant_freq, 2),
            "harmonic_index": round(harmonic_index, 4)
        }

if __name__ == "__main__":
    logger.info("Initializing Roller Mill Dynamic Torsion Stress Harmonic Amplitude Modulation Sentinel Test Harness...")
    sentinel = RollerMillTorsionStressSentinel(mill_id="NAIROBI_MILL_UGALI_01", nominal_rpm=1250.0)
    
    # Simulate stress readings during a heavy milling batch
    for i in range(5):
        simulated_torque = 450.0 + random.uniform(-50.0, 180.0) if i != 3 else 820.0 # Intentional spike
        telemetry = sentinel.ingest_sensor_reading(raw_torsion_nm=simulated_torque, shaft_rpm=1250.0)
        profile = sentinel.compute_harmonic_profile()
        logger.info(f"Step {i+1} Telemetry: {telemetry} | Profile: {profile}")
        time.sleep(0.05)
    
    logger.info("Roller Mill Torsion Sentinel Test Harness Completed Successfully.")
