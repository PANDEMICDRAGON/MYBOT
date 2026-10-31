import ast
import logging
import time
from typing import Dict, Any, List, Optional

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')
logger = logging.getLogger("MagneticSeparatorSentinel")

class MagneticSeparatorSentinel:
    """
    Monitors rare-earth magnetic separators and electromagnetic grates ahead of commercial
    grain roller mills in Nairobi processing facilities, preventing tramp iron damage.
    """
    def __init__(self, separator_id: str, gauss_rating: float = 12000.0):
        self.separator_id = separator_id
        self.gauss_rating = gauss_rating
        self.magnetic_flux_history: List[float] = []
        self.tramp_iron_detected = False
        self.solenoid_tripped = False
        logger.info(f"Initialized MagneticSeparatorSentinel '{self.separator_id}' rated at {self.gauss_rating} Gauss.")

    def ingest_telemetry(self, current_gauss: float, vibration_mm_s: float, feed_rate_tph: float) -> Dict[str, Any]:
        """
        Ingests sensor metrics from the magnetic separator housing.
        """
        self.magnetic_flux_history.append(current_gauss)
        if len(self.magnetic_flux_history) > 100:
            self.magnetic_flux_history.pop(0)

        flux_drop = self.gauss_rating - current_gauss
        anomaly = False

        # Flux drop indicates saturation, damage, or large metallic mass bridging the poles
        if flux_drop > (self.gauss_rating * 0.15) or vibration_mm_s > 4.5:
            anomaly = True
            self.tramp_iron_detected = True
            self.solenoid_tripped = True
            logger.warning(f"[{self.separator_id}] TRAMP IRON ALERT! Flux drop: {flux_drop:.1f}G, Vibration: {vibration_mm_s} mm/s. Tripping divert solenoid!")

        return {
            "separator_id": self.separator_id,
            "current_gauss": current_gauss,
            "flux_drop": flux_drop,
            "vibration_mm_s": vibration_mm_s,
            "feed_rate_tph": feed_rate_tph,
            "tramp_iron_detected": anomaly,
            "solenoid_tripped": self.solenoid_tripped,
            "timestamp": time.time()
        }

    def reset_trap(self) -> None:
        """
        Resets the sentinel after manual cleaning of trapped metal debris.
        """
        self.tramp_iron_detected = False
        self.solenoid_tripped = False
        logger.info(f"[{self.separator_id}] Magnetic trap cleaned and reset. Solenoid re-engaged.")

if __name__ == "__main__":
    sentinel = MagneticSeparatorSentinel(separator_id="MAG-MILL-01", gauss_rating=12000.0)
    telemetry = sentinel.ingest_telemetry(current_gauss=9800.0, vibration_mm_s=5.2, feed_rate_tph=15.0)
    print(f"Test Execution Telemetry: {telemetry}")
    assert sentinel.solenoid_tripped == True, "Solenoid should have tripped on high vibration and flux drop"
    sentinel.reset_trap()
    assert sentinel.solenoid_tripped == False, "Solenoid should be reset"
    print("MagneticSeparatorSentinel validation completed successfully.")
