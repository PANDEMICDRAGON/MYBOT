"""Nairobi Commercial Cold Room Defrost & Thermal Excursion Sentinel. Ensures cold room integrity, monitors evaporator coil temperatures, detects defrost failures, and safeguards perishable inventory in Nairobi, Kenya."""

import logging
import time
from typing import Dict, Any, List, Optional

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("ColdRoomDefrostSentinel")

class ColdRoomDefrostSentinel:
    """Monitors cold room temperatures, evaporator icing, and defrost cycles."""
    
    def __init__(self, room_id: str, target_temp_c: float = 4.0, max_defrost_duration_min: int = 45):
        self.room_id = room_id
        self.target_temp_c = target_temp_c
        self.max_defrost_duration_min = max_defrost_duration_min
        self.in_defrost = False
        self.defrost_start_time: Optional[float] = None
        self.temperature_history: List[float] = []
        self.coil_temp_history: List[float] = []
        logger.info(f"Initialized ColdRoomDefrostSentinel for room {room_id} (Target: {target_temp_c}°C)")

    def record_telemetry(self, room_temp: float, coil_temp: float, door_open: bool) -> Dict[str, Any]:
        """Ingests telemetry data and analyzes thermal stability and defrost cycles."""
        self.temperature_history.append(room_temp)
        self.coil_temp_history.append(coil_temp)
        
        # Keep rolling window of last 100 entries
        if len(self.temperature_history) > 100:
            self.temperature_history.pop(0)
        if len(self.coil_temp_history) > 100:
            self.coil_temp_history.pop(0)
            
        alerts = []
        status = "NOMINAL"
        
        # Thermal excursion check
        if room_temp > (self.target_temp_c + 6.0) and not self.in_defrost:
            status = "THERMAL_EXCURSION_CRITICAL"
            alerts.append(f"CRITICAL: Room temperature {room_temp}°C exceeds safe threshold!")
            
        # Evaporator icing / defrost detection
        if coil_temp <= -15.0 and not self.in_defrost:
            # Potential heavy frost accumulation, recommend defrost
            alerts.append("ADVISORY: Heavy frost accumulation detected on evaporator coils. Initiate defrost.")
            
        # Defrost cycle monitoring
        if coil_temp > 10.0 and not self.in_defrost:
            self.in_defrost = True
            self.defrost_start_time = time.time()
            logger.info(f"Defrost cycle initiated in room {self.room_id}.")
            
        if self.in_defrost:
            elapsed_min = (time.time() - (self.defrost_start_time or time.time())) / 60.0
            if elapsed_min > self.max_defrost_duration_min:
                status = "DEFROST_TIMEOUT_WARNING"
                alerts.append(f"WARNING: Defrost cycle exceeded maximum duration ({elapsed_min:.1f} mins)!")
            if coil_temp < 0.0:
                self.in_defrost = False
                self.defrost_start_time = None
                logger.info(f"Defrost cycle completed successfully in room {self.room_id}.")
                
        return {
            "room_id": self.room_id,
            "status": status,
            "room_temp": room_temp,
            "coil_temp": coil_temp,
            "in_defrost": self.in_defrost,
            "door_open": door_open,
            "alerts": alerts
        }

if __name__ == "__main__":
    sentinel = ColdRoomDefrostSentinel(room_id="NRB-COLD-01", target_temp_c=2.0)
    # Test normal operation
    res1 = sentinel.record_telemetry(room_temp=2.5, coil_temp=-5.0, door_open=False)
    print("Test 1:", res1)
    # Test defrost trigger
    res2 = sentinel.record_telemetry(room_temp=8.0, coil_temp=12.0, door_open=False)
    print(
    "Test 2:", res2)
