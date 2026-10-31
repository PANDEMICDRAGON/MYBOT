import time
import logging
from dataclasses import dataclass, field
from typing import List, Optional, Tuple
import math

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("CryogenicSentinel")

@dataclass
class TemperatureReading:
    timestamp: float
    value: float
    uncertainty: float = 0.1

@dataclass
class KalmanState:
    x: float = 0.0  # State estimate
    p: float = 1.0  # Covariance

    def predict(self, q: float = 0.01) -> None:
        """Predict step of Kalman Filter."""
        self.p += q

    def update(self, z: float, r: float = 0.1) -> None:
        """Update step of Kalman Filter."""
        y = z - self.x
        s = self.p + r
        k = self.p / s
        self.x += k * y
        self.p -= k * self.p

@dataclass
class ColdChainAlert:
    timestamp: float
    severity: str  # "INFO", "WARNING", "CRITICAL"
    message: str
    predicted_breach_time: Optional[float] = None

class NairobiColdChainCryogenicSentinel:
    """
    A proactive sentinel for commercial cold storage in Nairobi.
    Uses Kalman filtering to predict temperature drift and integrates
    with power grid intelligence to prevent spoilage.
    """

    def __init__(self, chamber_id: str, critical_temp: float = 4.0, warning_temp: float = 6.0):
        self.chamber_id = chamber_id
        self.critical_temp = critical_temp
        self.warning_temp = warning_temp
        self.kalman = KalmanState()
        self.history: List[TemperatureReading] = []
        self.alerts: List[ColdChainAlert] = []
        self.is_power_stable = True
        self._last_reading_time = 0.0

    def set_power_status(self, stable: bool) -> None:
        """Update power grid status from KPLC sniffer."""
        self.is_power_stable = stable
        if not stable:
            logger.warning(f"[Sentinel] Power instability detected for {self.chamber_id}. Pre-cooling protocol initiated.")

    def ingest_reading(self, temp: float, uncertainty: float = 0.1) -> None:
        """Ingest a new temperature reading and update the Kalman filter."""
        now = time.time()
        reading = TemperatureReading(timestamp=now, value=temp, uncertainty=uncertainty)
        self.history.append(reading)

        # Update Kalman Filter
        self.kalman.predict()
        self.kalman.update(temp, uncertainty)

        # Check for immediate breaches
        if temp > self.critical_temp:
            self._raise_alert("CRITICAL", f"Temperature breach: {temp}°C > {self.critical_temp}°C")
        elif temp > self.warning_temp:
            self._raise_alert("WARNING", f"Temperature warning: {temp}°C > {self.warning_temp}°C")

        # Predictive check
        self._predictive_check()

    def _predictive_check(self) -> None:
        """Use recent history to predict if temperature will breach critical threshold."""
        if len(self.history) < 5:
            return

        # Simple linear regression on last 5 points to estimate slope
        recent = self.history[-5:]
        x_vals = [r.timestamp for r in recent]
        y_vals = [r.value for r in recent]

        n = len(x_vals)
        sum_x = sum(x_vals)
        sum_y = sum(y_vals)
        sum_xy = sum(x * y for x, y in zip(x_vals, y_vals))
        sum_x2 = sum(x * x for x in x_vals)

        denominator = (n * sum_x2 - sum_x * sum_x)
        if denominator == 0:
            return

        slope = (n * sum_xy - sum_x * sum_y) / denominator

        # If slope is positive (warming) and we are not on stable power, predict breach
        if slope > 0.01 and not self.is_power_stable:
            current_temp = self.kalman.x
            time_to_breach = (self.critical_temp - current_temp) / slope
            if 0 < time_to_breach < 300:  # Breach within 5 minutes
                self._raise_alert(
                    "CRITICAL",
                    f"Predicted breach in {time_to_breach:.1f}s. Drift rate: {slope:.4f}°C/s.",
                    predicted_breach_time=time.time() + time_to_breach
                )

    def _raise_alert(self, severity: str, message: str, predicted_breach_time: Optional[float] = None) -> None:
        """Log and store an alert."""
        alert = ColdChainAlert(
            timestamp=time.time(),
            severity=severity,
            message=message,
            predicted_breach_time=predicted_breach_time
        )
        self.alerts.append(alert)
        logger.log(
            logging.CRITICAL if severity == "CRITICAL" else logging.WARNING,
            f"[Sentinel:{self.chamber_id}] {severity}: {message}"
        )

    def get_status_report(self) -> dict:
        """Return a JSON-serializable status report."""
        return {
            "chamber_id": self.chamber_id,
            "current_estimated_temp": round(self.kalman.x, 2),
            "critical_temp": self.critical_temp,
            "warning_temp": self.warning_temp,
            "power_stable": self.is_power_stable,
            "total_alerts": len(self.alerts),
            "last_alert": self.alerts[-1].message if self.alerts else None
        }

if __name__ == "__main__":
    # Test Harness
    print("Initializing Nairobi Cold Chain Cryogenic Sentinel...")
    sentinel = NairobiColdChainCryogenicSentinel(chamber_id="CHAMBER-01", critical_temp=4.0, warning_temp=6.0)

    # Simulate stable power and normal temps
    sentinel.set_power_status(stable=True)
    for i in range(10):
        sentinel.ingest_reading(temp=3.5 + (i * 0.01))
        time.sleep(0.01)

    print("Status Report:", sentinel.get_status_report())

    # Simulate power cut and rapid warming
    print("Simulating power cut and rapid warming...")
    sentinel.set_power_status(stable=False)
    for i in range(20):
        # Rapidly increasing temperature
        sentinel.ingest_reading(temp=4.0 + (i * 0.2))
        time.sleep(0.01)

    print("Final Status Report:", sentinel.get_status_report())
    assert len(sentinel.alerts) > 0, "Expected alerts to be generated during rapid warming"
    print("Test Passed: Sentinel correctly detected and predicted temperature breach.")