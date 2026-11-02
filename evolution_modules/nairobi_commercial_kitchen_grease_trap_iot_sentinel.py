"""
Nairobi Commercial Kitchen Grease Trap IoT Sentinel
Monitors grease separator levels, water temperature, and fat layer accumulation
for commercial kitchens in Nairobi, ensuring compliance with county health bylaws
and preventing drain clogs.
"""

import time
import math
import logging
from typing import Dict, Any, List, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("GreaseTrapSentinel")

class GreaseTrapSentinel:
    """Advanced IoT sentinel for commercial grease traps."""

    def __init__(self, trap_id: str, max_capacity_liters: float = 200.0):
        self.trap_id = trap_id
        self.max_capacity_liters = max_capacity_liters
        self.current_fat_level_cm = 0.0
        self.water_temperature_c = 25.0
        self.pH_level = 7.0
        self.flow_rate_lpm = 0.0
        self.last_service_timestamp = time.time()

    def ingest_telemetry(self, fat_cm: float, temp_c: float, ph: float, flow_lpm: float) -> Dict[str, Any]:
        """Ingest real-time IoT telemetry from grease trap sensors."""
        self.current_fat_level_cm = max(0.0, fat_cm)
        self.water_temperature_c = temp_c
        self.pH_level = max(0.0, min(14.0, ph))
        self.flow_rate_lpm = max(0.0, flow_lpm)
        
        logger.info(f"[{self.trap_id}] Telemetry updated: Fat={fat_cm}cm, Temp={temp_c}C, pH={ph}, Flow={flow_lpm}LPM")
        return self.evaluate_health()

    def evaluate_health(self) -> Dict[str, Any]:
        """Evaluate grease trap health and generate maintenance alerts."""
        # Assume standard trap depth is 50 cm
        max_depth_cm = 50.0
        fat_ratio = self.current_fat_level_cm / max_depth_cm
        
        status = "OPTIMAL"
        alerts = []
        
        if fat_ratio >= 0.8:
            status = "CRITICAL_CLEANOUT_REQUIRED"
            alerts.append("Fat layer exceeds 80% capacity! Risk of sewer line blockage.")
        elif fat_ratio >= 0.6:
            status = "WARNING"
            alerts.append("Fat layer approaches threshold. Schedule maintenance soon.")
            
        if self.water_temperature_c > 55.0:
            status = "WARNING"
            alerts.append("High water temperature detected; risk of emulsifying trapped fats into outflow.")
            
        if self.pH_level < 5.0 or self.pH_level > 10.0:
            status = "WARNING"
            alerts.append(f"Abnormal pH level ({self.pH_level}) detected; potential chemical corrosion risk.")

        return {
            "trap_id": self.trap_id,
            "status": status,
            "fat_layer_percentage": round(fat_ratio * 100, 2),
            "water_temperature_c": self.water_temperature_c,
            "pH_level": self.pH_level,
            "alerts": alerts,
            "timestamp": time.time()
        }

if __name__ == "__main__":
    sentinel = GreaseTrapSentinel(trap_id="TRAP_WESTLANDS_04")
    report = sentinel.ingest_telemetry(fat_cm=35.0, temp_c=42.5, ph=6.8, flow_lpm=15.2)
    print("Grease Trap Sentinel Report:", report)
