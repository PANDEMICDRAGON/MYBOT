import logging
import time
import statistics
from typing import Dict, List, Any, Optional

logging.basicConfig(level=logging.INFO, format='[%(asctime)s] [%(levelname)s] [%(name)s]: %(message)s')
logger = logging.getLogger("RollerMillDynamicLoadBalancer")

class RollerMillLoadBalancer:
    """
    Monitors electrical current draw and material feed rates across a bank of parallel roller mills
    in a Nairobi commercial grain milling plant, autonomously balancing pneumatic feed gates
    to optimize specific energy consumption and prevent localized motor overloads.
    """
    def __init__(self, mill_bank_id: str, nominal_load_amps: float = 45.0, max_imbalance_pct: float = 12.0):
        self.mill_bank_id = mill_bank_id
        self.nominal_load_amps = nominal_load_amps
        self.max_imbalance_pct = max_imbalance_pct
        self.mills: Dict[str, Dict[str, Any]] = {}
        logger.info(f"Initialized RollerMillLoadBalancer for bank {mill_bank_id}")

    def register_mill(self, mill_id: str, current_amps: float, feed_gate_position_pct: float) -> None:
        """Register or update mill sensor telemetry."""
        self.mills[mill_id] = {
            "current_amps": current_amps,
            "feed_gate_position_pct": feed_gate_position_pct,
            "timestamp": time.time(),
            "status": "ACTIVE"
        }

    def compute_load_balance(self) -> Dict[str, Any]:
        """
        Computes load distribution variance and determines corrective adjustments
        for pneumatic feed gates.
        """
        if not self.mills:
            return {"status": "NO_MILLS_REGISTERED", "adjustments": {}}

        currents = [data["current_amps"] for data in self.mills.values()]
        mean_current = statistics.mean(currents)
        max_current = max(currents)
        min_current = min(currents)
        
        imbalance_spread = ((max_current - min_current) / (mean_current if mean_current > 0 else 1.0)) * 100
        
        adjustments = {}
        critical_alert = imbalance_spread > self.max_imbalance_pct

        for mill_id, data in self.mills.items():
            deviation = data["current_amps"] - mean_current
            current_gate = data["feed_gate_position_pct"]
            
            # If mill is drawing too much current, reduce feed gate; if too little, increase.
            correction_delta = -0.5 * (deviation / (self.nominal_load_amps * 0.1))
            new_gate = max(5.0, min(100.0, current_gate + correction_delta))
            
            adjustments[mill_id] = {
                "current_deviation": round(deviation, 2),
                "recommended_gate_position": round(new_gate, 2)
            }

        return {
            "mill_bank_id": self.mill_bank_id,
            "mean_current_amps": round(mean_current, 2),
            "imbalance_spread_pct": round(imbalance_spread, 2),
            "critical_alert": critical_alert,
            "adjustments": adjustments
        }

if __name__ == "__main__":
    logger.info("Executing self-test harness for RollerMillDynamicLoadBalancer...")
    balancer = RollerMillLoadBalancer("NAIROBI_MILL_BANK_A")
    balancer.register_mill("MILL_01", 52.4, 75.0)
    balancer.register_mill("MILL_02", 41.1, 60.0)
    balancer.register_mill("MILL_03", 44.8, 65.0)
    
    report = balancer.compute_load_balance()
    logger.info(f"Load Balance Assessment Report: {report}")
    assert "imbalance_spread_pct" in report, "Report missing imbalance metric"
    logger.info("RollerMillDynamicLoadBalancer validation complete.")
