"""
Nairobi Commercial Cold Room & Blast Freezer Cryogenic Sentinel
Author: Cortana Autonomous Evolutionary Architect
Operator: Michael Obiero (Nairobi, Kenya)
"""

import time
import math
import random
import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] [ColdRoomSentinel]: %(message)s')
logger = logging.getLogger('ColdRoomSentinel')

@dataclass
class ColdRoomMetrics:
    room_id: str
    temperature_c: float
    humidity_pct: float
    evaporator_pressure_bar: float
    compressor_current_amps: float
    door_open_duration_sec: float
    power_phase_stable: bool
    timestamp: float = field(default_factory=time.time)

class CommercialColdRoomSentinel:
    """
    Monitors industrial cold rooms and blast freezers in Nairobi, reacting to
    power anomalies, thermal creep, and refrigerant pressure spikes.
    """
    def __init__(self, room_id: str, target_temp_c: float = -18.0, max_temp_c: float = -12.0):
        self.room_id = room_id
        self.target_temp_c = target_temp_c
        self.max_temp_c = max_temp_c
        self.history: List[ColdRoomMetrics] = []
        self.defrost_mode = False
        self.alarm_triggered = False

    def ingest_telemetry(self, metrics: ColdRoomMetrics) -> Dict[str, Any]:
        self.history.append(metrics)
        if len(self.history) > 1000:
            self.history.pop(0)
        return self._evaluate_status(metrics)

    def _evaluate_status(self, m: ColdRoomMetrics) -> Dict[str, Any]:
        actions = []
        status = "OPTIMAL"

        # Check power stability
        if not m.power_phase_stable:
            status = "CRITICAL_POWER_FAULT"
            actions.append("INITIATE_BACKUP_GENERATOR_TRANSFER")
            self.alarm_triggered = True

        # Check thermal breach
        elif m.temperature_c > self.max_temp_c:
            status = "THERMAL_CREEP_WARNING"
            actions.append("BOOST_COMPRESSOR_DUTY_CYCLE")
            if m.temperature_c > (self.max_temp_c + 5.0):
                status = "CRITICAL_DEFROST_OR_STALL"
                actions.append("DISPATCH_REFRIGERATION_TECH_KENYA")
                self.alarm_triggered = True

        # Check evaporator pressure anomaly
        if m.evaporator_pressure_bar < 1.0 or m.evaporator_pressure_bar > 6.0:
            actions.append("VALVE_PRESSURE_MODULATION_TRIGGERED")

        # Check prolonged door open
        if m.door_open_duration_sec > 120.0:
            actions.append("SOUND_LOCAL_BUZZER_DOOR_AJAR")

        return {
            "room_id": self.room_id,
            "status": status,
            "current_temp": m.temperature_c,
            "actions_taken": actions,
            "alarm_state": self.alarm_triggered,
            "timestamp": m.timestamp
        }

if __name__ == "__main__":
    sentinel = CommercialColdRoomSentinel(room_id="NRB-COLD-04")
    test_metrics = ColdRoomMetrics(
        room_id="NRB-COLD-04",
        temperature_c=-10.5,
        humidity_pct=85.0,
        evaporator_pressure_bar=2.4,
        compressor_current_amps=42.5,
        door_open_duration_sec=30.0,
        power_phase_stable=True
    )
    result = sentinel.ingest_telemetry(test_metrics)
    logger.info(f"Cold Room Diagnostics Result: {result}")
