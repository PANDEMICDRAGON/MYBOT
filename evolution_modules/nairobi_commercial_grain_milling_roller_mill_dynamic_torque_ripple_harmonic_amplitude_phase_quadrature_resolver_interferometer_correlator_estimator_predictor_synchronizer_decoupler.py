"""
Nairobi Commercial Grain Milling Roller Mill Dynamic Torque Ripple Harmonic Amplitude Phase
Quadrature Resolver Interferometer Correlator Estimator Predictor Synchronizer Decoupler Module.

Provides advanced real-time DSP decoupling for high-frequency torsional oscillations in commercial
roller mill drive trains, suppressing harmonic phase anomalies and protecting mechanical assets.
"""

import math
import statistics
import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class TorqueSample:
    timestamp: float
    raw_torque_nm: float
    harmonic_amplitude: float
    phase_angle_rad: float
    quadrature_component: float


@dataclass
class DecouplerTelemetry:
    mean_torque_nm: float
    decoupled_torque_nm: float
    harmonic_suppression_db: float
    phase_quadrature_error: float
    resonance_status: str
    timestamp: float = field(default_factory=time.time)


class RollerMillTorsionalDecoupler:
    """
    Processes roller mill torque telemetry streams, isolates harmonic ripple components,
    and applies counter-phase quadrature decoupling to damp mechanical vibrations.
    """

    def __init__(self, target_frequency_hz: float = 50.0, damping_factor: float = 0.85):
        self.target_frequency_hz = target_frequency_hz
        self.damping_factor = damping_factor
        self.buffer: List[TorqueSample] = []
        self.max_buffer_size = 256

    def ingest_sample(self, raw_torque: float, harmonic_amp: float, phase_rad: float, quadrature: float) -> DecouplerTelemetry:
        sample = TorqueSample(
            timestamp=time.time(),
            raw_torque_nm=raw_torque,
            harmonic_amplitude=harmonic_amp,
            phase_angle_rad=phase_rad,
            quadrature_component=quadrature
        )
        self.buffer.append(sample)
        if len(self.buffer) > self.max_buffer_size:
            self.buffer.pop(0)

        return self._compute_decoupling(sample)

    def _compute_decoupling(self, current: TorqueSample) -> DecouplerTelemetry:
        if len(self.buffer) < 5:
            return DecouplerTelemetry(
                mean_torque_nm=current.raw_torque_nm,
                decoupled_torque_nm=current.raw_torque_nm,
                harmonic_suppression_db=0.0,
                phase_quadrature_error=0.0,
                resonance_status="INITIALIZING"
            )

        torques = [s.raw_torque_nm for s in self.buffer]
        mean_torque = statistics.mean(torques)
        
        # Apply quadrature counter-phase correction
        correction_factor = current.harmonic_amplitude * math.cos(current.phase_angle_rad) * self.damping_factor
        decoupled_torque = current.raw_torque_nm - correction_factor - (current.quadrature_component * 0.1)

        # Estimate harmonic suppression in dB
        suppression_db = 20.0 * math.log10(max(abs(current.raw_torque_nm / (abs(decoupled_torque) + 1e-6)), 1.0))
        phase_error = abs(current.phase_angle_rad - (math.pi / 2.0))

        status = "OPTIMAL"
        if suppression_db < 3.0 or phase_error > 0.8:
            status = "RESONANCE_WARNING"
        elif suppression_db < 1.0:
            status = "CRITICAL_ATTENUATION_REQUIRED"

        return DecouplerTelemetry(
            mean_torque_nm=mean_torque,
            decoupled_torque_nm=decoupled_torque,
            harmonic_suppression_db=suppression_db,
            phase_quadrature_error=phase_error,
            resonance_status=status
        )


if __name__ == "__main__":
    decoupler = RollerMillTorsionalDecoupler(target_frequency_hz=60.0)
    print("Initializing Nairobi Commercial Roller Mill Torsional Decoupler...")
    
    # Simulate incoming roller mill sensor telemetry
    for i in range(10):
        raw = 450.0 + (i * 2.5) + (math.sin(i) * 15.0)
        amp = 12.4 + (i * 0.1)
        phase = 1.57 + (i * 0.05)
        quad = 2.1
        
        telemetry = decoupler.ingest_sample(raw, amp, phase, quad)
        print(f"Step {i+1}: Raw Torque={raw:.2f}Nm, Decoupled={telemetry.decoupled_torque_nm:.2f}Nm, "
              f"Suppression={telemetry.harmonic_suppression_db:.2f}dB, Status={telemetry.resonance_status}")
    
    print("Decoupler test execution completed successfully.")
