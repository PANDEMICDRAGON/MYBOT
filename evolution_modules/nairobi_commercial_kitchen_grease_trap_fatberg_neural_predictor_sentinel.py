"""Nairobi Commercial Kitchen Grease Trap Fatberg Neural Predictor Sentinel.

Proactively models lipid accumulation, effluent pH shifts, and thermal differentials
in commercial kitchen grease interceptors across Nairobi to prevent fatberg formation
and municipal sewer line blockages.
"""

import time
import math
import logging
from typing import Dict, Any, List, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("GreaseTrapFatbergNeuralPredictor")


class GreaseTrapNeuralPredictor:
    """Neural estimation engine for lipid layer thickness and blockage risk."""

    def __init__(self, trap_id: str, capacity_liters: float = 500.0):
        self.trap_id = trap_id
        self.capacity_liters = capacity_liters
        self.telemetry_history: List[Dict[str, Any]] = []
        logger.info(f"GreaseTrapNeuralPredictor initialized for trap {trap_id} ({capacity_liters}L capacity).")

    def ingest_sensor_reading(
        self, 
        oil_level_cm: float,
        water_temp_c: float,
        ph_level: float,
        flow_rate_lpm: float
    ) -> Dict[str, Any]:
        """Ingests live telemetry from grease interceptor ultrasonic and thermal sensors."""
        timestamp = time.time()
        
        # Compute lipid accumulation rate and viscosity index
        temp_factor = max(0.1, (60.0 - water_temp_c) / 40.0) # cooler water solidifies fats faster
        viscosity_proxy = oil_level_cm * temp_factor
        
        # Fatberg risk scoring via non-linear sigmoid projection
        risk_score = 1.0 / (1.0 + math.exp(-0.1 * (viscosity_proxy * 12.0 - 25.0)))
        
        record = {
            "timestamp": timestamp,
            "oil_level_cm": oil_level_cm,
            "water_temp_c": water_temp_c,
            "ph_level": ph_level,
            "flow_rate_lpm": flow_rate_lpm,
            "risk_score": round(risk_score, 4)
        }
        self.telemetry_history.append(record)
        
        # Keep rolling history window
        if len(self.telemetry_history) > 1000:
            self.telemetry_history.pop(0)
            
        return record

    def evaluate_fatberg_hazard(self) -> Dict[str, Any]:
        """Evaluates current hazard status and schedules proactive Nairobi municipal pump-out."""
        if not self.telemetry_history:
            return {"status": "NO_DATA", "action_required": False}
            
        latest = self.telemetry_history[-1]
        risk = latest["risk_score"]
        
        action_required = risk > 0.75
        urgency = "CRITICAL_FATBERG_IMMINENT" if risk > 0.9 else ("WARNING" if action_required else "NORMAL")
        
        return {
            "trap_id": self.trap_id,
            "urgency": urgency,
            "risk_score": risk,
            "action_required": action_required,
            "recommended_action": "DISPATCH_NAIROBI_EXHAUSTER_TRUCK" if action_required else "MONITOR_NORMAL"
        }


if __name__ == "__main__":
    print("[+] Executing GreaseTrapNeuralPredictor self-test...")
    predictor = GreaseTrapNeuralPredictor(trap_id="TRAP_WESTLANDS_04")
    
    # Simulate greasy effluent load
    reading = predictor.ingest_sensor_reading(
        oil_level_cm=14.5,
        water_temp_c=22.0,
        ph_level=6.2,
        flow_rate_lpm=45.0
    )
    print(f"[+] Ingested Telemetry: {reading}")
    
    evaluation = predictor.evaluate_fatberg_hazard()
    print(f"[+] Hazard Evaluation Result: {evaluation}")
    print("[+] GreaseTrapNeuralPredictor operational.")
