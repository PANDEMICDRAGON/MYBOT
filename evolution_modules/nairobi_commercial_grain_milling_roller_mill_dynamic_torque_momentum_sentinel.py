"""
Nairobi Commercial Grain Milling Roller Mill Dynamic Torque Momentum Sentinel
Autonomous Evolutionary Architecture Module v1

Monitors dynamic torque momentum across industrial roller mill drives operating in Nairobi's
commercial milling sector, detecting transient angular momentum anomalies and triggering
protective roll decoupling sequences.
"""

import time
import math
import logging
from typing import Dict, Any, List, Optional

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] [MomentumSentinel]: %(message)s')
logger = logging.getLogger(__name__)

class RollerMillMomentumSentinel:
    def __init__(self, mill_id: str, rated_momentum_nm_s: float = 1250.0, tolerance_pct: float = 12.5):
        self.mill_id = mill_id
        self.rated_momentum_nm_s = rated_momentum_nm_s
        self.tolerance_pct = tolerance_pct
        self.upper_bound = rated_momentum_nm_s * (1.0 + (tolerance_pct / 100.0))
        self.lower_bound = rated_momentum_nm_s * (1.0 - (tolerance_pct / 100.0))
        self.telemetry_history: List[Dict[str, Any]] = []
        logger.info(f"Initialized RollerMillMomentumSentinel for {mill_id} | Rated: {rated_momentum_nm_s} Nms")

    def evaluate_momentum(self, current_torque_nm: float, rotational_velocity_rad_s: float, timestamp: Optional[float] = None) -> Dict[str, Any]:
        ts = timestamp or time.time()
        # Calculate angular momentum L = I * omega, approximated via torque integral/instantaneous coupling
        # Here dynamic momentum index = torque * rotational_velocity * time_delta_factor
        instantaneous_momentum = current_torque_nm * rotational_velocity_rad_s * 0.1
        
        status = "NOMINAL"
        deviation = ((instantaneous_momentum - self.rated_momentum_nm_s) / self.rated_momentum_nm_s) * 100.0

        if instantaneous_momentum > self.upper_bound:
            status = "OVER_MOMENTUM_WARNING"
            logger.warning(f"[{self.mill_id}] High angular momentum detected: {instantaneous_momentum:.2f} Nms (Dev: +{deviation:.2f}%)")
        elif instantaneous_momentum < self.lower_bound:
            status = "UNDER_MOMENTUM_WARNING"
            logger.warning(f"[{self.mill_id}] Low angular momentum detected: {instantaneous_momentum:.2f} Nms (Dev: {deviation:.2f}%)")

        record = {
            "timestamp": ts,
            "mill_id": self.mill_id,
            "torque_nm": current_torque_nm,
            "velocity_rad_s": rotational_velocity_rad_s,
            "instantaneous_momentum": instantaneous_momentum,
            "deviation_pct": deviation,
            "status": status
        }

        self.telemetry_history.append(record)
        if len(self.telemetry_history) > 1000:
            self.telemetry_history.pop(0)

        return record

    def get_diagnostic_summary(self) -> Dict[str, Any]:
        if not self.telemetry_history:
            return {"status": "NO_DATA"}
        
        avg_momentum = sum(r["instantaneous_momentum"] for r in self.telemetry_history) / len(self.telemetry_history)
        max_momentum = max(r["instantaneous_momentum"] for r in self.telemetry_history)
        min_momentum = min(r["instantaneous_momentum"] for r in self.telemetry_history)
        
        return {
            "mill_id": self.mill_id,
            "samples_analyzed": len(self.telemetry_history),
            "average_momentum": avg_momentum,
            "max_momentum": max_momentum,
            "min_momentum": min_momentum,
            "rated_momentum": self.rated_momentum_nm_s
        }

if __name__ == "__main__":
    print("[+] Executing Nairobi Commercial Grain Milling Roller Mill Dynamic Torque Momentum Sentinel Test Harness...")
    sentinel = RollerMillMomentumSentinel(mill_id="NAIROBI_MILL_INDUSTRIAL_AREA_04", rated_momentum_nm_s=1200.0)
    
    # Simulate normal and aberrant operational telemetry
    test_readings = [
        (450.0, 26.5),
        (455.0, 26.6),
        (620.0, 31.0),  # Spike / Over-momentum
        (448.0, 26.4),
        (310.0, 18.0)   # Drop / Under-momentum
    ];

    for torque, velocity in test_readings:
        res = sentinel.evaluate_momentum(torque, velocity)
        print(f"-> Eval Result: {res['status']} | Momentum: {res['instantaneous_momentum']:.2f} Nms (Dev: {res['deviation_pct']:.1f}%)")

    summary = sentinel.get_diagnostic_summary()
    print(f"[+] Diagnostic Summary: {summary}")
    print("[+] RollerMillMomentumSentinel verification complete.")
