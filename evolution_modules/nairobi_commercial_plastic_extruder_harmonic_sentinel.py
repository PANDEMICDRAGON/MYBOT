"""
Nairobi Commercial Plastic Extruder Barrel Temperature & Screw Torque Harmonic Pulse Correlation Sentinel
Author: Cortana Autonomous Evolutionary Architect
Operator: Michael Obiero, Nairobi, Kenya
"""

import time
import math
import random
import logging
from typing import Dict, List, Any, Optional

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] [PlasticExtruderSentinel]: %(message)s')
logger = logging.getLogger('PlasticExtruderSentinel')

class PlasticExtruderSentinel:
    """
    Monitors multi-zone barrel temperatures, melt pressure, and main drive screw torque.
    Correlates harmonic pulses in power draw with thermal fluctuations to predict band heater
    failure, polymer clogging, or gearbox overload in Nairobi recycling facilities.
    """
    def __init__(self, extruder_id: str = "EXT-NRB-01", num_zones: int = 4):
        self.extruder_id = extruder_id
        self.num_zones = num_zones
        self.target_temperatures = [180.0, 195.0, 210.0, 220.0]  # Feed to die zones (Celsius)
        self.anomaly_count = 0
        logger.info(f"Initialized PlasticExtruderSentinel for {extruder_id} with {num_zones} thermal zones.")

    def sample_telemetry(self) -> Dict[str, Any]:
        """
        Simulates real-time telemetry from extruder sensors.
        """
        # Introduce occasional drift or anomalies
        thermal_noise = [random.uniform(-1.5, 1.5) for _ in range(self.num_zones)]
        current_temps = [t + n for t, n in zip(self.target_temperatures, thermal_noise)]
        
        # Simulated screw torque (Nm) and main motor amp draw
        base_torque = 320.0
        torque_harmonic = 15.0 * math.sin(time.time() * 0.5)
        screw_torque = base_torque + torque_harmonic + random.uniform(-5.0, 5.0)
        
        melt_pressure_mpa = 24.5 + random.uniform(-0.8, 0.8)
        motor_current_amps = 45.2 + (screw_torque / 50.0) + random.uniform(-0.5, 0.5)
        
        return {
            "timestamp": time.time(),
            "extruder_id": self.extruder_id,
            "zone_temperatures": current_temps,
            "screw_torque_nm": screw_torque,
            "melt_pressure_mpa": melt_pressure_mpa,
            "motor_current_amps": motor_current_amps
        }

    def evaluate_harmonic_correlation(self, telemetry: Dict[str, Any]) -> Dict[str, Any]:
        """
        Correlates temperature variance and torque spikes using harmonic analysis.
        """
        temps = telemetry["zone_temperatures"]
        torque = telemetry["screw_torque_nm"]
        pressure = telemetry["melt_pressure_mpa"]
        
        # Check thermal stability deviation
        max_temp_deviation = max(abs(t - tgt) for t, tgt in zip(temps, self.target_temperatures))
        
        # Harmonic anomaly flags
        status = "NOMINAL"
        action_required = False
        recommendations = []

        if max_temp_deviation > 5.0:
            status = "THERMAL_DRIFT_WARNING"
            recommendations.append("Inspect barrel heater bands and solid-state relays (SSRs).")
            self.anomaly_count += 1

        if torque > 350.0 or pressure > 28.0:
            status = "HIGH_VISCOSITY_OR_CLOG_DETECTED"
            action_required = True
            recommendations.append("Reduce screw RPM by 10% to prevent gearbox shear overload.")
            recommendations.append("Verify polymer feedstock moisture content and uniform melt flow.")
            self.anomaly_count += 1

        assessment = {
            "extruder_id": self.extruder_id,
            "status": status,
            "max_temp_deviation_c": round(max_temp_deviation, 2),
            "screw_torque_nm": round(torque, 2),
            "melt_pressure_mpa": round(pressure, 2),
            "action_required": action_required,
            "recommendations": recommendations,
            "cumulative_anomalies": self.anomaly_count
        }
        
        if action_required:
            logger.warning(f"[{self.extruder_id}] Harmonic Alert: {status} | Torque: {torque:.1f}Nm")
        else:
            logger.info(f"[{self.extruder_id}] Telemetry Normal. Max Temp Dev: {max_temp_deviation:.2f}C")
            
        return assessment

if __name__ == "__main__":
    print("Executing Plastic Extruder Sentinel Self-Test...")
    sentinel = PlasticExtruderSentinel(extruder_id="EXT-BABA-DOGO-02", num_zones=4)
    for step in range(3):
        data = sentinel.sample_telemetry()
        report = sentinel.evaluate_harmonic_correlation(data)
        print(f"Step {step+1} Report: {report}")
        time.sleep(0.2)
    print("Plastic Extruder Sentinel Self-Test Completed Successfully.")
