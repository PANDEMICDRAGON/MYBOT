"""
Nairobi Commercial Grain Milling Roller Mill Roller Gap Electro Acoustic Spectroscopy Sentinel
Autonomous Evolutionary Architecture Module #764

Monitors roller mill gap acoustics, spectral energy densities, and harmonic vibration anomalies
for high-throughput grain mills in Nairobi, Kenya.
"""

import logging
import time
import math
import random
from typing import Dict, List, Any, Optional

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')
logger = logging.getLogger("RollerGapAcousticSpectroscopySentinel")

class RollerGapAcousticSpectroscopySentinel:
    """
    Analyzes high-frequency acoustic emissions and gap clearance telemetry to detect
    imminent roller touch, bearing wear, or uneven grain feed distribution in roller mills.
    """

    def __init__(self, mill_id: str, roll_pair_id: str, target_gap_mm: float = 0.15):
        self.mill_id = mill_id
        self.roll_pair_id = roll_pair_id
        self.target_gap_mm = target_gap_mm
        self.acoustic_history: List[float] = []
        self.gap_history: List[float] = []
        self.anomaly_count = 0
        logger.info(f"Initialized Acoustic Spectroscopy Sentinel for Mill {self.mill_id}, Roll Pair {self.roll_pair_id}")

    def analyze_spectrum(self, vibration_db: float, measured_gap_mm: float, frequency_spectrum: List[float]) -> Dict[str, Any]:
        """
        Evaluates real-time acoustic spectrum and gap dimensions against nominal baselines.
        """
        self.acoustic_history.append(vibration_db)
        self.gap_history.append(measured_gap_mm)
        if len(self.acoustic_history) > 100:
            self.acoustic_history.pop(0)
            self.gap_history.pop(0)

        # Compute spectral energy concentration in high-frequency bands (e.g., 10kHz - 40kHz)
        hf_energy = sum(frequency_spectrum[int(len(frequency_spectrum)*0.6):]) if frequency_spectrum else 0.0
        gap_deviation = abs(measured_gap_mm - self.target_gap_mm)

        status = "OPTIMAL"
        corrective_action = "NONE"

        if gap_deviation > 0.05 or vibration_db > 85.0 or hf_energy > 500.0:
            self.anomaly_count += 1
            status = "WARNING"
            corrective_action = "ADJUST_HYDRAULIC_GAP_ACTUATOR"
            if gap_deviation > 0.1 or vibration_db > 95.0:
                status = "CRITICAL"
                corrective_action = "EMERGENCY_ROLL_DISENGAGE"

        assessment = {
            "mill_id": self.mill_id,
            "roll_pair_id": self.roll_pair_id,
            "measured_gap_mm": measured_gap_mm,
            "target_gap_mm": self.target_gap_mm,
            "gap_deviation_mm": round(gap_deviation, 4),
            "vibration_db": round(vibration_db, 2),
            "hf_spectral_energy": round(hf_energy, 2),
            "status": status,
            "corrective_action": corrective_action,
            "timestamp": time.time()
        }

        if status != "OPTIMAL":
            logger.warning(f"Acoustic anomaly detected on {self.roll_pair_id}: {assessment}")

        return assessment

    def get_diagnostics(self) -> Dict[str, Any]:
        return {
            "mill_id": self.mill_id,
            "roll_pair_id": self.roll_pair_id,
            "total_anomalies": self.anomaly_count,
            "avg_vibration_db": round(sum(self.acoustic_history) / max(len(self.acoustic_history), 1), 2),
            "avg_gap_mm": round(sum(self.gap_history) / max(len(self.gap_history), 1), 4)
        }

if __name__ == "__main__":
    logger.info("Executing self-test for RollerGapAcousticSpectroscopySentinel...")
    sentinel = RollerGapAcousticSpectroscopySentinel(mill_id="NAI_MILL_04", roll_pair_id="B1_FAST_SLOW")
    
    # Simulate normal and anomalous runs
    for i in range(5):
        mock_spectrum = [random.uniform(10, 50) for _ in range(50)]
        result = sentinel.analyze_spectrum(
            vibration_db=72.5 + random.uniform(-2, 2),
            measured_gap_mm=0.15 + random.uniform(-0.01, 0.01),
            frequency_spectrum=mock_spectrum
        )
        print(f"Test Iteration {i}: Status -> {result['status']}")

    # Simulate touch/anomaly
    anomaly_spectrum = [random.uniform(100, 300) for _ in range(50)]
    anomaly_result = sentinel.analyze_spectrum(
        vibration_db=98.2,
        measured_gap_mm=0.02,
        frequency_spectrum=anomaly_spectrum
    )
    print(f"Anomaly Test: Status -> {anomaly_result['status']}, Action -> {anomaly_result['corrective_action']}")
    print(f"Diagnostics: {sentinel.get_diagnostics()}")
    logger.info("Module self-test completed successfully.")
