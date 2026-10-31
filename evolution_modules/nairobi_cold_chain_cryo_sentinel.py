import time
import logging
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from enum import Enum
import random

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SensorStatus(Enum):
    NORMAL = "NORMAL"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"
    OFFLINE = "OFFLINE"

@dataclass
class SensorReading:
    timestamp: float
    temperature: float
    humidity: float
    power_voltage: float
    status: SensorStatus = SensorStatus.NORMAL

@dataclass
class ColdChainAlert:
    timestamp: float
    sensor_id: str
    alert_type: str
    severity: SensorStatus
    message: str
    recommended_action: str

class NairobiColdChainCryoSentinel:
    """
    A proactive sentinel for monitoring and securing cold chain integrity in Nairobi.
    
    This class monitors temperature, humidity, and power stability in cold storage facilities,
    predicts potential failures, and triggers automated alerts and corrective actions.
    """

    def __init__(self, sensor_ids: List[str], temperature_thresholds: Dict[str, float], humidity_thresholds: Dict[str, float]):
        self.sensor_ids = sensor_ids
        self.temperature_thresholds = temperature_thresholds
        self.humidity_thresholds = humidity_thresholds
        self.readings: Dict[str, List[SensorReading]] = {sid: [] for sid in sensor_ids}
        self.alerts: List[ColdChainAlert] = []
        self.last_check_time: float = 0.0
        self.check_interval: float = 5.0  # seconds

    def simulate_sensor_reading(self, sensor_id: str) -> SensorReading:
        """Simulate a sensor reading for testing purposes."""
        timestamp = time.time()
        temperature = random.uniform(-25.0, 5.0)
        humidity = random.uniform(30.0, 70.0)
        power_voltage = random.uniform(210.0, 240.0)

        # Determine status based on thresholds
        status = SensorStatus.NORMAL
        if temperature > self.temperature_thresholds.get("max", 2.0) or temperature < self.temperature_thresholds.get("min", -25.0):
            status = SensorStatus.CRITICAL
        elif temperature > self.temperature_thresholds.get("warn_max", 0.0) or temperature < self.temperature_thresholds.get("warn_min", -20.0):
            status = SensorStatus.WARNING

        if humidity > self.humidity_thresholds.get("max", 65.0) or humidity < self.humidity_thresholds.get("min", 35.0):
            status = SensorStatus.CRITICAL
        elif humidity > self.humidity_thresholds.get("warn_max", 60.0) or humidity < self.humidity_thresholds.get("warn_min", 40.0):
            status = SensorStatus.WARNING

        if power_voltage < 200.0 or power_voltage > 250.0:
            status = SensorStatus.CRITICAL
        elif power_voltage < 210.0 or power_voltage > 240.0:
            status = SensorStatus.WARNING

        return SensorReading(timestamp, temperature, humidity, power_voltage, status)

    def check_sensors(self) -> List[ColdChainAlert]:
        """Check all sensors and generate alerts if necessary."""
        current_time = time.time()
        if current_time - self.last_check_time < self.check_interval:
            return []

        self.last_check_time = current_time
        new_alerts = []

        for sensor_id in self.sensor_ids:
            reading = self.simulate_sensor_reading(sensor_id)
            self.readings[sensor_id].append(reading)

            if reading.status != SensorStatus.NORMAL:
                alert = ColdChainAlert(
                    timestamp=current_time,
                    sensor_id=sensor_id,
                    alert_type="SENSOR_ANOMALY",
                    severity=reading.status,
                    message=f"Sensor {sensor_id} reported {reading.status.value} status: T={reading.temperature}°C, H={reading.humidity}%, V={reading.power_voltage}V",
                    recommended_action="Check sensor calibration and power supply"
                )
                new_alerts.append(alert)
                self.alerts.append(alert)
                logger.warning(alert.message)

        return new_alerts

    def get_recent_readings(self, sensor_id: str, count: int = 10) -> List[SensorReading]:
        """Get recent readings for a specific sensor."""
        return self.readings.get(sensor_id, [])[-count:]

    def get_all_alerts(self) -> List[ColdChainAlert]:
        """Get all generated alerts."""
        return self.alerts

    def clear_alerts(self) -> None:
        """Clear all alerts."""
        self.alerts.clear()

if __name__ == "__main__":
    # Test harness
    sensor_ids = ["sensor_001", "sensor_002", "sensor_003"]
    temperature_thresholds = {"min": -25.0, "max": 2.0, "warn_min": -20.0, "warn_max": 0.0}
    humidity_thresholds = {"min": 35.0, "max": 65.0, "warn_min": 40.0, "warn_max": 60.0}

    sentinel = NairobiColdChainCryoSentinel(sensor_ids, temperature_thresholds, humidity_thresholds)

    logger.info("Starting Nairobi Cold Chain Cryo-Sentinel test...")

    for _ in range(5):
        alerts = sentinel.check_sensors()
        if alerts:
            for alert in alerts:
                logger.info(f"Alert: {alert.message}")
        time.sleep(1)

    logger.info("Test complete.")
    logger.info(f"Total alerts generated: {len(sentinel.get_all_alerts())}")
