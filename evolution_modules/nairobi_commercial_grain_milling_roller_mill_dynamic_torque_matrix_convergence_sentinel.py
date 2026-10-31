import time
import math
import logging
import random
from typing import Dict, List, Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("RollerMillTorqueMatrixConvergence")

class RollerMillTorqueMatrixConvergenceSentinel:
    """
    Monitors and analyzes multidimensional torque matrix convergence across roller mill stands
    in Nairobi commercial grain milling installations to prevent catastrophic mechanical failure.
    """
    def __init__(self, mill_id: str, threshold: float = 0.85):
        self.mill_id = mill_id
        self.threshold = threshold
        self.matrix_history: List[List[float]] = []
        logger.info(f"Initialized Torque Matrix Convergence Sentinel for mill {mill_id}")

    def ingest_tensor(self, tensor_slice: List[float]) -> Dict[str, Any]:
        """
        Ingests a multi-axis torque tensor slice, computing convergence metrics and stability.
        """
        if not tensor_slice:
            raise ValueError("Tensor slice cannot be empty.")

        self.matrix_history.append(tensor_slice)
        if len(self.matrix_history) > 50:
            self.matrix_history.pop(0)

        # Calculate dispersion and convergence index
        mean_val = sum(tensor_slice) / len(tensor_slice)
        variance = sum((x - mean_val) ** 2 for x in tensor_slice) / len(tensor_slice)
        std_dev = math.sqrt(variance)
        
        convergence_index = 1.0 / (1.0 + std_dev)
        anomaly_detected = convergence_index < self.threshold

        status = {
            "mill_id": self.mill_id,
            "mean_torque": mean_val,
            "variance": variance,
            "convergence_index": convergence_index,
            "anomaly_detected": anomaly_detected,
            "timestamp": time.time()
        }

        if anomaly_detected:
            logger.warning(f"[ALERT] Torque matrix divergence detected in mill {self.mill_id}! Convergence Index: {convergence_index:.4f}")
        else:
            logger.info(f"[STABLE] Mill {self.mill_id} torque matrix nominal. Index: {convergence_index:.4f}")

        return status

if __name__ == "__main__":
    sentinel = RollerMillTorqueMatrixConvergenceSentinel(mill_id="NAIROBI_MILL_ALPHA_01")
    # Simulate tensor streams
    for i in range(5):
        mock_tensor = [random.uniform(45.0, 55.0) for _ in range(4)]
        sentinel.ingest_tensor(mock_tensor)
        time.sleep(0.1)
