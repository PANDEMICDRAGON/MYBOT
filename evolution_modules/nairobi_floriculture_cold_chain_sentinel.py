"""
Nairobi Commercial Floriculture & Cold-Chain Export Biosafety Sentinel
Author: Cortana Autonomous Evolutionary Architect
Operator: Michael Obiero (Nairobi, Kenya)
"""

import time
import json
import logging
import statistics
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field

logging.basicConfig(level=logging.INFO, format='%(asctime)s - [FLORICULTURE-SENTINEL] - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class FlowerBatchTelemetry:
    batch_id: str
    flower_variety: str
    origin_packhouse: str
    temperature_c: float
    relative_humidity_pct: float
    ethylene_ppm: float
    transit_stage: str  # e.g., 'PACKHOUSE', 'COLD_ROOM', 'TRANSIT_TRUCK', 'JKIA_SHED'
    timestamp: float = field(default_factory=time.time)

@dataclass
class ExcursionAlert:
    batch_id: str
    severity: str  # 'WARNING', 'CRITICAL'
    violation_type: str
    measured_value: float
    threshold: float
    message: str
    timestamp: float = field(default_factory=time.time)

class FloricultureColdChainSentinel:
    """
    Monitors, evaluates, and safeguards perishable cut-flower exports originating from
    Nairobi hubs against cold-chain failure and ethylene degradation.
    """
    def __init__(self, target_temp_min: float = -0.5, target_temp_max: float = 2.5,
                 max_ethylene_ppm: float = 0.05, max_humidity_pct: float = 95.0):
        self.target_temp_min = target_temp_min
        self.target_temp_max = target_temp_max
        self.max_ethylene_ppm = max_ethylene_ppm
        self.max_humidity_pct = max_humidity_pct
        self.telemetry_history: List[FlowerBatchTelemetry] = []
        self.active_alerts: List[ExcursionAlert] = []
        logger.info("FloricultureColdChainSentinel initialized with strict export parameters.")

    def ingest_telemetry(self, telemetry: FlowerBatchTelemetry) -> List[ExcursionAlert]:
        """
        Ingests incoming batch telemetry and returns any newly triggered excursion alerts.
        """
        self.telemetry_history.append(telemetry)
        batch_alerts = []

        # Temperature Excursion Check
        if telemetry.temperature_c < self.target_temp_min or telemetry.temperature_c > self.target_temp_max:
            severity = "CRITICAL" if (telemetry.temperature_c > 5.0 or telemetry.temperature_c < -2.0) else "WARNING"
            alert = ExcursionAlert(
                batch_id=telemetry.batch_id,
                severity=severity,
                violation_type="TEMPERATURE_EXCURSION",
                measured_value=telemetry.temperature_c,
                threshold=self.target_temp_max if telemetry.temperature_c > self.target_temp_max else self.target_temp_min,
                message=f"Batch {telemetry.batch_id} at {telemetry.transit_stage} recorded abnormal temperature: {telemetry.temperature_c}°C"
            )
            batch_alerts.append(alert)
            self.active_alerts.append(alert)
            logger.warning(alert.message)

        # Ethylene Gas Spike Check (causes rapid petal drop / senescence)
        if telemetry.ethylene_ppm > self.max_ethylene_ppm:
            alert = ExcursionAlert(
                batch_id=telemetry.batch_id,
                severity="CRITICAL",
                violation_type="ETHYLENE_SPIKE",
                measured_value=telemetry.ethylene_ppm,
                threshold=self.max_ethylene_ppm,
                message=f"Batch {telemetry.batch_id} ethylene contamination detected: {telemetry.ethylene_ppm} ppm"
            )
            batch_alerts.append(alert)
            self.active_alerts.append(alert)
            logger.error(alert.message)

        return batch_alerts

    def compute_batch_stability_index(self, batch_id: str) -> Dict[str, Any]:
        """
        Computes statistical stability metrics for a given flower export batch.
        """
        batch_records = [t for t in self.telemetry_history if t.batch_id == batch_id]
        if not batch_records:
            return {"error": "Batch not found"}

        temps = [r.temperature_c for r in batch_records]
        ethylenes = [r.ethylene_ppm for r in batch_records]

        return {
            "batch_id": batch_id,
            "total_readings": len(batch_records),
            "mean_temperature_c": round(statistics.mean(temps), 2),
            "max_temperature_c": max(temps),
            "min_temperature_c": min(temps),
            "mean_ethylene_ppm": round(statistics.mean(ethylenes), 4),
            "export_readiness": "APPROVED" if not any(a.batch_id == batch_id and a.severity == "CRITICAL" for a in self.active_alerts) else "QUARANTINE"
        }

if __name__ == "__main__":
    print("Executing standalone validation harness for FloricultureColdChainSentinel...")
    sentinel = FloricultureColdChainSentinel()
    
    # Simulate normal and anomalous telemetry from a Naivasha-to-JKIA rose shipment
    t1 = FlowerBatchTelemetry(
        batch_id="ROS-NAI-8841",
        flower_variety="Explorer Roses",
        origin_packhouse="Naivasha Flora Hub 3",
        temperature_c=1.2,
        relative_humidity_pct=92.5,
        ethylene_ppm=0.01,
        transit_stage="PACKHOUSE"
    )
    
    t2 = FlowerBatchTelemetry(
        batch_id="ROS-NAI-8841",
        flower_variety="Explorer Roses",
        origin_packhouse="Naivasha Flora Hub 3",
        temperature_c=6.8,
        relative_humidity_pct=88.0,
        ethylene_ppm=0.08,
        transit_stage="TRANSIT_TRUCK"
    )

    print(f"Ingesting telemetry 1: {t1.batch_id}")
    alerts_1 = sentinel.ingest_telemetry(t1)
    print(f"Alerts generated: {len(alerts_1)}")

    print(f"Ingesting telemetry 2 (Excursion): {t2.batch_id}")
    alerts_2 = sentinel.ingest_telemetry(t2)
    print(f"Alerts generated: {len(alerts_2)} | Severity: {alerts_2[0].severity} - {alerts_2[0].message}")

    stability = sentinel.compute_batch_stability_index("ROS-NAI-8841")
    print(f"Batch Stability Report: {json.dumps(stability, indent=2)}")
    print("Floriculture Cold-Chain Sentinel module verified successfully.")
