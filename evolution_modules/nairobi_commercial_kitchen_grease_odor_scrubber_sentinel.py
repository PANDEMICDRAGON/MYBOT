import logging
import time
import statistics
from typing import Dict, List, Any, Optional

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')
logger = logging.getLogger("GreaseOdorScrubberSentinel")

class KitchenGreaseScrubberSentinel:
    """
    Monitors exhaust airflow, UV-C ozone lamp degradation, electrostatic precipitator (ESP)
    voltage, and VOC sensors for Nairobi commercial kitchen ventilation systems.
    """
    def __init__(self, kitchen_id: str, target_voc_ppm: float = 5.0):
        self.kitchen_id = kitchen_id
        self.target_voc_ppm = target_voc_ppm
        self.esp_voltage_kv = 12.0
        self.uv_lamp_hours = 0.0
        self.exhaust_airflow_cfm = 2500.0
        self.telemetry_history: List[Dict[str, Any]] = []
        logger.info(f"Initialized KitchenGreaseScrubberSentinel for {kitchen_id}")

    def ingest_telemetry(self, voc_ppm: float, exhaust_temp_c: float, static_pressure_pa: float) -> Dict[str, Any]:
        """Ingests live sensor telemetry and returns autonomous adjustment directives."""
        self.uv_lamp_hours += 0.1
        
        # Autonomous voltage adjustment based on VOC levels
        if voc_ppm > self.target_voc_ppm:
            adjustment = min(2.0, (voc_ppm - self.target_voc_ppm) * 0.4)
            self.esp_voltage_kv = min(18.0, self.esp_voltage_kv + adjustment)
            status = "BOOSTING_ESP_VOLTAGE"
        else:
            if self.esp_voltage_kv > 10.0:
                self.esp_voltage_kv -= 0.1
            status = "OPTIMAL"

        # Maintenance check for UV lamps
        maintenance_required = self.uv_lamp_hours > 8000.0

        record = {
            "timestamp": time.time(),
            "voc_ppm": voc_ppm,
            "exhaust_temp_c": exhaust_temp_c,
            "static_pressure_pa": static_pressure_pa,
            "esp_voltage_kv": round(self.esp_voltage_kv, 2),
            "uv_lamp_hours": round(self.uv_lamp_hours, 1),
            "status": status,
            "maintenance_required": maintenance_required
        }
        self.telemetry_history.append(record);
        if len(self.telemetry_history) > 100:
            self.telemetry_history.pop(0)
            
        return record

    def get_system_analytics(self) -> Dict[str, Any]:
        """Computes rolling performance metrics across recorded telemetry."""
        if not self.telemetry_history:
            return {"error": "No telemetry recorded"}
            
        voc_levels = [r["voc_ppm"] for r in self.telemetry_history]
        pressures = [r["static_pressure_pa"] for r in self.telemetry_history]
        
        return {
            "kitchen_id": self.kitchen_id,
            "mean_voc_ppm": round(statistics.mean(voc_levels), 2),
            "peak_voc_ppm": max(voc_levels),
            "mean_static_pressure_pa": round(statistics.mean(pressures), 2),
            "current_esp_voltage_kv": round(self.esp_voltage_kv, 2),
            "uv_lamp_status": "CRITICAL_REPLACE" if self.uv_lamp_hours > 8000.0 else "OPERATIONAL"
        }

if __name__ == "__main__":
    sentinel = KitchenGreaseScrubberSentinel("Westlands_Grill_Hub_01")
    # Test pulse ingestion
    telemetry = sentinel.ingest_telemetry(voc_ppm=7.2, exhaust_temp_c=45.5, static_pressure_pa=120.0)
    logger.info(f"Test Telemetry Result: {telemetry}")
    analytics = sentinel.get_system_analytics()
    logger.info(f"Test Analytics: {analytics}")
