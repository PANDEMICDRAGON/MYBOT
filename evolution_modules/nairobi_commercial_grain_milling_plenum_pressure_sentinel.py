import time
import logging
from typing import Dict, Any, List, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("PlenumPressureSentinel")

class PlenumPressureSentinel:
    """
    Monitors negative and positive pneumatic pressures in milling plenums, ducting,
    and cyclone separators across Nairobi industrial grain facilities.
    """
    def __init__(self, target_static_pressure_pa: float = -1200.0, tolerance_pa: float = 150.0):
        self.target_static_pressure_pa = target_static_pressure_pa
        self.tolerance_pa = tolerance_pa
        self.anomaly_log: List[Dict[str, Any]] = []

    def evaluate_pressure(self, zone_id: str, current_pressure_pa: float, airflow_velocity_mps: float) -> Dict[str, Any]:
        """
        Evaluates real-time static pressure and air velocity against safe operating parameters.
        """
        deviation = current_pressure_pa - self.target_static_pressure_pa
        status = "OPTIMAL"
        action_required = False

        if abs(deviation) > self.tolerance_pa:
            status = "WARNING_PRESSURE_DRIFT"
            action_required = True
            if deviation > 0:
                status = "CRITICAL_POSITIVE_PRESSURE_RISK"

        if airflow_velocity_mps < 18.0:
            status = "CRITICAL_LOW_AIR_VELOCITY"
            action_required = True

        record = {
            "timestamp": time.time(),
            "zone_id": zone_id,
            "pressure_pa": current_pressure_pa,
            "velocity_mps": airflow_velocity_mps,
            "status": status,
            "action_required": action_required
        }

        if action_required:
            self.anomaly_log.append(record)
            logger.warning(f"[PLENUM SENTINEL] Zone {zone_id} alert: {status} (Pressure: {current_pressure_pa}Pa, Vel: {airflow_velocity_mps}m/s)")
        else:
            logger.info(f"[PLENUM SENTINEL] Zone {zone_id} stable. Pressure: {current_pressure_pa}Pa.")

        return record

    def get_system_health(self) -> Dict[str, Any]:
        return {
            "target_pressure": self.target_static_pressure_pa,
            "total_anomalies_recorded": len(self.anomaly_log),
            "operational_status": "SECURE" if len(self.anomaly_log) < 5 else "ATTENTION_REQUIRED"
        }

if __name__ == "__main__":
    sentinel = PlenumPressureSentinel(target_static_pressure_pa=-1250.0)
    res1 = sentinel.evaluate_pressure("PLENUM_A_ASPIRATION", -1260.0, 22.5)
    res2 = sentinel.evaluate_pressure("PLENUM_B_CYCLONE", -950.0, 16.0)
    print("Health Check:", sentinel.get_system_health())
