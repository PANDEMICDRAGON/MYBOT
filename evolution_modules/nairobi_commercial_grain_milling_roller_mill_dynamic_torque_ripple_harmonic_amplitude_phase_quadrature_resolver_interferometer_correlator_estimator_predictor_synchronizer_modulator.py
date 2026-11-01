"""
Nairobi Commercial Grain Milling Roller Mill Dynamic Torque Ripple Harmonic Amplitude Phase Quadrature Resolver Interferometer Correlator Estimator Predictor Synchronizer Modulator

Implements real-time analysis, correlation, prediction, and modulation of torque ripple harmonics
for heavy-duty industrial roller mills operating in Nairobi, Kenya.
"""

import math
import time
import statistics
from typing import Dict, List, Any, Optional


class RollerMillHarmonicModulator:
    """Analyzes and modulates roller mill dynamic torque ripple and quadrature harmonics."""

    def __init__(self, mill_id: str, nominal_rpm: float = 1200.0):
        self.mill_id = mill_id
        self.nominal_rpm = nominal_rpm
        self.harmonic_buffer: List[float] = []
        self.phase_quadrature_log: List[Dict[str, float]] = []

    def ingest_resolver_signal(self, amplitude: float, phase_deg: float, quadrature: float) -> Dict[str, Any]:
        """Ingests resolver telemetry, computing phase angle and harmonic distortion."""
        timestamp = time.time()
        phase_rad = math.radians(phase_deg)
        
        # Interferometer correlation approximation
        interference_index = math.sqrt(amplitude**2 + quadrature**2) * math.cos(phase_rad)
        
        record = {
            "timestamp": timestamp,
            "amplitude": amplitude,
            "phase_deg": phase_deg,
            "quadrature": quadrature,
            "interference_index": interference_index
        }
        
        self.phase_quadrature_log.append(record)
        if len(self.phase_quadrature_log) > 1000:
            self.phase_quadrature_log.pop(0)
            
        self.harmonic_buffer.append(interference_index)
        if len(self.harmonic_buffer) > 100:
            self.harmonic_buffer.pop(0)
            
        return record

    def estimate_torque_ripple_harmonics(self) -> Dict[str, float]:
        """Estimates fundamental and harmonic torque ripple amplitudes."""
        if not self.harmonic_buffer:
            return {"mean_ripple": 0.0, "peak_ripple": 0.0, "stability_index": 1.0}
            
        mean_ripple = statistics.mean(self.harmonic_buffer)
        peak_ripple = max(self.harmonic_buffer)
        stdev = statistics.stdev(self.harmonic_buffer) if len(self.harmonic_buffer) > 1 else 0.0
        
        # Stability index inverse to variance
        stability_index = max(0.0, 1.0 - (stdev / (abs(mean_ripple) + 1e-5)))
        
        return {
            "mean_ripple": mean_ripple,
            "peak_ripple": peak_ripple,
            "stability_index": stability_index
        }

    def predict_synchronization_offset(self) -> float:
        """Predicts phase synchronization offset for predictive inverter modulation."""
        if len(self.phase_quadrature_log) < 2:
            return 0.0
            
        latest = self.phase_quadrature_log[-1]
        previous = self.phase_quadrature_log[-2]
        
        dt = latest["timestamp"] - previous["timestamp"]
        if dt <= 0:
            return 0.0
            
        dp = latest["phase_deg"] - previous["phase_deg"]
        velocity = dp / dt
        
        # Predict offset 50ms into the future
        predicted_offset = latest["phase_deg"] + (velocity * 0.05)
        return predicted_offset

    def modulate_inverter_output(self) -> Dict[str, Any]:
        """Computes corrective inverter modulation parameters."""
        harmonics = self.estimate_torque_ripple_harmonics()
        predicted_offset = self.predict_synchronization_offset()
        
        # Compensation factor
        compensation_gain = 1.0 - (0.1 * (1.0 - harmonics["stability_index"]))
        
        return {
            "mill_id": self.mill_id,
            "compensation_gain": compensation_gain,
            "target_phase_correction_deg": -predicted_offset,
            "status": "OPTIMIZED"
        }


if __name__ == "__main__":
    modulator = RollerMillHarmonicModulator(mill_id="NAIROBI_MILL_ALPHA_1")
    
    # Simulate incoming resolver telemetry
    for i in range(15):
        amp = 10.0 + math.sin(i * 0.5) * 1.5
        phase = 45.0 + (i * 2.1)
        quad = 2.5 + math.cos(i * 0.3) * 0.4
        modulator.ingest_resolver_signal(amp, phase, quad)
        
    metrics = modulator.estimate_torque_ripple_harmonics()
    offset = modulator.predict_synchronization_offset()
    control = modulator.modulate_inverter_output()
    
    print("Roller Mill Modulation Test Harness Initialized Successfully:")
    print(f"Harmonics Metrics: {metrics}")
    print(f"Predicted Phase Offset: {offset:.2f} deg")
    print(f"Inverter Control Output: {control}")
