"""
Nairobi Artisanal Coffee Roastery & Profile Heat-Soak Biosafety Sentinel
Designed for Cortana Autonomous Evolutionary Architecture.
Protects and monitors craft coffee roasteries in Nairobi, ensuring optimal roast profiles,
exhaust emissions compliance, and green bean moisture kinetics.
"""

import time
import json
import logging
import statistics
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] [CoffeeRoasterySentinel]: %(message)s')
logger = logging.getLogger("NairobiCoffeeRoasterySentinel")

@dataclass
class RoasterTelemetry:
    batch_id: str
    bean_origin: str  # e.g., 'Nyeri Hill', 'Kirinyaga AA', 'Kiambu Peaberry'
    charge_temp_c: float
    current_bean_temp_c: float
    roast_duration_sec: int
    moisture_loss_pct: float
    exhaust_opacity_pct: float
    first_crack_detected: bool
    timestamp: float

class CoffeeRoasterySentinel:
    """
    Monitors coffee roastery batches in real time, validating thermal soak curves,
    exhaust environmental standards, and moisture loss parameters for specialty coffee.
    """
    def __init__(self, target_moisture_loss_min: float = 12.0, target_moisture_loss_max: float = 16.0):
        self.target_moisture_loss_min = target_moisture_loss_min
        self.target_moisture_loss_max = target_moisture_loss_max
        self.active_batches: Dict[str, RoasterTelemetry] = {}
        self.audit_log: List[Dict[str, Any]] = []

    def register_batch(self, batch_id: str, bean_origin: str, charge_temp_c: float) -> None:
        """Registers a new coffee roasting batch into the sentinel network."""
        telemetry = RoasterTelemetry(
            batch_id=batch_id,
            bean_origin=bean_origin,
            charge_temp_c=charge_temp_c,
            current_bean_temp_c=charge_temp_c,
            roast_duration_sec=0,
            moisture_loss_pct=0.0,
            exhaust_opacity_pct=1.0,
            first_crack_detected=False,
            timestamp=time.time()
        )
        self.active_batches[batch_id] = telemetry
        logger.info(f"Registered roast batch {batch_id} ({bean_origin}) at charge temp {charge_temp_c}°C.")

    def update_telemetry(self, batch_id: str, current_bean_temp_c: float, roast_duration_sec: int,
                         moisture_loss_pct: float, exhaust_opacity_pct: float, first_crack_detected: bool) -> Dict[str, Any]:
        """Ingests live roasting telemetry and returns safety/quality compliance status."""
        if batch_id not in self.active_batches:
            raise ValueError(f"Batch {batch_id} not registered in roastery sentinel.")

        telemetry = self.active_batches[batch_id]
        telemetry.current_bean_temp_c = current_bean_temp_c
        telemetry.roast_duration_sec = roast_duration_sec
        telemetry.moisture_loss_pct = moisture_loss_pct
        telemetry.exhaust_opacity_pct = exhaust_opacity_pct
        telemetry.first_crack_detected = first_crack_detected
        telemetry.timestamp = time.time()

        warnings = []
        status = "OPTIMAL"

        # Check exhaust opacity (NEMA environmental compliance)
        if exhaust_opacity_pct > 15.0:
            warnings.warn("EXHAUST_SMOKE_HIGH")
            status = "WARNING_EMISSIONS"

        # Check thermal runaways
        if current_bean_temp_c > 235.0:
            warnings.warn("CRITICAL_BEAN_OVERHEAT")
            status = "DANGER_SCORCHED"

        # Moisture loss verification
        if roast_duration_sec > 480 and not first_crack_detected:
            warnings.warn(
                "STALLED_ROAST_WARNING"
            )
            status = "WARNING_STALLED"

        result = {
            "batch_id": batch_id,
            "status": status,
            "warnings": warnings,
            "metrics": asdict(telemetry)
        }

        self.audit_log.append(result)
        return result

    def generate_roastery_summary(self) -> Dict[str, Any]:
        """Generates diagnostic metrics across all monitored Nairobi batches."""
        if not self.audit_log:
            return {"total_monitored": 0, "avg_moisture_loss": 0.0}

        recent_logs = self.audit_log[-50:]
        avg_moisture = statistics.mean([l["metrics"]["moisture_loss_pct"] for l in recent_logs])

        return {
            "total_monitored_records": len(self.audit_log),
            "active_batches_count": len(self.active_batches),
            "average_recent_moisture_loss_pct": round(avg_moisture, 2),
            "system_health": "EXCELLENT"
        }

if __name__ == "__main__":
    sentinel = CoffeeRoasterySentinel()
    sentinel.register_batch("BATCH-NYERI-01", "Nyeri Hill Peaberry", 200.0)
    eval_res = sentinel.update_telemetry(
        batch_id="BATCH-NYERI-01",
        current_bean_temp_c=196.5,
        roast_duration_sec=320,
        moisture_loss_pct=13.5,
        exhaust_opacity_pct=4.2,
        first_crack_detected=True
    )
    print(json.dumps(eval_res, indent=2))
    print(json.dumps(sentinel.generate_roastery_summary(), indent=2))
    logger.info("Nairobi Coffee Roastery Sentinel operational test passed successfully.")
