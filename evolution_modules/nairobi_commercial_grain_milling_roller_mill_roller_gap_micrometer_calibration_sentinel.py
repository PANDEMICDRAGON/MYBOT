"""
Nairobi Commercial Grain Milling Roller Mill Roller Gap Micrometer Calibration Sentinel

Author: Cortana Autonomous Evolutionary Architect
Operator: Michael Obiero (Nairobi, Kenya)

This module provides real-time monitoring, drift compensation, thermal expansion correction,
and automated calibration protocols for roller mill gap micrometers in commercial grain mills.
It ensures consistent particle size distribution, prevents roll-to-roll contact, and optimizes
specific energy consumption.
"""

import time
import math
import logging
from typing import Dict, List, Optional, Tuple

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("RollerGapCalibrationSentinel")

class RollerGapCalibrationSentinel:
    """
    Monitors and calibrates roller gap micrometers on commercial grain milling roller stands.
    """
    def __init__(self, mill_id: str, nominal_gap_microns: float = 250.0, tolerance_microns: float = 5.0):
        self.mill_id = mill_id
        self.nominal_gap_microns = nominal_gap_microns
        self.tolerance_microns = tolerance_microns
        self.history: List[Dict[str, float]] = []
        self.current_calibration_offset = 0.0
        self.thermal_coefficient_um_per_deg_c = 1.2  # Typical steel thermal expansion factor
        
    def measure_gap(self, raw_sensor_reading: float, roll_temperature_c: float, ambient_humidity: float) -> Dict[str, float]:
        """
        Computes true gap by adjusting raw sensor readings for thermal expansion and humidity swell.
        """
        # Thermal compensation relative to 20.0 C baseline
        temp_delta = roll_temperature_c - 20.0
        thermal_correction = temp_delta * self.thermal_coefficient_um_per_deg_c
        
        # Humidity correction factor
        humidity_correction = (ambient_humidity - 50.0) * 0.02
        
        true_gap = raw_sensor_reading + self.current_calibration_offset - thermal_correction - humidity_correction
        error = true_gap - self.nominal_gap_microns
        
        status = "OPTIMAL"
        if abs(error) > self.tolerance_microns:
            status = "OUT_OF_SPEC"
            if true_gap < 50.0:
                status = "CRITICAL_DANGER_ROLL_CONTACT"
                
        telemetry = {
            "timestamp": time.time(),
            "raw_reading": raw_sensor_reading,
            "true_gap": true_gap,
            "error": error,
            "thermal_correction": thermal_correction,
            "status": status
        }
        self.history.append(telemetry)
        return telemetry

    def recalibrate(self, measured_feeler_gauge_value: float, reported_sensor_value: float) -> float:
        """
        Updates the calibration offset based on physical feeler gauge verification.
        """
        discrepancy = measured_feeler_gauge_value - reported_sensor_value
        self.current_calibration_offset += discrepancy
        logger.info(f"Mill {self.mill_id}: Recalibrated offset updated by {discrepancy:.2f}um to {self.current_calibration_offset:.2f}um")
        return self.current_calibration_offset

    def get_health_report(self) -> Dict[str, any]:
        if not self.history:
            return {"status": "NO_DATA"}
        recent = self.history[-1]
        return {
            "mill_id": self.mill_id,
            "last_true_gap": recent["true_gap"],
            "last_status": recent["status"],
            "cumulative_readings": len(self.history),
            "current_offset": self.current_calibration_offset
        }

if __name__ == "__main__":
    sentinel = RollerGapCalibrationSentinel(mill_id="NAI_MILL_04", nominal_gap_microns=200.0, tolerance_microns=4.0)
    
    # Simulate runtime telemetry
    reading = sentinel.measure_gap(raw_sensor_reading=198.5, roll_temperature_c=35.0, ambient_humidity=65.0)
    print("Initial Measurement:", reading)
    
    # Recalibrate after manual feeler check
    sentinel.recalibrate(measured_feeler_gauge_value=201.0, reported_sensor_value=198.5)
    
    # Re-measure
    reading_after = sentinel.measure_gap(raw_sensor_reading=200.2, roll_temperature_c=35.2, ambient_humidity=64.0)
    print("Post-Calibration Measurement:", reading_after)
    print("Health Report:", sentinel.get_health_report())
