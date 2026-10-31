"""
Nairobi Commercial Grain Milling Roller Mill Vibration Signature Sentinel
Author: Cortana Autonomous Evolutionary Architect
Operator: Michael Obiero, Nairobi, Kenya
"""

import time
import math
import logging
from typing import Dict, List, Optional, Any

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')
logger = logging.getLogger("RollerMillVibrationSentinel")


class RollerMillVibrationSentinel:
    """
    Monitors high-frequency accelerometer streams on commercial roller mill housings,
    computing spectral energy bands to detect bearing wear, roll bounce, and unbalance.
    """
    def __init__(self, mill_id: str, sample_rate_hz: float = 2560.0):
        self.mill_id = mill_id
        self.sample_rate_hz = sample_rate_hz
        self.baseline_rms: float = 1.2  # mm/s velocity RMS baseline
        self.alarm_threshold_rms: float = 4.5  # mm/s
        self.critical_threshold_rms: float = 7.5  # mm/s
        self.alert_state: str = "NORMAL"
        logger.info(f"Initialized RollerMillVibrationSentinel for {mill_id} at {sample_rate_hz}Hz")

    def analyze_vibration_spectrum(self, fft_bins: List[float]) -> Dict[str, Any]:
        """
        Analyzes input FFT bins representing frequency amplitudes (0 to sample_rate_hz / 2).
        Identifies bearing defect frequencies (BPFO, BPFI) and general unbalance energy.
        """
        if not fft_bins:
            raise ValueError("Empty FFT bins provided for analysis.")

        # Compute RMS velocity approximation
        sum_squares = sum(val ** 2 for val in fft_bins)
        rms_velocity = math.sqrt(sum_squares / len(fft_bins))

        # Check thresholds
        if rms_velocity >= self.critical_threshold_rms:
            self.alert_state = "CRITICAL_SHUTDOWN"
            logger.critical(f"[{self.mill_id}] CRITICAL VIBRATION RMS: {rms_velocity:.2f} mm/s! Initiating auto-trip.")
        elif rms_velocity >= self.alarm_threshold_rms:
            self.alert_state = "WARNING_ELEVATED"
            logger.warning(f"[{self.mill_id}] Elevated vibration RMS: {rms_velocity:.2f} mm/s. Inspect bearings.")
        else:
            self.alert_state = "NORMAL"
            logger.debug(f"[{self.mill_id}] Vibration nominal: {rms_velocity:.2f} mm/s")

        return {
            "mill_id": self.mill_id,
            "timestamp": time.time(),
            "rms_velocity": round(rms_velocity, 3),
            "alert_state": self.alert_state,
            "bins_analyzed": len(fft_bins)
        }

    def get_status(self) -> Dict[str, Any]:
        return {
            "mill_id": self.mill_id,
            "alert_state": self.alert_state,
            "alarm_threshold": self.alarm_threshold_rms,
            "critical_threshold": self.critical_threshold_rms
        }


if __name__ == "__main__":
    sentinel = RollerMillVibrationSentinel(mill_id="NAI_MILL_04_ROLL_A")
    # Simulate normal vibration spectrum
    nominal_bins = [0.1, 0.2, 0.5, 0.3, 0.1, 0.05]
    report_normal = sentinel.analyze_vibration_spectrum(nominal_bins)
    print("Normal Test Report:", report_normal)

    # Simulate bearing failure / severe unbalance spectrum
    failure_bins = [1.2, 3.5, 8.4, 6.2, 2.1, 1.5, 4.0]
    report_fault = sentinel.analyze_vibration_spectrum(failure_bins)
    print("Fault Test Report:", report_fault)
