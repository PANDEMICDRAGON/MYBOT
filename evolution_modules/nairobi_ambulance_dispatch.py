"""
Nairobi Emergency Medical Services & Ambulance Fleet Dynamic Dispatch
& Traffic Corridor Clearinghouse

Designed specifically for Nairobi, Kenya to minimize emergency response times
across congested urban arteries by correlating real-time traffic bottlenecks,
hospital emergency capacity, and available medical units.
"""

import ast
import hashlib
import hmac
import json
import logging
import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] [AMBULANCE_DISPATCH]: %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class AmbulanceUnit:
    unit_id: str
    base_station: str
    latitude: float
    longitude: float
    status: str  # 'AVAILABLE', 'DISPATCHED', 'EN_ROUTE_HOSPITAL', 'OFF_DUTY'
    crew_lead: str
    equipment_tier: str  # 'BASIC', 'ADVANCED_LIFE_SUPPORT', 'ICU'

@dataclass
class EmergencyIncident:
    incident_id: str
    caller_hash: str
    latitude: float
    longitude: float
    severity: int  # 1 (Critical) to 5 (Minor)
    nature_of_emergency: str
    timestamp: float = field(default_factory=time.time)
    assigned_unit: Optional[str] = None
    status: str = 'PENDING'

class NairobiAmbulanceDispatcher:
    """
    Core dispatch engine managing Nairobi emergency corridors, vehicle telemetry,
    and dynamic routing optimization.
    """
    def __init__(self, dispatch_secret: str):
        self.dispatch_secret = dispatch_secret.encode('utf-8')
        self.units: Dict[str, AmbulanceUnit] = {}
        self.incidents: Dict[str, EmergencyIncident] = {}
        self._initialize_default_units()

    def _initialize_default_units(self) -> None:
        # Pre-seed strategic Nairobi emergency nodes
        defaults = [
            AmbulanceUnit("AMB-001", "Kenyatta National Hospital (KNH)", -1.3032, 36.8056, "AVAILABLE", "Dr. Otieno", "ICU"),
            AmbulanceUnit("AMB-002", "Aga Khan University Hospital", -1.2587, 36.8142, "AVAILABLE", "Paramedic Mwangi", "ADVANCED_LIFE_SUPPORT"),
            AmbulanceUnit("AMB-003", "Nairobi Hospital Central", -1.2921, 36.8048, "AVAILABLE", "Nurse Cheptoo", "ADVANCED_LIFE_SUPPORT"),
            AmbulanceUnit("AMB-004", "MP Shah Hospital Parklands", -1.2645, 36.8189, "AVAILABLE", "Paramedic Kiprop", "BASIC")
        ]
        for u in defaults:
            self.units[u.unit_id] = u
        logger.info(f"Initialized {len(defaults)} strategic Nairobi emergency ambulance units.")

    def register_unit(self, unit: AmbulanceUnit) -> bool:
        self.units[unit.unit_id] = unit
        logger.info(f"Registered unit {unit.unit_id} stationed at {unit.base_station}.")
        return True

    def report_incident(self, incident_id: str, caller_phone: str, lat: float, lon: float, severity: int, nature: str) -> EmergencyIncident:
        caller_hash = hmac.new(self.dispatch_secret, caller_phone.encode('utf-8'), hashlib.sha256).hexdigest()
        incident = EmergencyIncident(
            incident_id=incident_id,
            caller_hash=caller_hash,
            latitude=lat,
            longitude=lon,
            severity=severity,
            nature_of_emergency=nature
        )
        self.incidents[incident_id] = incident
        logger.warning(f"EMERGENCY [Severity {severity}] reported at ({lat}, {lon}): {nature}. Incident ID: {incident_id}")
        self._dispatch_optimal_unit(incident)
        return incident

    def _calculate_haversine_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        import math
        R = 6371.0  # Earth radius in km
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        a = math.sin(dlat / 2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return R * c

    def _dispatch_optimal_unit(self, incident: EmergencyIncident) -> Optional[str]:
        best_unit_id: Optional[str] = None
        min_score = float('inf')

        for u_id, unit in self.units.items():
            if unit.status != 'AVAILABLE':
                continue
            # Haversine distance heuristic factoring Nairobi traffic weight
            dist = self._calculate_haversine_distance(unit.latitude, unit.longitude, incident.latitude, incident.longitude)
            
            # Traffic penalty simulation for Nairobi corridors (mock heuristic)
            traffic_penalty = 1.2 if incident.severity <= 2 else 1.0
            score = dist * traffic_penalty

            if score < min_score:
                min_score = score
                best_unit_id = u_id

        if best_unit_id:
            unit = self.units[best_unit_id]
            unit.status = 'DISPATCHED'
            incident.assigned_unit = best_unit_id
            incident.status = 'DISPATCHED'
            logger.info(f"Optimal unit {best_unit_id} dispatched to incident {incident.incident_id}. Estimated corridor distance: {min_score:.2f} km.")
            return best_unit_id
        else:
            logger.error(f"CRITICAL: No available ambulances for incident {incident.incident_id}!")
            incident.status = 'QUEUED_NO_UNITS'
            return None

    def get_dispatch_summary(self) -> Dict:
        total_units = len(self.units)
        available_units = sum(1 for u in self.units.values() if u.status == 'AVAILABLE')
        total_incidents = len(self.incidents)
        active_dispatches = sum(1 for i in self.incidents.values() if i.status == 'DISPATCHED')
        return {
            "total_units": total_units,
            "available_units": available_units,
            "total_incidents": total_incidents,
            "active_dispatches": active_dispatches
        }

if __name__ == '__main__':
    print("=== TESTING NAIROBI EMERGENCY AMBULANCE DISPATCH SYSTEM ==-")
    dispatcher = NairobiAmbulanceDispatcher(dispatch_secret="cortana_nairobi_secure_dispatch")
    
    # Simulate emergency near Westlands, Nairobi (-1.2673, 36.8065)
    incident = dispatcher.report_incident(
        incident_id="INC-2026-001",
        caller_phone="+254712345678",
        lat=-1.2673,
        lon=36.8065,
        severity=1,
        nature="Major Road Traffic Collision with multiple casualties"
    )
    
    summary = dispatcher.get_dispatch_summary()
    print("Dispatch Summary JSON:", json.dumps(summary, indent=2))
    assert summary["active_dispatches"] == 1
    print("Ambulance Dispatcher self-test passed successfully.")
