"""
Nairobi Commercial Grain Milling Roller Mill Dynamic Torque Ripple Harmonic Amplitude Phase Quadrature Resolver Interferometer Correlator Estimator Predictor Synchronizer Attenuator Module.

Provides real-time analysis, phase quadrature decomposition, interferometric correlation, and active harmonic attenuation for heavy-duty industrial roller mill drive systems in Nairobi, Kenya.
"""

import math
import time
import logging
from typing import Dict, List, Any, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("RollerMillHarmonicAttenuator")

class RollerMillHarmonicAttenuator:
    """
    Computes phase-quadrature components and interferometric correlations of roller mill
    drive torque ripples, applying targeted attenuation signals to stabilize operations.
    """
    
    def __init__(self, sample_rate_hz: float = 1000.0, harmonic_order: int = 5):
        self.sample_rate_hz = sample_rate_hz
        self.harmonic_order = harmonic_order
        self.attenuation_gain = 0.85
        self.state_history: List[Dict[str, float]] = []
        logger.info("Initialized RollerMillHarmonicAttenuator at %.1f Hz (Order %d)", sample_rate_hz, harmonic_order)
        
    def process_telemetry(self, raw_torque_nm: float, current_rpm: float, timestamp: Optional[float] = None) -> Dict[str, Any]:
        ts = timestamp if timestamp is not None else time.time()
        omega = (current_rpm * 2.0 * math.pi) / 60.0
        
        # Phase quadrature quadrature estimation (simulated resolver output)
        phase_rad = (omega * ts) % (2.0 * math.pi)
        quadrature_i = raw_torque_nm * math.cos(phase_rad * self.harmonic_order)
        quadrature_q = raw_torque_nm * math.sin(phase_rad * self.harmonic_order)
        
        amplitude = math.sqrt(quadrature_i**2 + quadrature_q**2)
        phase_angle = math.atan2(quadrature_q, quadrature_i)
        
        # Interferometric correlation index
        correlation_index = amplitude / (abs(raw_torque_nm) + 1e-6)
        
        # Active attenuation compensation
        attenuation_signal = - (quadrature_i * self.attenuation_gain)
        compensated_torque = raw_torque_nm + attenuation_signal
        
        result = {
            "timestamp": ts,
            "raw_torque_nm": raw_torque_nm,
            "current_rpm": current_rpm,
            "amplitude": amplitude,
            "phase_angle": phase_angle,
            "correlation_index": correlation_index,
            "attenuation_signal": attenuation_signal,
            "compensated_torque": compensated_torque
        }
        
        self.state_history.append(result)
        if len(self.state_history) > 1000:
            self.state_history.pop(0)
            
        return result

    def get_diagnostics(self) -> Dict[str, Any]:
        if not self.state_history:
            return {"status": "IDLE", "samples_processed": 0}
        latest = self.state_history[-1]
        return {
            "status": "ACTIVE",
            "samples_processed": len(self.state_history),
            "latest_amplitude": latest["amplitude"],
            "latest_compensated_torque": latest["compensated_torque"]
        }

if __name__ == "__main__":
    print("Executing RollerMillHarmonicAttenuator self-test harness...")
    attenuator = RollerMillHarmonicAttenuator()
    # Simulate roller mill telemetry
    test_telemetry = [(
        150.0 + 25.0 * math.sin(i * 0.1),
        1450.0 + 5.0 * math.cos(i * 0.05)
    ) for i in range(50)]
    
    for idx, (torque, rpm) in enumerate(test_telemetry):
        res = attenuator.process_telemetry(torque, rpm)
        print(f"Sample {idx}: Raw={res['raw_torque_nm']:.2f}Nm, Amp={res['amplitude']:.2f}, Comp={res['compensated_torque']:.2f}Nm")
        
    print("Diagnostics:", attenuator.get_diagnostics())
    print("RollerMillHarmonicAttenuator module executed successfully.")
