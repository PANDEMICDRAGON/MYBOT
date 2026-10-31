import time
import logging
import statistics
from typing import Dict, List, Optional, Any

logging.basicConfig(level=logging.INFO, format='%(asctime)s - [CHECK_WEIGHER_SENTINEL] - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class CommercialGrainMillingCheckWeigherSentinel:
    """
    Monitors high-speed dynamic check-weighers on Nairobi commercial grain milling packaging lines.
    Executes statistical process control (SPC), rejects underweight/overweight flour bags,
    and ensures compliance with KEBS net weight standards.
    """
    def __init__(self, target_net_mass_kg: float = 2.0, tolerance_pct: float = 0.5):
        self.target_net_mass_kg = target_net_mass_kg
        self.tolerance_pct = tolerance_pct
        self.lower_limit = target_net_mass_kg * (1.0 - (tolerance_pct / 100.0))
        self.upper_limit = target_net_mass_kg * (1.0 + (tolerance_pct / 100.0))
        self.bag_history: List[Dict[str, Any]] = []
        self.reject_count = 0
        self.accepted_count = 0
        logger.info(f"CheckWeigher Initialized. Target: {target_net_mass_kg}kg, Tolerance: ±{tolerance_pct}%")

    def process_bag_reading(self, bag_id: str, measured_mass_kg: float) -> Dict[str, Any]:
        """
        Evaluates a dynamic scale reading for a packaged bag of flour.
        """
        timestamp = time.time()
        is_underweight = measured_mass_kg < self.lower_limit
        is_overweight = measured_mass_kg > self.upper_limit
        status = "ACCEPTED"
        
        if is_underweight:
            status = "REJECT_UNDERWEIGHT"
            self.reject_count += 1
        elif is_overweight:
            status = "REJECT_OVERWEIGHT"
            self.reject_count += 1
        else:
            self.accepted_count += 1

        record = {
            "bag_id": bag_id,
            "timestamp": timestamp,
            "measured_mass_kg": measured_mass_kg,
            "target_mass_kg": self.target_net_mass_kg,
            "status": status,
            "deviation_pct": ((measured_mass_kg - self.target_net_mass_kg) / self.target_net_mass_kg) * 100.0
        }
        
        self.bag_history.append(record)
        if len(self.bag_history) > 1000:
            self.bag_history.pop(0)
            
        if status != "ACCEPTED":
            logger.warning(f"Pneumatic Reject Actuator Triggered! Bag {bag_id} Mass: {measured_mass_kg}kg ({status})")
            
        return record

    def get_spc_metrics(self) -> Dict[str, Any]:
        """
        Computes Statistical Process Control metrics (mean, standard deviation, Cp/Cpk approximation).
        """
        if not self.bag_history:
            return {"status": "NO_DATA"}
            
        masses = [b["measured_mass_kg"] for b in self.bag_history]
        mean_mass = statistics.mean(masses)
        stdev = statistics.stdev(masses) if len(masses) > 1 else 0.0
        
        total_processed = self.accepted_count + self.reject_count
        reject_rate = (self.reject_count / total_processed * 100.0) if total_processed > 0 else 0.0
        
        # Process Capability Cp calculation (Tolerance Spread / 6*sigma)
        tolerance_spread = (self.upper_limit - self.lower_limit)
        cp = (tolerance_spread / (6 * stdev)) if stdev > 0 else float('inf')

        return {
            "total_processed": total_processed,
            "accepted_count": self.accepted_count,
            "reject_count": self.reject_count,
            "reject_rate_pct": round(reject_rate, 2),
            "mean_mass_kg": round(mean_mass, 4),
            "stdev_kg": round(stdev, 4),
            "cp_index": round(cp, 2),
            "kebs_compliance": reject_rate < 1.0
        }

if __name__ == "__main__":
    logger.info("Executing Check Weigher Sentinel Self-Test...")
    sentinel = CommercialGrainMillingCheckWeigherSentinel(target_net_mass_kg=2.0, tolerance_pct=1.0)
    
    # Simulate normal and aberrant bag weights
    test_readings = [("BAG-001", 2.002), ("BAG-002", 1.995), ("BAG-003", 1.950), ("BAG-004", 2.015), ("BAG-005", 2.055)]
    for bid, mass in test_readings:
        res = sentinel.process_bag_reading(bid, mass)
        print(res)
        
    spc = sentinel.get_spc_metrics()
    logger.info(f"SPC Metrics Summary: {spc}")
    logger.info("Check Weigher Sentinel Self-Test Completed Successfully.")
