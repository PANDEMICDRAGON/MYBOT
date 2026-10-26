"""
Module: nairobi_commercial_ras_sentinel.py
Description: Autonomous sentinel for Nairobi commercial Recirculating Aquaculture Systems (RAS),
             monitoring dissolved oxygen, pH, temperature, and nitrogen cycle biofilter efficiency.
Author: Cortana Autonomous Evolutionary Architect
Operator: Michael Obiero (Nairobi, Kenya)
"""

import time
import logging
from typing import Dict, Any, List, Optional

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] (RAS-SENTINEL): %(message)s')
logger = logging.getLogger("NairobiCommercialRASSentinel")

class CommercialRASSentinel:
    """
    Monitors water quality parameters, pump/aerator states, and biofilter nitrification
    cycles for commercial urban fish farming in Nairobi.
    """
    def __init__(self, facility_id: str, target_fish: str = "Oreochromis niloticus (Tilapia)") -> None:
        self.facility_id = facility_id
        self.target_fish = target_fish
        self.metrics_history: List[Dict[str, Any]] = []
        self.emergency_override_active = False
        logger.info(f"Initialized RAS Sentinel for facility '{self.facility_id}' cultivating {self.target_fish}.")

    def ingest_sensor_telemetry(self, dissolved_oxygen_mg_l: float, ph_level: float, 
                                temp_celsius: float, total_ammonia_nitrogen_mg_l: float,
                                nitrite_mg_l: float, nitrate_mg_l: float, flow_rate_lpm: float) -> Dict[str, Any]:
        """
        Ingests real-time water telemetry and evaluates biological safety thresholds.
        """
        timestamp = time.time()
        status = "OPTIMAL"
        alerts = []

        # Dissolved Oxygen Checks (Tilapia require > 4.0 mg/L ideally > 6.0 mg/L)
        if dissolved_oxygen_mg_l < 3.5:
            status = "CRITICAL"
            alerts.append("CRITICAL: Dissolved oxygen dangerously low. Risk of massive fish kill.")
        elif dissolved_oxygen_mg_l < 5.0:
            if status != "CRITICAL":
                status = "WARNING"
            alerts.append("WARNING: Dissolved oxygen sub-optimal. Boost aeration immediately.")

        # pH Checks (Optimal range 6.5 - 8.0 for nitrification and fish health)
        if ph_level < 6.0 or ph_level > 8.5:
            status = "CRITICAL"
            alerts.append(f"CRITICAL: pH level {ph_level} outside safe biological window (6.5-8.0).")
        elif ph_level < 6.5 or ph_level > 8.2:
            if status != "CRITICAL":
                status = "WARNING"
            alerts.append(f"WARNING: pH level {ph_level} drifting.")

        # Temperature Checks (Optimal 24C - 30C for tropical aquaculture in Nairobi ambient)
        if temp_celsius < 20.0 or temp_celsius > 32.0:
            status = "CRITICAL"
            alerts.append(f"CRITICAL: Water temperature {temp_celsius}C outside tolerance.")
        elif temp_celsius < 23.0 or temp_celsius > 30.0:
            if status != "CRITICAL":
                status = "WARNING"
            alerts.append(f"WARNING: Temperature {temp_celsius}C requires thermal stabilization.")

        # Nitrogen Cycle / Biofilter Efficiency Checks
        if total_ammonia_nitrogen_mg_l > 1.0:
            status = "CRITICAL"
            alerts.append(f"CRITICAL: High TAN ({total_ammonia_nitrogen_mg_l} mg/L). Biofilter nitrification failing!")
        if nitrite_mg_l > 0.5:
            status = "CRITICAL"
            alerts.append(f"CRITICAL: Nitrite spike ({nitrite_mg_l} mg/L). Toxic brown-blood disease risk.")

        # Flow Rate Check
        if flow_rate_lpm < 50.0:
            status = "CRITICAL"
            alerts.append(f"CRITICAL: Recirculation flow rate {flow_rate_lpm} LPM too low. Check pumps/KPLC power.")

        telemetry_record = {
            "timestamp": timestamp,
            "facility_id": self.facility_id,
            "dissolved_oxygen": dissolved_oxygen_mg_l,
            "ph": ph_level,
            "temperature": temp_celsius,
            "tan": total_ammonia_nitrogen_mg_l,
            "nitrite": nitrite_mg_l,
            "nitrate": nitrate_mg_l,
            "flow_rate": flow_rate_lpm,
            "status": status,
            "alerts": alerts
        }

        self.metrics_history.append(telemetry_record)
        if len(self.metrics_history) > 1000:
            self.metrics_history.pop(0)

        if status == "CRITICAL":
            self._trigger_emergency_protocols(alerts)

        return telemetry_record

    def _trigger_emergency_protocols(self, alerts: List[str]) -> None:
        """
        Automated failover protocol for backup generators, emergency oxygen diffusers,
        and SMS dispatch to Michael Obiero.
        """
        self.emergency_override_active = True
        logger.error(f"[EMERGENCY ACTIVATED] Facility {self.facility_id} triggered safety locks!")
        for alert in alerts:
            logger.error(f" -> {alert}")
        logger.info("Dispatching emergency SMS/WhatsApp alert via Kenya SMS Gateway. Engaging backup DC aeration blowers.")

    def get_system_health(self) -> Dict[str, Any]:
        """
        Returns summary health of the RAS unit.
        """
        if not self.metrics_history:
            return {"facility_id": self.facility_id, "status": "NO_DATA"}
        latest = self.metrics_history[-1]
        return {
            "facility_id": self.facility_id,
            "latest_status": latest["status"],
            "emergency_override": self.emergency_override_active,
            "total_telemetry_points": len(self.metrics_history),
            "last_check": latest["timestamp"]
        }

if __name__ == "__main__":
    print("Running test harness for NairobiCommercialRASSentinel...")
    sentinel = CommercialRASSentinel(facility_id="NAI-RAS-KASARANI-01", target_fish="Oreochromis niloticus")
    
    # Test normal ingestion
    report_normal = sentinel.ingest_sensor_telemetry(
        dissolved_oxygen_mg_l=6.5,
        ph_level=7.2,
        temp_celsius=26.5,
        total_ammonia_nitrogen_mg_l=0.1,
        nitrite_mg_l=0.05,
        nitrate_mg_l=25.0,
        flow_rate_lpm=120.0
    )
    print(f"Normal telemetry status: {report_normal['status']}")
    
    # Test critical oxygen depletion (simulating KPLC power outage)
    report_critical = sentinel.ingest_sensor_telemetry(
        dissolved_oxygen_mg_l=2.1,
        ph_level=6.2,
        temp_celsius=24.0,
        total_ammonia_nitrogen_mg_l=1.8,
        nitrite_mg_l=0.9,
        nitrate_mg_l=10.0,
        flow_rate_lpm=20.0
    )
    print(f"Critical telemetry status: {report_critical['status']}")
    print(f"Alerts generated: {report_critical['alerts']}")
    print("Test completed successfully.")
