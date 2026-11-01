"""
Nairobi Commercial Grain Milling Roller Mill Dynamic Torque Ripple Harmonic Amplitude Phase Quadrature Resolver Sentinel

Author: Cortana, Autonomous Evolutionary Architect
Operator: Michael Obiero, Nairobi, Kenya

Provides advanced real-time mathematical resolution of quadrature phase angle components in roller mill
armature torque ripples, safeguarding industrial milling assets in Nairobi's industrial districts.
"""

import math
import time
import logging
from typing import Dict, Any, List, Optional

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] [QUADRATURE-RESOLVER]: %(message)s')
logger = logging.getLogger(__name__)

class RollerMillQuadratureResolverSentinel:
    """
    Monitors, calculates, and resolves quadrature phase shifts and harmonic amplitudes
    of roller mill drive torques in commercial milling facilities.
    """
    def __init__(self, mill_id: str, nominal_torque_nm: float = 250.0, sample_window: int = 64):
        self.mill_id = mill_id
        self.nominal_torque_nm = nominal_torque_nm
        self.sample_window = sample_window
        self.torque_samples: List[float] = []
        self.anomaly_count = 0
        logger.info(f"Initialized Quadrature Resolver Sentinel for Mill: {self.mill_id} (Nominal: {nominal_torque_nm} Nm)")

    def ingest_torque_reading(self, torque_nm: float) -> Dict[str, Any]:
        """
        Ingests a raw torque sample, computes in-phase and quadrature components, and evaluates stability.
        """
        self.torque_samples.append(torque_nm)
        if len(self.torque_samples) > self.sample_window:
            self.torque_samples.pop(0)

        metrics = self._compute_quadrature_transform()
        status = self._evaluate_status(metrics)
        return {
            "mill_id": self.mill_id,
            "timestamp": time.time(),
            "metrics": metrics,
            "status": status
        }

    def _compute_quadrature_transform(self) -> Dict[str, float]:
        if not self.torque_samples:
            return {"in_phase_amplitude": 0.0, "quadrature_amplitude": 0.0, "phase_angle_rad": 0.0}

        n = len(self.torque_samples)
        mean_val = sum(self.torque_samples) / n
        
        # Discrete quadrature approximation (sin/cos projection against fundamental frequency)
        i_comp = 0.0
        q_comp = 0.0
        for idx, val in enumerate(self.torque_samples):
            angle = 2.0 * math.pi * idx / n
            deviation = val - mean_val
            i_comp += deviation * math.cos(angle)
            q_comp += deviation * math.sin(angle)

        i_comp = (2.0 / n) * i_comp
        q_comp = (2.0 / n) * q_comp

        amplitude = math.sqrt(i_comp**2 + q_comp**2)
        phase_rad = math.atan2(q_comp, i_comp)

        return {
            "in_phase_amplitude": round(i_comp, 4),
            "quadrature_amplitude": round(q_comp, 4),
            "total_harmonic_amplitude": round(amplitude, 4),
            "phase_angle_rad": round(phase_rad, 4)
        }

    def _evaluate_status(self, metrics: Dict[str, float]) -> str:
        tha = metrics["total_harmonic_amplitude"]
        threshold = self.nominal_torque_nm * 0.15
        if tha > threshold:
            self.anomaly_count += 1
            logger.warning(f"[{self.mill_id}] High harmonic amplitude detected: {tha} Nm exceeds threshold {threshold} Nm!")
            return "WARNING_EXCESSIVE_QUADRATURE_RIPPLE"
        return "NOMINAL"

    def get_telemetry(self) -> Dict[str, Any]:
        return {
            "mill_id": self.mill_id,
            "anomaly_count": self.anomaly_count,
            "samples_tracked": len(self.torque_samples)
        }

if __name__ == "__main__":
    sentinel = RollerMillQuadratureResolverSentinel(mill_id="NAI_MILL_ALPHA_04")
    # Simulate smooth to erratic torque readings
    for i in range(100):
        simulated_torque = 250.0 + 25.0 * math.sin(i * 0.2) + (10.0 if i > 80 else 0.0) * math.cos(i * 0.5)
        result = sentinel.ingest_torque_reading(simulated_torque)
    print(f"Final Sentinel Telemetry: {sentinel.get_telemetry()}")
