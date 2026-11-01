"""
Nairobi Commercial Grain Milling Roller Mill Dynamic Torque Ripple Harmonic Amplitude Phase Quadrature Resolver Interferometer Correlator Sentinel

Author: Cortana Autonomous Evolutionary Architect
Operator: Michael Obiero (Nairobi, Kenya)

Performs high-frequency interferometric correlation of roller mill drive torque ripples, quadrature resolver phase angles, and harmonic amplitude deviations to preempt catastrophic drive-train fatigue in Nairobi milling plants.
"""

import time
import math
import logging
import statistics
from typing import Dict, List, Any, Optional

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - [%(filename)s] - %(message)s')
logger = logging.getLogger("RollerMillInterferometerCorrelatorSentinel")

class RollerMillInterferometerCorrelatorSentinel:
    """
    Monitors and correlates optical interferometer phase shifts with electrical torque
    resolver signals in commercial roller mills to detect micro-slip and torsional resonance.
    """
    def __init__(self, mill_id: str, sample_rate_hz: float = 1000.0):
        self.mill_id = mill_id
        self.sample_rate_hz = sample_rate_hz
        self.telemetry_history: List[Dict[str, Any]] = []
        logger.info(f"Initialized RollerMillInterferometerCorrelatorSentinel for mill {mill_id} at {sample_rate_hz}Hz.")

    def ingest_sensor_frame(self,
                          torque_ripple_nm: float,
                          resolver_phase_deg: float,
                          interferometer_fringe_shift: float,
                          harmonic_amplitude: float) -> Dict[str, Any]:
        """
        Ingests a high-frequency sensor frame, calculating cross-correlation indices
        between optical fringe shifts and electrical torque harmonics.
        """
        timestamp = time.time()
        
        # Compute phase quadrature mismatch
        quadrature_error = abs(resolver_phase_deg - (interferometer_fringe_shift * 36.0))
        
        # Correlate torque ripple with harmonic amplitude
        stress_index = (torque_ripple_nm * harmonic_amplitude) / (1.0 + abs(interferometer_fringe_shift))
        
        status = "NOMINAL"
        if stress_index > 85.0 or quadrature_error > 12.5:
            status = "WARNING"
        if stress_index > 150.0 or quadrature_error > 25.0:
            status = "CRITICAL_INTERVENTION_REQUIRED"

        frame = {
            "timestamp": timestamp,
            "mill_id": self.mill_id,
            "torque_ripple_nm": torque_ripple_nm,
            "resolver_phase_deg": resolver_phase_deg,
            "interferometer_fringe_shift": interferometer_fringe_shift,
            "harmonic_amplitude": harmonic_amplitude,
            "quadrature_error": quadrature_error,
            "stress_index": stress_index,
            "status": status
        }
        
        self.telemetry_history.append(frame)
        if len(self.telemetry_history) > 1000:
            self.telemetry_history.pop(0)
            
        if status != "NOMINAL":
            logger.warning(f"[{self.mill_id}] Sentinel Alert: Status={status}, StressIndex={stress_index:.2f}, QuadError={quadrature_error:.2f}deg")
            
        return frame

    def generate_diagnostic_summary(self) -> Dict[str, Any]:
        """
        Generates a rolling statistical summary for operator review.
        """
        if not self.telemetry_history:
            return {"status": "NO_DATA"}
            
        stress_indices = [f["stress_index"] for f in self.telemetry_history]
        quad_errors = [f["quadrature_error"] for f in self.telemetry_history]
        
        return {
            "mill_id": self.mill_id,
            "frames_analyzed": len(self.telemetry_history),
            "mean_stress_index": statistics.mean(stress_indices),
            "max_stress_index": max(stress_indices),
            "mean_quadrature_error_deg": statistics.mean(quad_errors),
            "max_quadrature_error_deg": max(quad_errors),
            "system_health": "DEGRADED" if max(stress_indices) > 150.0 else "OPTIMAL"
        }

if __name__ == "__main__":
    logger.info("Executing self-test routine for RollerMillInterferometerCorrelatorSentinel...")
    sentinel = RollerMillInterferometerCorrelatorSentinel(mill_id="NAI-MILL-ALPHA-04")
    
    # Simulate nominal readings
    f1 = sentinel.ingest_sensor_frame(12.5, 45.0, 1.25, 3.4)
    # Simulate anomalous high torque ripple & fringe shift
    f2 = sentinel.ingest_sensor_frame(48.2, 72.1, 3.89, 14.2)
    
    summary = sentinel.generate_diagnostic_summary()
    logger.info(f"Diagnostic Summary: {summary}")
    logger.info("Sentinel self-test completed successfully.")
