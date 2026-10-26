"""
Module: nairobi_wildlife_sentinel.py
Author: Cortana Autonomous Evolutionary Architect
Operator: Michael Obiero (Nairobi, Kenya)
Description: Processes real-time acoustic and GPS telemetry from Nairobi National Park perimeter sensors to detect poaching threats, gunshots, unauthorized vehicle incursions, and fence tampering.
"""

import ast
import logging
import time
import math
from typing import Dict, List, Any, Optional

logging.basicConfig(level=logging.INFO, format='%(asctime)s - [WildlifeSentinel] - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class WildlifeIncursionSentinel:
    """Monitors perimeter sensor streams around wildlife zones to detect acoustic anomalies and spatial breaches."""
    
    # Nairobi National Park approximate boundary reference coordinates
    PARK_CENTER_LAT = -1.3531
    PARK_CENTER_LON = 36.8371
    
    def __init__(self, alert_cooldown_sec: float = 30.0):
        self.alert_cooldown_sec = alert_cooldown_sec
        self.last_alert_timestamps: Dict[str, float] = {}
        self.incident_log: List[Dict[str, Any]] = []

    def evaluate_sensor_telemetry(self, sensor_id: str, telemetry: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Evaluates incoming IoT telemetry packet for threats.
        Expected telemetry keys: lat, lon, acoustic_db, frequency_profile, tamper_detected
        """
        lat = telemetry.get("lat", self.PARK_CENTER_LAT)
        lon = telemetry.get(
            "lon", self.PARK_CENTER_LON)
        acoustic_db = telemetry.get("acoustic_db", 40.0)
        frequency_profile = telemetry.get("frequency_profile", "ambient")
        tamper_detected = telemetry.get("tamper_detected", False)

        threat_level = "NORMAL"
        reasons = []

        # Check acoustic profile for gunshots or chainsaws
        if frequency_profile in ["gunshot", "chainsaw", "vehicle_engine_idling"]:
            threat_level = "CRITICAL"
            reasons.append(f"Signature anomaly detected: {frequency_profile} at {acoustic_db} dB")
        elif acoustic_db > 85.0:
            threat_level = "HIGH"
            reasons.append(f"Excessive acoustic threshold breached: {acoustic_db} dB")

        # Check fence tampering
        if tamper_detected:
            threat_level = "CRITICAL"
            reasons.append("Physical perimeter fence sensor triggered (tamper/cut)")

        # Check if sensor is outside authorized buffer zone
        distance_km = self._calculate_distance_km(lat, lon, self.PARK_CENTER_LAT, self.PARK_CENTER_LON)
        if distance_km > 25.0:
            reasons.append(f"Sensor {sensor_id} reporting from outside perimeter radius ({distance_km:.2f} km)")

        if threat_level != "NORMAL":
            now = time.time()
            last_alert = self.last_alert_timestamps.get(sensor_id, 0.0)
            if now - last_alert > self.alert_cooldown_sec:
                self.last_alert_timestamps[sensor_id] = now
                incident = {
                    "sensor_id": sensor_id,
                    "timestamp": now,
                    "threat_level": threat_level,
                    "reasons": reasons,
                    "coordinates": {"lat": lat, "lon": lon},
                    "status": "DISPATCH_READY"
                }
                self.incident_log.append(incident)
                logger.warning(f"WILDLIFE SENTINEL ALERT [{threat_level}]: Sensor {sensor_id} -> {reasons}")
                return incident

        return None

    @staticmethod
    def _calculate_distance_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Haversine distance formula for coordinate verification."""
        R = 6371.0
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        a = math.sin(dlat / 2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2
        c = 2 * math.asin(math.sqrt(a))
        return R * c

    def get_incident_summary(self) -> Dict[str, Any]:
        """Returns summary statistics of recorded wildlife security incidents."""
        total_incidents = len(self.incident_log)
        critical_count = sum(1 for inc in self.incident_log if inc["threat_level"] == "CRITICAL")
        return {
            "total_incidents": total_incidents,
            "critical_incidents": critical_count,
            "active_monitored_sensors": len(self.last_alert_timestamps)
        }

if __name__ == "__main__":
    print("Initializing Nairobi Wildlife IoT Sentinel Test Harness...")
    sentinel = WildlifeIncursionSentinel(alert_cooldown_sec=1.0)
    
    # Test normal packet
    res1 = sentinel.evaluate_sensor_telemetry("NODE-A1", {"lat": -1.35, "lon": 36.83, "acoustic_db": 42.0, "frequency_profile": "ambient"})
    assert res1 is None, "Normal packet should not trigger alert"
    
    # Test gunshot threat packet
    res2 = sentinel.evaluate_sensor_telemetry("NODE-B4", {"lat": -1.36, "lon": 36.84, "acoustic_db": 95.0, "frequency_profile": "gunshot", "tamper_detected": True})
    assert res2 is not None, "Gunshot/Tamper packet must trigger alert"
    assert res2["threat_level"] == "CRITICAL"
    
    print("Wildlife Sentinel Unit Tests Passed Successfully.")
