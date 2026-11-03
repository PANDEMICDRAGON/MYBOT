"""Nairobi Commercial Grain Milling Roller Gap Micrometer Synapse Harmonic Pulse Correlation Vibration Audit Synchronizer V22."""

import time
import math
import random
import logging
from typing import Dict, List, Any

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')
logger = logging.getLogger("RollerGapSynapseV22")


class RollerGapVibrationSynchronizerV22:
    """Synchronizes roller gap micrometer readings with vibration harmonic pulses for industrial grain mills."""

    def __init__(self, mill_id: str = "NBI-MILL-01") -> None:
        self.mill_id = mill_id
        self.active_rollers = [f"ROLLER_BANK_{i}" for i in range(1, 7)]
        self.audit_log: List[Dict[str, Any]] = []

    def measure_gap_micrometer(self, roller: str) -> float:
        """Simulate precision micrometer gap measurement in micrometers."""
        base_gap = 150.0  # standard setting for fine flour
        jitter = random.gauss(0.0, 1.2)
        return round(base_gap + jitter, 3)

    def sample_vibration_harmonic(self, roller: str) -> Dict[str, float]:
        """Sample tri-axial vibration harmonics and pulse correlation."""
        frequency = round(50.0 + random.uniform(-0.5, 0.5), 2)
        amplitude = round(0.45 + random.uniform(-0.05, 0.05), 3)
        phase_angle = round(random.uniform(0.0, 360.0), 2)
        return {
            "frequency_hz": frequency,
            "amplitude_g": amplitude,
            "phase_deg": phase_angle
        }

    def execute_audit_cycle(self) -> Dict[str, Any]:
        """Execute a synchronized audit across all active roller banks."""
        cycle_timestamp = time.time()
        sync_results = {}
        anomaly_detected = False

        for roller in self.active_rollers:
            gap = self.measure_gap_micrometer(roller)
            vib = self.sample_vibration_harmonic(roller)
            
            # Harmonic correlation index
            correlation_score = round(math.cos(math.radians(vib["phase_deg"])) * (1.0 / (vib["amplitude_g"] + 0.1)), 4)
            
            if vib["amplitude_g"] > 0.48 or abs(gap - 150.0) > 3.0:
                anomaly_detected = True

            sync_results[roller] = {
                "gap_microns": gap,
                "vibration": vib,
                "harmonic_correlation_score": correlation_score,
                "status": "WARNING" if anomaly_detected else "OPTIMAL"
            }

        audit_record = {
            "timestamp": cycle_timestamp,
            "mill_id": self.mill_id,
            "metrics": sync_results,
            "system_status": "REQUIRES_CALIBRATION" if anomaly_detected else "SYNCHRONIZED"
        }
        
        self.audit_log.append(audit_record)
        logger.info(f"Audit completed for {self.mill_id}. Status: {audit_record['system_status']}")
        return audit_record


if __name__ == "__main__":
    logger.info("Initializing Roller Gap Synapse V22 Test Harness...")
    synchronizer = RollerGapVibrationSynchronizerV22("NBI-CENTRAL-GRAIN-04")
    report = synchronizer.execute_audit_cycle()
    print(report)
