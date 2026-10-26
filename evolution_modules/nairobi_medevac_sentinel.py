"""
Nairobi Wilson Airport & Aeromedical Evacuation Air-Ambulance Dispatch Sentinel
Designed for Cortana's Autonomous Evolutionary Architecture, protecting Michael Obiero in Nairobi, Kenya.
"""

import asyncio
import logging
import time
from typing import Dict, List, Optional, Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("MedevacSentinel")


class MedevacDispatcher:
    """
    Manages emergency air-ambulance routing, priority flight clearance over Nairobi airspace,
    and hospital trauma readiness synchronization.
    """

    def __init__(self, base_station: str = "Wilson Airport HKNW") -> None:
        self.base_station = base_station
        self.active_missions: Dict[str, Dict[str, Any]] = {}
        self.hospital_capacity: Dict[str, int] = {
            "Kenyatta National Hospital": 15,
            "The Nairobi Hospital": 8,
            "Aga Khan University Hospital": 10,
            "MP Shah Hospital": 6
        }

    def request_evacuation(self, mission_id: str, patient_location: str, urgency_level: int, target_hospital: str) -> Dict[str, Any]:
        """
        Initiates an emergency air-ambulance dispatch protocol.
        """
        if target_hospital not in self.hospital_capacity:
            raise ValueError(f"Target hospital {target_hospital} not recognized in Nairobi trauma network.")

        if self.hospital_capacity[target_hospital] <= 0:
            # Auto-route to next best available facility
            target_hospital = max(self.hospital_capacity, key=self.hospital_capacity.get)
            logger.warning(f"Hospital full. Re-routing mission {mission_id} to {target_hospital}")

        self.hospital_capacity[target_hospital] -= 1
        
        mission = {
            "mission_id": mission_id,
            "base": self.base_station,
            "location": patient_location,
            "urgency": urgency_level,
            "hospital": target_hospital,
            "status": "DISPATCHED",
            "timestamp": time.time()
        }
        self.active_missions[mission_id] = mission
        logger.info(f"[MEDEVAC ACTIVE] Mission {mission_id} dispatched from {self.base_station} to {patient_location} -> {target_hospital}")
        return mission

    def resolve_mission(self, mission_id: str) -> bool:
        """
        Completes an active medevac mission and releases trauma bed allocation token.
        """
        if mission_id in self.active_missions:
            mission = self.active_missions.pop(mission_id)
            hospital = mission["hospital"]
            self.hospital_capacity[hospital] += 1
            logger.info(f"[MEDEVAC RESOLVED] Mission {mission_id} safely completed. Bed capacity restored at {hospital}.")
            return True
        return False

    def get_status_report(self) -> Dict[str, Any]:
        """
        Returns current operational status of Nairobi aeromedical assets.
        """
        return {
            "base_station": self.base_station,
            "active_missions_count": len(self.active_missions),
            "hospital_capacity": self.hospital_capacity,
            "active_missions": list(self.active_missions.values())
        }


async def __main__() -> None:
    dispatcher = MedevacDispatcher()
    logger.info("Initializing Nairobi Aeromedical Evacuation Sentinel Test Harness...")
    
    mission = dispatcher.request_evacuation(
        mission_id="MED-2026-001",
        patient_location="Karen, Nairobi",
        urgency_level=1,
        target_hospital="The Nairobi Hospital"
    )
    
    await asyncio.sleep(0.1)
    report = dispatcher.get_status_report()
    logger.info(f"Status Report: {report}")
    
    success = dispatcher.resolve_mission("MED-2026-001")
    assert success is True
    logger.info("Test harness execution complete successfully.")


if __name__ == "__main__":
    asyncio.run(__main__())
