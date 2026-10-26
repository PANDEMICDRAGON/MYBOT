"""
Nairobi National Cereals and Produce Board (NCPB) Grain Silo IoT Humidity, Pest & Fumigation Compliance Sentinel
Module for real-time monitoring of grain storage metrics, moisture tracking, aflatoxin risk analysis,
and automated regulatory compliance for agricultural depots in Nairobi, Kenya.
"""

import logging
import json
import time
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] [GrainSiloSentinel]: %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class SiloTelemetry:
    silo_id: str
    location: str
    grain_type: str
    temperature_celsius: float
    moisture_percentage: float
    co2_ppm: float
    last_fumigation_date: str
    operator: str

class GrainSiloSentinel:
    """
    Monitors silo telemetry to detect spoilage risks, high moisture, or pest infestation
    in compliance with KEBS (Kenya Bureau of Standards) grain storage regulations.
    """
    
    MAX_SAFE_MOISTURE = 13.5  # KEBS standard for maize/wheat storage
    MAX_SAFE_TEMP = 28.0      # Celsius
    MAX_SAFE_CO2 = 800.0      # ppm indicating insect activity

    def __init__(self, depot_name: str = "NCPB Embakasi Central") -> None:
        self.depot_name = depot_name
        self.telemetry_history: List[Dict[str, Any]] = []
        logger.info(f"Initialized GrainSiloSentinel for depot: {self.depot_name}")

    def evaluate_silo(self, telemetry: SiloTelemetry) -> Dict[str, Any]:
        """
        Evaluates silo metrics against safety thresholds and computes risk scores.
        """
        warnings = []
        risk_score = 0.0

        if telemetry.moisture_percentage > self.MAX_SAFE_MOISTURE:
            over = telemetry.moisture_percentage - self.MAX_SAFE_MOISTURE
            warnings.warn(f"High moisture detected: {telemetry.moisture_percentage}% (Limit: {self.MAX_SAFE_MOISTURE}%)")
            risk_score += over * 15.0

        if telemetry.temperature_celsius > self.MAX_SAFE_TEMP:
            over = telemetry.temperature_celsius - self.MAX_SAFE_TEMP
            warnings.append(f"Elevated temperature: {telemetry.temperature_celsius}°C (Limit: {self.MAX_SAFE_TEMP}°C)")
            risk_score += over * 5.0

        if telemetry.co2_ppm > self.MAX_SAFE_CO2:
            excess = telemetry.co2_ppm - self.MAX_SAFE_CO2
            warnings.append(f"High CO2 concentration ({telemetry.co2_ppm} ppm) indicates possible pest infestation!")
            risk_score += (excess / 100.0) * 10.0

        risk_score = min(max(risk_score, 0.0), 100.0)
        status = "OPTIMAL"
        if risk_score > 70.0:
            status = "CRITICAL_ACTION_REQUIRED"
        elif risk_score > 30.0:
            status = "WARNING_MONITOR_CLOSELY"

        assessment = {
            "silo_id": telemetry.silo_id,
            "location": telemetry.location,
            "grain_type": telemetry.grain_type,
            "risk_score": round(risk_score, 2),
            "status": status,
            "warnings": warnings,
            "timestamp": time.time()
        }

        self.telemetry_history.append(assessment)
        logger.info(f"Evaluated Silo {telemetry.silo_id}: Status [{status}], Risk [{risk_score:.1f}%]")
        return assessment

    def get_audit_trail(self) -> List[Dict[str, Any]]:
        return self.telemetry_history

if __name__ == "__main__":
    sentinel = GrainSiloSentinel()
    
    sample_telemetry = SiloTelemetry(
        silo_id="SILO-NBI-042",
        location="Embakasi Depot, Nairobi",
        grain_type="White Maize",
        temperature_celsius=31.5,
        moisture_percentage=14.8,
        co2_ppm=950.0,
        last_fumigation_date="2025-01-10",
        operator="Michael Obiero"
    )

    result = sentinel.evaluate_silo(sample_telemetry)
    print(json.dumps(result, indent=2))
