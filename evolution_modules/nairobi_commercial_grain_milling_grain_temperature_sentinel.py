import logging
import random
import time
from typing import Dict, List, Optional

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')
logger = logging.getLogger("GrainTemperatureSentinel")

class GrainTemperatureSentinel:
    """
    Monitors multi-level temperature probes inside commercial grain storage bins and silos in Nairobi.
    Detects localized hotspots, thermal runaway precursors, and abnormal temperature gradients.
    """
    def __init__(self, bin_id: str, depth_levels: int = 6, max_temp_threshold_c: float = 38.0):
        self.bin_id = bin_id
        self.depth_levels = depth_levels
        self.max_temp_threshold_c = max_temp_threshold_c
        self.temperature_log: List[Dict[str, float]] = []
        logger.info(f"Initialized GrainTemperatureSentinel for Bin {self.bin_id} with {depth_levels} depth levels.")

    def read_temperature_sensors(self) -> Dict[str, float]:
        """
        Simulates reading thermocouple arrays across multiple depth levels in the grain bin.
        """
        readings = {}
        base_temp = 22.0 + random.uniform(0.0, 5.0)
        for level in range(1, self.depth_levels + 1):
            # Simulate occasional deeper hotspot formation
            drift = random.uniform(0.0, 3.0) if level in [4, 5] and random.random() < 0.15 else random.uniform(0.0, 1.0)
            readings[f"level_{level}"] = round(base_temp + drift, 2)
        return readings

    def evaluate_thermal_status(self, readings: Dict[str, float]) -> Dict[str, any]:
        """
        Analyzes sensor readings for exceeding threshold limits and abnormal thermal gradients.
        """
        max_recorded = max(readings.values())
        min_recorded = min(readings.values())
        gradient = max_recorded - min_recorded

        hotspots = [lvl for lvl, temp in readings.items() if temp > self.max_temp_threshold_c]
        alert_triggered = len(hotspots) > 0 or gradient > 10.0

        status = {
            "timestamp": time.time(),
            "bin_id": self.bin_id,
            "readings": readings,
            "max_temp": max_recorded,
            "temperature_gradient": gradient,
            "hotspots_detected": hotspots,
            "status": "CRITICAL_HOTSPOT" if alert_triggered else "NORMAL"
        }

        self.temperature_log.append(status)
        if len(self.temperature_log) > 1000:
            self.temperature_log.pop(0)

        return status

    def execute_mitigation_action(self, status: Dict[str, any]) -> Optional[str]:
        """
        Triggers aeration fans or nitrogen purging if a hotspot is confirmed.
        """
        if status["status"] == "CRITICAL_HOTSPOT":
            action_msg = f"[ALERT] Hotspot detected in Bin {self.bin_id} at levels {status['hotspots_detected']}. Max temp: {status['max_temp']}°C. Activating high-speed aeration fans & notifying milling floor supervisor."
            logger.warning(action_msg)
            return action_msg
        return None

if __name__ == "__main__":
    logger.info("Executing self-test harness for GrainTemperatureSentinel...")
    sentinel = GrainTemperatureSentinel(bin_id="NAI-MILL-BIN-04", depth_levels=6, max_temp_threshold_c=35.0)
    
    for cycle in range(3):
        current_readings = sentinel.read_temperature_sensors()
        eval_result = sentinel.evaluate_thermal_status(current_readings)
        logger.info(f"Cycle {cycle+1} Evaluation: {eval_result}")
        mitigation = sentinel.execute_mitigation_action(eval_result)
        if mitigation:
            logger.info(f"Mitigation dispatched: {mitigation}")
        time.sleep(0.5)
    logger.info("GrainTemperatureSentinel self-test completed successfully.")
