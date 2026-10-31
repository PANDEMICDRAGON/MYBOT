"""Nairobi Commercial Grain Milling Roller Mill Roll Thermal Drift & Bearing Temp Sentinel."""

import time
import logging
import statistics
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field

logging.basicConfig(level=logging.INFO, format='%(asctime)s - [ROLLER_THERMAL_SENTINEL] - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class ThermalTelemetry:
    timestamp: float
    mill_id: str
    drive_side_temp_c: float
    operator_side_temp_c: float
    housing_temp_c: float
    ambient_temp_c: float
    vibration_mm_s: float

@dataclass
class ThermalDriftAnalysis:
    mill_id: str
    status: str
    delta_temp_drive: float
    delta_temp_operator: float
    thermal_asymmetry: float
    recommendation: str

class RollerMillThermalDriftSentinel:
    """Monitors thermal dynamics of commercial roller mills in grain processing."""
    
    def __init__(self, warning_threshold_c: float = 65.0, critical_threshold_c: float = 80.0, max_asymmetry_c: float = 7.0):
        self.warning_threshold_c = warning_threshold_c
        self.critical_threshold_c = critical_threshold_c
        self.max_asymmetry_c = max_asymmetry_c
        self.telemetry_history: Dict[str, List[ThermalTelemetry]] = {}

    def ingest(self, telemetry: ThermalTelemetry) -> ThermalDriftAnalysis:
        if telemetry.mill_id not in self.telemetry_history:
            self.telemetry_history[telemetry.mill_id] = []
            
        history = self.telemetry_history[telemetry.mill_id]
        history.append(telemetry)
        if len(history) > 100:
            history.pop(0)
            
        base_ambient = telemetry.ambient_temp_c
        delta_drive = telemetry.drive_side_temp_c - base_ambient
        delta_operator = telemetry.operator_side_temp_c - base_ambient
        asymmetry = abs(telemetry.drive_side_temp_c - telemetry.operator_side_temp_c)
        
        status = "OPTIMAL"
        recommendation = "Thermal profile within nominal parameters. Roll parallel is stable."
        
        if (telemetry.drive_side_temp_c >= self.critical_threshold_c or 
            telemetry.operator_side_temp_c >= self.critical_threshold_c or 
            telemetry.housing_temp_c >= self.critical_threshold_c):
            status = "CRITICAL_EMERGENCY_SHUTDOWN"
            recommendation = "CRITICAL: Bearing or roll temp exceeds safety limit. Trigger hydraulic roll separation & emergency stop."
            logger.error(f"[{telemetry.mill_id}] {recommendation} (Drive: {telemetry.drive_side_temp_c}°C, Operator: {telemetry.operator_side_temp_c}°C)")
            
        elif asymmetry > self.max_asymmetry_c:
            status = "WARNING_THERMAL_ASYMMETRY"
            recommendation = f"WARNING: Thermal asymmetry ({asymmetry:.2f}°C) exceeds tolerance. Adjust cooling water flow or check feed distribution."
            logger.warning(f"[{telemetry.mill_id}] {recommendation}")
            
        elif (telemetry.drive_side_temp_c >= self.warning_threshold_c or 
              telemetry.operator_side_temp_c >= self.warning_threshold_c):
            status = "WARNING_ELEVATED_TEMP"
            recommendation = "ELEVATED: Bearings running hot. Increase lubrication feed rate and inspect oil mist system."
            logger.warning(f"[{telemetry.mill_id}] {recommendation}")
            
        return ThermalDriftAnalysis(
            mill_id=telemetry.mill_id,
            status=status,
            delta_temp_drive=delta_drive,
            delta_temp_operator=delta_operator,
            thermal_asymmetry=asymmetry,
            recommendation=recommendation
        )

if __name__ == "__main__":
    sentinel = RollerMillThermalDriftSentinel()
    sample_telemetry = ThermalTelemetry(
        timestamp=time.time(),
        mill_id="RM-ENTERPRISE-04",
        drive_side_temp_c=72.5,
        operator_side_temp_c=63.0,
        housing_temp_c=68.0,
        ambient_temp_c=24.0,
        vibration_mm_s=2.4
    )
    analysis = sentinel.ingest(sample_telemetry)
    print(f"Roll Thermal Analysis Result: {analysis}")
