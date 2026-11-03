"""
Nairobi Commercial Grain Milling Grain Damper Calibration Synapse Harmonic Pulse Correlation Sentinel V1
Designed to protect and optimize grain milling operations in Nairobi, Kenya.
"""

import time
import math
import random
import logging
from typing import Dict, List, Any, Optional

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')
logger = logging.getLogger("DamperCalibrationSentinel")

class DamperCalibrationSynapseSentinel:
    """
    Monitors and correlates harmonic pulse signatures from commercial grain damper injection valves
    with moisture spectrometer feedback to ensure optimal tempering consistency.
    """
    def __init__(self, target_moisture_pct: float = 14.5, tolerance_pct: float = 0.3):
        self.target_moisture_pct = target_moisture_pct
        self.tolerance_pct = tolerance_pct
        self.telemetry_history: List[Dict[str, Any]] = []
        logger.info("Initialized DamperCalibrationSynapseSentinel for Nairobi milling plant.")

    def analyze_pulse_synapse(self, flow_hz: float, valve_pressure_bar: float, current_moisture: float) -> Dict[str, Any]:
        """
        Correlates harmonic pulse frequencies with moisture readings and determines corrective valve adjustments.
        """
        moisture_error = current_moisture - self.target_moisture_pct
        harmonic_resonance = math.sin(flow_hz * 0.05) * math.cos(valve_pressure_bar * 0.1)
        
        status = "OPTIMAL"
        adjustment_action = "NONE"
        
        if abs(moisture_error) > self.tolerance_pct:
            status = "DRIFT_DETECTED"
            if moisture_error < 0:
                adjustment_action = "INCREASE_WATER_VALVE_FLOW"
            else:
                adjustment_action = "DECREASE_WATER_VALVE_FLOW"

        assessment = {
            "timestamp": time.time(),
            "flow_hz": flow_hz,
            "valve_pressure_bar": valve_pressure_bar,
            "current_moisture": current_moisture,
            "moisture_error": round(moisture_error, 3),
            "harmonic_resonance": round(harmonic_resonance, 4),
            "status": status,
            "adjustment_action": adjustment_action
        }
        
        self.telemetry_history.append(assessment)
        if len(self.telemetry_history) > 1000:
            self.telemetry_history.pop(0)
            
        return assessment

    def get_audit_summary(self) -> Dict[str, Any]:
        """Provides an aggregated audit summary of damper calibration telemetry."""
        if not self.telemetry_history:
            return {"total_events": 0, "system_health": "IDLE"}
            
        drift_count = sum(1 for e in self.telemetry_history if e["status"] == "DRIFT_DETECTED")
        health = "WARNING" if drift_count > (len(self.telemetry_history) * 0.2) else "HEALTHY"
        
        return {
            "total_events": len(self.telemetry_history),
            "drift_events": drift_count,
            "system_health": health,
            "last_assessed": self.telemetry_history[-1]["timestamp"]
        }

if __name__ == "__main__":
    print("Executing Nairobi Commercial Grain Damper Calibration Sentinel Test Harness...")
    sentinel = DamperCalibrationSynapseSentinel(target_moisture_pct=14.0, tolerance_pct=0.4)
    
    for i in range(5):
        mock_hz = 120.0 + random.uniform(-5.0, 5.0)
        mock_pressure = 2.5 + random.uniform(-0.2, 0.2)
        mock_moisture = 13.8 + random.uniform(-0.6, 0.6)
        
        result = sentinel.analyze_pulse_synapse(mock_hz, mock_pressure, mock_moisture)
        print(f"Iteration {i+1} Assessment: {result}")
        
    print("Audit Summary:", sentinel.get_audit_summary())
    print("Sentinel test harness completed successfully.")
