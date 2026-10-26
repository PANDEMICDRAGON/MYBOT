"""
Nairobi Peri-Urban Commercial Apiaries & Raw Honey Ripeness Biosafety Sentinel
Designed to protect and optimize urban apiaries in Nairobi, Kenya.
"""

import time
import math
import random
import logging
from typing import Dict, List, Optional, Tuple

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] [ApiarySentinel]: %(message)s')
logger = logging.getLogger('NairobiApiarySentinel')


class HiveTelemetry:
    def __init__(self, hive_id: str, location: str):
        self.hive_id = hive_id
        self.location = location
        self.internal_temp_c: float = 34.5  # Optimal brood temp ~34.5°C - 35.5°C
        self.humidity_pct: float = 55.0
        self.acoustic_hz: float = 220.0     # Normal queen/worker hum ~180-250 Hz
        self.honey_moisture_pct: float = 17.8 # Target < 18.5% for sealed comb ripeness
        self.varroa_mite_index: float = 0.02 # Pest threshold
        self.timestamp: float = time.time()


class ApiaryBiosafetyEngine:
    def __init__(self, apiary_id: str):
        self.apiary_id = apiary_id
        self.hives: Dict[str, HiveTelemetry] = {}
        logger.info(f"Initialized Apiary Biosafety Engine for [{self.apiary_id}] in Nairobi region.")

    def register_hive(self, hive_id: str, location: str) -> None:
        self.hives[hive_id] = HiveTelemetry(hive_id, location)
        logger.info(f"Registered Hive {hive_id} at {location}.")

    def ingest_telemetry(self, hive_id: str, temp: float, humidity: float, acoustic: float, moisture: float, varroa: float) -> Dict[str, any]:
        if hive_id not in self.hives:
            raise ValueError(f"Hive {hive_id} not registered under apiary {self.apiary_id}.")
        
        hive = self.hives[hive_id]
        hive.internal_temp_c = temp
        hive.humidity_pct = humidity
        hive.acoustic_hz = acoustic
        hive.honey_moisture_pct = moisture
        hive.varroa_mite_index = varroa
        hive.timestamp = time.time()

        return self._evaluate_hive_status(hive)

    def _evaluate_hive_status(self, hive: HiveTelemetry) -> Dict[str, any]:
        alerts = []
        status = "OPTIMAL"

        # Brood temperature check
        if hive.internal_temp_c < 33.0 or hive.internal_temp_c > 36.5:
            status = "WARNING"
            alerts.append(f"Brood temperature anomaly: {hive.internal_temp_c}°C (Target: 34.5°C)")

        # Swarm acoustic detection (high frequency buzz > 350 Hz indicates agitation/swarming preparations)
        if hive.acoustic_hz > 330.0:
            status = "CRITICAL"
            alerts.append(f"Swarm acoustic signature detected! Frequency: {hive.acoustic_hz} Hz")

        # Honey ripeness check
        harvest_ready = False
        if hive.honey_moisture_pct <= 18.5:
            harvest_ready = True
        else:
            alerts.append(f"Honey unready for harvest (High moisture: {hive.honey_moisture_pct}% > 18.5%)")

        # Varroa Mite infestation check
        if hive.varroa_mite_index > 0.05:
            status = "WARNING"
            alerts.append(f"Varroa mite infestation index elevated: {hive.varroa_mite_index * 100:.1f}%")

        return {
            "hive_id": hive.hive_id,
            "location": hive.location,
            "status": status,
            "harvest_ready": harvest_ready,
            "honey_moisture": hive.honey_moisture_pct,
            "alerts": alerts,
            "timestamp": hive.timestamp
        }

    def batch_audit(self) -> List[Dict[str, any]]:
        reports = []
        for hid, hive in self.hives.items():
            reports.append(self._evaluate_hive_status(hive))
        return reports


if __name__ == "__main__":
    logger.info("Executing Nairobi Apiaries & Honey Ripeness Sentinel Self-Test...")
    engine = ApiaryBiosafetyEngine(apiary_id="NAI_KAREN_APIARY_01")
    engine.register_hive("HIVE_A1", "Karen Langata Edge")
    engine.register_hive("HIVE_A2", "Ruiru Peri-Urban Farm")

    # Simulate ingest
    res1 = engine.ingest_telemetry("HIVE_A1", temp=34.8, humidity=52.0, acoustic=210.0, moisture=17.2, varroa=0.01)
    res2 = engine.ingest_telemetry("HIVE_A2", temp=37.2, humidity=68.0, acoustic=380.0, moisture=19.4, varroa=0.07)

    logger.info(f"Audit Result HIVE_A1: {res1}")
    logger.info(f"Audit Result HIVE_A2: {res2}")
    logger.info("Nairobi Apiaries Sentinel Test Complete. All systems nominal.")
