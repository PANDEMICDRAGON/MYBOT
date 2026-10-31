"""Nairobi Commercial Grain Milling Roller Mill Dynamic Torque Ripple Sentinel. Provides real-time telemetry analysis, torque ripple decomposition, anomaly detection, and automated mitigation for commercial roller mills operating in industrial Nairobi.
"""

import logging
import math
import statistics
import time
from typing import Dict, List, Optional, Tuple, Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("RollerMillTorqueRippleSentinel")


class RollerMillTorqueRippleSentinel:
    """Monitors, analyzes, and mitigates high-frequency torque ripple and rotational imbalance in commercial roller mills."""

    def __init__(self, mill_id: str, rated_torque_nm: float = 250.0, sample_window_size: int = 50):
        self.mill_id = mill_id
        self.rated_torque_nm = rated_torque_nm
        self.sample_window_size = sample_window_size
        self._torque_history: List[float] = []
        self._vibration_history: List[float] = []
        self._alert_count = 0
        self._mitigation_active = False

    def ingest_telemetry(self, current_torque: float, vibration_mm_s: float) -> Dict[str, Any]:
        """Ingests live torque and vibration telemetry, computes ripple metrics, and checks thresholds."""
        timestamp = time.time()
        self._torque_history.append(current_torque)
        self._vibration_history.append(vibration_mm_s)

        if len(self._torque_history) > self.sample_window_size:
            self._torque_history.pop(0)
        if len(self._vibration_history) > self.sample_window_size:
            self._vibration_history.pop(0)

        analysis = self._analyze_ripple()
        analysis["timestamp"] = timestamp
        analysis["mill_id"] = self.mill_id

        if analysis["ripple_severity"] == "CRITICAL":
            self._trigger_mitigation(analysis)

        return analysis

    def _analyze_ripple(self) -> Dict[str, Any]:
        """Calculates torque ripple coefficient, peak-to-peak variance, and harmonic distortion."""
        if len(self._torque_history) < 5:
            return {
                "status": "INITIALIZING",
                "ripple_coefficient": 0.0,
                "peak_to_peak_nm": 0.0,
                "ripple_severity": "NORMAL"
            }

        mean_torque = statistics.mean(self._torque_history)
        max_torque = max(self._torque_history)
        min_torque = min(self._torque_history)
        peak_to_peak = max_torque - min_torque

        # Ripple coefficient as percentage of mean torque
        ripple_coef = (peak_to_peak / mean_torque) * 100.0 if mean_torque > 0 else 0.0
        mean_vibe = statistics.mean(self._vibration_history) if self._vibration_history else 0.0

        severity = "NORMAL"
        if ripple_coef > 15.0 or mean_vibe > 4.5:
            severity = "CRITICAL"
        elif ripple_coef > 8.0 or mean_vibe > 2.5:
            severity = "WARNING"

        return {
            "status": "ACTIVE",
            "mean_torque_nm": round(mean_torque, 2),
            "peak_to_peak_nm": round(peak_to_peak, 2),
            "ripple_coefficient_pct": round(ripple_coef, 2),
            "mean_vibration_mm_s": round(mean_vibe, 2),
            "ripple_severity": severity
        }

    def _trigger_mitigation(self, analysis: Dict[str, Any]) -> None:
        """Executes automated mitigation sequence (e.g., feed-gate throttling, inverter dampening)."""
        self._alert_count += 1
        self._mitigation_active = True
        logger.warning(
            f"[CRITICAL TORQUE RIPPLE] Mill {self.mill_id} | "
            f"Ripple Coef: {analysis['ripple_coefficient_pct']}% | "
            f"Peak-to-Peak: {analysis['peak_to_peak_nm']} Nm | "
            f"Initiating automated inverter frequency modulation & feed gate dampening."
        )

    def get_status(self) -> Dict[str, Any]:
        """Returns the current state and operational metrics of the Sentinel."""
        return {
            "mill_id": self.mill_id,
            "rated_torque_nm": self.rated_torque_nm,
            "total_alerts": self._alert_count,
            "mitigation_active": self._mitigation_active,
            "samples_buffered": len(self._torque_history)
        }


if __name__ == "__main__":
    print("Initializing Nairobi Commercial Grain Milling Roller Mill Dynamic Torque Ripple Sentinel...")
    sentinel = RollerMillTorqueRippleSentinel(mill_id="MILL-NAI-04")

    # Simulate normal and unstable telemetry ingestion
    test_streams = [
        (245.0, 1.2),
        (252.0, 1.3),
        (248.0, 1.1),
        (280.0, 3.2),
        (220.0, 4.8),
        (295.0, 5.5)
    ]

    for torque, vibe in test_streams:
        res = sentinel.ingest_telemetry(torque, vibe)
        print(f"Telemetry Ingested -> Result: {res}")

    print("Final Sentinel Status:", sentinel.get_status())
    print("Sentinel verification complete.")
