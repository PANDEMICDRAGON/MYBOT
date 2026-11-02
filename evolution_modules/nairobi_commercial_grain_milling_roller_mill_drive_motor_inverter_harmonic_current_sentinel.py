"""
Nairobi Commercial Grain Milling Roller Mill Drive Motor Inverter Harmonic Current Sentinel
Designed for autonomous oversight of VFD harmonic distortion and thermal stress in Nairobi industrial mills.
"""

import time
import math
import logging
from typing import Dict, List, Any, Optional

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] [%(name)s]: %(message)s')
logger = logging.getLogger("InverterHarmonicSentinel")


class InverterHarmonicSentinel:
    """
    Monitors VFD inverter harmonic distortion, carrier frequency ripple, and IGBT thermal profiles
    for heavy-duty grain milling roller mill drive motors.
    """

    def __init__(self, mill_id: str, rated_voltage: float = 415.0, max_thd_limit: float = 5.0):
        self.mill_id = mill_id
        self.rated_voltage = rated_voltage
        self.max_thd_limit = max_thd_limit
        self.telemetry_history: List[Dict[str, Any]] = []
        self.mitigation_active = False
        logger.info(f"InverterHarmonicSentinel initialized for mill: {self.mill_id} with THD limit: {self.max_thd_limit}%")

    def analyze_harmonic_telemetry(self, current_thd: float, voltage_thd: float, igbt_temp_c: float, carrier_freq_khz: float) -> Dict[str, Any]:
        """
        Analyzes incoming electrical telemetry and assesses harmonic risk and thermal degradation.
        """
        timestamp = time.time()
        
        # Compute harmonic severity index
        thd_excess = max(0.0, current_thd - self.max_thd_limit)
        thermal_stress_factor = max(0.0, (igbt_temp_c - 75.0) / 35.0)  # Baseline safe IGBT temp 75C
        severity_score = (thd_excess * 1.5) + (thermal_stress_factor * 2.5)
        
        status = "NOMINAL"
        action_required = "NONE"
        
        if severity_score > 3.0:
            status = "CRITICAL"
            action_required = "IMMEDIATE_VFD_DE_RATING_OR_FILTER_ENGAGEMENT"
            self.mitigation_active = True
            logger.warning(f"[{self.mill_id}] CRITICAL HARMONIC ANOMALY! Current THD: {current_thd}%, IGBT Temp: {igbt_temp_c}C")
        elif severity_score > 1.5:
            status = "WARNING"
            action_required = "MONITOR_ACTIVE_FRONT_END_HARMONIC_FILTERS"
            self.mitigation_active = False
            logger.info(f"[{self.mill_id}] WARNING: Elevated harmonic distortion detected. THD: {current_thd}%")
        else:
            self.mitigation_active = False

        record = {
            "timestamp": timestamp,
            "current_thd": current_thd,
            "voltage_thd": voltage_thd,
            "igbt_temp_c": igbt_temp_c,
            "carrier_freq_khz": carrier_freq_khz,
            "severity_score": round(severity_score, 4),
            "status": status,
            "action_required": action_required
        }
        
        self.telemetry_history.append(record)
        if len(self.telemetry_history) > 1000:
            self.telemetry_history.pop(0)
            
        return record

    def generate_mitigation_command(self) -> Dict[str, Any]:
        """
        Generates feedback control directives for VFD parameter adjustment.
        """
        if not self.mitigation_active:
            return {"command": "HOLD", "modulation_index_adjustment": 0.0, "active_damping": False}
            
        return {
            "command": "REDUCE_PWM_CARRIER_AND_ENGAGE_LC_TRAP",
            "modulation_index_adjustment": -0.05,
            "active_damping": True,
            "message": "Autonomous harmonic suppression protocols engaged to protect milling motor insulation."
        }


if __name__ == "__main__":
    print("Initializing InverterHarmonicSentinel Test Harness...")
    sentinel = InverterHarmonicSentinel(mill_id="NAIROBI_MILL_LINE_04")
    
    # Simulate normal operation
    res1 = sentinel.analyze_harmonic_telemetry(current_thd=2.1, voltage_thd=1.5, igbt_temp_c=62.5, carrier_freq_khz=4.0)
    print(f"Test 1 Status: {res1['status']} | Severity: {res1['severity_score']}")
    
    # Simulate severe harmonic distortion spike (e.g., non-linear load imbalance)
    res2 = sentinel.analyze_harmonic_telemetry(current_thd=7.8, voltage_thd=4.2, igbt_temp_c=88.0, carrier_freq_khz=4.0)
    print(f"Test 2 Status: {res2['status']} | Action: {res2['action_required']}")
    
    cmd = sentinel.generate_mitigation_command()
    print(f"Mitigation Directive Generated: {cmd}")
    print("InverterHarmonicSentinel test sequence completed successfully.")
