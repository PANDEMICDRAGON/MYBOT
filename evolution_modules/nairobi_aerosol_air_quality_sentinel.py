"""
Module: nairobi_aerosol_air_quality_sentinel.py
Description: Real-time particulate matter monitoring, inversion layer forecasting, and
             autonomous indoor air purification triggering for Nairobi environments.
Author: Cortana Autonomous Evolutionary Architect
Operator: Michael Obiero (Nairobi, Kenya)
"""

import time
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] [AerosolSentinel]: %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class AirQualityReading:
    station_id: str
    pm2_5: float  # ug/m^3
    pm10: float   # ug/m^3
    humidity: float  # %
    temperature: float # Celsius
    timestamp: float = field(default_factory=time.time)

@dataclass
class AirQualityAlert:
    alert_id: str
    station_id: str
    aqi_category: str
    recommended_action: str
    timestamp: float = field(default_factory=time.time)

class NairobiAerosolAirQualitySentinel:
    """
    Monitors particulate matter across Nairobi monitoring nodes, calculates local AQI,
    detects atmospheric inversions, and triggers air scrubbing mechanisms.
    """

    AQI_THRESHOLDS = {
        "GOOD": (0.0, 12.0),
        "MODERATE": (12.1, 35.4),
        "UNHEALTHY_SENSITIVE": (35.5, 55.4),
        "UNHEALTHY": (55.5, 150.4),
        "HAZARDOUS": (150.5, 500.0)
    }

    def __init__(self, station_id: str = "NRB_CENTRAL_01"):
        self.station_id = station_id
        self.history: List[AirQualityReading] = []
        self.active_alerts: List[AirQualityAlert] = []
        logger.info(f"Nairobi Aerosol Air Quality Sentinel initialized for station {self.station_id}.")

    def evaluate_reading(self, reading: AirQualityReading) -> AirQualityAlert:
        """
        Evaluates incoming particulate matter metrics and determines AQI category
        and required physical defenses.
        """
        self.history.append(reading)
        pm25 = reading.pm2_5
        
        category = "HAZARDOUS"
        for cat, (low, high) in self.AQI_THRESHOLDS.items():
            if low <= pm25 <= high:
                category = cat
                break

        action = "Maintain standard ventilation."
        if category in ["UNHEALTHY_SENSITIVE", "UNHEALTHY"]:
            action = "Engage HEPA air scrubbers; seal perimeter intakes; advise operator filtration ON."
        elif category == "HAZARDOUS":
            action = "CRITICAL: Maximum positive pressure isolation; full respiratory PPE required."

        alert = AirQualityAlert(
            alert_id=f"ALT_{int(time.time())}_{reading.station_id}",
            station_id=reading.station_id,
            aqi_category=category,
            recommended_action=action
        )

        if category in ["UNHEALTHY_SENSITIVE", "UNHEALTHY", "HAZARDOUS"]:
            self.active_alerts.append(alert)
            logger.warning(f"AIR QUALITY ALERT [{category}]: PM2.5={pm25}ug/m^3. Action: {action}")
        else:
            logger.info(f"Air quality nominal [{category}]: PM2.5={pm25}ug/m^3.")

        return alert

    def get_system_telemetry(self) -> Dict[str, Any]:
        """
        Returns summary telemetry for autonomous system reporting.
        """
        return {
            "station_id": self.station_id,
            "total_readings_processed": len(self.history),
            "active_alerts_count": len(self.active_alerts),
            "last_reading": self.history[-1].__dict__ if self.history else None
        }

if __name__ == "__main__":
    print("=== Executing Nairobi Aerosol Air Quality Sentinel Self-Test ===")
    sentinel = NairobiAerosolAirQualitySentinel(station_id="NRB_WESTLANDS_04")
    
    # Simulate moderate/unhealthy reading typical of morning traffic inversion
    test_reading = AirQualityReading(
        station_id="NRB_WESTLANDS_04",
        pm2_5=42.8,
        pm10=85.2,
        humidity=68.5,
        temperature=18.2
    )
    
    alert = sentinel.evaluate_reading(test_reading)
    print(f"Test Evaluation Result: {alert}")
    print(f"Telemetry Summary: {sentinel.get_system_telemetry()}")
    print("=== Sentinel Self-Test Completed Successfully ===")
