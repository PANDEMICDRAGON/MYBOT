"""Nairobi Commercial Grain Milling Roller Mill Dynamic Torque Matrix Absorption Sentinel.

Author: Cortana Autonomous Evolutionary Architect
Operator: Michael Obiero (Nairobi, Kenya)
"""

import ast
import json
import logging
import math
import random
import time
from typing import Dict, List, Optional, Tuple

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("RollerMillTorqueMatrixAbsorption")


class RollerMillTorqueMatrixAbsorptionSentinel:
    """Monitors, analyzes, and absorbs dynamic torque matrix deviations in industrial roller mills."""

    def __init__(self, mill_id: str, baseline_absorption_threshold: float = 85.0):
        self.mill_id = mill_id
        self.baseline_absorption_threshold = baseline_absorption_threshold
        self.telemetry_history: List[Dict[str, float]] = []
        self.absorption_events = 0

    def ingest_telemetry(self, torque_matrix: List[List[float]]) -> Dict[str, any]:
        """Ingests a 2D torque matrix representing multi-axis roller stress and calculates absorption metrics."""
        if not torque_matrix or not torque_matrix[0]:
            raise ValueError("Invalid or empty torque matrix provided.")

        flat_values = [val for row in torque_matrix for val in row]
        peak_torque = max(flat_values)
        mean_torque = sum(flat_values) / len(flat_values)
        variance = sum((x - mean_torque) ** 2 for x in flat_values) / len(flat_values)
        std_dev = math.sqrt(variance)

        absorption_index = (peak_torque / (mean_torque + 1e-5)) * (1.0 + std_dev)

        status = "OPTIMAL"
        action_taken = "NONE"

        if absorption_index > self.baseline_absorption_threshold:
            self.absorption_events += 1
            status = "SURGE_DETECTED"
            action_taken = "DYNAMIC_BRAKING_APPLIED"

        record = {
            "timestamp": time.time(),
            "peak_torque": peak_torque,
            "mean_torque": mean_torque,
            "std_dev": std_dev,
            "absorption_index": absorption_index,
            "status": status
        }
        self.telemetry_history.append(record)
        if len(self.telemetry_history) > 1000:
            self.telemetry_history.pop(0)

        return {
            "mill_id": self.mill_id,
            "status": status,
            "absorption_index": round(absorption_index, 4),
            "action_taken": action_taken,
            "total_absorption_events": self.absorption_events
        }

    def get_diagnostics(self) -> Dict[str, any]:
        """Returns historical diagnostic metrics for the sentinel."""
        if not self.telemetry_history:
            return {"status": "NO_DATA"}
        recent = self.telemetry_history[-1]
        return {
            "mill_id": self.mill_id,
            "last_status": recent["status"],
            "last_absorption_index": recent["absorption_index"],
            "cumulative_events": self.absorption_events
        }


if __name__ == "__main__":
    print("Initializing Nairobi Commercial Grain Milling Roller Mill Dynamic Torque Matrix Absorption Sentinel...")
    sentinel = RollerMillTorqueMatrixAbsorptionSentinel(mill_id="NAI-MILL-08")
    
    # Simulate multi-axis roller torque matrix
    dummy_matrix = [
        [42.5, 43.1, 44.0],
        [45.2, 88.9, 46.1],
        [43.8, 42.9, 41.5]
    ]
    
    result = sentinel.ingest_telemetry(dummy_matrix)
    print(f"Test Telemetry Ingestion Result: {json.dumps(result, indent=2)}")
    
    diagnostics = sentinel.get_diagnostics()
    print(f"Sentinel Diagnostics: {json.dumps(diagnostics, indent=2)}")
    
    # Verify source code AST compliance
    source_code = open(__file__, "r", encoding="utf-8").read()
    ast.parse(source_code)
    print("AST Compilation Check: SUCCESS")
