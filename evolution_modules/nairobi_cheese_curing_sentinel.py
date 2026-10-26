"""
Module: nairobi_cheese_curing_sentinel.py
Description: Autonomous biosafety and environmental telemetry sentinel for artisanal cheese
             curing caves and cold rooms in Nairobi, Kenya.
Author: Cortana Autonomous Evolutionary Architect
Operator: Michael Obiero
"""

import json
import logging
import math
import time
from typing import Dict, List, Optional, Tuple

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] (CheeseSentinel): %(message)s"
)
logger = logging.getLogger("nairobi_cheese_curing_sentinel")


class CheeseBatchProfile:
    """Represents a specific batch of artisanal cheese undergoing affine curing."""
    
    def __init__(self, batch_id: str, variety: str, target_temp_c: float, 
                 target_humidity_pct: float, target_ph: float, age_days: int):
        self.batch_id = batch_id
        self.variety = variety
        self.target_temp_c = target_temp_c
        self.target_humidity_pct = target_humidity_pct
        self.target_ph = target_ph
        self.age_days = age_days


class CheeseCuringSentinel:
    """
    Monitors environmental conditions, predicts mold/rind defects, and automates
    remediation triggers for urban Nairobi artisanal cheese cellars.
    """
    
    def __init__(self, cellar_id: str):
        self.cellar_id = cellar_id
        self.active_batches: Dict[str, CheeseBatchProfile] = {}
        self.telemetry_history: List[Dict] = []

    def register_batch(self, profile: CheeseBatchProfile) -> None:
        """Registers a new cheese batch into the curing sentinel."""
        self.active_batches[profile.batch_id] = profile
        logger.info(f"Registered batch {profile.batch_id} ({profile.variety}) in cellar {self.cellar_id}.")

    def evaluate_environment(self, batch_id: str, current_temp_c: float, 
                           current_humidity_pct: float, current_ph: float) -> Dict:
        """
        Evaluates real-time sensor readings against target specs for a given batch.
        Calculates biosafety risk scores and deviation vectors.
        """
        if batch_id not in self.active_batches:
            raise ValueError(f"Batch {batch_id} not found in active cellar registry.")

        profile = self.active_batches[batch_id]
        
        temp_diff = abs(current_temp_c - profile.target_temp_c)
        humidity_diff = abs(current_humidity_pct - profile.target_humidity_pct)
        ph_diff = abs(current_ph - profile.target_ph)

        # Defect risk heuristics
        # High humidity + high temp promotes mucor / undesired wild mold growth
        mold_risk_factor = max(0.0, (current_humidity_pct - 85.0) / 15.0) * max(0.0, (current_temp_c - 12.0) / 10.0)
        mold_risk_pct = round(min(100.0, mold_risk_factor * 100.0), 2)

        # Lactococcal acidification deviation check
        acidification_anomaly = ph_diff > 0.4

        # Overall health score (0-100, 100 being optimal)
        penalty = (temp_diff * 5.0) + (humidity_diff * 2.0) + (ph_diff * 15.0) + (mold_risk_pct * 0.2)
        health_score = max(0.0, round(100.0 - penalty, 2))

        status = "OPTIMAL"
        remediation_action = "NONE"

        if health_score < 60.0 or mold_risk_pct > 40.0:
            status = "CRITICAL_DEFECT_RISK"
            if current_humidity_pct > profile.target_humidity_pct:
                remediation_action = "TRIGGER_DEHUMIDIFIER_AND_INCREASE_EXHAUST"
            else:
                remediation_action = "ADJUST_HVAC_COMPRESSOR_CYCLE"
        elif health_score < 80.0:
            status = "WARNING"
            remediation_action = "FINE_TUNE_AIR_CIRCULATION"

        telemetry_record = {
            "timestamp": time.time(),
            "cellar_id": self.cellar_id,
            "batch_id": batch_id,
            "health_score": health_score,
            "mold_risk_pct": mold_risk_pct,
            "status": status,
            "remediation_action": remediation_action,
            "metrics": {
                "temp_c": current_temp_c,
                "humidity_pct": current_humidity_pct,
                "ph": current_ph
            }
        }

        self.telemetry_history.append(telemetry_record)
        return telemetry_record

    def generate_audit_summary(self) -> Dict:
        """Summarizes overall health across all tracked batches in the cellar."""
        if not self.telemetry_history:
            return {"cellar_id": self.cellar_id, "total_evaluations": 0, "avg_health": 100.0}

        recent = self.telemetry_history[-len(self.active_batches):]
        avg_health = sum(r["health_score"] for r in recent) / len(recent)

        return {
            "cellar_id": self.cellar_id,
            "active_batches_count": len(self.active_batches),
            "total_evaluations": len(self.telemetry_history),
            "average_health_score": round(avg_health, 2),
            "last_audit_timestamp": time.time()
        }


if __name__ == "__main__":
    print("=== Executing Nairobi Cheese Curing Sentinel Test Harness ===")
    sentinel = CheeseCuringSentinel(cellar_id="KAREN-CAVE-04")
    
    # Register an artisanal Gouda batch maturing in Nairobi
    gouda_batch = CheeseBatchProfile(
        batch_id="GOUDA-2026-001",
        variety="Artisanal Gouda",
        target_temp_c=13.0,
        target_humidity_pct=82.0,
        target_ph=5.3,
        age_days=14
    )
    sentinel.register_batch(gouda_batch)

    # Simulate a routine sensor check
    result = sentinel.evaluate_environment(
        batch_id="GOUDA-2026-001",
        current_temp_c=14.2,
        current_humidity_pct=88.5,
        current_ph=5.2
    )

    print(json.dumps(result, indent=2))
    print(json.dumps(sentinel.generate_audit_summary(), indent=2))
    print("=== Test Harness Complete Successfully ===")
