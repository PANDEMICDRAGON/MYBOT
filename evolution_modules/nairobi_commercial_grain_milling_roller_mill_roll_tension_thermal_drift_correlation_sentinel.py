import logging
import math
import statistics
import time
from typing import Dict, List, Optional, Tuple

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')
logger = logging.getLogger('RollerMillThermalDriftSentinel')

class RollerMillThermalDriftSentinel:
    """
    Monitors and correlates thermal drift on commercial roller mill roll assemblies
    against mechanical tension telemetry, compensating for thermal expansion in real-time.
    """
    def __init__(self, mill_id: str, thermal_expansion_coefficient: float = 0.000011,
                 nominal_gap_microns: float = 250.0, baseline_temp_celsius: float = 25.0):
        self.mill_id = mill_id
        self.alpha = thermal_expansion_coefficient
        self.nominal_gap = nominal_gap_microns
        self.baseline_temp = baseline_temp_celsius
        self.telemetry_history: List[Dict[str, float]] = []
        logger.info(f"Initialized RollerMillThermalDriftSentinel for mill [{self.mill_id}]")

    def record_telemetry(self, bearing_temp_c: float, current_tension_kn: float,
                         measured_gap_microns: float) -> Dict[str, float]:
        """
        Records sensor telemetry and calculates required thermal compensation.
        """
        timestamp = time.time()
        temp_delta = bearing_temp_c - self.baseline_temp
        
        # Theoretical thermal expansion adjustment (assuming 1000mm roll length base)
        estimated_expansion = self.nominal_gap * self.alpha * temp_delta * 1000.0
        corrected_target_gap = self.nominal_gap - estimated_expansion
        
        gap_error = measured_gap_microns - corrected_target_gap
        
        record = {
            "timestamp": timestamp,
            "bearing_temp": bearing_temp_c,
            "tension_kn": current_tension_kn,
            "measured_gap": measured_gap_microns,
            "corrected_target_gap": corrected_target_gap,
            "gap_error": gap_error
        }
        self.telemetry_history.append(record)
        if len(self.telemetry_history) > 1000:
            self.telemetry_history.pop(0)
            
        return record

    def compute_correlation_metrics(self) -> Dict[str, float]:
        """
        Computes statistical correlation between thermal drift and gap deviation.
        """
        if len(self.telemetry_history) < 5:
            return {"status": "insufficient_data"}
            
        temps = [r["bearing_temp"] for r in self.telemetry_history]
        errors = [r["gap_error"] for r in self.telemetry_history]
        tensions = [r["tension_kn"] for r in self.telemetry_history]
        
        return {
            "mean_temp": statistics.mean(temps),
            "temp_stdev": statistics.stdev(temps) if len(temps) > 1 else 0.0,
            "mean_gap_error": statistics.mean(errors),
            "max_gap_error": max(errors),
            "mean_tension": statistics.mean(tensions),
            "samples": len(self.telemetry_history)
        }

    def generate_actuator_adjustment_signal(self) -> float:
        """
        Generates micro-adjustment step for hydraulic tension/gap actuator.
        """
        if not self.telemetry_history:
            return 0.0
        latest = self.telemetry_history[-1]
        # Proportional feedback correction
        adjustment_micron = -0.15 * latest["gap_error"]
        return round(adjustment_micron, 3)

if __name__ == "__main__":
    sentinel = RollerMillThermalDriftSentinel(mill_id="NAI_UGALI_MILL_04")
    # Simulate warming cycle
    for i in range(10):
        temp = 25.0 + (i * 1.5)
        tension = 45.0 - (i * 0.2)
        gap = 250.0 + (i * 0.8)
        res = sentinel.record_telemetry(temp, tension, gap)
        logger.info(f"Simulation step {i}: Temp={temp}C, GapError={res['gap_error']:.2f}um, Adj={sentinel.generate_actuator_adjustment_signal()}um")
        
    metrics = sentinel.compute_correlation_metrics()
    logger.info(f"Audit Metrics Summary: {metrics}")
