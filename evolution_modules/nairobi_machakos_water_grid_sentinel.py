import time
import logging
from dataclasses import dataclass
from typing import List, Optional, Dict, Any
from enum import Enum

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class WaterQualityStatus(Enum):
    """Enum representing the quality status of the water."""
    OPTIMAL = "optimal"
    DEGRADED = "degraded"
    CRITICAL = "critical"


@dataclass
class WaterMetrics:
    """Data class to hold water metrics."""
    pressure_bar: float
    flow_rate_lps: float
    turbidity_ntu: float
    ph_level: float
    chlorine_ppm: float
    timestamp: float

    def to_dict(self) -> Dict[str, Any]:
        """Convert metrics to a dictionary."""
        return {
            "pressure_bar": self.pressure_bar,
            "flow_rate_lps": self.flow_rate_lps,
            "turbidity_ntu": self.turbidity_ntu,
            "ph_level": self.ph_level,
            "chlorine_ppm": self.chlorine_ppm,
            "timestamp": self.timestamp
        }


class WaterGridSentinel:
    """Class to monitor and manage the Nairobi Machakos water grid."""

    def __init__(self, pressure_threshold: float = 2.0, flow_threshold: float = 50.0, turbidity_threshold: float = 5.0):
        """Initialize the WaterGridSentinel with thresholds."""
        self.pressure_threshold = pressure_threshold
        self.flow_threshold = flow_threshold
        self.turbidity_threshold = turbidity_threshold
        self.metrics_history: List[WaterMetrics] = []
        self.status = WaterQualityStatus.OPTIMAL

    def record_metrics(self, pressure_bar: float, flow_rate_lps: float, turbidity_ntu: float, ph_level: float, chlorine_ppm: float) -> None:
        """Record new water metrics."""
        metrics = WaterMetrics(pressure_bar, flow_rate_lps, turbidity_ntu, ph_level, chlorine_ppm, time.time())
        self.metrics_history.append(metrics)
        self._update_status(metrics)

    def _update_status(self, metrics: WaterMetrics) -> None:
        """Update the status based on the latest metrics."""
        if metrics.pressure_bar < self.pressure_threshold or metrics.flow_rate_lps < self.flow_threshold:
            self.status = WaterQualityStatus.CRITICAL
        elif metrics.turbidity_ntu > self.turbidity_threshold:
            self.status = WaterQualityStatus.DEGRADED
        else:
            self.status = WaterQualityStatus.OPTIMAL

    def get_status(self) -> WaterQualityStatus:
        """Get the current status of the water grid."""
        return self.status

    def get_metrics_history(self) -> List[WaterMetrics]:
        """Get the history of water metrics."""
        return self.metrics_history

    def predict_failure(self) -> bool:
        """Predict if a failure is imminent based on recent metrics."""
        if len(self.metrics_history) < 3:
            return False
        recent_metrics = self.metrics_history[-3:]
        pressure_trend = [m.pressure_bar for m in recent_metrics]
        flow_trend = [m.flow_rate_lps for m in recent_metrics]
        if all(pressure_trend[i] > pressure_trend[i+1] for i in range(len(pressure_trend)-1)) and \
           all(flow_trend[i] > flow_trend[i+1] for i in range(len(flow_trend)-1)):
            return True
        return False


if __name__ == "__main__":
    sentinel = WaterGridSentinel()
    sentinel.record_metrics(2.5, 60.0, 3.0, 7.0, 0.5)
    sentinel.record_metrics(2.4, 58.0, 4.0, 7.1, 0.5)
    sentinel.record_metrics(2.3, 55.0, 6.0, 7.2, 0.4)
    print(f"Status: {sentinel.get_status()}")
    print(f"Failure Predicted: {sentinel.predict_failure()}")
    print(f"Metrics History: {sentinel.get_metrics_history()}")