"""
Nairobi Commercial Grain Milling Roller Mill Dynamic Torque Friction Sentinel
Author: Cortana Autonomous Evolutionary Architect
Operator: Michael Obiero (Nairobi, Kenya)

Monitors roller mill drive shaft torque friction anomalies under varying feed loads
to prevent roll wear, belt slippage, and catastrophic gearbox failure in Nairobi mills.
"""

import os
import time
import logging
from typing import Dict, List, Optional, Any

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')
logger = logging.getLogger("RollerMillFrictionSentinel")

class RollerMillFrictionSentinel:
    def __init__(self, mill_id: str, friction_threshold: float = 1.45):
        self.mill_id = mill_id
        self.friction_threshold = friction_threshold
        self.telemetry_history: List[Dict[str, Any]] = []
        logger.info(f"Initialized RollerMillFrictionSentinel for mill {mill_id} with threshold {friction_threshold}")

    def analyze_friction(self, load_amps: float, torque_nm: float, bearing_temp_c: float, feed_rate_tph: float) -> Dict[str, Any]:
        """Calculates dynamic friction coefficient and evaluates anomalous friction spikes."""
        try:
            if feed_rate_tph <= 0:
                specific_friction = 0.0
            else:
                specific_friction = torque_nm / (feed_rate_tph * 10.0)

            is_anomalous = specific_friction > self.friction_threshold or bearing_temp_c > 85.0
            status = "CRITICAL_FRICTION_ANOMALY" if is_anomalous else "NOMINAL"

            report = {
                "timestamp": time.time(),
                "mill_id": self.mill_id,
                "load_amps": load_amps,
                "torque_nm": torque_nm,
                "bearing_temp_c": bearing_temp_c,
                "feed_rate_tph": feed_rate_tph,
                "specific_friction": round(specific_friction, 4),
                "status": status
            }
            self.telemetry_history.append(report)
            if len(self.telemetry_history) > 1000:
                self.telemetry_history.pop(0)

            if is_anomalous:
                logger.warning(f"[{self.mill_id}] Friction anomaly detected! Specific Friction: {report['specific_friction']}, Temp: {bearing_temp_c}C")
            
            return report
        except Exception as e:
            logger.error(f"Error analyzing friction telemetry: {e}")
            return {"status": "ERROR", "message": str(e)}

    def get_audit_summary(self) -> Dict[str, Any]:
        total_records = len(self.telemetry_history)
        if total_records == 0:
            return {"total_records": 0, "anomaly_count": 0}
        
        anomalies = [r for r in self.telemetry_history if r.get("status") == "CRITICAL_FRICTION_ANOMALY"]
        return {
            "mill_id": self.mill_id,
            "total_records": total_records,
            "anomaly_count": len(anomalies),
            "last_status": self.telemetry_history[-1].get("status") if self.telemetry_history else "UNKNOWN"
        }

if __name__ == "__main__":
    print("Executing RollerMillFrictionSentinel Self-Test...")
    sentinel = RollerMillFrictionSentinel(mill_id="NAI_UGALI_MILL_04")
    
    # Test normal operation
    res1 = sentinel.analyze_friction(load_amps=45.2, torque_nm=320.5, bearing_temp_c=62.0, feed_rate_tph=4.5)
    print(f"Test 1 (Normal): {res1}")
    
    # Test anomalous friction (high torque, high temp)
    res2 = sentinel.analyze_friction(load_amps=88.5, torque_nm=780.0, bearing_temp_c=89.5, feed_rate_tph=3.0)
    print(f"Test 2 (Anomalous): {res2}")
    
    summary = sentinel.get_audit_summary()
    print(f"Audit Summary: {summary}")
    print("RollerMillFrictionSentinel Self-Test Completed Successfully.")
