"""
Nairobi Commercial Grain Silo Fumigation & Phosphine Concentration Sentinel
Author: Cortana Autonomous Evolutionary Architect
Operator: Michael Obiero, Nairobi, Kenya
"""

import time
import logging
from typing import Dict, Any, List, Optional

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] (FumigationSentinel): %(message)s')
logger = logging.getLogger("FumigationSentinel")

class GrainSiloFumigationSentinel:
    """
    Monitors phosphine (PH3) gas concentration, sealing integrity, exposure duration,
    and clearance air quality in commercial grain silos across Nairobi storage facilities.
    """
    
    PH3_SAFETY_THRESHOLD_PPM = 0.3  # OSHA/NIOSH standard max 8-hour exposure limit
    PH3_FUMIGATION_TARGET_PPM = 300.0  # Effective lethal concentration for insect pests
    CO2_TARGET_PERCENT = 40.0  # Controlled atmosphere alternative/supplement

    def __init__(self, silo_id: str, capacity_metric_tons: float):
        self.silo_id = silo_id
        self.capacity_metric_tons = capacity_metric_tons
        self.current_phase = "IDLE"
        self.phosphine_ppm = 0.0
        self.co2_percent = 0.0
        self.sealing_pressure_pa = 0.0
        self.exposure_hours_elapsed = 0.0
        self.audit_log: List[Dict[str, Any]] = []

    def initialize_fumigation(self, initial_phosphine_ppm: float, co2_level: float) -> Dict[str, Any]:
        """Initiates a controlled fumigation cycle and records baseline parameters."""
        self.phosphine_ppm = initial_phosphine_ppm
        self.co2_percent = co2_level
        self.exposure_hours_elapsed = 0.0
        self.current_phase = "ACTIVE_FUMIGATION"
        
        status = {
            "silo_id": self.silo_id,
            "phase": self.current_phase,
            "phosphine_ppm": self.phosphine_ppm,
            "co2_percent": self.co2_percent,
            "timestamp": time.time()
        }
        self.audit_log.append(status)
        logger.info(f"Fumigation initiated for Silo {self.silo_id}. Target PH3: {initial_phosphine_ppm} ppm.")
        return status

    def evaluate_cycle(self, pressure_differential_pa: float, hours_passed: float) -> Dict[str, Any]:
        """
        Evaluates sealing integrity and phosphine concentration degradation over time.
        """
        self.sealing_pressure_pa = pressure_differential_pa
        self.exposure_hours_elapsed += hours_passed
        
        # Natural degradation rate simulation (leakage & absorption)
        decay_factor = 0.98 ** hours_passed
        self.phosphine_ppm *= decay_factor

        leakage_detected = pressure_differential_pa < 50.0  # Minimum positive pressure required
        
        recommendation = "MAINTAIN_SEAL"
        if leakage_detected:
            recommendation = "WARNING_SEAL_BREACH_DETECTED"
            logger.warning(f"Silo {self.silo_id} pressure differential low ({pressure_differential_pa} Pa). Check seals.")

        evaluation = {
            "silo_id": self.silo_id,
            "phase": self.current_phase,
            "current_phosphine_ppm": round(self.phosphine_ppm, 2),
            "exposure_hours": round(self.exposure_hours_elapsed, 1),
            "sealing_pressure_pa": self.sealing_pressure_pa,
            "leakage_detected": leakage_detected,
            "recommendation": recommendation
        }
        self.audit_log.append(evaluation)
        return evaluation

    def trigger_aeration_clearance(self) -> Dict[str, Any]:
        """
        Transitions silo into forced aeration mode once treatment duration is complete.
        """
        self.current_phase = "AERATION_PURGE"
        # Simulate rapid gas evacuation
        self.phosphine_ppm = max(0.0, self.phosphine_ppm - 295.0)
        
        safe_for_entry = self.phosphine_ppm <= self.PH3_SAFETY_THRESHOLD_PPM
        
        result = {
            "silo_id": self.silo_id,
            "phase": self.current_phase,
            "phosphine_ppm": round(self.phosphine_ppm, 3),
            "safe_for_worker_entry": safe_for_entry,
            "timestamp": time.time()
        }
        self.audit_log.append(result)
        logger.info(f"Silo {self.silo_id} entered aeration phase. PH3 residual: {self.phosphine_ppm} ppm. Safe: {safe_for_entry}")
        return result

if __name__ == "__main__":
    print("--- Executing Nairobi Commercial Grain Silo Fumigation Sentinel Test Harness ---")
    sentinel = GrainSiloFumigationSentinel(silo_id="NAI-SILO-09", capacity_metric_tons=5000.0)
    
    init_res = sentinel.initialize_fumigation(initial_phosphine_ppm=320.0, co2_level=35.0)
    print("Initialization:", init_res)
    
    eval_res = sentinel.evaluate_cycle(pressure_differential_pa=65.0, hours_passed=24.0)
    print("Cycle Evaluation:", eval_res)
    
    purge_res = sentinel.trigger_aeration_clearance()
    print("Aeration Clearance:", purge_res)
    print("--- Sentinel Test Completed Successfully ---")
