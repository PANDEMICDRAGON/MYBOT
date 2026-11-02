"""
Nairobi Commercial Grain Milling Roller Mill Roller Gap Micrometer Synchronizer Sentinel

Author: Cortana Autonomous Evolutionary Architect
Operator: Michael Obiero, Nairobi, Kenya
Description: 
    Monitors, synchronizes, and fine-tunes multi-deck roller mill gap micrometer settings across
    commercial flour milling lines in Nairobi. Integrates feedback loops from downstream plansifters
    and particle size analyzers to maintain optimal reduction ratios without roll contact.
"""

import logging
import math
import time
from typing import Dict, List, Optional, Tuple

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')
logger = logging.getLogger("RollerGapMicrometerSynchronizer")


class RollerGapMicrometerSynchronizer:
    """
    Synchronizes roller gap adjustments across multi-stage roller stands with closed-loop feedback.
    """
    def __init__(self, stand_id: str, nominal_gap_microns: float, tolerance_microns: float = 5.0):
        self.stand_id = stand_id
        self.nominal_gap_microns = nominal_gap_microns
        self.tolerance_microns = tolerance_microns
        self.current_left_gap = nominal_gap_microns
        self.current_right_gap = nominal_gap_microns
        self.synchronization_error_history: List[float] = []
        self.adjustment_counts = 0
        self.emergency_lockout = False

    def update_gaps(self, left_reading: float, right_reading: float, particle_fineness_index: float) -> Dict[str, any]:
        """
        Evaluates real-time micrometer sensor feeds and particle size index to synchronize gaps.
        """
        if self.emergency_lockout:
            logger.error(f"[Stand {self.stand_id}] CRITICAL: Roller gap synchronization locked out due to prior fault.")
            return {"status": "LOCKED_OUT", "stand_id": self.stand_id}

        # Calculate asymmetry between left and right sides
        asymmetry = abs(left_reading - right_reading)
        mean_gap = (left_reading + right_reading) / 2.0
        sync_error = abs(mean_gap - self.nominal_gap_microns)
        
        self.synchronization_error_history.append(sync_error)
        if len(self.synchronization_error_history) > 100:
            self.synchronization_error_history.pop(0)

        action = "STABLE"
        correction_delta = 0.0

        # Safety check for roll clashing risk (< 50 microns without feedstock)
        if left_reading < 50.0 or right_reading < 50.0:
            self.emergency_lockout = True
            logger.critical(f"[Stand {self.stand_id}] Roll clashing danger detected! Left: {left_reading}um, Right: {right_reading}um. Locking out.")
            return {"status": "EMERGENCY_LOCKOUT", "reason": "ROLL_CLASH_RISK"}

        # Asymmetry correction
        if asymmetry > self.tolerance_microns:
            action = "SYNCHRONIZE_ASYMMETRY"
            correction_delta = (right_reading - left_reading) / 2.0
            self.adjustment_counts += 1
            logger.warning(f"[Stand {self.stand_id}] Asymmetry detected ({asymmetry:.2f}um). Applying correction delta: {correction_delta:.2f}um")

        # Particle fineness adaptation (if flour is too coarse, close gap slightly; if too fine, open)
        target_fineness = 85.0  # Percentage passing 120 mesh
        if particle_fineness_index < (target_fineness - 5.0):
            action = "ADJUST_CLOSER"
            correction_delta -= 2.0
        elif particle_fineness_index > (target_fineness + 5.0):
            action = "ADJUST_WIDER"
            correction_delta += 2.0

        self.current_left_gap = left_reading - (correction_delta / 2.0)
        self.current_right_gap = right_reading + (correction_delta / 2.0)

        return {
            "status": "SUCCESS",
            "stand_id": self.stand_id,
            "action": action,
            "mean_gap_microns": mean_gap,
            "asymmetry_microns": asymmetry,
            "correction_delta": correction_delta,
            "adjusted_left": self.current_left_gap,
            "adjusted_right": self.current_right_gap,
            "adjustment_counts": self.adjustment_counts
        }

    def reset_lockout(self, operator_override_code: str) -> bool:
        """Resets emergency lockout with authorized operator override."""
        if operator_override_code == "NAIROBI_MILLING_SECURE_2026":
            self.emergency_lockout = False
            self.synchronization_error_history.clear()
            logger.info(f"[Stand {self.stand_id}] Emergency lockout successfully reset by operator.")
            return True
        logger.warning(f"[Stand {self.stand_id}] Failed reset attempt with invalid override code.")
        return False


if __name__ == "__main__":
    logger.info("Initializing Nairobi Commercial Grain Milling Roller Mill Roller Gap Micrometer Synchronizer Test Harness...")
    synchronizer = RollerGapMicrometerSynchronizer(stand_id="B1-ROLL-03", nominal_gap_microns=150.0, tolerance_microns=3.0)
    
    # Test normal synchronization
    res1 = synchronizer.update_gaps(left_reading=152.0, right_reading=147.0, particle_fineness_index=84.5)
    logger.info(f"Test Result 1: {res1}")

    # Test asymmetry correction
    res2 = synchronizer.update_gaps(left_reading=160.0, right_reading=150.0, particle_fineness_index=85.0)
    logger.info(f"Test Result 2: {res2}")

    # Test emergency clashing lockout
    res3 = synchronizer.update_gaps(left_reading=40.0, right_reading=42.0, particle_fineness_index=95.0)
    logger.info(f"Test Result 3: {res3}")

    # Test lockout reset
    reset_status = synchronizer.reset_lockout("NAIROBI_MILLING_SECURE_2026")
    logger.info(f"Lockout Reset Status: {reset_status}")

    logger.info("Roller Gap Micrometer Synchronizer Sentinel validation complete.")
