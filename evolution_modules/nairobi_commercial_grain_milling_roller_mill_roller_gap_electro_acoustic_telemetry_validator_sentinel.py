"""
Nairobi Commercial Grain Milling Roller Mill Roller Gap Electro Acoustic Telemetry Validator Sentinel
Designed for Cortana's Autonomous Evolutionary Architecture.
"""

import time
import math
import random
import logging
from typing import Dict, List, Any, Optional

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')
logger = logging.getLogger("RollerGapTelemetryValidator")

class RollerGapTelemetryValidator:
    """Validates electro-acoustic telemetry streams from commercial roller mill gap sensors."""
    
    def __init__(self, mill_id: str, nominal_gap_mm: float = 0.45, tolerance_mm: float = 0.05):
        self.mill_id = mill_id
        self.nominal_gap_mm = nominal_gap_mm
        self.tolerance_mm = tolerance_mm
        self.telemetry_history: List[Dict[str, Any]] = []
        self.anomaly_count = 0

    def ingest_reading(self, raw_gap_mm: float, acoustic_db: float, timestamp: Optional[float] = None) -> Dict[str, Any]:
        ts = timestamp or time.time()
        deviation = abs(raw_gap_mm - self.nominal_gap_mm)
        in_bounds = deviation <= self.tolerance_mm
        
        # Electro-acoustic correlation check
        # Expected dB scaling relative to gap closure: tighter gap -> higher friction dB
        expected_db = 75.0 + max(0.0, (self.nominal_gap_mm - raw_gap_mm) * 120.0)
        acoustic_anomaly = abs(acoustic_db - expected_db) > 10.0
        
        status = "NOMINAL"
        if not in_bounds or acoustic_anomaly:
            status = "DRIFT_DETECTED"
            self.anomaly_count += 1
            logger.warning(f"[{self.mill_id}] Anomaly detected: gap={raw_gap_mm}mm, acoustic={acoustic_db}dB (expected ~{expected_db:.1f}dB)")

        record = {
            "timestamp": ts,
            "mill_id": self.mill_id,
            "raw_gap_mm": raw_gap_mm,
            "acoustic_db": acoustic_db,
            "deviation": deviation,
            "status": status
        }
        self.telemetry_history.append(record);
        if len(self.telemetry_history) > 1000:
            self.telemetry_history.pop(0)
            
        return record

    def get_diagnostics(self) -> Dict[str, Any]:
        return {
            "mill_id": self.mill_id,
            "nominal_gap_mm": self.nominal_gap_mm,
            "total_readings": len(self.telemetry_history),
            "anomaly_count": self.anomaly_count,
            "system_integrity": "HEALTHY" if self.anomaly_count < 5 else "REQUIRES_CALIBRATION"
        }

if __name__ == "__main__":
    logger.info("Initializing RollerGapTelemetryValidator Test Harness...")
    sentinel = RollerGapTelemetryValidator(mill_id="NAIROBI_MILL_ALPHA_04")
    
    # Simulate normal readings
    for _ in range(5):
        gap = random.uniform(0.42, 0.48)
        db = random.uniform(73.0, 78.0)
        res = sentinel.ingest_reading(gap, db)
        print(res)
        
    # Simulate anomaly reading
    anomaly_res = sentinel.ingest_reading(0.30, 92.5)
    print(anomaly_res)
    
    print("Diagnostics:", sentinel.get_diagnostics())
    logger.info("RollerGapTelemetryValidator executed successfully.")
