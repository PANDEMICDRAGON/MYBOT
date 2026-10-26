import logging
import time
from typing import Dict, Any, List, Optional

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')
logger = logging.getLogger("MushroomSpawnSentinel")

class MushroomSpawnSentinel:
    """
    Monitors and governs commercial mushroom spawn incubation units, autoclave pressure sterilization,
    substrate moisture, and HEPA laminar flow integrity for urban agricultural facilities in Nairobi.
    """
    def __init__(self, facility_id: str, max_temp_c: float = 121.5, min_humidity_pct: float = 85.0):
        self.facility_id = facility_id
        self.max_temp_c = max_temp_c
        self.min_humidity_pct = min_humidity_pct
        self.telemetry_history: List[Dict[str, Any]] = []
        logger.info(f"Initialized MushroomSpawnSentinel for facility: {self.facility_id}")

    def ingest_telemetry(self, batch_id: str, chamber_temp_c: float, pressure_psi: float, humidity_pct: float, hepa_airflow_mps: float) -> Dict[str, Any]:
        """
        Ingests real-time sensor streams from incubation and sterilization chambers.
        """
        timestamp = time.time()
        status = "OPTIMAL"
        alerts = []

        # Autoclave sterilization check
        if chamber_temp_c > self.max_temp_c:
            alerts.append(f"CRITICAL: Sterilization chamber overheating ({chamber_temp_c}°C > {self.max_temp_c}°C)")
            status = "HAZARD"

        # Incubation humidity check
        if humidity_pct < self.min_humidity_pct:
            alerts.append(f"WARNING: Incubation humidity low ({humidity_pct}% < {self.min_humidity_pct}%)")
            if status != "HAZARD":
                status = "DEGRADED"

        # Laminar flow HEPA check (ideal > 0.45 m/s)
        if hepa_airflow_mps < 0.40:
            alerts.append(f"CRITICAL: HEPA laminar airflow compromised ({hepa_airflow_mps} m/s)")
            status = "HAZARD"

        record = {
            "timestamp": timestamp,
            "batch_id": batch_id,
            "chamber_temp_c": chamber_temp_c,
            "pressure_psi": pressure_psi,
            "humidity_pct": humidity_pct,
            "hepa_airflow_mps": hepa_airflow_mps,
            "status": status,
            "alerts": alerts
        }

        self.telemetry_history.append(record)
        logger.info(f"Processed batch {batch_id}: Status -> {status}, Alerts -> {len(alerts)}")
        return record

    def get_facility_health(self) -> Dict[str, Any]:
        """Summarizes overall facility biological safety index."""
        if not self.telemetry_history:
            return {"facility_id": self.facility_id, "health_index": 1.0, "active_batches": 0}
        
        hazard_count = sum(1 for r in self.telemetry_history if r["status"] == "HAZARD")
        total_records = len(self.telemetry_history)
        health_index = max(0.0, 1.0 - (hazard_count / total_records))

        return {
            "facility_id": self.facility_id,
            "health_index": round(health_index, 4),
            "total_telemetry_points": total_records,
            "recent_status": self.telemetry_history[-1]["status"]
        }

if __name__ == "__main__":
    sentinel = MushroomSpawnSentinel(facility_id="NAIROBI-MUSHROOM-HUB-01")
    res = sentinel.ingest_telemetry(
        batch_id="OYSTER-2026-X9",
        chamber_temp_c=121.0,
        pressure_psi=15.2,
        humidity_pct=88.5,
        hepa_airflow_mps=0.48
    )
    print("Test Ingestion Result:", res)
    print("Facility Health Summary:", sentinel.get_facility_health())
