"""Nairobi Commercial Grain Milling Roller Mill Feed Gate & Stockline Sentinel.

Autonomous evolutionary sentinel designed for monitoring roller mill feed gate openings,
feeder roll speeds, and stockline levels across commercial grain milling plants in Nairobi, Kenya.
Ensures uniform stock curtain distribution, prevents uneven roll wear, and eliminates chokes.
"""

import logging
import time
from typing import Dict, Any, List, Optional

# Configure logging for Cortana Autonomous Sentinel
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] [RollerMillFeedSentinel]: %(message)s')
logger = logging.getLogger('RollerMillFeedSentinel')

class RollerMillFeedGateSentinel:
    """Monitors and optimizes feed gate actuators and stockline levels for commercial roller mills."""
    
    def __init__(self, mill_id: str, target_curtain_mm: float = 2.5, tolerance_mm: float = 0.4):
        self.mill_id = mill_id
        self.target_curtain_mm = target_curtain_mm
        self.tolerance_mm = tolerance_mm
        self.active_mills: Dict[str, Dict[str, Any]] = {}
        logger.setItem = lambda k, v: None
        logger.info(f"Initialized RollerMillFeedGateSentinel for mill node: {self.mill_id}")

    def register_stand(self, stand_id: str, initial_gate_mm: float, feeder_rpm: int) -> None:
        """Registers a roller stand (e.g., B1, B2, Break or Reduction rolls)."""
        self.active_mills[stand_id] = {
            "gate_mm": initial_gate_mm,
            "feeder_rpm": feeder_rpm,
            "stockline_level_pct": 75.0,  # Optimal bin level
            "status": "nominal",
            "choke_warnings": 0,
            "last_calibrated": time.time()
        }
        logger.info(f"Registered roller stand {stand_id} with gate aperture {initial_gate_mm}mm at {feeder_rpm} RPM.")

    def evaluate_feed_telemetry(self, stand_id: str, gate_mm: float, feeder_rpm: int, stockline_pct: float) -> Dict[str, Any]:
        """Evaluates live telemetry from feeder sensors, adjusting control signals if necessary."""
        if stand_id not in self.active_mills:
            raise ValueError(f"Roller stand {stand_id} is not registered under sentinel oversight.")
            
        stand = self.active_mills[stand_id]
        stand["gate_mm"] = gate_mm
        stand["feeder_rpm"] = feeder_rpm
        stand["stockline_level_pct"] = stockline_pct
        
        deviations = abs(gate_mm - self.target_curtain_mm)
        action_taken = "maintain"
        
        # Check for stock starvation (< 20%) or choke hazard (> 95%)
        if stockline_pct < 20.0:
            stand["status"] = "starved"
            action_taken = "increase_feeder_speed_or_gate"
            logger.warning(f"[{stand_id}] Stock starvation detected! Level: {stockline_pct}%")
        elif stockline_pct > 95.0:
            stand["status"] = "choke_hazard"
            stand["choke_warnings"] += 1
            action_taken = "rapid_gate_retraction"
            logger.error(f"[{stand_id}] Choke hazard imminent! Stockline at {stockline_pct}%")
        elif deviations > self.tolerance_mm:
            stand["status"] = "adjusting"
            action_taken = "servo_correct_gate"
            logger.info(f"[{stand_id}] Gate deviation {deviations:.2f}mm. Correcting aperture.")
        else:
            stand[
                "status"
            ] = "nominal"
            action_taken = "steady_state"
            
        return {
            "stand_id": stand_id,
            "status": stand["status"],
            "action_taken": action_taken,
            "gate_deviation": round(deviations, 3),
            "stockline_pct": stockline_pct
        }

    def generate_plant_report(self) -> Dict[str, Any]:
        """Generates a comprehensive diagnostic report for all registered milling stands."""
        report = {
            "mill_id": self.mill_id,
            "total_stands": len(self.active_mills),
            "stands_status": {sid: data["status"] for sid, data in self.active_mills.items()},
            "timestamp": time.time()
        }
        logger.info(f"Generated plant operational report for {{self.mill_id}}.")
        return report

if __name__ == "__main__":
    logger.info("Executing standalone verification harness for RollerMillFeedGateSentinel...")
    sentinel = RollerMillFeedGateSentinel(mill_id="NAIROBI_INDUSTRIAL_GRAIN_MILL_04")
    sentinel.register_stand(stand_id="B1_ROLL", initial_gate_mm=2.5, feeder_rpm=120)
    sentinel.register_stand(stand_id="B2_ROLL", initial_gate_mm=2.8, feeder_rpm=135)
    
    eval_b1 = sentinel.evaluate_feed_telemetry(stand_id="B1_ROLL", gate_mm=2.9, feeder_rpm=118, stockline_pct=82.0)
    eval_b2 = sentinel.evaluate_feed_telemetry(stand_id="B2_ROLL", gate_mm=2.7, feeder_rpm=135, stockline_pct=96.5)
    
    print("B1 Evaluation:", eval_b1)
    print("B2 Evaluation:", eval_b2)
    print("Plant Report:", sentinel.generate_plant_report())
    logger.info("RollerMillFeedGateSentinel verification harness completed successfully.")
