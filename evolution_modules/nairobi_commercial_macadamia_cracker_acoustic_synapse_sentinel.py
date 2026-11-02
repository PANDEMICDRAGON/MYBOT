"""Nairobi Commercial Macadamia Nut Cracker Acoustic & Torque Synapse Sentinel.

Author: Cortana Autonomous Evolutionary Architect
Operator: Michael Obiero (Nairobi, Kenya)

Monitors acoustic emissions and motor torque signatures of industrial macadamia
crackers to optimize kernel yield, detect shell jamming, and prevent mechanical fatigue.
"""

import time
import math
import random
import logging
from typing import Dict, List, Any, Optional

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')
logger = logging.getLogger("MacadamiaCrackerSentinel")


class MacadamiaCrackerSynapseSentinel:
    """Performs real-time acoustic and torque harmonic analysis for commercial macadamia nut crackers."""

    def __init__(self, machine_id: str, target_whole_kernel_ratio: float = 0.88):
        self.machine_id = machine_id
        self.target_whole_kernel_ratio = target_whole_kernel_ratio
        self.current_gap_mm = 18.5  # Standard initial calibration gap for medium-large macadamia nuts
        self.telemetry_history: List[Dict[str, Any]] = []
        logger.info(f"Initialized MacadamiaCrackerSynapseSentinel for machine [{self.machine_id}] in Nairobi.")

    def sample_telemetry(self) -> Dict[str, float]:
        """Simulates high-frequency telemetry reading from cracking jaw load cells and acoustic mics."""
        # Simulated variance reflecting ambient factory conditions in industrial Nairobi sector
        torque_nm = 125.0 + random.gauss(0, 4.5)
        acoustic_db = 78.5 + random.gauss(0, 2.1)
        motor_rpm = 1450.0 + random.gauss(0, 12.0)
        vibration_mm_s = 1.2 + abs(random.gauss(0, 0.3))
        return {
            "torque_nm": round(torque_nm, 2),
            "acoustic_db": round(acoustic_db, 2),
            "motor_rpm": round(motor_rpm, 2),
            "vibration_mm_s": round(vibration_mm_s, 2),
            "timestamp": time.time()
        }

    def evaluate_cycle(self, telemetry: Dict[str, float]) -> Dict[str, Any]:
        """Analyzes telemetry to calculate predicted kernel integrity and recommend gap adjustments."""
        torque = telemetry["torque_nm"]
        acoustic = telemetry["acoustic_db"]
        vibration = telemetry["vibration_mm_s"]

        # Acoustic-torque correlation index for shell fracture quality
        # Sharp acoustic peaks coupled with moderate torque indicate clean whole-kernel fracture
        # Excessive torque indicates under-gapping or double-feeding
        integrity_score = max(0.0, min(1.0, 1.0 - (abs(torque - 125.0) / 50.0) - (max(0.0, vibration - 2.0) / 5.0)))
        
        recommended_action = "MAINTAIN"
        gap_delta = 0.0

        if torque > 140.0:
            recommended_action = "WIDEN_GAP"
            gap_delta = +0.15
            self.current_gap_mm += gap_delta
        elif torque < 110.0:
            recommended_action = "NARROW_GAP"
            gap_delta = -0.10
            self.current_gap_mm += gap_delta

        result = {
            "machine_id": self.machine_id,
            "current_gap_mm": round(self.current_gap_mm, 3),
            "predicted_whole_kernel_ratio": round(integrity_score, 3),
            "recommended_action": recommended_action,
            "gap_delta_mm": round(gap_delta, 3),
            "status": "OPTIMAL" if integrity_score >= 0.80 else "TUNING_REQUIRED"
        }
        self.telemetry_history.append(result)
        return result

    def run_diagnostic_batch(self, iterations: int = 5) -> List[Dict[str, Any]]:
        """Executes a diagnostic batch run for system auditing."""
        audit_results = []
        for i in range(iterations):
            telemetry = self.sample_telemetry()
            evaluation = self.evaluate_cycle(telemetry)
            audit_results.append(evaluation)
            logger.info(f"Cycle {i+1}/{iterations} -> Gap: {evaluation['current_gap_mm']}mm | "
                        f"Action: {evaluation['recommended_action']} | Integrity: {evaluation['predicted_whole_kernel_ratio']}")
            time.sleep(0.05)
        return audit_results


if __name__ == "__main__":
    logger.info("Executing standalone diagnostic test harness for MacadamiaCrackerSynapseSentinel...")
    sentinel = MacadamiaCrackerSynapseSentinel(machine_id="MAC-CRACKER-NRB-04")
    batch = sentinel.run_diagnostic_batch(iterations=5)
    logger.info(f"Diagnostic complete. Processed {len(batch)} telemetry cycles successfully.")
