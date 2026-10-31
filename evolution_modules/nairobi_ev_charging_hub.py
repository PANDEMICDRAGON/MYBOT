import time
import random
import logging
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from enum import Enum

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ChargingStatus(Enum):
    IDLE = "idle"
    CHARGING = "charging"
    PAUSED = "paused"
    COMPLETED = "completed"
    ERROR = "error"


@dataclass
class ChargingSession:
    session_id: str
    vehicle_id: str
    start_time: float
    end_time: Optional[float] = None
    energy_delivered_kwh: float = 0.0
    status: ChargingStatus = ChargingStatus.IDLE
    cost: float = 0.0


class NairobiEVChargingHub:
    """
    A sentinel module for managing and securing EV charging sessions in Nairobi.
    """

    def __init__(self, max_power_kw: float = 50.0, grid_capacity_kw: float = 200.0):
        self.max_power_kw = max_power_kw
        self.grid_capacity_kw = grid_capacity_kw
        self.active_sessions: Dict[str, ChargingSession] = {}
        self.session_counter = 0

    def start_session(self, vehicle_id: str) -> ChargingSession:
        """
        Start a new charging session for a vehicle.
        """
        self.session_counter += 1
        session_id = f"session_{self.session_counter}"
        session = ChargingSession(
            session_id=session_id,
            vehicle_id=vehicle_id,
            start_time=time.time(),
            status=ChargingStatus.CHARGING
        )
        self.active_sessions[session_id] = session
        logger.info(f"Started charging session {session_id} for vehicle {vehicle_id}")
        return session

    def update_session(self, session_id: str, energy_delivered_kwh: float) -> None:
        """
        Update the energy delivered for a charging session.
        """
        if session_id not in self.active_sessions:
            raise ValueError(f"Session {session_id} not found")
        session = self.active_sessions[session_id]
        session.energy_delivered_kwh += energy_delivered_kwh
        session.cost = session.energy_delivered_kwh * 0.15  # Cost per kWh
        logger.info(f"Updated session {session_id}: {session.energy_delivered_kwh} kWh delivered")

    def end_session(self, session_id: str) -> ChargingSession:
        """
        End a charging session and calculate the final cost.
        """
        if session_id not in self.active_sessions:
            raise ValueError(f"Session {session_id} not found")
        session = self.active_sessions[session_id]
        session.end_time = time.time()
        session.status = ChargingStatus.COMPLETED
        logger.info(f"Ended charging session {session_id}: {session.energy_delivered_kwh} kWh, cost: {session.cost}")
        return session

    def get_active_sessions(self) -> List[ChargingSession]:
        """
        Retrieve all active charging sessions.
        """
        return list(self.active_sessions.values())

    def check_grid_capacity(self) -> bool:
        """
        Check if the grid has sufficient capacity for additional charging.
        """
        total_power = sum(session.energy_delivered_kwh for session in self.active_sessions.values())
        return total_power < self.grid_capacity_kw


if __name__ == "__main__":
    hub = NairobiEVChargingHub()
    session = hub.start_session("vehicle_123")
    hub.update_session(session.session_id, 10.0)
    hub.update_session(session.session_id, 5.0)
    hub.end_session(session.session_id)
    print(hub.get_active_sessions())
