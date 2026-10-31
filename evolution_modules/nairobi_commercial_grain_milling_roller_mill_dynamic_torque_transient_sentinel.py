"""Nairobi Commercial Grain Milling Roller Mill Dynamic Torque Transient Sentinel module.

Monitors roller mill drive shaft torque transients, high-frequency torsional oscillations,
and load spikes to prevent gear box shear and belt failure in Nairobi industrial flour mills.
"""

import ast
import logging
import random
import time
from typing import Dict, List, Optional, Any

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("TorqueTransientSentinel")


class RollerMillTorqueTransientSentinel:
    """Analyzes high-frequency torque transients on commercial roller mill shafts."""

    def __init__(self, mill_id: str, transient_threshold_nm: float = 1250.0, max_oscillation_hz: float = 45.0):
        self.mill_id = mill_id
        self.transient_threshold_nm = transient_threshold_nm
        self.max_oscillation_hz = max_oscillation_hz
        self.telemetry_history: List[Dict[str, Any]] = []
        self.alarm_state = False

    def ingest_telemetry(self, torque_nm: float, oscillation_hz: float, bearing_temp_c: float) -> Dict[str, Any]:
        """Ingests a telemetry sample and evaluates dynamic torque transient risk."""
        timestamp = time.time()
        transient_detected = torque_nm > self.transient_threshold_nm or oscillation_hz > self.max_oscillation_hz
        
        record = {
            "timestamp": timestamp,
            "mill_id": self.mill_id,
            "torque_nm": torque_nm,
            "oscillation_hz": oscillation_hz,
            "bearing_temp_c": bearing_temp_c,
            "transient_detected": transient_detected
        }
        
        self.telemetry_history.append(record)
        if len(self.telemetry_history) > 1000:
            self.telemetry_history.pop(0)

        if transient_detected:
            self.alarm_state = True
            logger.warning(
                f"[ALERT] Roller Mill {self.mill_id} transient spike! Torque: {torque_nm} Nm "
                f"(Threshold: {self.transient_threshold_nm}), Oscillation: {oscillation_hz} Hz"
            )
        else:
            self.alarm_state = False

        return record

    def get_status(self) -> Dict[str, Any]:
        """Returns the current health and anomaly state of the roller mill sentinel."""
        recent_samples = self.telemetry_history[-10:] if self.telemetry_history else []
        avg_torque = sum(s["torque_nm"] for s in recent_samples) / len(recent_samples) if recent_samples else 0.0
        
        return {
            "mill_id": self.mill_id,
            "alarm_state": self.alarm_state,
            "sample_count": len(self.telemetry_history),
            "recent_average_torque_nm": round(avg_torque, 2)
        }


if __name__ == "__main__":
    sentinel = RollerMillTorqueTransientSentinel(mill_id="NAI-MILL-04")
    print(f"Initializing {sentinel.mill_id} Torque Transient Sentinel...")
    
    for i in range(5):
        sim_torque = random.uniform(900.0, 1350.0)
        sim_hz = random.uniform(10.0, 50.0)
        sim_temp = random.uniform(60.0, 85.0)
        result = sentinel.ingest_telemetry(sim_torque, sim_hz, sim_temp)
        print(f"Iteration {i+1}: {result}")
    
    print("Final Sentinel Status:", sentinel.get_status())
    
    # Validate syntax self-integrity
    code_string = open(__file__, "r", encoding="utf-8").read()
    parsed_tree = ast.parse(code_string)
    print(f"AST compilation check passed successfully: {len(parsed_tree.body)} nodes parsed.")
