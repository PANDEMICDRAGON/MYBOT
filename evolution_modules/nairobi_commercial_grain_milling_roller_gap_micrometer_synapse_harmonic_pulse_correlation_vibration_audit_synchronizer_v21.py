"""
Nairobi Commercial Grain Milling Roller Gap Micrometer Synapse Harmonic Pulse
Correlation Vibration Audit Synchronizer V21

Designed for high-throughput commercial flour mills in Nairobi, Kenya.
Provides real-time micrometer gap telemetry, harmonic vibration auditing,
adaptive pulse correlation, and automated self-healing fault suppression.
"""

import os
import time
import math
import random
import logging
import threading
from typing import Dict, List, Any, Optional

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')
logger = logging.getLogger("RollerGapSynapseV21")

class RollerGapMicrometerSynapse:
    """
    Core engine for auditing roller mill gaps, vibration spectra, and
    harmonic correlation matrices.
    """
    def __init__(self, mill_id: str = "NAIROBI_MILL_01") -> None:
        self.mill_id = mill_id
        self.is_active = False
        self._lock = threading.Lock()
        self.gap_microns = 250.0  # standard baseline gap
        self.vibration_amplitude_mm_s = 1.2
        self.harmonic_frequency_hz = 50.0
        self.audit_log: List[Dict[str, Any]] = []

    def start_synchronizer(self) -> None:
        with self._lock:
            self.is_active = True
        logger.info(f"[{self.mill_id}] Roller Gap Micrometer Synapse V21 activated.")

    def stop_synchronizer(self) -> None:
        with self._lock:
            self.is_active = False
        logger.info(f"[{self.mill_id}] Roller Gap Micrometer Synapse V21 deactivated.")

    def sample_sensors(self) -> Dict[str, float]:
        """Simulates high-precision eddy current micrometer and accelerometer telemetry."""
        with self._lock:
            # Introduce slight operational drift with stochastic noise
            noise = random.gauss(0, 0.05)
            vibration_noise = random.gauss(0, 0.02)
            
            self.gap_microns += noise
            self.vibration_amplitude_mm_s = max(0.1, self.vibration_amplitude_mm_s + vibration_noise)
            
            return {
                "timestamp": time.time(),
                "gap_microns": round(self.gap_microns, 3),
                "vibration_amplitude_mm_s": round(self.vibration_amplitude_mm_s, 3),
                "harmonic_frequency_hz": self.harmonic_frequency_hz
            }

    def evaluate_harmonic_correlation(self, telemetry: Dict[str, float]) -> Dict[str, Any]:
        """Calculates harmonic pulse correlation and flags out-of-tolerance wear."""
        gap = telemetry["gap_microns"]
        vib = telemetry["vibration_amplitude_mm_s"]
        
        # Correlation index calculation
        target_gap = 250.0
        gap_deviation = abs(gap - target_gap)
        correlation_score = math.exp(-0.01 * gap_deviation) * max(0.0, (5.0 - vib) / 5.0)
        
        status = "OPTIMAL"
        adjustment_required = 0.0

        if gap_deviation > 10.0 or vib > 3.0:
            status = "WARNING_DRIFT"
            adjustment_required = target_gap - gap
        if vib > 4.5 or gap_deviation > 25.0:
            status = "CRITICAL_ANOMALY"
            adjustment_required = target_gap - gap

        audit_entry = {
            "timestamp": telemetry["timestamp"],
            "gap_microns": gap,
            "vibration_mm_s": vib,
            "correlation_score": round(correlation_score, 4),
            "status": status,
            "adjustment_required_microns": round(adjustment_required, 3)
        }

        with self._lock:
            self.audit_log.append(audit_entry)
            if len(self.audit_log) > 1000:
                self.audit_log.pop(0)

        return audit_entry

    def execute_self_healing_correction(self, audit_result: Dict[str, Any]) -> None:
        """Applies automated stepper motor adjustments to correct roller gap."""
        adj = audit_result["adjustment_required_microns"]
        if abs(adj) > 0.001:
            with self._lock:
                self.gap_microns += adj
                # dampen vibration response
                self.vibration_amplitude_mm_s = max(0.5, self.vibration_amplitude_mm_s * 0.95)
            logger.info(f"[{self.mill_id}] Self-healing executed: Adjusted gap by {adj:.3f} microns. New gap: {self.gap_microns:.3f} um.")

if __name__ == "__main__":
    logger.info("Initializing Roller Gap Synapse V21 Test Harness...")
    synapse = RollerGapMicrometerSynapse(mill_id="NAIROBI_UNGA_MILL_04")
    synapse.start_synchronizer()
    
    for cycle in range(5):
        telemetry_data = synapse.sample_sensors()
        result = synapse.evaluate_harmonic_correlation(telemetry_data)
        logger.info(f"Cycle {cycle+1} Audit: {result}")
        if result["status"] != "OPTIMAL":
            synapse.execute_self_healing_correction(result)
        time.sleep(0.1)
        
    synapse.stop_synchronizer()
    logger.info("Roller Gap Synapse V21 Test Harness Completed Successfully.")
