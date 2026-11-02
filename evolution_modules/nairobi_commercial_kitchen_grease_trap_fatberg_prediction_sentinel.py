"""Nairobi Commercial Kitchen Grease Trap Fatberg Prediction Sentinel.

Monitors influent temperature, pH, flow rate, and lipid accumulation in commercial
kitchen grease interceptors across Nairobi, predicting fatberg crystallization thresholds
and triggering automated enzymatic dosing or pump flushing cycles.
"""

import time
import math
import logging
from typing import Dict, Any, List, Optional

logging.basicConfig(level=logging.INFO, format='[%(asctime)s] [FATBERG_SENTINEL] [%(levelname)s] %(message)s')
logger = logging.getLogger('FatbergSentinel')


class GreaseTrapFatbergPredictor:
    """Predicts and mitigates fatberg crystallization in commercial kitchen grease traps."""

    def __init__(self, trap_id: str, capacity_liters: float = 500.0):
        self.trap_id = trap_id
        self.capacity_liters = capacity_liters
        self.accumulated_lipid_kg = 12.5  # Baseline initial load
        self.water_temp_history: List[float] = []
        self.ph_history: List[float] = []
        self.flow_rate_history: List[float] = []
        logger.info(f"Grease Trap Sentinel initialized for {{self.trap_id}} (Capacity: {{self.capacity_liters}}L).")

    def ingest_telemetry(self, temp_c: float, ph: float, flow_rate_lpm: float, lipid_ppm: float) -> Dict[str, Any]:
        """Ingests live telemetry from grease trap IoT sensors."""
        self.water_temp_history.append(temp_c)
        self.ph_history.append(ph)
        self.flow_rate_history.append(flow_rate_lpm)

        # Keep rolling window of last 50 readings
        if len(self.water_temp_history) > 50:
            self.water_temp_history.pop(0)
            self.ph_history.pop(0)
            self.flow_rate_history.pop(0)

        # Calculate lipid deposition rate based on cooling effect and ppm
        # Lower temperatures (< 35 C) cause fats to solidify rapidly
        cooling_factor = max(0.0, (40.0 - temp_c) / 40.0)
        deposition = (lipid_ppm * flow_rate_lpm * 0.0001) * (1.0 + cooling_factor)
        self.accumulated_lipid_kg += deposition

        risk_score = self._calculate_fatberg_risk(temp_c, ph, self.accumulated_lipid_kg)

        mitigation_action = "NONE"
        if risk_score > 80.0:
            mitigation_action = "HIGH_PRESSURE_HOT_WATER_FLUSH_AND_BIOLOGICAL_DOSING"
        elif risk_score > 50.0:
            mitigation_action = "ENZYMATIC_SURFACTANT_INJECTION"

        return {
            "trap_id": self.trap_id,
            "current_lipid_load_kg": round(self.accumulated_lipid_kg, 2),
            "risk_score": round(risk_score, 2),
            "mitigation_action": mitigation_action,
            "timestamp": time.time()
        }

    def _calculate_fatberg_risk(self, temp_c: float, ph: float, lipid_load: float) -> float:
        """Calculates a 0-100 risk score for saponification and fatberg formation."""
        # Saponification accelerates in alkaline conditions (pH > 8.0) and lower temps
        ph_risk = max(0.0, (ph - 7.0) * 20.0)
        temp_risk = max(0.0, (45.0 - temp_c) * 1.5)
        capacity_ratio = (lipid_load / self.capacity_liters) * 100.0

        raw_score = (ph_risk * 0.3) + (temp_risk * 0.3) + (capacity_ratio * 0.4)
        return min(100.0, max(0.0, raw_score))

    def flush_trap(self) -> bool:
        """Executes simulated automated remediation cycle."""
        logger.info(f"Executing automated thermal-enzymatic flush for {{self.trap_id}}...")
        self.accumulated_lipid_kg = max(0.0, self.accumulated_lipid_kg * 0.2)  # 80% reduction
        return True


if __name__ == "__main__":
    sentinel = GreaseTrapFatbergPredictor(trap_id="NRB_REST_GREASE_042")
    
    # Simulate dinner rush telemetry stream
    sample_readings = [
        (38.5, 7.2, 25.0, 450.0),
        (32.0, 7.8, 60.0, 850.0),
        (28.1, 8.4, 80.0, 1200.0),
        (24.5, 8.9, 95.0, 1500.0)
    ]

    for t, p, f, l in sample_readings:
        status = sentinel.ingest_telemetry(temp_c=t, ph=p, flow_rate_lpm=f, lipid_ppm=l)
        logger.info(f"Telemetry Evaluated: {{status}}")
        if status["risk_score"] > 50.0:
            sentinel.flush_trap()
