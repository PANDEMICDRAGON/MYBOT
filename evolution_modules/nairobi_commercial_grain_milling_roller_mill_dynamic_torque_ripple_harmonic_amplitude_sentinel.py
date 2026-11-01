"""
Nairobi Commercial Grain Milling Roller Mill Dynamic Torque Ripple Harmonic Amplitude Sentinel
Author: Cortana Autonomous Evolutionary Architect
Operator: Michael Obiero, Nairobi, Kenya

Monitors roller mill drive train torque ripple harmonics to detect gear mesh anomalies,
belt eccentricities, and bearing degradation in commercial grain processing facilities.
"""

import time
import math
import logging
from typing import Dict, List, Any, Optional

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')
logger = logging.getLogger("RollerMillHarmonicSentinel")

class RollerMillHarmonicSentinel:
    def __init__(self, mill_id: str, nominal_rpm: float = 1450.0, harmonic_orders: List[int] = None):
        self.mill_id = mill_id
        self.nominal_rpm = nominal_rpm
        self.harmonic_orders = harmonic_orders or [1, 2, 3, 6, 12]
        self.baseline_amplitudes: Dict[int, float] = {order: 0.15 for order in self.harmonic_orders}
        self.anomaly_threshold_multiplier = 2.5
        logger.info(f"Initialized RollerMillHarmonicSentinel for mill {mill_id} at {nominal_rpm} RPM.")

    def ingest_torque_spectrum(self, frequency_spectrum: Dict[float, float]) -> Dict[str, Any]:
        """
        Analyzes incoming FFT frequency spectrum data against expected harmonic orders.
        frequency_spectrum format: {frequency_hz: amplitude_nm}
        """
        fundamental_freq = self.nominal_rpm / 60.0
        results = {
            "mill_id": self.mill_id,
            "timestamp": time.time(),
            "status": "NORMAL",
            "anomalous_harmonics": [],
            "metrics": {}
        }

        for order in self.harmonic_orders:
            target_freq = fundamental_freq * order
            # Find closest frequency bin within 1.5 Hz tolerance
            matched_amp = 0.0
            for freq, amp in frequency_spectrum.items():
                if abs(freq - target_freq) <= 1.5:
                    matched_amp = max(matched_amp, amp)

            results["metrics"][f"harmonic_{order}x_amplitude"] = matched_amp
            baseline = self.baseline_amplitudes.get(order, 0.15)

            if matched_amp > (baseline * self.anomaly_threshold_multiplier):
                results["anomalous_harmonics"].append({
                    "order": order,
                    "expected_frequency_hz": target_freq,
                    "measured_amplitude": matched_amp,
                    "baseline_amplitude": baseline
                })

        if results["anomalous_harmonics"]:
            results["status"] = "WARNING"
            logger.warning(f"[ALERT] Roller mill {self.mill_id} exhibiting harmonic anomalies: {results['anomalous_harmonics']}")
        else:
            logger.info(f"[OK] Roller mill {self.mill_id} harmonic spectrum within normal operational bounds.")

        return results

    def calibrate_baseline(self, calibration_spectrum: Dict[float, float]) -> None:
        """Calibrates normal baseline harmonic amplitudes from a known good state."""
        fundamental_freq = self.nominal_rpm / 60.0
        for order in self.harmonic_orders:
            target_freq = fundamental_freq * order
            matched_amp = 0.15
            for freq, amp in calibration_spectrum.items():
                if abs(freq - target_freq) <= 1.5:
                    matched_amp = amp
                    break
            self.baseline_amplitudes[order] = matched_amp
        logger.info(f"Baseline calibrated for mill {self.mill_id}: {self.baseline_amplitudes}")

if __name__ == "__main__":
    sentinel = RollerMillHarmonicSentinel(mill_id="NAI-MILL-04")
    # Simulate healthy spectrum
    sample_spectrum = {24.1: 0.14, 48.2: 0.12, 72.3: 0.10, 144.6: 0.08, 289.2: 0.05}
    sentinel.calibrate_baseline(sample_spectrum)
    
    # Simulate anomalous spectrum with high 3rd harmonic
    anomalous_spectrum = {24.1: 0.14, 48.2: 0.13, 72.3: 0.65, 144.6: 0.08, 289.2: 0.06}
    evaluation = sentinel.ingest_torque_spectrum(anomalous_spectrum)
    print(f"Test Harness Evaluation Result: {evaluation}")
