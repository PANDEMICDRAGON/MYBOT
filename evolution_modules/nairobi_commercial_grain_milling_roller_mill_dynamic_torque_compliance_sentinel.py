import logging
import time
import statistics
from typing import Dict, List, Any

logging.basicConfig(level=logging.INFO, format='%(asctime)s - [%(levelname)s] - %(name)s - %(message)s')
logger = logging.getLogger("DynamicTorqueComplianceSentinel")

class RollerMillTorqueComplianceSentinel:
    """
    Monitors roller mill dynamic torque compliance against expected baseline distributions,
    detecting micro-anomalies, slippage vectors, and mechanical binding forces.
    """
    def __init__(self, mill_id: str, torque_threshold_nm: float = 450.0):
        self.mill_id = mill_id
        self.torque_threshold_nm = torque_threshold_nm
        self.history: List[float] = []
        self.violations_detected = 0

    def ingest_telemetry(self, current_torque: float) -> Dict[str, Any]:
        """
        Ingests a torque reading, evaluates compliance, and updates internal state.
        """
        self.history.append(current_torque)
        if len(self.history) > 100:
            self.history.pop(0)

        mean_torque = statistics.mean(self.history)
        stdev_torque = statistics.stdev(self.history) if len(self.history) > 1 else 0.0

        compliant = current_torque <= self.torque_threshold_nm
        status = "NORMAL"

        if not compliant:
            self.violations_detected += 1
            status = "CRITICAL_OVER_TORQUE"
            logger.warning(f"[{self.mill_id}] Torque violation! Current: {current_torque} Nm > Threshold: {self.torque_threshold_nm} Nm")
        elif stdev_torque > (self.torque_threshold_nm * 0.15):
            status = "WARNING_HIGH_FLUTTER"
            logger.info(f"[{self.mill_id}] High torque variance detected. Stdev: {stdev_torque:.2f}")

        return {
            "mill_id": self.mill_id,
            "current_torque_nm": current_torque,
            "mean_torque_nm": mean_torque,
            "stdev_torque_nm": stdev_torque,
            "compliant": compliant,
            "status": status,
            "total_violations": self.violations_detected,
            "timestamp": time.time()
        }

if __name__ == "__main__":
    logger.info("Initializing Nairobi Commercial Grain Milling Roller Mill Dynamic Torque Compliance Sentinel Test Harness...")
    sentinel = RollerMillTorqueComplianceSentinel(mill_id="NAIROBI_MILL_UGALI_01", torque_threshold_nm=420.0)
    
    test_readings = [310.2, 315.5, 320.1, 410.0, 435.6, 318.0]
    for r in test_readings:
        res = sentinel.ingest_telemetry(r)
        logger.info(f"Telemetry Result: {res}")
    logger.info("Sentinel test harness completed successfully.")
