import logging
import time
from typing import Dict, List, Optional, Any

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] [IcePlantSentinel]: %(message)s')
logger = logging.getLogger('NairobiCommercialIcePlantSentinel')

class IcePlantSentinel:
    """
    Monitors commercial ice manufacturing parameters in Nairobi Industrial Area, tracking
    ammonia compressor pressures, brine tank temperatures, ice harvesting cycle duration,
    and KPLC power phase stability.
    """
    def __init__(self, plant_id: str = "NBI-ICE-01") -> None:
        self.plant_id = plant_id
        self.compressor_status: str = "STANDBY"
        self.suction_pressure_bar: float = 2.1
        self.discharge_pressure_bar: float = 12.5
        self.brine_temp_c: float = -12.0
        self.harvest_cycle_count: int = 0
        self.alarm_state: bool = False
        self.logs: List[str] = []

    def update_metrics(self, suction: float, discharge: float, brine_temp: float, compressor_active: bool) -> Dict[str, Any]:
        """Ingests live telemetry from industrial refrigeration sensors."""
        self.suction_pressure_bar = suction
        self.discharge_pressure_bar = discharge
        self.brine_temp_c = brine_temp
        self.compressor_status = "RUNNING" if compressor_active else "STANDBY"
        
        # Safety threshold evaluations
        anomalies = []
        if self.discharge_pressure_bar > 16.0:
            anomalies.append("HIGH_DISCHARGE_PRESSURE_WARNING")
            self.alarm_state = True
        if self.suction_pressure_bar < 0.8:
            anomalies.append("LOW_SUCTION_PRESSURE_CAVITATION_RISK")
            self.alarm_state = True
        if self.brine_temp_c > -5.0 and self.compressor_status == "RUNNING":
            anomalies.append("BRINE_TEMP_ELEVATED_FREEZING_DELAY")
            
        if not anomalies:
            self.alarm_state = False
            
        report = {
            "plant_id": self.plant_id,
            "timestamp": time.time(),
            "status": self.compressor_status,
            "suction_bar": self.suction_pressure_bar,
            "discharge_bar": self.discharge_pressure_bar,
            "brine_temp_c": self.brine_temp_c,
            "alarm": self.alarm_state,
            "anomalies": anomalies
        }
        self.logs.append(str(report))
        logger.info(f"Ice Plant Telemetry Processed: {report}")
        return report

    def trigger_emergency_shutdown(self) -> Dict[str, str]:
        """Executes safe shutdown protocol in case of refrigerant leak or severe power surge."""
        self.compressor_status = "EMERGENCY_SHUTDOWN"
        self.alarm_state = True
        msg = f"CRITICAL: Plant {self.plant_id} emergency refrigerant isolation triggered for operator safety."
        logger.warning(msg)
        return {"status": "SUCCESS", "action": "SHUTDOWN", "message": msg}

if __name__ == "__main__":
    sentinel = IcePlantSentinel("NBI-INDUSTRIAL-ICE-04")
    metrics = sentinel.update_metrics(suction=1.9, discharge=14.2, brine_temp=-11.5, compressor_active=True)
    print("Test Metrics Output:", metrics)
    shutdown_res = sentinel.trigger_emergency_shutdown()
    print("Test Shutdown Output:", shutdown_res)
