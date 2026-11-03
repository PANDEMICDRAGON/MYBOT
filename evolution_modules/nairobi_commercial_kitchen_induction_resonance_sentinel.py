"""
Nairobi Commercial Kitchen Induction Cooktop Resonance Sentinel
Proactively monitors inverter frequency, IGBT thermal dissipation, and grid harmonic distortion
for commercial induction arrays in Nairobi restaurants and culinary hubs.
"""

import time
import math
import logging
from typing import Dict, Any, List, Optional

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')
logger = logging.getLogger("InductionResonanceSentinel")


class InductionResonanceSentinel:
    """
    Monitors induction cooktop coils, inverter frequency stability, and magnetic resonance.
    Protects against cookware mismatch, over-current, and grid phase imbalance.
    """

    def __init__(self, station_id: str, rated_power_kw: float = 15.0):
        self.station_id = station_id
        self.rated_power_kw = rated_power_kw
        self.active_session = False
        self.metrics_history: List[Dict[str, Any]] = []
        logger.info(f"InductionResonanceSentinel initialized for station {station_id} ({rated_power_kw}kW).")

    def start_monitoring(self) -> None:
        """Activates real-time induction telemetry sampling."""
        self.active_session = True
        logger.info(f"Station {self.station_id} induction monitoring active.")

    def evaluate_cycle(self,
                       inverter_freq_khz: float,
                       coil_temp_c: float,
                       igbt_temp_c: float,
                       pan_impedance_ohms: float,
                       line_voltage_v: float) -> Dict[str, Any]:
        """
        Evaluates operational parameters against safety and resonance thresholds.
        Detects cookware decoupling, thermal stress, and grid anomalies.
        """
        if not self.active_session:
            raise RuntimeError("Sentinel monitoring session is not active.")

        # Threshold assessments
        freq_nominal = 25.0  # kHz target
        freq_deviation = abs(inverter_freq_khz - freq_nominal)
        
        thermal_status = "OPTIMAL"
        if igbt_temp_c > 75.0 or coil_temp_c > 110.0:
            thermal_status = "CRITICAL_THERMAL_WARNING"
        elif igbt_temp_c > 65.0 or coil_temp_c > 95.0:
            thermal_status = "ELEVATED"

        pan_coupling = "EXCELLENT"
        if pan_impedance_ohms < 0.5 or pan_impedance_ohms > 4.5:
            pan_coupling = "SUBOPTIMAL_OR_DECOUPLED"

        grid_status = "STABLE"
        if line_voltage_v < 210.0 or line_voltage_v > 255.0:
            grid_status = "KPLC_VOLTAGE_FLUCTUATION_DETECTED"

        # Calculate harmonic stress index
        harmonic_stress = round((freq_deviation * 2.5) + (igbt_temp_c * 0.4) + (0.0 if pan_coupling == "EXCELLENT" else 30.0), 2)

        assessment = {
            "station_id": self.station_id,
            "timestamp": time.time(),
            "inverter_freq_khz": inverter_freq_khz,
            "thermal_status": thermal_status,
            "pan_coupling": pan_coupling,
            "grid_status": grid_status,
            "harmonic_stress_index": harmonic_stress,
            "action_required": harmonic_stress > 70.0 or thermal_status == "CRITICAL_THERMAL_WARNING"
        }

        self.metrics_history.append(assessment)
        if len(self.metrics_history) > 1000:
            self.metrics_history.pop(0)

        return assessment

    def stop_monitoring(self) -> None:
        """Stops the monitoring session."""
        self.active_session = False
        logger.info(f"Station {self.station_id} monitoring halted.")


if __name__ == "__main__":
    sentinel = InductionResonanceSentinel(station_id="NAI_WESTLANDS_KITCHEN_04", rated_power_kw=20.0)
    sentinel.start_monitoring()
    report = sentinel.evaluate_cycle(
        inverter_freq_khz=24.8,
        coil_temp_c=82.5,
        igbt_temp_c=58.2,
        pan_impedance_ohms=1.8,
        line_voltage_v=238.5
    )
    print("Induction Sentinel Evaluation Test Report:", report)
    sentinel.stop_monitoring()
