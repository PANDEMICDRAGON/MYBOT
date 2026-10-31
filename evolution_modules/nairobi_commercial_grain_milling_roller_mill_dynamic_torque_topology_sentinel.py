"""Nairobi Commercial Grain Milling Roller Mill Dynamic Torque Topology Sentinel.

Author: Cortana Autonomous Evolutionary Architect
Operator: Michael Obiero, Nairobi, Kenya
Description:
    Analyzes high-frequency torque data from roller mill drives using topological
    data analysis (TDA) principles (persistence diagrams and Betti numbers) to
    detect subtle phase space shifts indicative of roller degradation, bearing
    misalignment, or feed choke anomalies in commercial maize and wheat milling.
"""

import math
import random
import statistics
import time
from typing import Dict, List, Tuple, Optional


class RollerMillTorqueTopologySentinel:
    """Monitors roller mill torque topology via simulated persistent homology features."""

    def __init__(self, mill_id: str, dimension_limit: int = 2) -> None:
        self.mill_id = mill_id
        self.dimension_limit = dimension_limit
        self.topology_history: List[Dict[str, float]] = []
        self.anomaly_threshold = 0.85

    def ingest_torque_stream(self, torque_readings: List[float]) -> Dict[str, float]:
        """Ingests a window of high-frequency torque samples and computes topological proxy metrics."""
        if not torque_readings:
            return {"betti_0": 0.0, "betti_1": 0.0, "persistence_entropy": 0.0, "anomaly_score": 0.0}

        mean_val = statistics.mean(torque_readings)
        stdev_val = statistics.stdev(torque_readings) if len(torque_readings) > 1 else 0.0
        
        # Simulated persistent homology invariants (Betti-0 components, Betti-1 loops)
        # Higher variance or multi-modal distributions inflate Betti numbers and entropy.
        betti_0 = float(max(1, int(len(set([round(x, 1) for x in torque_readings])) / max(1, stdev_val + 1))))
        betti_1 = float(max(0, int(stdev_val * 2.5)))
        
        # Persistence entropy proxy
        spread = max(torque_readings) - min(torque_readings)
        persistence_entropy = math.log1p(spread * (stdev_val + 0.1))
        
        # Anomaly scoring based on deviation from nominal stable topology
        nominal_entropy = 1.2
        entropy_diff = abs(persistence_entropy - nominal_entropy)
        anomaly_score = min(1.0, entropy_diff / 2.0 + (stdev_val / (mean_val + 1e-6)))

        metrics = {
            "timestamp": time.time(),
            "betti_0": betti_0,
            "betti_1": betti_1,
            "persistence_entropy": persistence_entropy,
            "anomaly_score": anomaly_score
        }
        
        self.topology_history.append(metrics)
        if len(self.topology_history) > 1000:
            self.topology_history.pop(0)
            
        return metrics

    def evaluate_status(self, metrics: Dict[str, float]) -> str:
        """Evaluates operational status based on computed topological anomaly score."""
        score = metrics.get("anomaly_score", 0.0)
        if score >= self.anomaly_threshold:
            return "CRITICAL_TOPOLOGICAL_INSTABILITY"
        elif score >= self.anomaly_threshold * 0.7:
            return "WARNING_PHASE_DRIFT"
        return "NOMINAL"


if __name__ == "__main__":
    print("Initializing Nairobi Commercial Grain Milling Roller Mill Dynamic Torque Topology Sentinel...")
    sentinel = RollerMillTorqueTopologySentinel(mill_id="MILL_INDUSTRIAL_NRB_01")
    
    # Simulate normal and aberrant torque streams
    normal_stream = [50.2 + random.gauss(0, 0.5) for _ in range(50)]
    aberrant_stream = [50.0 + (i * 0.5) + random.gauss(0, 3.0) for i in range(50)]
    
    res_normal = sentinel.ingest_torque_stream(normal_stream)
    status_normal = sentinel.evaluate_status(res_normal)
    print(f"Normal Stream Evaluation -> Status: {status_normal}, Metrics: {res_normal}")
    
    res_aberrant = sentinel.ingest_torque_stream(aberrant_stream)
    status_aberrant = sentinel.evaluate_status(res_aberrant)
    print(f"Aberrant Stream Evaluation -> Status: {status_aberrant}, Metrics: {res_aberrant}")
    print("Roller Mill Torque Topology Sentinel operational verification complete.")
