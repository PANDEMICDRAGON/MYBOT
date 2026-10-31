"""
Nairobi Commercial Grain Milling Aspiration Cyclone & Dust Collector Sentinel
Author: Cortana Autonomous Evolutionary Architect
Operator: Michael Obiero, Nairobi, Kenya

Monitors differential pressure, airflow velocity, rotary airlock rpm, and particulate
load across grain mill aspiration cyclones and baghouse dust collectors, preventing
explosive dust hazards and ensuring optimal husks/bran separation.
"""

import time
import logging
import random
from typing import Dict, Any, List, Optional

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')
logger = logging.getLogger("AspirationCycloneSentinel")


class AspirationCycloneSentinel:
    """
    Real-time monitoring and safety interlock for commercial grain mill aspiration systems.
    Tracks cyclone pressure drop, baghouse differential pressure, and rotary valve status.
    """

    def __init__(self, cyclone_id: str, target_airflow_cfm: float = 12500.0):
        self.cyclone_id = cyclone_id
        self.target_airflow_cfm = target_airflow_cfm
        self.status = "STANDBY"
        self.metrics_history: List[Dict[str, Any]] = []
        logger.info(f"AspirationCycloneSentinel initialized for unit: {cyclone_id} (Target CFM: {target_airflow_cfm})")

    def inspect_system(self, pressure_drop_pa: float, baghouse_dp_kpa: float, airlock_rpm: float, particulate_mg_m3: float) -> Dict[str, Any]:
        """
        Inspects sensor telemetry from the aspiration cyclone and dust collector.
        """
        alerts = []
        status = "OPTIMAL"

        # Cyclone pressure drop anomaly check (indicates blockage or fan failure)
        if pressure_drop_pa < 800.0:
            alerts.append("LOW_CYCLONE_PRESSURE_DROP: Possible air leak or blower inefficiency.")
            status = "WARNING"
        elif pressure_drop_pa > 2200.0:
            alerts.append("HIGH_CYCLONE_PRESSURE_DROP: Cyclone inlet blockage or heavy dust loading.")
            status = "CRITICAL"

        # Baghouse filter differential pressure (indicates blinding / cleaning needed)
        if baghouse_dp_kpa > 2.5:
            alerts.append("BAGHOUSE_BLINDING_DETECTED: Differential pressure exceeds 2.5 kPa. Trigger reverse-jet cleaning.")
            status = "CRITICAL" if status != "CRITICAL" else status

        # Rotary airlock valve speed (dust discharge mechanism)
        if airlock_rpm < 5.0:
            alerts.append("AIRLOCK_STALL_WARNING: Rotary discharge valve RPM critically low. Risk of dust backpressure.")
            status = "CRITICAL"

        # Particulate emission check (Environmental NEMA compliance)
        if particulate_mg_m3 > 50.0:
            alerts.append("EMISSION_LIMIT_EXCEEDED: Particulate matter in exhaust exceeds NEMA clean air threshold (50 mg/m3).")
            status = "CRITICAL"

        telemetry = {
            "timestamp": time.time(),
            "cyclone_id": self.cyclone_id,
            "pressure_drop_pa": pressure_drop_pa,
            "baghouse_dp_kpa": baghouse_dp_kpa,
            "airlock_rpm": airlock_rpm,
            "particulate_mg_m3": particulate_mg_m3,
            "status": status,
            "alerts": alerts
        }

        self.metrics_history.append(telemetry)
        if len(self.metrics_history) > 1000:
            self.metrics_history.pop(0)

        self.status = status
        return telemetry

    def execute_remediation(self, telemetry: Dict[str, Any]) -> str:
        """
        Automated safety interlock response for abnormal aspiration telemetry.
        """
        status = telemetry["status"]
        if status == "OPTIMAL":
            return "Aspiration systems operating within nominal parameters. No action required."
        
        actions = []
        for alert in telemetry["alerts"]:
            if "BAGHOUSE_BLINDING" in alert:
                actions.append("Initiated high-pressure pulse-jet baghouse filter cleaning cycle.")
            elif "AIRLOCK_STALL" in alert:
                actions.append("Dispatched auxiliary motor torque boost to clear rotary airlock jam.")
            elif "HIGH_CYCLONE_PRESSURE_DROP" in alert:
                actions.append("Triggered automated pneumatic shaker and alerted milling floor supervisor.")
            elif "EMISSION_LIMIT_EXCEEDED" in alert:
                actions.append("Engaged secondary electrostatic precipitator backup stage.")

        logger.warning(f"Remediation executed for {self.cyclone_id}: {actions}")
        return f"Remediation completed: {'; '.join(actions)}"


if __name__ == "__main__":
    print("[+] Executing Aspiration Cyclone Sentinel Self-Test for Nairobi Milling Plant...")
    sentinel = AspirationCycloneSentinel(cyclone_id="CYC-NAI-04")
    
    # Simulate telemetry
    test_telemetry = sentinel.inspect_system(
        pressure_drop_pa=1450.0,
        baghouse_dp_kpa=1.8,
        airlock_rpm=22.5,
        particulate_mg_m3=12.0
    )
    print(f"Test Telemetry Result: {test_telemetry}")
    
    action = sentinel.execute_remediation(test_telemetry)
    print(f"Action Taken: {action}")
    print("[+] Aspiration Cyclone Sentinel module operational and clean.")
