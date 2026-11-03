"""
Nairobi Commercial Grain Milling Bag Sewing Thread Tension Harmonic Pulse Correlation Sentinel V2
Autonomously engineered by Cortana for Michael Obiero.
"""

import math
import random
import time
from typing import Dict, List, Optional, Tuple


class BagSewingThreadHarmonicSentinel:
    """Monitors high-speed bag sewing machine thread tension and vibrational harmonics."""

    def __init__(self, machine_id: str, nominal_tension_newtons: float = 18.5):
        self.machine_id = machine_id
        self.nominal_tension = nominal_tension_newtons
        self.tension_buffer: List[float] = []
        self.harmonic_spectrum: Dict[float, float] = {}
        self.anomaly_count = 0
        self.status = "STANDBY"

    def ingest_sensor_reading(self, tension_reading: float, vibration_amplitude: float) -> Dict[str, any]:
        """Ingests live tension and vibration telemetry and calculates harmonic stress."""
        self.tension_buffer.append(tension_reading)
        if len(self.tension_buffer) > 100:
            self.tension_buffer.pop(0)

        # Calculate variance and harmonic deviation
        mean_tension = sum(self.tension_buffer) / len(self.tension_buffer)
        deviation = abs(tension_reading - self.nominal_tension)
        
        # Simulate harmonic pulse correlation check
        harmonic_spike = vibration_amplitude * (1.0 + (deviation / self.nominal_tension))
        
        health_score = max(0.0, 100.0 - (harmonic_spike * 5.0))
        
        if health_score < 75.0:
            self.anomaly_count += 1
            self.status = "WARNING: THREAD FATIGUE DETECTED"
        else:
            self.status = "HEALTHY"

        return {
            "machine_id": self.machine_id,
            "mean_tension": round(mean_tension, 2),
            "harmonic_spike": round(harmonic_spike, 4),
            "health_score": round(health_score, 2),
            "anomaly_count": self.anomaly_count,
            "status": self.status,
            "timestamp": time.time()
        }

    def calibrate_tension(self, new_baseline: float) -> None:
        """Recalibrates nominal thread tension for varying flour bag specifications."""
        self.nominal_tension = new_baseline
        self.tension_buffer.clear()
        self.status = "CALIBRATED"


if __name__ == "__main__":
    sentinel = BagSewingThreadHarmonicSentinel(machine_id="SEW-LINE-04-NRB")
    print(f"Initializing {sentinel.machine_id}...")
    
    # Simulate runtime telemetry stream
    for i in range(5):
        simulated_tension = 18.5 + random.uniform(-3.5, 4.2)
        simulated_vibration = random.uniform(1.1, 3.8)
        report = sentinel.ingest_sensor_reading(simulated_tension, simulated_vibration)
        print(f"[Telemetry Cycle {i+1}] Report: {report}")
        time.sleep(0.05)
    
    print("Bag sewing harmonic pulse correlation sentinel test completed successfully.")
