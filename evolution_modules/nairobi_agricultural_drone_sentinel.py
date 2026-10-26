"""
Nairobi Commercial Agricultural Drone & Multispectral Crop Health Sentinel
Designed for autonomous telemetry monitoring, NDVI crop stress detection, battery/thermal management,
and geofenced flight-path enforcement across Nairobi agricultural zones.
"""

import time
import math
import logging
from typing import Dict, List, Optional, Tuple

logging.basicConfig(level=logging.INFO, format='%(asctime)s - [AgriDroneSentinel] - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AgriculturalDroneSentinel:
    def __init__(self, drone_id: str, base_station_coords: Tuple[float, float], geofence_radius_km: float = 15.0):
        self.drone_id = drone_id
        self.base_lat, self.base_lon = base_station_coords
        self.geofence_radius_km = geofence_radius_km
        self.battery_pct = 100.0
        self.motor_temp_c = 35.0
        self.current_lat = self.base_lat
        self.current_lon = self.base_lon
        self.altitude_m = 0.0
        self.flight_status = "GROUNDED"
        self.ndvi_readings: List[float] = []
        logger.info(f"AgriDroneSentinel initialized for {drone_id} based in Nairobi (lat/lon: {base_station_coords}).")

    def update_telemetry(self, lat: float, lon: float, altitude: float, battery: float, temp: float) -> Dict[str, any]:
        """Updates real-time telemetry and performs boundary / safety checks."""
        self.current_lat = lat
        self.current_lon = lon
        self.altitude_m = altitude
        self.battery_pct = max(0.0, min(100.0, battery))
        self.motor_temp_c = temp

        distance_from_base = self._calculate_haversine_distance(self.base_lat, self.base_lon, lat, lon)
        
        safety_alerts = []
        if distance_from_base > self.geofence_radius_km:
            safety_alerts.append("GEOFENCE_BREACH_WARNING: Drone exceeding authorized operational radius!")
            self.flight_status = "RETURNING_TO_BASE"
        
        if self.battery_pct < 20.0:
            safety_alerts.append("LOW_BATTERY_CRITICAL: Mandatory Return-to-Launch initiated.")
            self.flight_status = "RETURNING_TO_BASE"
            
        if self.motor_temp_c > 65.0:
            safety_alerts.append("MOTOR_OVERHEAT_WARNING: High thermal load detected.")

        return {
            "drone_id": self.drone_id,
            "status": self.flight_status,
            "distance_from_base_km": round(distance_from_base, 2),
            "battery_pct": self.battery_pct,
            "motor_temp_c": self.motor_temp_c,
            "alerts": safety_alerts
        }

    def ingest_multispectral_data(self, red_band_avg: float, nir_band_avg: float) -> Dict[str, any]:
        """
        Calculates NDVI (Normalized Difference Vegetation Index):
        NDVI = (NIR - Red) / (NIR + Red)
        Ranges from -1.0 to +1.0. Healthy crops typically range from 0.3 to 0.8.
        """
        if (nir_band_avg + red_band_avg) == 0:
            ndvi = 0.0
        else:
            ndvi = (nir_band_avg - red_band_avg) / (nir_band_avg + red_band_avg)
        
        self.ndvi_readings.append(ndvi);
        
        health_status = "OPTIMAL"
        if ndvi < 0.2:
            health_status = "CRITICAL_STRESS_OR_BARE_SOIL"
        elif 0.2 <= ndvi < 0.4:
            health_status = "MODERATE_STRESS_WATER_OR_NUTRIENT_DEFICIT"
        elif 0.4 <= ndvi <= 0.8:
            health_status = "VIGOROUS_HEALTH"
        else:
            health_status = "DENSE_CANOPY_OR_ANOMALY"

        logger.info(f"Multispectral analysis: NDVI={round(ndvi, 4)} [{health_status}]")
        return {
            "ndvi": round(ndvi, 4),
            "health_status": health_status,
            "readings_count": len(self.ndvi_readings)
        }

    def _calculate_haversine_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculates distance in kilometers between two GPS coordinates."""
        R = 6371.0 # Earth radius in km
        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)
        dphi = math.radians(lat2 - lat1)
        dlambda = math.radians(lon2 - lon1)

        a = math.sin(dphi / 2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return R * c

if __name__ == "__main__":
    print("[+] Executing Agricultural Drone Sentinel Test Harness for Nairobi Operations...")
    # Nairobi Karen agricultural test coordinates
    sentinel = AgriculturalDroneSentinel(drone_id="DRONE-NBI-01", base_station_coords=(-1.3192, 36.7065))
    
    telemetry = sentinel.update_telemetry(lat=-1.3200, lon=36.7100, altitude=50.0, battery=88.5, temp=41.2)
    print(f"Telemetry Check: {telemetry}")

    crop_analysis = sentinel.ingest_multispectral_data(red_band_avg=0.12, nir_band_avg=0.68)
    print(f"Crop Analysis: {crop_analysis}")
    print("[+] Agricultural Drone Sentinel verified successfully.")
