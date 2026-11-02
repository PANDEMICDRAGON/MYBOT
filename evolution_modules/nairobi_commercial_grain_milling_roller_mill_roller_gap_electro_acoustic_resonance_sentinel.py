"""
Nairobi Commercial Grain Milling Roller Mill Roller Gap Electro Acoustic Resonance Sentinel

Monitors real-time acoustic emission signatures and electromagnetic actuator feedback across
roller mill nip gaps in Nairobi grain processing plants, preventing uneven grinding, roller wear, and thermal degradation.
"""

import os
import time
import math
import logging
import statistics
from typing import Dict, List, Any, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("RollerGapElectroAcousticSentinel")

class RollerGapElectroAcousticSentinel:
    def __init__(self, mill_id: str, target_gap_microns: float = 150.0, tolerance_microns: float = 2.5):
        self.mill_id = mill_id
        self.target_gap_microns = target_gap_microns
        self.tolerance_microns = tolerance_microns
        self.acoustic_history: List[float] = []
        self.gap_history: List[float] = []
        self.anomaly_count = 0
        logger.info(f"Initialized Electro-Acoustic Resonance Sentinel for mill [{self.mill_id}]")

    def analyze_nip_sample(self, acoustic_db: float, measured_gap_microns: float, servo_current_ma: float) -> Dict[str, Any]:
        """
        Analyzes live acoustic emission (dB), measured nip gap, and servo actuator current.
        Detects micro-deviations, chokes, or bearing resonance.
        """
        self.acoustic_history.append(acoustic_db)
        self.gap_history.append(measured_gap_microns);
        
        if len(self.acoustic_history) > 100:
            self.acoustic_history.pop(0);
        if len(self.gap_history) > 100:
            self.gap_history.pop(0);

        gap_deviation = measured_gap_microns - self.target_gap_microns
        is_gap_out_of_bounds = abs(gap_deviation) > self.tolerance_microns
        
        mean_acoustic = statistics.mean(self.acoustic_history)
        acoustic_spike = acoustic_db > (mean_acoustic + 6.0)
        
        status = "OPTIMAL"
        corrective_action = "NONE"
        
        if is_gap_out_of_bounds and acoustic_spike:
            status = "CRITICAL_NIP_RESONANCE"
            corrective_action = "EMERGENCY_SERVO_RETRACT_AND_FEED_SLOWDOWN"
            self.anomaly_count += 1
        elif is_gap_out_of_bounds:
            status = "GAP_DRIFT_WARNING"
            corrective_action = "ADJUST_ELECTRO_HYDRAULIC_STEPPER"
        elif acoustic_spike:
            status = "UNRECOGNIZED_HARD_OBJECT_DETECTED"
            corrective_action = "TRIGGER_MAGNETIC_TRAP_FLUSH"

        telemetry = {
            "mill_id": self.mill_id,
            "timestamp": time.time(),
            "acoustic_db": acoustic_db,
            "measured_gap_microns": measured_gap_microns,
            "gap_deviation_microns": round(gap_deviation, 2),
            "servo_current_ma": servo_current_ma,
            "status": status,
            "corrective_action": corrective_action,
            "anomaly_count": self.anomaly_count
        }
        
        if status != "OPTIMAL":
            logger.warning(f"[{self.mill_id}] Sentinel Alert: {status} | Action: {corrective_action} | Deviation: {round(gap_deviation, 2)}um")
            
        return telemetry

if __name__ == "__main__":
    sentinel = RollerGapElectroAcousticSentinel(mill_id="NAI_UNGA_MILL_04")
    sample_data = [
        (72.5, 150.2, 410.0),
        (73.1, 150.1, 412.0),
        (85.4, 154.8, 480.5), # Spike / Drift
        (72.8, 150.0, 411.2)
    ]
    for ac, mg, sc in sample_data:
        res = sentinel.analyze_nip_sample(ac, mg, sc)
        print(res)
