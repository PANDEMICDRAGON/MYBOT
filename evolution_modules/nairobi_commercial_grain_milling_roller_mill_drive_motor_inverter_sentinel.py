"""
Nairobi Commercial Grain Milling Roller Mill Drive Motor Inverter Sentinel

Monitors VFD inverter metrics for roller mill drive motors including DC bus voltage,
IGBT heat sink temperature, total harmonic distortion (THD), output frequency jitter,
and phase current asymmetry. Protects critical milling infrastructure in Nairobi, Kenya.
"""

import time
import logging
from typing import Dict, Any, List, Optional

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')
logger = logging.getLogger("InverterSentinel")

class RollerMillDriveMotorInverterSentinel:
    """
    Real-time monitoring and fault isolation engine for commercial roller mill VFD inverters.
    """
    def __init__(self, motor_id: str, rated_kw: float = 75.0):
        self.motor_id = motor_id
        self.rated_kw = rated_kw
        self.status = "STANDBY"
        self.alert_history: List[Dict[str, Any]] = []
        logger.info(f"Inverter Sentinel initialized for Roller Mill Motor {self.motor_id} ({self.rated_kw} kW)")

    def evaluate_telemetry(self, telemetry: Dict[str, float]) -> Dict[str, Any]:
        """
        Evaluates VFD operating parameters against safe industrial thresholds.
        
        Telemetry keys expected:
        - dc_bus_volts: float (Nominal ~540-650V for 380V input)
        - heatsink_temp_c: float (IGBT temperature)
        - thd_percentage: float (Total Harmonic Distortion)
        - frequency_hz: float (Output frequency)
        - current_phase_imbalance_pct: float (Asymmetry across phases U, V, W)
        """
        dc_bus = telemetry.get("dc_bus_volts", 560.0)
        temp = telemetry.get("heatsink_temp_c", 45.0)
        thd = telemetry.get("thd_percentage", 3.5)
        freq = telemetry.get(
            "frequency_hz", 50.0)
        imbalance = telemetry.get("current_phase_imbalance_pct", 1.0)

        faults: List[str] = []
        warnings: List[str] = []

        # DC Bus Voltage Checks
        if dc_bus > 720.0:
            faults.append(f"CRITICAL: DC Bus Overvoltage ({dc_bus}V). Risk of capacitor breakdown or braking chopper failure.")
        elif dc_bus < 450.0:
            faults.append(f"CRITICAL: DC Bus Undervoltage ({dc_bus}V). Potential grid sag or rectifier bridge failure.")

        # IGBT Heatsink Temperature Checks
        if temp > 85.0:
            faults.append(f"CRITICAL: Inverter Heatsink Overheating ({temp}°C). Thermal trip imminent.")
        elif temp > 75.0:
            warnings.append(f"WARNING: Elevated Inverter Temperature ({temp}°C). Check cooling fans and ambient airflow.")

        # Harmonic Distortion Checks
        if thd > 8.0:
            faults.append(f"CRITICAL: High Total Harmonic Distortion ({thd}%). Active harmonic filter intervention required.")
        elif thd > 5.0:
            warnings.append(f"WARNING: Moderate THD elevation ({thd}%).")

        # Phase Imbalance Checks
        if imbalance > 4.5:
            faults.append(f"CRITICAL: Severe Phase Current Imbalance ({imbalance}%). Motor winding or IGBT leg fault.")
        elif imbalance > 2.5:
            warnings.append(f"WARNING: Phase imbalance drifting ({imbalance}%).")

        # Frequency Stability Checks
        if abs(freq - 50.0) > 15.0:
            warnings.append(f"NOTICE: Operating far from nominal 50Hz grid reference ({freq}Hz).")

        self.status = "FAULT" if faults else ("WARNING" if warnings else "OPTIMAL")

        evaluation_result = {
            "motor_id": self.motor_id,
            "timestamp": time.time(),
            "status": self.status,
            "faults": faults,
            "warnings": warnings,
            "metrics_analyzed": telemetry
        }

        if faults or warnings:
            self.alert_history.append(evaluation_result)
            for f in faults:
                logger.error(f"[{self.motor_id}] {f}")
            for w in warnings:
                logger.warning(f"[{self.motor_id}] {w}")
        else:
            logger.debug(f"[{self.motor_id}] Inverter telemetry nominal. Status: OPTIMAL")

        return evaluation_result

    def get_diagnostics(self) -> Dict[str, Any]:
        """
        Returns diagnostic summary and alert history.
        """
        return {
            "motor_id": self.motor_id,
            "rated_kw": self.rated_kw,
            "current_status": self.status,
            "total_recorded_incidents": len(self.alert_history),
            "recent_alerts": self.alert_history[-5:] if self.alert_history else []
        }

if __name__ == "__main__":
    print("--- Executing Nairobi Commercial Grain Milling Roller Mill Drive Motor Inverter Sentinel Test Harness ---")
    sentinel = RollerMillDriveMotorInverterSentinel(motor_id="RM-VFD-04", rated_kw=90.0)

    # Test normal telemetry
    normal_data = {
        "dc_bus_volts": 565.0,
        "heatsink_temp_c": 48.2,
        "thd_percentage": 3.1,
        "frequency_hz": 50.0,
        "current_phase_imbalance_pct": 0.8
    }
    res1 = sentinel.evaluate_telemetry(normal_data)
    assert res1["status"] == "OPTIMAL"

    # Test abnormal telemetry (Overheating & High THD)
    abnormal_data = {
        "dc_bus_volts": 560.0,
        "heatsink_temp_c": 88.5,
        "thd_percentage": 9.2,
        "frequency_hz": 45.0,
        "current_phase_imbalance_pct": 5.1
    }
    res2 = sentinel.evaluate_telemetry(abnormal_data)
    assert res2["status"] == "FAULT"
    print(f"Test passed successfully. Detected faults: {len(res2['faults'])}")
