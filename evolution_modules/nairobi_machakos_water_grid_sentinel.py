import time
import random
from typing import List, Dict, Optional
from dataclasses import dataclass

@dataclass
class PressureReading:
    timestamp: float
    pressure_kpa: float
    flow_rate_lpm: float

class NairobiMachakosWaterGridSentinel:
    """
    Monitors the Machakos water grid for pressure and flow anomalies.
    """

    def __init__(self, pressure_threshold_kpa: float = 300.0, flow_threshold_lpm: float = 1000.0):
        self.pressure_threshold_kpa = pressure_threshold_kpa
        self.flow_threshold_lpm = flow_threshold_lpm
        self.readings: List[PressureReading] = []

    def add_reading(self, pressure_kpa: float, flow_rate_lpm: float) -> None:
        """Add a new pressure and flow reading."""
        reading = PressureReading(time.time(), pressure_kpa, flow_rate_lpm)
        self.readings.append(reading)

    def detect_anomalies(self) -> List[Dict[str, float]]:
        """Detect anomalies in pressure and flow readings."""
        anomalies = []
        for reading in self.readings:
            if reading.pressure_kpa > self.pressure_threshold_kpa:
                anomalies.append({
                    'timestamp': reading.timestamp,
                    'type': 'high_pressure',
                    'value': reading.pressure_kpa
                })
            if reading.flow_rate_lpm > self.flow_threshold_lpm:
                anomalies.append({
                    'timestamp': reading.timestamp,
                    'type': 'high_flow',
                    'value': reading.flow_rate_lpm
                })
        return anomalies

    def clear_readings(self) -> None:
        """Clear all stored readings."""
        self.readings.clear()

if __name__ == '__main__':
    sentinel = NairobiMachakosWaterGridSentinel()
    for _ in range(10):
        sentinel.add_reading(random.uniform(200, 400), random.uniform(500, 1500))
    anomalies = sentinel.detect_anomalies()
    print(f"Detected {len(anomalies)} anomalies")
    sentinel.clear_readings()
