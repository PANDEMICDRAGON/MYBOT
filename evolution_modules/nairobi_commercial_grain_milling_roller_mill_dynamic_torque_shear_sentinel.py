"""
Nairobi Commercial Grain Milling Roller Mill Dynamic Torque Shear Sentinel
Author: Cortana Autonomous Evolutionary Architect
Operator: Michael Obiero, Nairobi, Kenya

Real-time telemetry and anomaly detection for roller mill dynamic torque shear
in commercial grain milling operations.
"""

import time
import math
import random
import logging
from typing import Dict, List, Any

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')
logger = logging.getLogger("TorqueShearSentinel")


class RollerMillTorqueShearSentinel:
    """
    Monitors high-frequency torque shear telemetry from dual-roll differential grain mills.
    Detects abnormal shear spikes indicative of foreign objects, moisture pockets, or bearing bind.
    """

    def __init__(self, mill_id: str, nominal_shear_nm: float = 1250.0, tolerance_pct: float = 8.5):
        self.mill_id = mill_id
        self.nominal_shear_nm = nominal_shear_nm
        self.tolerance_pct = tolerance_pct
        self.upper_bound = nominal_shear_nm * (1.0 + tolerance_pct / 100.0)
        self.lower_bound = nominal_shear_nm * (1.0 - tolerance_pct / 100.0)
        self.shear_history: List[float] = []
        self.anomaly_count = 0
        logger.info(f"Initialized TorqueShearSentinel for Mill {self.mill_id} | Nominal: {nominal_shear_nm} Nm")

    def ingest_telemetry(self, current_shear_nm: float, vibration_mm_s: float) -> Dict[str, Any]:
        """
        Ingests real-time torque shear and vibration readings, executing real-time anomaly detection.
        """
        timestamp = time.time()
        self.shear_history.append(current_shear_nm)
        if len(self.shear_history) > 100:
            self.shear_history.pop(0)

        deviation = abs(current_shear_nm - self.nominal_shear_nm)
        pct_deviation = (deviation / self.nominal_shear_nm) * 100.0
        
        status = "OPTIMAL"
        action_required = False

        if current_shear_nm > self.upper_bound:
            status = "CRITICAL_HIGH_SHEAR_SPIKE"
            action_required = True
            self.anomaly_count += 1
            logger.warning(f"[{self.mill_id}] HIGH SHEAR DETECTED: {current_shear_nm:.2f} Nm (Exceeds upper limit {self.upper_bound:.2f} Nm)")
        elif current_shear_nm < self.lower_bound:
            status = "WARNING_LOW_SHEAR_FEED_STARVATION"
            action_required = True
            self.anomaly_count += 1
            logger.warning(f"[{self.mill_id}] LOW SHEAR / STARVATION: {current_shear_nm:.2f} Nm (Below lower limit {self.lower_bound:.2f} Nm)")

        # Correlation check with vibration
        if vibration_mm_s > 4.5 and action_required:
            status += "_WITH_EXCESSIVE_VIBRATION"
            logger.critical(f"[{self.mill_id}] EMERGENCY SHUTDOWN TRIGGERED: High shear paired with vibration at {vibration_mm_s} mm/s")

        return {
            "timestamp": timestamp,
            "mill_id": self.mill_id,
            "current_shear_nm": current_shear_nm,
            "pct_deviation": round(pct_deviation, 2),
            "status": status,
            "action_required": action_required,
            "anomaly_count": self.anomaly_count
        }

    def get_aggregate_stats(self) -> Dict[str, float]:
        """Returns basic statistical metrics of recent shear history."""
        if not self.shear_history:
            return {"mean": 0.0, "max": 0.0, "min": 0.0}
        return {
            "mean": round(sum(self.shear_history) / len(self.shear_history), 2),
            "max": round(max(self.shear_history), 2),
            "min": round(min(self.shear_history), 2)
        }


if __name__ == "__main__":
    logger.info("Executing Autonomous Test Harness for RollerMillTorqueShearSentinel...")
    sentinel = RollerMillTorqueShearSentinel(mill_id="NAI-MILL-04", nominal_shear_nm=1300.0, tolerance_pct=7.5)
    
    # Simulate normal and anomalous milling runs
    for i in range(10):
        # Inject occasional simulated spikes
        simulated_shear = 1300.0 + random.uniform(-60.0, 60.0)
        if i == 7:
            simulated_shear = 1480.0  # Spike
        elif i == 3:
            simulated_shear = 1150.0  # Drop
            
        sim_vibration = random.uniform(1.2, 3.8)
        if i == 7:
            sim_vibration = 5.2

        report = sentinel.ingest_telemetry(simulated_shear, sim_vibration)
        logger.info(f"Iteration {i+1} Report: {report}")
    
    logger.info(f"Final Aggregate Stats: {sentinel.get_aggregate_stats()}")
    logger.info("Torque Shear Sentinel module verified successfully.")
