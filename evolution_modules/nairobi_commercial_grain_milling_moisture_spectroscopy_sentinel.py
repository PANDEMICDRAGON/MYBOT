"""
Module: nairobi_commercial_grain_milling_moisture_spectroscopy_sentinel.py
Description: Inline NIR spectroscopy sentinel for commercial grain milling plants in Nairobi,
             monitoring moisture, protein, and starch to prevent spoilage and optimize roller gap pressure.
Author: Cortana Autonomous Evolutionary Architect
"""

import time
import math
import random
import logging
from typing import Dict, List, Any, Optional

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')
logger = logging.getLogger("GrainMillingMoistureSentinel")

class GrainMoistureSpectroscopySentinel:
    """
    Monitors grain stream near-infrared (NIR) spectra, computes moisture percentage, protein content,
    and starch integrity, triggering corrective actions if parameters deviate from optimal milling thresholds.
    """
    
    def __init__(self, target_moisture: float = 13.5, tolerance: float = 0.8):
        self.target_moisture = target_moisture
        self.tolerance = tolerance
        self.telemetry_history: List[Dict[str, Any]] = []
        logger.info("Initialized GrainMoistureSpectroscopySentinel (Target Moisture: %.1f%%)", target_moisture)

    def analyze_stream(self, batch_id: str, nir_absorbance_readings: List[float]) -> Dict[str, Any]:
        """
        Analyzes raw NIR absorbance spectra readings to estimate moisture, protein, and starch levels.
        """
        if not nir_absorbance_readings:
            raise ValueError("Empty NIR absorbance readings provided.")

        # Simulated spectroscopic calculation
        avg_absorbance = sum(nir_absorbance_readings) / len(nir_absorbance_readings)
        estimated_moisture = round(self.target_moisture + (avg_absorbance * 2.5) + random.uniform(-0.3, 0.3), 2)
        estimated_protein = round(11.0 + (avg_absorbance * 1.2) + random.uniform(-0.2, 0.2), 2)
        estimated_starch = round(70.0 - (estimated_moisture * 0.5) + random.uniform(-0.5, 0.5), 2)

        deviation = abs(estimated_moisture - self.target_moisture)
        status = "OPTIMAL"
        adjustment_action = "NONE"

        if deviation > self.tolerance:
            if estimated_moisture > self.target_moisture:
                status = "HIGH_MOISTURE"
                adjustment_action = "INCREASE_DRYER_TEMPERATURE_AND_AIRFLOW"
            else:
                status = "LOW_MOISTURE"
                adjustment_action = "ENGAGE_WATER_DAMPER_ADDITION"

        record = {
            "timestamp": time.time(),
            "batch_id": batch_id,
            "estimated_moisture": estimated_moisture,
            "estimated_protein": estimated_protein,
            "estimated_starch": estimated_starch,
            "status": status,
            "adjustment_action": adjustment_action
        }

        self.telemetry_history.append(record)
        logger.info("Batch %s analyzed: Moisture=%.2f%%, Status=%s, Action=%s", 
                    batch_id, estimated_moisture, status, adjustment_action)
        return record

    def get_audit_summary(self) -> Dict[str, Any]:
        """
        Returns summary statistics across all analyzed batches.
        """
        if not self.telemetry_history:
            return {"total_batches": 0, "avg_moisture": 0.0}

        moistures = [r["estimated_moisture"] for r in self.telemetry_history]
        return {
            "total_batches": len(self.telemetry_history),
            "avg_moisture": round(sum(moistures) / len(moistures), 2),
            "max_moisture": max(moistures),
            "min_moisture": min(moistures)
        }

if __name__ == "__main__":
    sentinel = GrainMoistureSpectroscopySentinel()
    sample_readings = [0.12, 0.15, 0.14, 0.16, 0.13]
    result = sentinel.analyze_stream("BATCH-NBI-9921", sample_readings)
    print("Test Analysis Result:", result)
    print("Audit Summary:", sentinel.get_audit_summary())
