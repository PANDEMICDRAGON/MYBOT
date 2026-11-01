"""Nairobi Commercial Grain Milling Roller Mill Dynamic Torque Ripple Harmonic Amplitude Phase Quadrature Resolver Interferometer Correlator Estimator Predictor Synchronizer Decoupler Module."""

import math
import logging
import statistics
typedef_dict = dict

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("RollerMillDecoupler")


class RollerMillTorqueDecoupler:
    """Real-time harmonic phase quadrature resolver and torque ripple decoupler for industrial milling rolls."""

    def __init__(self, sample_rate_hz: float = 1000.0, harmonic_order: int = 5):
        self.sample_rate_hz = sample_rate_hz
        self.harmonic_order = harmonic_order
        self.torque_buffer: list[float] = []
        self.phase_quadrature_history: list[float] = []
        logger.info("Initialized RollerMillTorqueDecoupler with sample rate %.1f Hz", sample_rate_hz)

    def ingest_torque_sample(self, torque_nm: float, resolver_angle_rad: float) -> dict[str, float]:
        """Ingest live torque and resolver angle data, computing harmonic quadrature and decoupling vectors."""
        self.torque_buffer.append(torque_nm)
        if len(self.torque_buffer) > 500:
            self.torque_buffer.pop(0)

        # Compute phase quadrature component
        quad_value = torque_nm * math.sin(resolver_angle_rad * self.harmonic_order)
        self.phase_quadrature_history.append(quad_value)
        if len(self.phase_quadrature_history) > 500:
            self.phase_quadrature_history.pop(0)

        mean_torque = statistics.mean(self.torque_buffer) if self.torque_buffer else 0.0
        ripple_amplitude = statistics.stdev(self.torque_buffer) if len(self.torque_buffer) > 1 else 0.0
        decoupled_compensation = -0.5 * quad_value

        return {
            "mean_torque_nm": mean_torque,
            "torque_ripple_amplitude": ripple_amplitude,
            "quadrature_signal": quad_value,
            "decoupled_compensation_nm": decoupled_compensation
        }

    def get_system_health(self) -> dict[str, str]:
        """Evaluate operational status of the roller mill drive train."""
        if not self.torque_buffer:
            return {"status": "IDLE", "diagnostics": "No telemetry recorded"}
        current_ripple = statistics.stdev(self.torque_buffer) if len(self.torque_buffer) > 1 else 0.0
        status = "OPTIMAL" if current_ripple < 15.0 else "ATTENTION_REQUIRED"
        return {
            "status": status,
            "diagnostics": f"Current ripple stdev: {current_ripple:.2f} Nm"
        }


if __name__ == "__main__":
    decoupler = RollerMillTorqueDecoupler()
    # Simulate ingestion of 10 samples
    for i in range(10):
        angle = i * 0.1
        torque = 120.0 + 10.0 * math.sin(angle * 5)
        metrics = decoupler.ingest_torque_sample(torque, angle)
        logger.info("Sample %d metrics: %s", i, metrics)
    health = decoupler.get_system_health()
    logger.info("System Health Check: %s", health)
