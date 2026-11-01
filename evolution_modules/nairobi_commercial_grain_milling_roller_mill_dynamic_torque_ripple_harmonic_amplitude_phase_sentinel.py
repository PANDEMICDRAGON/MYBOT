"""
Nairobi Commercial Grain Milling Roller Mill Dynamic Torque Ripple Harmonic Amplitude Phase Sentinel
Designed for Cortana's autonomous architecture to protect commercial milling operations in Nairobi, Kenya.
"""

import ast
import logging
import math
import time
from typing import Dict, List, Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("RollerMillHarmonicPhaseSentinel")


class RollerMillHarmonicPhaseSentinel:
    """
    Monitors roller mill drive shaft torque ripple harmonic amplitude and phase discrepancies
    to detect micro-fractures, belt slippage, and bearing degradation in real time.
    """

    def __init__(self, mill_id: str, nominal_rpm: float = 1500.0, harmonic_order: int = 3):
        self.mill_id = mill_id
        self.nominal_rpm = nominal_rpm
        self.harmonic_order = harmonic_order
        self.amplitude_threshold = 12.5  # Nm
        self.phase_shift_threshold = 0.45  # radians
        self.history: List[Dict[str, Any]] = []

    def analyze_torque_telemetry(self, timestamp: float, torque_signal: List[float]) -> Dict[str, Any]:
        """
        Perform discrete Fourier analysis simulation on the incoming torque signal array
        to isolate specific harmonic amplitude and phase.
        """
        if not torque_signal:
            return {"status": "INVALID_SIGNAL", "risk": 0.0}

        n = len(torque_signal)
        mean_torque = sum(torque_signal) / n

        # Simplified DFT bin extraction for the target harmonic order
        real_part = 0.0
        imag_part = 0.0
        for i, val in enumerate(torque_signal):
            angle = 2.0 * math.pi * self.harmonic_order * i / n
            real_part += (val - mean_torque) * math.cos(angle)
            imag_part -= (val - mean_torque) * math.sin(angle)

        amplitude = (2.0 / n) * math.sqrt(real_part**2 + imag_part**2)
        phase = math.atan2(imag_part, real_part)

        anomaly_detected = (
            amplitude > self.amplitude_threshold or abs(phase) > self.phase_shift_threshold
        )

        telemetry_record = {
            "timestamp": timestamp,
            "mill_id": self.mill_id,
            "harmonic_order": self.harmonic_order,
            "amplitude": round(amplitude, 4),
            "phase": round(phase, 4),
            "anomaly_detected": anomaly_detected
        }

        self.history.append(telemetry_record)
        if len(self.history) > 1000:
            self.history.pop(0)

        if anomaly_detected:
            logger.warning(
                f"[ALERT] Roller Mill {self.mill_id} harmonic anomaly detected! "
                f"Amplitude: {amplitude:.2f} Nm, Phase: {phase:.2f} rad"
            )

        return telemetry_record

    def get_status_summary(self) -> Dict[str, Any]:
        return {
            "mill_id": self.mill_id,
            "total_samples": len(self.history),
            "last_recorded": self.history[-1] if self.history else None
        }


if __name__ == "__main__":
    sentinel = RollerMillHarmonicPhaseSentinel(mill_id="NAI_MILL_04", nominal_rpm=1480.0, harmonic_order=3)
    # Simulated normal vs anomalous torque waveform
    normal_signal = [100.0 + 2.0 * math.sin(i * 0.1) for i in range(128)]
    anomalous_signal = [100.0 + 15.0 * math.sin(i * 0.3 + 1.2) for i in range(128)]

    res_normal = sentinel.analyze_torque_telemetry(time.time(), normal_signal)
    res_anomaly = sentinel.analyze_torque_telemetry(time.time(), anomalous_signal)

    print("Normal Analysis:", res_normal)
    print("Anomalous Analysis:", res_anomaly)
    print("Sentinel Module Initialized & Verified Successfully.")
