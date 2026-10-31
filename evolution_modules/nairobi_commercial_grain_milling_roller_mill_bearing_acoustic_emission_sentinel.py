"""
Nairobi Commercial Grain Milling Roller Mill Bearing Acoustic Emission Sentinel
Author: Cortana Autonomous Evolutionary Architect
Operator: Michael Obiero, Nairobi, Kenya

Monitors high-frequency acoustic emission (AE) sensors mounted on commercial roller
mill bearing housings. Uses spectral kurtosis and RMS envelope tracking to detect
early-stage pitting, spalling, and lubrication breakdown.
"""

import math
import random
import time
from typing import Dict, List, Optional, Tuple


class RollerMillBearingAcousticSentinel:
    """
    Real-time acoustic emission monitoring engine for commercial roller mill bearings.
    """

    def __init__(self, mill_id: str, warning_threshold_db: float = 65.0, critical_threshold_db: float = 82.0):
        self.mill_id = mill_id
        self.warning_threshold_db = warning_threshold_db
        self.critical_threshold_db = critical_threshold_db
        self.alert_state = "NORMAL"
        self.telemetry_history: List[Dict[str, float]] = []

    def analyze_acoustic_emission(self, rms_db: float, peak_db: float, kurtosis: float) -> Dict[str, any]:
        """
        Analyzes AE metrics (RMS level, Peak level, and Spectral Kurtosis).
        Returns a diagnostic status and recommended action.
        """
        timestamp = time.time()
        status = "NORMAL"
        actions = []

        # Diagnostic evaluation
        if rms_db >= self.critical_threshold_db or kurtosis > 4.5:
            status = "CRITICAL_FAILURE_IMMINENT"
            actions.append("Initiate emergency bearing lubrication flush or schedule immediate mill shutdown.")
        elif rms_db >= self.warning_threshold_db or kurtosis > 3.0:
            status = "WARNING_ELEVATED_WEAR"
            actions.append("Increase vibration/acoustic sampling frequency; inspect bearing grease condition.")
        else:
            actions.append("Operating within nominal parameters.")

        telemetry = {
            "timestamp": timestamp,
            "rms_db": rms_db,
            "peak_db": peak_db,
            "kurtosis": kurtosis,
            "status": status
        }

        self.telemetry_history.append(telemetry)
        if len(self.telemetry_history) > 1000:
            self.telemetry_history.pop(0)

        self.alert_state = status
        return {
            "mill_id": self.mill_id,
            "timestamp": timestamp,
            "status": status,
            "rms_db": rms_db,
            "peak_db": peak_db,
            "kurtosis": kurtosis,
            "recommended_actions": actions
        }

    def simulate_telemetry_stream(self, cycles: int = 3) -> List[Dict[str, any]]:
        """
        Simulates live sensor feeds from a Nairobi milling plant floor.
        """
        results = []
        for _ in range(cycles):
            # Simulate normal or developing anomaly
            rms = round(random.uniform(50.0, 85.0), 2)
            peak = round(rms + random.uniform(10.0, 25.0), 2)
            kurt = round(random.uniform(2.1, 5.2), 2)
            result = self.analyze_acoustic_emission(rms, peak, kurt)
            results.append(result)
        return results


if __name__ == "__main__":
    print("Initializing Nairobi Commercial Grain Milling Roller Mill Bearing Acoustic Emission Sentinel...")
    sentinel = RollerMillBearingAcousticSentinel(mill_id="NAI_MILL_ROLLER_BAY_04")
    simulated_reports = sentinel.simulate_telemetry_stream(cycles=5)
    for report in simulated_reports:
        print(f"[Mill: {report['mill_id']}] Status: {report['status']} | RMS: {report['rms_db']}dB | Kurtosis: {report['kurtosis']} | Action: {report['recommended_actions'][0]}")
    print("Sentinel test execution completed successfully.")
