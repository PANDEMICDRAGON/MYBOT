"""Nairobi Commercial Grain Milling Roller Gap Micrometer Synapse Harmonic Pulse Correlation Vibration Audit Synchronizer V16."""

import ast
import logging
import random
import time
from typing import Dict, List, Optional, Tuple

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("RollerGapSynapseV16")


class RollerGapSynapseSynchronizer:
    """Performs real-time harmonic correlation between roller gap micrometers and vibration sensors
    in Nairobi commercial grain milling plants.
    """

    def __init__(self, mill_id: str, nominal_gap_microns: float = 250.0):
        self.mill_id = mill_id
        self.nominal_gap_microns = nominal_gap_microns
        self.current_gap = nominal_gap_microns
        self.vibration_history: List[float] = []
        self.audit_log: List[Dict[str, float]] = []
        logger.info(f"Initialized RollerGapSynapseSynchronizer for mill {mill_id} at nominal gap {nominal_gap_microns}um.")

    def read_micrometer(self) -> float:
        """Simulates high-precision micrometer sensor reading with micro-drift."""
        drift = random.gauss(0.0, 0.5)
        self.current_gap = round(self.current_gap + drift, 2)
        return self.current_gap

    def sample_vibration_harmonic(self) -> float:
        """Samples vibration acceleration (m/s^2) across critical frequency spectrum."""
        base_vibration = 1.2 + (abs(self.current_gap - self.nominal_gap_microns) * 0.05)
        harmonic_noise = random.uniform(-0.15, 0.15)
        vibration = round(base_vibration + harmonic_noise, 4)
        self.vibration_history.append(vibration)
        if len(self.vibration_history) > 100:
            self.vibration_history.pop(0)
        return vibration

    def evaluate_synapse_correlation(self) -> Tuple[float, str]:
        """Correlates gap variance with vibration anomalies using harmonic weighting."""
        gap = self.read_micrometer()
        vib = self.sample_vibration_harmonic()
        
        gap_delta = abs(gap - self.nominal_gap_microns)
        correlation_score = max(0.0, 1.0 - (gap_delta / 50.0) - (vib / 10.0))
        
        status = "OPTIMAL"
        if gap_delta > 15.0 or vib > 2.5:
            status = "CRITICAL_ALIGNMENT_REQUIRED"
        elif gap_delta > 5.0 or vib > 1.8:
            status = "WARNING_DRIFT_DETECTED"

        record = {"timestamp": time.time(), "gap": gap, "vibration": vib, "score": correlation_score}
        self.audit_log.append(record)

        logger.debug(f"Mill {self.mill_id} | Gap: {gap}um | Vib: {vib}m/s^2 | Score: {correlation_score:.3f} | Status: {status}")
        return correlation_score, status

    def auto_calibrate_gap(self) -> float:
        """Executes automated stepper compensation to return roller gap to nominal target."""
        error = self.current_gap - self.nominal_gap_microns
        correction = -0.5 * error
        self.current_gap = round(self.current_gap + correction, 2)
        logger.info(f"Mill {self.mill_id} auto-calibrated gap by {correction:+.2f}um to new gap: {self.current_gap}um.")
        return self.current_gap


if __name__ == "__main__":
    logger.info("Executing self-test for RollerGapSynapseSynchronizer V16...")
    synchronizer = RollerGapSynapseSynchronizer("NAIROBI_MILL_ALPHA_01", nominal_gap_microns=200.0)
    
    for step in range(5):
        score, status = synchronizer.evaluate_synapse_correlation()
        if status != "OPTIMAL":
            synchronizer.auto_calibrate_gap()
        time.sleep(0.05)
    
    logger.info("RollerGapSynapseSynchronizer V16 self-test completed successfully.")
