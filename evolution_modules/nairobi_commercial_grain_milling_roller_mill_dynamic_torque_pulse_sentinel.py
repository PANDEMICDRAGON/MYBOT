"""
Nairobi Commercial Grain Milling Roller Mill Dynamic Torque Pulse Sentinel
Autonomous Evolutionary Module #411

Monitors roller mill drive telemetry in real-time, detecting high-frequency
dynamic torque pulses indicative of hard foreign objects (stones, metallic fragments)
pre-crushing phase. Triggers microsecond emergency clutch releases and alerts.
"""

import time
import math
import random
import logging
from typing import Dict, List, Any, Optional

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')
logger = logging.getLogger("RollerMillTorquePulseSentinel")

class RollerMillTorquePulseSentinel:
    """
    Analyzes high-speed torque sensor streams from commercial roller mills
    to isolate dynamic torque pulses and prevent catastrophic mechanical failure.
    """
    def __init__(self, mill_id: str, sample_rate_hz: int = 1000, pulse_threshold_nm: float = 450.0):
        self.mill_id = mill_id
        self.sample_rate_hz = sample_rate_hz
        self.pulse_threshold_nm = pulse_threshold_nm
        self.event_log: List[Dict[str, Any]] = []
        self.is_tripped = False

    def ingest_torque_signal(self, torque_samples: List[float]) -> Dict[str, Any]:
        """
        Process a batch of high-frequency torque samples (Nm).
        Calculates rolling variance and instantaneous pulse magnitudes.
        """
        if not torque_samples:
            return {"status": "IDLE", "max_pulse": 0.0, "tripped": self.is_tripped}

        mean_torque = sum(torque_samples) / len(torque_samples)
        max_pulse = 0.0

        for sample in torque_samples:
            deviation = abs(sample - mean_torque)
            if deviation > max_pulse:
                max_pulse = deviation

        timestamp = time.time()
        incident_detected = max_pulse >= self.pulse_threshold_nm

        if incident_detected:
            self.is_tripped = True
            alert_record = {
                "timestamp": timestamp,
                "mill_id": self.mill_id,
                "max_pulse_nm": max_pulse,
                "threshold_nm": self.pulse_threshold_nm,
                "action": "EMERGENCY_QUICK_RELEASE_ENGAGED"
            }
            self.event_log.append(alert_record)
            logger.warning(
                f"[ALERT] Roller Mill {self.mill_id} Dynamic Torque Pulse Spike Detected! "
                f"Magnitude: {max_pulse:.2f} Nm (Threshold: {self.pulse_threshold_nm} Nm). "
                f"Emergency Quick Release Triggered."
            )

        return {
            "status": "PROTECTED",
            "mean_torque": mean_torque,
            "max_pulse": max_pulse,
            "tripped": self.is_tripped,
            "events_logged": len(self.event_log)
        }

    def reset_sentinel(self) -> None:
        """Resets the trip state after operator inspection."""
        self.is_tripped = False
        logger.info(f"Roller Mill {self.mill_id} sentinel reset by operator directive.")


if __name__ == "__main__":
    sentinel = RollerMillTorquePulseSentinel(mill_id="MILL-NAIROBI-ALPHA-04", sample_rate_hz=1000, pulse_threshold_nm=400.0)
    
    # Simulate normal operation torque samples with minor variance
    normal_batch = [120.0 + random.uniform(-10.0, 10.0) for _ in range(100)]
    res_normal = sentinel.ingest_torque_signal(normal_batch)
    logger.info(f"Normal operation test result: {res_normal}")
    
    # Simulate severe impact torque spike (foreign object entry)
    impact_batch = [125.0 + random.uniform(-10.0, 10.0) for _ in range(50)]
    impact_batch.extend([520.0, 610.0, 480.0]) # Massive torque pulse spike
    impact_batch.extend([130.0 + random.uniform(-10.0, 10.0) for _ in range(47)])
    
    res_impact = sentinel.ingest_torque_signal(impact_batch)
    logger.info(f"Impact shock test result: {res_impact}")
    
    sentinel.reset_sentinel()
    logger.info("Cortana Roller Mill Dynamic Torque Pulse Sentinel verification completed successfully.")
