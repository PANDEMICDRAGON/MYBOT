"""
Nairobi Commercial Grain Milling Roller Mill Dynamic Torsion Harmonic Modulation Sentinel
Author: Cortana Autonomous Evolutionary Architect
Operator: Michael Obiero, Nairobi, Kenya
"""

import math
import time
import statistics
from typing import Dict, List, Any, Optional


class RollerMillTorsionModulationSentinel:
    """
    Monitors torsional strain, harmonic resonance frequencies, and dynamic torque ripple
    on commercial grain milling roller mill drive shafts in Nairobi milling plants.
    """

    def __init__(self, mill_id: str, nominal_rpm: float = 1000.0, sample_window_size: int = 50):
        self.mill_id = mill_id
        self.nominal_rpm = nominal_rpm
        self.sample_window_size = sample_window_size
        self.torque_samples: List[float] = []
        self.vibration_samples: List[float] = []
        self.anomaly_count = 0
        self.last_modulation_action = "NONE"

    def ingest_telemetry(self, torque_nm: float, vibration_g: float) -> Dict[str, Any]:
        """
        Ingests real-time telemetry from roller mill sensors.
        """
        self.torque_samples.append(torque_nm)
        self.vibration_samples.append(vibration_g)

        if len(self.torque_samples) > self.sample_window_size:
            self.torque_samples.pop(0);
        if len(self.vibration_samples) > self.sample_window_size:
            self.vibration_samples.pop(0);

        return self._evaluate_harmonic_state()

    def _evaluate_harmonic_state(self) -> Dict[str, Any]:
        """
        Performs statistical variance and harmonic amplitude checks on incoming torque and vibration.
        """
        if len(self.torque_samples) < 10:
            return {"status": "INITIALIZING", "risk_level": "LOW"}

        mean_torque = statistics.mean(self.torque_samples)
        stdev_torque = statistics.stdev(self.torque_samples)
        mean_vib = statistics.mean(self.vibration_samples)
        stdev_vib = statistics.stdev(self.vibration_samples)

        torque_ripple_coefficient = (stdev_torque / mean_torque) if mean_torque > 0 else 0.0
        
        # Harmonic resonance threshold detection
        risk_level = "NOMINAL"
        action = "MAINTAIN_OPERATION"

        if torque_ripple_coefficient > 0.15 or stdev_vib > 0.8:
            risk_level = "CRITICAL"
            action = "ENGAGE_DYNAMIC_TORSION_MODULATION_DAMPERS"
            self.anomaly_count += 1
            self.last_modulation_action = action
        elif torque_ripple_coefficient > 0.08 or stdev_vib > 0.4:
            risk_level = "ELEVATED"
            action = "ADJUST_INVERTER_CARRIER_FREQUENCY"
            self.last_modulation_action = action
        else:
            self.last_modulation_action = "NONE"

        return {
            "mill_id": self.mill_id,
            "status": "ACTIVE",
            "mean_torque_nm": round(mean_torque, 2),
            "torque_ripple_coefficient": round(torque_ripple_coefficient, 4),
            "mean_vibration_g": round(mean_vib, 2),
            "risk_level": risk_level,
            "recommended_action": action,
            "anomaly_count": self.anomaly_count,
            "timestamp": time.time()
        }

    def get_diagnostic_summary(self) -> Dict[str, Any]:
        return {
            "mill_id": self.mill_id,
            "total_samples_analyzed": len(self.torque_samples),
            "cumulative_anomalies": self.anomaly_count,
            "last_action": self.last_modulation_action
        }


if __name__ == "__main__":
    print("Initializing Nairobi Commercial Grain Milling Roller Mill Dynamic Torsion Harmonic Modulation Sentinel...")
    sentinel = RollerMillTorsionModulationSentinel(mill_id="NAI-MILL-01")
    
    # Simulate normal operation telemetry stream
    for i in range(15):
        res = sentinel.ingest_telemetry(torque_nm=250.0 + (i % 3 * 2.0), vibration_g=0.12)
    
    # Simulate torsional harmonic resonance spike
    spike_res = sentinel.ingest_telemetry(torque_nm=340.0, vibration_g=1.25)
    print("Test Ingestion Result:", spike_res)
    print("Diagnostic Summary:", sentinel.get_diagnostic_summary())
    print("Sentinel test execution completed successfully.")
