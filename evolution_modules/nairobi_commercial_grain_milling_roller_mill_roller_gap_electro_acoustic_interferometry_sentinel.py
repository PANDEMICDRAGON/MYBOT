"""
Nairobi Commercial Grain Milling Roller Mill Roller Gap Electro Acoustic Interferometry Sentinel
Author: Cortana Autonomous Evolutionary Architect
Operator: Michael Obiero (Nairobi, Kenya)

Performs real-time electro-acoustic interferometry on commercial roller mill roll gaps,
analyzing phase shifts and standing wave perturbations to prevent destructive roll clashes
and ensure uniform flour particle size distribution.
"""

import logging
import time
import math
import random
from typing import Dict, Any, List, Optional

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')
logger = logging.getLogger("RollerGapInterferometrySentinel")

class RollerGapElectroAcousticInterferometrySentinel:
    """
    Monitors roller mill roll gaps using electro-acoustic standing wave interferometry.
    Calculates phase variance, amplitude distortion, and predicts mechanical wear or gap drift.
    """
    def __init__(self, mill_id: str, nominal_gap_microns: float = 150.0, operating_frequency_hz: float = 40000.0):
        self.mill_id = mill_id
        self.nominal_gap_microns = nominal_gap_microns
        self.operating_frequency_hz = operating_frequency_hz
        self.phase_history: List[float] = []
        self.amplitude_history: List[float] = []
        self.max_history_len = 100
        logger.info(f"Initialized Interferometry Sentinel for Mill {self.mill_id} at {nominal_gap_microns}um gap, {operating_frequency_hz}Hz wave.")

    def sample_acoustic_wave(self, raw_phase_shift: float, raw_amplitude: float) -> Dict[str, Any]:
        """
        Ingests raw acoustic wave sensor telemetry, updates sliding windows, and evaluates gap integrity.
        """
        self.phase_history.append(raw_phase_shift)
        self.amplitude_history.append(raw_amplitude)
        if len(self.phase_history) > self.max_history_len:
            self.phase_history.pop(0)
            self.amplitude_history.pop(0)

        # Compute drift and interference metrics
        mean_phase = sum(self.phase_history) / len(self.phase_history)
        mean_amplitude = sum(self.amplitude_history) / len(self.amplitude_history)
        
        # Interferometry gap calculation model
        wavelength_um = 343000.0 / self.operating_frequency_hz  # Approx sound speed in air/metal proxy
        estimated_gap_deviation = (mean_phase / (2 * math.pi)) * wavelength_um
        current_estimated_gap = self.nominal_gap_microns + estimated_gap_deviation

        # Anomaly detection (e.g., rapid phase inversion or amplitude collapse)
        anomaly_score = abs(raw_phase_shift - mean_phase) * (1.0 / (raw_amplitude + 1e-5))
        status = "OPTIMAL"
        action_required = False

        if anomaly_score > 0.75 or current_estimated_gap < (self.nominal_gap_microns * 0.5):
            status = "CRITICAL_RISK_OF_ROLL_CLASH"
            action_required = True
            logger.warning(f"[{self.mill_id}] CRITICAL: Potential roll clash detected! Estimated gap: {current_estimated_gap:.2f}um")
        elif anomaly_score > 0.4:
            status = "WARNING_GAP_DRIFT"
            logger.info(f"[{self.mill_id}] WARNING: Gap drift detected. Estimated gap: {current_estimated_gap:.2f}um")

        telemetry = {
            "mill_id": self.mill_id,
            "timestamp": time.time(),
            "nominal_gap_microns": self.nominal_gap_microns,
            "estimated_gap_microns": round(current_estimated_gap, 3),
            "mean_phase_shift": round(mean_phase, 4),
            "mean_amplitude": round(mean_amplitude, 4),
            "anomaly_score": round(anomaly_score, 4),
            "status": status,
            "action_required": action_required
        }
        return telemetry

if __name__ == "__main__":
    print(f"Executing standalone test harness for RollerGapElectroAcousticInterferometrySentinel...")
    sentinel = RollerGapElectroAcousticInterferometrySentinel(mill_id="NAIROBI_MILL_ALPHA_04", nominal_gap_microns=120.0)
    
    # Simulate normal and aberrant telemetry stream
    for i in range(5):
        sim_phase = random.uniform(0.1, 0.3)
        sim_amp = random.uniform(8.5, 10.0)
        res = sentinel.sample_acoustic_wave(sim_phase, sim_amp)
        print(f"Step {i}: Status -> {res['status']}, Est Gap -> {res['estimated_gap_microns']}um")

    # Inject anomaly
    print("Injecting anomalous collision signal...")
    clash_res = sentinel.sample_acoustic_wave(raw_phase_shift=2.8, raw_amplitude=0.4)
    print(f"Clash Test Result: Status -> {clash_res['status']}, Action -> {clash_res['action_required']}")
    print("Sentinel test completed successfully.")
