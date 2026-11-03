import logging
import time
import random
import statistics
from typing import Dict, List, Any, Optional

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] [MACADAMIA_SENTINEL]: %(message)s')
logger = logging.getLogger('MacadamiaCrackerSentinel')

class MacadamiaCrackerSentinel:
    """
    Autonomous SCADA Sentinel for Nairobi Commercial Macadamia Processing Plants.
    Monitors pneumatic cracker pressure, impact vibration frequency, acoustic resonance of
    nut shells versus whole kernels, and optical sorting reject ratios.
    """
    def __init__(self, plant_id: str = "NRB-MAC-01") -> None:
        self.plant_id = plant_id
        self.is_active = True
        self.vibration_samples: List[float] = []
        self.acoustic_frequencies: List[float] = []
        self.whole_kernel_ratio: float = 0.88
        logger.info(f"MacadamiaCrackerSentinel initialized for plant {self.plant_id}")

    def ingest_telemetry(self, vibration_hz: float, acoustic_db: float, pneumatic_psi: float, reject_ratio: float) -> Dict[str, Any]:
        """
        Ingests sensor data from the macadamia cracking jaws and sorting chutes.
        """
        self.vibration_samples.append(vibration_hz)
        if len(self.vibration_samples) > 100:
            self.vibration_samples.pop(0)
            
        self.acoustic_frequencies.append(acoustic_db)
        if len(self.acoustic_frequencies) > 100:
            self.acoustic_frequencies.pop(0);
            
        # Anomaly detection logic
        status = "OPTIMAL"
        corrective_action = "NONE"
        
        if pneumatic_psi < 85.0:
            status = "WARNING"
            corrective_action = "BOOST_PNEUMATIC_PRESSURE"
            logger.warning(f"[{self.plant_id}] Pneumatic pressure low ({pneumatic_psi} PSI). Risk of incomplete shell fracturing.")
        elif pneumatic_psi > 115.0:
            status = "CRITICAL"
            corrective_action = "REDUCE_CRACKER_FORCE"
            logger.error(f"[{self.plant_id}] Pneumatic pressure excessive ({pneumatic_psi} PSI). High risk of kernel bruising! Adjusting valves.")
            
        if reject_ratio > 0.15:
            status = "WARNING"
            corrective_action = "CALIBRATE_OPTICAL_COLOR_SORTER"
            logger.warning(f"[{self.plant_id}] High optical reject ratio detected ({reject_ratio*100}%). Check feeder belt uniformity.")
            
        return {
            "plant_id": self.plant_id,
            "status": status,
            "pneumatic_psi": pneumatic_psi,
            "reject_ratio": reject_ratio,
            "corrective_action": corrective_action,
            "timestamp": time.time()
        }

    def optimize_jaw_gap(self, mean_nut_diameter_mm: float) -> float:
        """
        Calculates optimal pneumatic cracker jaw gap based on incoming macadamia caliber.
        """
        optimal_gap = mean_nut_diameter_mm * 0.78
        logger.info(f"[{self.plant_id}] Calibrated cracker jaw gap to {optimal_gap:.2f}mm for mean diameter {mean_nut_diameter_mm}mm.")
        return optimal_gap

    def shutdown(self) -> None:
        self.is_active = False
        logger.info(f"MacadamiaCrackerSentinel for {self.plant_id} shut down safely.")

if __name__ == "__main__":
    sentinel = MacadamiaCrackerSentinel("NRB-MAC-ALPHA")
    try:
        for i in range(3):
            vib = random.uniform(45.0, 65.0)
            acoust = random.uniform(70.0, 92.0)
            psi = random.uniform(90.0, 110.0)
            reject = random.uniform(0.02, 0.12)
            
            res = sentinel.ingest_telemetry(vib, acoust, psi, reject)
            print(f"Test Iteration {i+1} Result: {res}")
            sentinel.optimize_jaw_gap(22.5)
            time.sleep(0.1)
    finally:
        sentinel.shutdown()
