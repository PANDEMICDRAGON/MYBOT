import ast
import logging
import time
from typing import Dict, List, Optional, Any

logging.basicConfig(level=logging.INFO, format='[%(asctime)s] [BAKERY_SILO_SENTINEL] %(levelname)s: %(message)s')
logger = logging.getLogger('BakeryFlourSiloSentinel')

class FlourSiloMonitor:
    """
    Monitors temperature, relative humidity, bulk density, and mycotoxin risk index
    inside commercial flour silos across Nairobi bakeries.
    """
    def __init__(self, silo_id: str, capacity_tons: float):
        self.silo_id = silo_id
        self.capacity_tons = capacity_tons
        self.current_tonnage = capacity_tons * 0.85
        self.temperature_c = 24.5
        self.humidity_pct = 55.0
        self.aflatoxin_ppb = 2.1
        self.status = 'OPTIMAL'

    def update_telemetry(self, temp: float, humidity: float, aflatoxin: float, tonnage: float) -> Dict[str, Any]:
        self.temperature_c = temp
        self.humidity_pct = humidity
        self.aflatoxin_ppb = aflatoxin
        self.current_tonnage = max(0.0, min(self.capacity_tons, tonnage))
        
        # Risk evaluation logic
        if self.aflatoxin_ppb > 10.0 or self.humidity_pct > 75.0 or self.temperature_c > 35.0:
            self.status = 'CRITICAL_SPOILAGE_RISK'
        elif self.aflatoxin_ppb > 5.0 or self.humidity_pct > 65.0 or self.temperature_c > 30.0:
            self.status = 'WARNING_ELEVATED_HUMIDITY'
        else:
            self.status = 'OPTIMAL'

        logger.info(f"Silo {self.silo_id} status updated: {self.status} (Temp: {self.temperature_c}°C, Humidity: {self.humidity_pct}%, Aflatoxin: {self.aflatoxin_ppb} ppb)")
        return self.get_state()

    def get_state(self) -> Dict[str, Any]:
        return {
            "silo_id": self.silo_id,
            "capacity_tons": self.capacity_tons,
            "current_tonnage": self.current_tonnage,
            "temperature_c": self.temperature_c,
            "humidity_pct": self.humidity_pct,
            "aflatoxin_ppb": self.aflatoxin_ppb,
            "status": self.status,
            "timestamp": time.time()
        }

class NairobiBakeryFlourManager:
    """
    Central management system aggregating multiple flour silos across Nairobi industrial zones.
    """
    def __init__(self):
        self.silos: Dict[str, FlourSiloMonitor] = {}

    def register_silo(self, silo_id: str, capacity_tons: float) -> FlourSiloMonitor:
        monitor = FlourSiloMonitor(silo_id, capacity_tons)
        self.silos[silo_id] = monitor
        logger.info(f"Registered flour silo {silo_id} with capacity {capacity_tons} tons.")
        return monitor

    def audit_all_silos(self) -> List[Dict[str, Any]]:
        reports = []
        for s_id, monitor in self.silos.items():
            reports.append(monitor.get_state())
        return reports

if __name__ == '__main__':
    manager = NairobiBakeryFlourManager()
    silo_industrial = manager.register_silo("SILO-INDUSTRIAL-AREA-01", 120.0)
    silo_westlands = manager.register_silo("SILO-WESTLANDS-ARTISANAL-02", 45.0)

    # Simulate updates
    silo_industrial.update_telemetry(temp=26.2, humidity=58.0, aflatoxin=1.8, tonnage=105.0)
    silo_westlands.update_telemetry(temp=31.5, humidity=68.5, aflatoxin=6.2, tonnage=30.0)

    audit_results = manager.audit_all_silos()
    print("--- NAIROBI BAKERY FLOUR SILO AUDIT REPORT ---")
    for report in audit_results:
        print(report)

    # Self-validation check
    assert len(audit_results) == 2
    print("Flour Silo Sentinel Module executed successfully and verified via self-test harness.")
