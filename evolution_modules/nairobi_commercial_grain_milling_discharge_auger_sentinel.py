import time
import logging
from typing import Dict, Any, List

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')
logger = logging.getLogger("DischargeAugerSentinel")

class DischargeAugerSentinel:
    """
    Monitors commercial grain mill discharge auger telemetry (motor current, RPM, and vibration)
    to detect incipient jams, blockages, or mechanical overloads before failure occurs.
    """
    def __init__(self, auger_id: str, rated_current_amps: float = 18.5, max_rpm: float = 120.0):
        self.auger_id = auger_id
        self.rated_current_amps = rated_current_amps
        self.max_rpm = max_rpm
        self.status = "NORMAL"
        self.telemetry_history: List[Dict[str, Any]] = []

    def analyze_telemetry(self, current_amps: float, rpm: float, vibration_mm_s: float) -> Dict[str, Any]:
        """
        Analyzes live sensor feeds from the discharge auger motor and drive assembly.
        """
        timestamp = time.time()
        current_load_pct = (current_amps / self.rated_current_amps) * 100.0
        rpm_drop_pct = max(0.0, ((self.max_rpm - rpm) / self.max_rpm) * 100.0)

        diagnostic = {
            "auger_id": self.auger_id,
            "timestamp": timestamp,
            "current_load_pct": round(current_load_pct, 2),
            "rpm_drop_pct": round(rpm_drop_pct, 2),
            "vibration_mm_s": round(vibration_mm_s, 2),
            "action_required": "NONE"
        }

        if current_load_pct > 140.0 or rpm_drop_pct > 35.0:
            self.status = "CRITICAL_JAM"
            diagnostic["action_required"] = "EMERGENCY_STOP_AND_REVERSE"
            logger.error(f"[{self.auger_id}] CRITICAL JAM DETECTED! Load: {current_load_pct}%, RPM Drop: {rpm_drop_pct}%")
        elif current_load_pct > 115.0 or rpm_drop_pct > 15.0 or vibration_mm_s > 7.5:
            self.status = "WARNING_OVERLOAD"
            diagnostic["action_required"] = "REDUCE_INFEED_RATE"
            logger.warning(f"[{self.auger_id}] Warning: High torque or vibration. Load: {current_load_pct}%, Vib: {vibration_mm_s} mm/s")
        else:
            self.status = "NORMAL"
            logger.info(f"[{self.auger_id}] Telemetry nominal. Load: {current_load_pct}%, RPM: {rpm}")

        self.telemetry_history.append(diagnostic)
        if len(self.telemetry_history) > 100:
            self.telemetry_history.pop(0)

        return diagnostic

if __name__ == "__main__":
    sentinel = DischargeAugerSentinel(auger_id="AUGER_LINE_04")
    # Test nominal condition
    print(sentinel.analyze_telemetry(current_amps=14.2, rpm=118.0, vibration_mm_s=2.1))
    # Test overload condition
    print(sentinel.analyze_telemetry(current_amps=22.0, rpm=95.0, vibration_mm_s=8.5))
    # Test critical jam condition
    print(sentinel.analyze_telemetry(current_amps=27.5, rpm=45.0, vibration_mm_s=14.2))
