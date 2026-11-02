"""
Nairobi Commercial Grain Milling Roller Mill Roller Gap Micrometer Correlation Synchronizer

Provides real-time analytics, drift compensation, and synchronization for roller mill gaps
using micrometer feedback loops and motor load correlation in industrial milling plants.
"""

import time
import math
import logging
from typing import Dict, List, Optional, Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("RollerGapCorrelationSynchronizer")

class RollerGapSynchronizer:
    """Synchronizes and calibrates roller mill gaps via micrometer feedback and load correlation."""

    def __init__(self, mill_id: str, nominal_gap_mm: float = 0.15):
        self.mill_id = mill_id
        self.nominal_gap_mm = nominal_gap_mm
        self.current_gap_mm = nominal_gap_mm
        self.calibration_offset = 0.0
        self.history: List[Dict[str, Any]] = []

    def measure_gap(self, raw_micrometer_reading: float, motor_load_amps: float, temperature_c: float) -> Dict[str, Any]:
        """Correlates raw micrometer readings with thermal expansion and motor load."""
        # Thermal expansion coefficient compensation (e.g., steel roll expansion)
        thermal_expansion_delta = (temperature_c - 25.0) * 0.0012
        adjusted_gap = raw_micrometer_reading + self.calibration_offset - thermal_expansion_delta
        
        # Load correction factor (higher load tightens effective gap slightly due to roll deflection)
        load_deflection_delta = (motor_load_amps - 45.0) * 0.0001 if motor_load_amps > 45.0 else 0.0
        final_effective_gap = adjusted_gap - load_deflection_delta

        deviation = final_effective_gap - self.nominal_gap_mm
        
        record = {
            "timestamp": time.time(),
            "mill_id": self.mill_id,
            "raw_micrometer": raw_micrometer_reading,
            "temperature_c": temperature_c,
            "motor_load_amps": motor_load_amps,
            "effective_gap_mm": round(final_effective_gap, 4),
            "deviation_mm": round(deviation, 4),
            "status": "OPTIMAL" if abs(deviation) < 0.02 else "DRIFT_DETECTED"
        }
        
        self.history.append(record)
        if len(self.history) > 1000:
            self.history.pop(0)
            
        return record

    def auto_calibrate(self, target_gap: float) -> float:
        """Calculates and applies automated calibration offset."""
        if not self.history:
            return self.calibration_offset
            
        latest = self.history[-1]
        error = target_gap - latest["effective_gap_mm"]
        self.calibration_offset += error * 0.5
        logger.info(f"Mill {self.mill_id} auto-calibrated. New offset: {self.calibration_offset:.4f}mm")
        return self.calibration_offset

if __name__ == "__main__":
    sync = RollerGapSynchronizer(mill_id="NAI_MILL_04", nominal_gap_mm=0.12)
    metrics = sync.measure_gap(raw_micrometer_reading=0.125, motor_load_amps=48.5, temperature_c=32.0)
    print(f"Initial Sync Result: {metrics}")
    offset = sync.auto_calibrate(target_gap=0.12)
    print(f"Calibration Offset Applied: {offset}")
