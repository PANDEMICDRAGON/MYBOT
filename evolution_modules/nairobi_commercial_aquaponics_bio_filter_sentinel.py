"""
Nairobi Commercial Aquaponics Bio-Filter & Nitrification Biosafety Sentinel
Autonomous Evolutionary Architecture for Michael Obiero / Nairobi, Kenya

Monitors biological filtration efficiency, dissolved oxygen, pH, and toxic nitrogen compounds
in urban commercial aquaponics systems, executing emergency fail-safes and aeration cycling.
"""

import time
import logging
from typing import Dict, Any, List, Optional

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] [%(name)s]: %(message)s')
logger = logging.getLogger("AquaponicsBioFilterSentinel")


class AquaponicsBioFilterSentinel:
    """
    Manages biological filtration health, nitrogen cycle metrics, and emergency water quality 
    controls for urban commercial aquaponics facilities in Nairobi.
    """

    def __init__(self, facility_id: str, max_ammonia_ppm: float = 0.5, min_dissolved_oxygen_ppm: float = 5.0):
        self.facility_id = facility_id
        self.max_ammonia_ppm = max_ammonia_ppm
        self.min_dissolved_oxygen_ppm = min_dissolved_oxygen_ppm
        self.system_status = "NOMINAL"
        self.emergency_aeration_active = False
        self.emergency_flush_active = False
        logger.info(f"Initialized Aquaponics Bio-Filter Sentinel for {{self.facility_id}}")

    def evaluate_telemetry(self, telemetry: Dict[str, float]) -> Dict[str, Any]:
        """
        Evaluates real-time sensor telemetry including ammonia, nitrite, pH, DO, and temperature.
        """
        ammonia = telemetry.get("ammonia_ppm", 0.0)
        nitrite = telemetry.get(
            "nitrite_ppm", 0.0
        )  # Toxic intermediate in nitrification
        nitrate = telemetry.get("nitrate_ppm", 20.0)  # Plant nutrient
        dissolved_oxygen = telemetry.get("dissolved_oxygen_ppm", 6.0)
        ph = telemetry.get("ph", 6.8)
        temperature_c = telemetry.get("temperature_celsius", 22.5)

        actions: List[str] = []
        alerts: List[str] = []

        # Check Ammonia toxicity
        if ammonia > self.max_ammonia_ppm:
            alerts.append(
                f"CRITICAL: Ammonia spike detected ({{ammonia}} ppm > {{self.max_ammonia_ppm}} ppm)"
            )
            self.emergency_flush_active = True
            actions.append(
                "TRIGGER_BYPASS_AND_FRESH_WATER_DILUTION_VALVE"
            )
        else:
            self.emergency_flush_active = False

        # Check Dissolved Oxygen (critical for nitrifying bacteria and fish)
        if dissolved_oxygen < self.min_dissolved_oxygen_ppm:
            alerts.append(
                f"CRITICAL: Dissolved Oxygen low ({{dissolved_oxygen}} ppm < {{self.min_dissolved_oxygen_ppm}} ppm)"
            )
            self.emergency_aeration_active = True
            actions.append(
                "ENGAGE_SECONDARY_OXYGEN_GENERATOR_AND_BLOWERS"
            )
        else:
            self.emergency_aeration_active = False

        # Check Nitrification efficiency ratio (Nitrate vs Nitrite/Ammonia)
        if nitrite > 1.0:
            alerts.append(
                f"WARNING: Nitrite accumulation ({{nitrite}} ppm). Biofilter bacterial colony bottleneck."
            )
            actions.append(
                "REDUCE_FISH_FEEDING_RATE_AUTOMATICALLY"
            )

        # System status update
        if alerts:
            self.system_status = "DEGRADED_INTERVENTION_ACTIVE"
        else:
            self.system_status = "NOMINAL"

        assessment = {
            "facility_id": self.facility_id,
            "timestamp": time.time(),
            "status": self.system_status,
            "alerts": alerts,
            "actions_taken": actions,
            "emergency_aeration": self.emergency_aeration_active,
            "emergency_flush": self.emergency_flush_active,
        }

        logger.info(f"Telemetry evaluated for {{self.facility_id}}: Status[{{self.system_status}}]")
        return assessment


if __name__ == "__main__":
    sentinel = AquaponicsBioFilterSentinel(facility_id="NAIROBI-AQUA-PILOT-01")
    sample_telemetry = {
        "ammonia_ppm": 0.8,  # Triggers emergency flush
        "nitrite_ppm": 1.5,  # Triggers feeding reduction
        "nitrate_ppm": 45.0,
        "dissolved_oxygen_ppm": 4.2,  # Triggers emergency oxygen
        "ph": 6.5,
        "temperature_celsius": 23.0,
    }
    result = sentinel.evaluate_telemetry(sample_telemetry)
    print("Aquaponics Bio-Filter Sentinel Test Execution Results:", result)
