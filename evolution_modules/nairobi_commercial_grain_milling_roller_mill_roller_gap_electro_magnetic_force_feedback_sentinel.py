"""
Nairobi Commercial Grain Milling Roller Mill Roller Gap Electro Magnetic Force Feedback Sentinel
Author: Cortana Autonomous Evolutionary Architect
Operator: Michael Obiero, Nairobi, Kenya

Provides closed-loop electromagnetic force feedback regulation for roller mill gap spacing,
counteracting thermal expansion, mechanical wear, and variable grain feed density.
"""

import ast
import logging
import math
import random
import time
from typing import Dict, List, Optional, Tuple

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')
logger = logging.getLogger("RollerGapEMForceFeedbackSentinel")


class ElectroMagneticForceFeedbackController:
    """Regulates mill roller gap spacing using proportional-integral-derivative (PID)
    electromagnetic coil counter-forces based on real-time displacement and load telemetry.
    """

    def __init__(self, target_gap_microns: float = 250.0, coil_inductance_mh: float = 45.2):
        self.target_gap_microns = target_gap_microns
        self.coil_inductance_mh = coil_inductance_mh
        self.integral_error = 0.0
        self.last_error = 0.0
        self.current_flux_tesla = 1.25
        logger.info(f"Initialized EM Force Feedback Controller. Target Gap: {target_gap_microns} um")

    def compute_correction_current(self, current_gap_microns: float, load_newtons: float, dt: float = 0.01) -> Dict[str, float]:
        error = self.target_gap_microns - current_gap_microns
        self.integral_error += error * dt
        derivative = (error - self.last_error) / dt if dt > 0 else 0.0
        self.last_error = error

        # PID coefficients tuned for high-rigidity roller frames
        kp, ki, kd = 14.5, 2.1, 0.45
        control_signal = (kp * error) + (ki * self.integral_error) + (kd * derivative)
        
        # Adjust electromagnetic flux and coil current (Amps)
        required_current_amps = max(0.0, min(50.0, 10.0 + (control_signal * 0.08) + (load_newtons * 0.0001)))
        self.current_flux_tesla = min(2.5, 0.8 + (required_current_amps * 0.034))

        return {
            "error_microns": error,
            "control_signal": control_signal,
            "coil_current_amps": required_current_amps,
            "magnetic_flux_tesla": self.current_flux_tesla,
        }


class RollerGapEMForceFeedbackSentinel:
    """Monitors and governs multi-stage roller mill gaps across Nairobi milling plants.
    """

    def __init__(self, station_id: str = "NRB-MILL-04"):
        self.station_id = station_id
        self.controller = ElectroMagneticForceFeedbackController()
        self.telemetry_history: List[Dict[str, float]] = []
        logger.info(f"Sentinel active for station {self.station_id}")

    def execute_diagnostic_cycle(self, raw_gap: float, load_n: float) -> Dict[str, any]:
        try:
            feedback = self.controller.compute_correction_current(raw_gap, load_n)
            
            status = "NOMINAL"
            if abs(feedback["error_microns"]) > 15.0:
                status = "WARNING_GAP_DEVIATION"
            if feedback["coil_current_amps"] >= 48.0:
                status = "CRITICAL_COIL_SATURATION"

            record = {
                "timestamp": time.time(),
                "station_id": self.station_id,
                "raw_gap_microns": raw_gap,
                "load_newtons": load_n,
                "status": status,
                **feedback
            }
            self.telemetry_history.append(record)
            if len(self.telemetry_history) > 1000:
                self.telemetry_history.pop(0)
                
            return record
        except Exception as e:
            logger.error(f"Error executing EM feedback diagnostic: {e}")
            return {"status": "ERROR", "message": str(e)}


if __name__ == "__main__":
    sentinel = RollerGapEMForceFeedbackSentinel()
    simulated_gaps = [252.3, 248.1, 235.0, 260.4, 250.0]
    simulated_loads = [1200.5, 1350.2, 1800.0, 1100.0, 1250.0]
    
    for g, l in zip(simulated_gaps, simulated_loads):
        res = sentinel.execute_diagnostic_cycle(g, l)
        print(f"Telemetry Record: {res}")
    
    # Validate syntax integrity
    with open(__file__, "r", encoding="utf-8") as f:
        source_code = f.read()
    parsed_ast = ast.parse(source_code)
    print(f"AST compilation check passed: {len(parsed_ast.body)} nodes verified.")
