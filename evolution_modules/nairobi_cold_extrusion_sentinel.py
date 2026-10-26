import logging
import time
import statistics
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] [ColdExtrusionSentinel]: %(message)s')
logger = logging.getLogger('NairobiColdExtrusionSentinel')

@dataclass
class ExtrusionMetrics:
    timestamp: float
    machine_id: str
    zone_temperatures: List[float]
    die_pressure_bar: float
    motor_torque_nm: float
    screw_rpm: float
    cooling_flow_lpm: float
    anomaly_flag: bool = False

class ColdExtrusionSentinel:
    """
    Monitors industrial polymer cold extrusion machinery in Nairobi industrial sectors,
    detecting pressure spikes, thermal runaway, and mechanical binding before structural failure.
    """
    def __init__(self, machine_id: str, max_pressure_bar: float = 350.0, max_torque_nm: float = 1200.0):
        self.machine_id = machine_id
        self.max_pressure_bar = max_pressure_bar
        self.max_torque_nm = max_torque_nm
        self.telemetry_history: List[ExtrusionMetrics] = []
        self.active_alerts: List[str] = []
        logger.info(f"Initialized ColdExtrusionSentinel for machine: {machine_id}")

    def ingest_telemetry(self, zone_temps: List[float], die_pressure: float, motor_torque: float, rpm: float, cooling_flow: float) -> ExtrusionMetrics:
        timestamp = time.time()
        anomaly = False
        self.active_alerts.clear()

        if die_pressure > self.max_pressure_bar:
            anomaly = True
            alert = f"CRITICAL: Die pressure {die_pressure} bar exceeds safe threshold ({self.max_pressure_bar} bar)!"
            self.active_alerts.append(alert)
            logger.error(alert)

        if motor_torque > self.max_torque_nm:
            anomaly = True
            alert = f"CRITICAL: Motor torque {motor_torque} Nm exceeds safety limit ({self.max_torque_nm} Nm)!"
            self.active_alerts.append(alert)
            logger.error(alert)

        if cooling_flow < 15.0:
            anomaly = True
            alert = f"WARNING: Cooling water flow rate low ({cooling_flow} LPM). Thermal jacket risk!"
            self.active_alerts.append(alert)
            logger.warning(alert)

        metrics = ExtrusionMetrics(
            timestamp=timestamp,
            machine_id=self.machine_id,
            zone_temperatures=zone_temps,
            die_pressure_bar=die_pressure,
            motor_torque_nm=motor_torque,
            screw_rpm=rpm,
            cooling_flow_lpm=cooling_flow,
            anomaly_flag=anomaly
        )

        self.telemetry_history.append(metrics)
        if len(self.telemetry_history) > 1000:
            self.telemetry_history.pop(0)

        return metrics

    def analyze_stability(self) -> Dict[str, Any]:
        if not self.telemetry_history:
            return {"status": "NO_DATA"}

        pressures = [m.die_pressure_bar for m in self.telemetry_history]
        torques = [m.motor_torque_nm for m in self.telemetry_history]

        return {
            "machine_id": self.machine_id,
            "samples_analyzed": len(self.telemetry_history),
            "mean_pressure_bar": round(statistics.mean(pressures), 2),
            "max_pressure_observed": round(max(pressures), 2),
            "mean_torque_nm": round(statistics.mean(torques), 2),
            "max_torque_observed": round(max(torques), 2),
            "active_alerts_count": len(self.active_alerts),
            "system_healthy": len(self.active_alerts) == 0
        }

if __name__ == "__main__":
    sentinel = ColdExtrusionSentinel(machine_id="EXTRUDER_IND_04_NAIROBI")
    # Simulate normal and anomalous runs
    m1 = sentinel.ingest_telemetry([185.5, 190.2, 188.4], 210.5, 650.0, 45.0, 25.0)
    m2 = sentinel.ingest_telemetry([220.0, 235.1, 229.0], 365.0, 1250.0, 30.0, 10.0)
    
    report = sentinel.analyze_stability()
    print("Cold Extrusion Diagnostic Report:", report)
