"""
Nairobi Domestic Liquefied Petroleum Gas (LPG) Cylinder Safety & Automated Refill Sentinel
Proactively monitors residential and commercial gas cylinder weight, ambient LPG/methane levels,
and provides automated alerts and emergency valve cutoff telemetry for Nairobi households.
"""

import os
import sys
import json
import time
import logging
from typing import Dict, Any, List, Optional

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')
logger = logging.getLogger("NairobiKitchenGasSentinel")

class LPGContainer:
    def __init__(self, cylinder_id: str, capacity_kg: float, tare_weight_kg: float, vendor: str):
        self.cylinder_id = cylinder_id
        self.capacity_kg = capacity_kg
        self.tare_weight_kg = tare_weight_kg
        self.vendor = vendor
        self.current_gross_weight_kg: float = capacity_kg + tare_weight_kg
        self.status: str = "ACTIVE"
        self.installation_date: float = time.time()

    def net_gas_weight(self) -> float:
        return max(0.0, self.current_gross_weight_kg - self.tare_weight_kg)

    def percentage_remaining(self) -> float:
        return (self.net_gas_weight() / self.capacity_kg) * 100.0

class NairobiKitchenGasSentinel:
    """Monitors gas sensors, scale telemetry, and automates safety responses for Nairobi kitchens."""
    def __init__(self, warning_threshold_pct: float = 15.0, ppm_danger_threshold: float = 300.0):
        self.warning_threshold_pct = warning_threshold_pct
        self.ppm_danger_threshold = ppm_danger_threshold
        self.cylinders: Dict[str, LPGContainer] = {}
        self.valve_open: bool = True
        self.alert_history: List[Dict[str, Any]] = []

    def register_cylinder(self, cylinder_id: str, capacity_kg: float, tare_weight_kg: float, vendor: str) -> LPGContainer:
        container = LPGContainer(cylinder_id, capacity_kg, tare_weight_kg, vendor)
        self.cylinders[cylinder_id] = container
        logger.info(f"Registered LPG Cylinder {cylinder_id} ({capacity_kg}kg) from {vendor}.")
        return container

    def update_telemetry(self, cylinder_id: str, gross_weight_kg: float, gas_ppm: float) -> Dict[str, Any]:
        if cylinder_id not in self.cylinders:
            raise ValueError(f"Cylinder {cylinder_id} not registered.")
        
        cylinder = self.cylinders[cylinder_id]
        cylinder.current_gross_weight_kg = gross_weight_kg
        rem_pct = cylinder.percentage_remaining()
        
        status_report = {
            "cylinder_id": cylinder_id,
            "vendor": cylinder.vendor,
            "net_weight_kg": round(cylinder.net_gas_weight(), 2),
            "capacity_kg": cylinder.capacity_kg,
            "percentage_remaining": round(rem_pct, 1),
            "gas_ppm": gas_ppm,
            "valve_open": self.valve_open,
            "timestamp": time.time(),
            "alerts": []
        }

        # Check gas leak via PPM
        if gas_ppm >= self.ppm_danger_threshold:
            self.valve_open = False
            alert_msg = f"CRITICAL: LPG leak detected! PPM: {gas_ppm}. Automated emergency solenoid valve CLOSED."
            logger.error(alert_msg)
            status_report["alerts"].append(alert_msg)
            status_report["valve_open"] = self.valve_open
            self._log_alert("CRITICAL_LEAK", alert_msg)

        # Check low fuel replenishment threshold
        elif rem_pct <= self.warning_threshold_pct:
            alert_msg = f"WARNING: Cylinder {cylinder_id} at {rem_pct:.1f}%. Refill or exchange required in Nairobi distribution network."
            logger.warning(alert_msg)
            status_report["alerts"].append(alert_msg)
            self._log_alert("LOW_FUEL", alert_msg)

        return status_report

    def verify_refill_integrity(self, cylinder_id: str, declared_net_kg: float, actual_gross_kg: float) -> Dict[str, Any]:
        """Detects fraudulent under-filled cylinders common in unregulated local distribution."""
        if cylinder_id not in self.cylinders:
            raise ValueError(f"Cylinder {cylinder_id} not registered.")
        cylinder = self.cylinders[cylinder_id]
        calculated_net = actual_gross_kg - cylinder.tare_weight_kg
        discrepancy = declared_net_kg - calculated_net

        is_fraudulent = discrepancy > 0.5 # half kg tolerance
        report = {
            "cylinder_id": cylinder_id,
            "vendor": cylinder.vendor,
            "declared_net_kg": declared_net_kg,
            "actual_net_kg": round(calculated_net, 2),
            "discrepancy_kg": round(discrepancy, 2),
            "fraudulent_refill_detected": is_fraudulent
        }
        if is_fraudulent:
            logger.warning(f"FRAUD ALERT: Cylinder {cylinder_id} ({cylinder.vendor}) is underfilled by {discrepancy:.2f}kg!")
        return report

    def _log_alert(self, alert_type: str, message: str):
        self.alert_history.append({
            "type": alert_type,
            "message": message,
            "timestamp": time.time()
        })

def main():
    print("Initializing Nairobi Kitchen Gas Sentinel...")
    sentinel = NairobiKitchenGasSentinel()
    
    # Register 13kg cylinder commonly used in Nairobi
    sentinel.register_cylinder(
        cylinder_id="NBO-CYL-0094",
        capacity_kg=13.0,
        tare_weight_kg=15.2,
        vendor="TotalEnergies Kenya"
    )

    # Test normal telemetry
    report_normal = sentinel.update_telemetry("NBO-CYL-0094", gross_weight_kg=22.0, gas_ppm=15.0)
    print("Normal Telemetry:", json.dumps(report_normal, indent=2))

    # Test refill integrity check (Underfilled scam check)
    integrity = sentinel.verify_refill_integrity("NBO-CYL-0094", declared_net_kg=13.0, actual_gross_kg=26.5)
    print("Refill Integrity:", json.dumps(integrity, indent=2))

    # Test emergency gas leak condition
    report_danger = sentinel.update_telemetry("NBO-CYL-0094", gross_weight_kg=22.0, gas_ppm=350.0)
    print("Emergency Telemetry:", json.dumps(report_danger, indent=2))
    print("Gas Sentinel verification complete.")

if __name__ == "__main__":
    main()
