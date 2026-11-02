"""
Nairobi Commercial Grain Milling Roller Mill Roller Gap Micrometer Calibration Sentinel

Author: Cortana Autonomous Evolutionary Architect
Operator: Michael Obiero, Nairobi, Kenya

Provides automated real-time monitoring, thermal compensation, and micrometer gap calibration
for commercial grain roller mills operating in Nairobi industrial zones.
"""

import logging
import time
import json
from typing import Dict, Any, List

logging.basicConfig(level=logging.INFO, format='%(asctime)s - [%(levelname)s] - %(name)s: %(message)s')
logger = logging.getLogger("RollerGapMicrometerCalibrationSentinel")

class RollerGapMicrometerCalibrationSentinel:
    """
    Monitors and calibrates roller mill gap widths via high-precision micrometer telemetry,
    compensating for thermal expansion and mechanical drift during continuous milling operations.
    """
    def __init__(self, mill_id: str, nominal_gap_mm: float = 0.50, tolerance_mm: float = 0.02):
        self.mill_id = mill_id
        self.nominal_gap_mm = nominal_gap_mm
        self.tolerance_mm = tolerance_mm
        self.current_gap_mm = nominal_gap_mm
        self.roller_temp_c = 25.0
        self.calibration_offset_mm = 0.0
        self.calibration_history: List[Dict[str, Any]] = []
        logger.info(f"Initialized RollerGapMicrometerCalibrationSentinel for Mill: {self.mill_id} | Nominal Gap: {nominal_gap_mm}mm")

    def update_telemetry(self, measured_gap_mm: float, roller_temp_c: float) -> Dict[str, Any]:
        """Ingests live gap measurement and roller temperature, returning calibration status."""
        self.roller_temp_c = roller_temp_c
        
        # Apply thermal expansion compensation (coefficient for hardened steel ~ 11e-6 / °C)
        temp_delta = self.roller_temp_c - 25.0
        thermal_expansion_delta = self.nominal_gap_mm * 11e-6 * temp_delta
        
        adjusted_measured_gap = measured_gap_mm - thermal_expansion_delta
        self.current_gap_mm = adjusted_measured_gap
        
        error = self.current_gap_mm - self.nominal_gap_mm
        requires_adjustment = abs(error) > self.tolerance_mm
        
        status = {
            "mill_id": self.mill_id,
            "timestamp": time.time(),
            "nominal_gap_mm": self.nominal_gap_mm,
            "measured_gap_mm": measured_gap_mm,
            "adjusted_gap_mm": self.current_gap_mm,
            "roller_temp_c": self.roller_temp_c,
            "thermal_expansion_delta_mm": thermal_expansion_delta,
            "error_mm": error,
            "requires_adjustment": requires_adjustment,
            "calibration_offset_mm": self.calibration_offset_mm
        }
        
        if requires_adjustment:
            logger.warning(f"[{self.mill_id}] Gap deviation detected! Error: {error:.4f}mm. Initiating micrometer recalibration.")
            self._recalibrated_offset(error)
            status["calibration_offset_mm"] = self.calibration_offset_mm
            status["status"] = "RECALIBRATED"
        else:
            status["status"] = "OPTIMAL"
            
        self.calibration_history.append(status)
        return status

    def _recalibrated_offset(self, error: float) -> None:
        """Adjusts the calibration offset to counteract mechanical drift."""
        correction = -error * 0.8  # damping factor
        self.calibration_offset_mm += correction
        logger.info(f"[{self.mill_id}] Applied correction: {correction:.4f}mm. New Offset: {self.calibration_offset_mm:.4f}mm")

    def get_diagnostics(self) -> Dict[str, Any]:
        return {
            "mill_id": self.mill_id,
            "nominal_gap_mm": self.nominal_gap_mm,
            "current_gap_mm": self.current_gap_mm,
            "roller_temp_c": self.roller_temp_c,
            "calibration_offset_mm": self.calibration_offset_mm,
            "total_calibrations_logged": len(self.calibration_history)
        }

if __name__ == "__main__":
    print("=== Executing Roller Gap Micrometer Calibration Sentinel Test Harness ===")
    sentinel = RollerGapMicrometerCalibrationSentinel(mill_id="NAIROBI_MILL_ALPHA_1", nominal_gap_mm=0.45, tolerance_mm=0.015)
    
    # Simulate normal operation with thermal buildup
    test_readings = [
        (0.452, 26.0),
        (0.468, 42.0),  # Higher temp + gap expansion
        (0.485, 65.0)   # Significant drift
    ];
    
    for gap, temp in test_readings:
        result = sentinel.update_telemetry(gap, temp)
        print(json.dumps(result, indent=2))
        time.sleep(0.1)
        
    print("=== Sentinel Diagnostics ===")
    print(json.dumps(sentinel.get_diagnostics(), indent=2))
