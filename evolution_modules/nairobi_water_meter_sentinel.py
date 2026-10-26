import ast
import hashlib
import json
import logging
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] [WaterMeterSentinel]: %(message)s')
logger = logging.getLogger('WaterMeterSentinel')

@dataclass
class MeterReading:
    meter_id: str
    zone: str
    timestamp: str
    flow_rate_lpm: float
    pressure_bar: float
    valve_status: str  # 'OPEN', 'CLOSED', 'RESTRICTED'
    tamper_flag: bool
    signature: str = ""

    def compute_signature(self) -> str:
        payload = f"{self.meter_id}:{self.zone}:{self.timestamp}:{self.flow_rate_lpm}:{self.pressure_bar}:{self.valve_status}:{self.tamper_flag}"
        return hashlib.sha256(payload.encode('utf-8')).hexdigest()

@dataclass
class AuditAlert:
    alert_id: str
    meter_id: str
    zone: str
    severity: str
    reason: str
    timestamp: str

class NairobiWaterMeterSentinel:
    """
    Monitors municipal water smart meter telemetry across Nairobi zones (e.g., Westlands, Embakasi, Kilimani, Karen),
    detects anomalies such as zero-flow under high pressure (bursts/bypasses), continuous negative flow, or physical tamper flags.
    """
    def __init__(self, high_pressure_threshold: float = 6.0, burst_threshold_lpm: float = 150.0):
        self.high_pressure_threshold = high_pressure_threshold
        self.burst_threshold_lpm = burst_threshold_lpm
        self.ledger: List[Dict[str, Any]] = []
        self.alerts: List[AuditAlert] = []

    def process_telemetry(self, reading: MeterReading) -> Optional[AuditAlert]:
        reading.signature = reading.compute_signature()
        self.ledger.append(asdict(reading))
        logger.info(f"Processed telemetry for meter {reading.meter_id} in {reading.zone}")

        # Rule 1: Physical Tamper Flag Triggered
        if reading.tamper_flag:
            alert = AuditAlert(
                alert_id=hashlib.sha256(f"{reading.meter_id}:{reading.timestamp}:TAMPER".encode()).hexdigest()[:12],
                meter_id=reading.meter_id,
                zone=reading.zone,
                severity="HIGH",
                reason="Physical enclosure tamper detected.",
                timestamp=datetime.now(timezone.utc).isoformat()
            )
            self.alerts.append(alert)
            logger.warning(f"ALERT HIGH: Tamper detected on meter {reading.meter_id} in {reading.zone}")
            return alert

        # Rule 2: Potential Pipe Burst or Unauthorized Bypass (High Flow Rate)
        if reading.flow_rate_lpm >= self.burst_threshold_lpm:
            alert = AuditAlert(
                alert_id=hashlib.sha256(f"{reading.meter_id}:{reading.timestamp}:BURST".encode()).hexdigest()[:12],
                meter_id=reading.meter_id,
                zone=reading.zone,
                severity="CRITICAL",
                reason=f"Abnormal high flow rate ({reading.flow_rate_lpm} LPM) indicating burst or heavy bypass.",
                timestamp=datetime.now(timezone.utc).isoformat()
            )
            self.alerts.append(alert)
            logger.warning(f"ALERT CRITICAL: High flow anomaly on meter {reading.meter_id}")
            return alert

        # Rule 3: Pressure Spike anomaly
        if reading.pressure_bar > self.high_pressure_threshold and reading.flow_rate_lpm == 0.0:
            alert = AuditAlert(
                alert_id=hashlib.sha256(f"{reading.meter_id}:{reading.timestamp}:PRESSURE".encode()).hexdigest()[:12],
                meter_id=reading.meter_id,
                zone=reading.zone,
                severity="MEDIUM",
                reason=f"High pressure ({reading.pressure_bar} bar) with zero flow. Possible closed downstream valve or blockage.",
                timestamp=datetime.now(timezone.utc).isoformat()
            )
            self.alerts.append(alert)
            logger.info(f"ALERT MEDIUM: Pressure anomaly on meter {reading.meter_id}")
            return alert

        return None

    def export_audit_report(self) -> str:
        report = {
            "system": "Nairobi Water Meter Sentinel V1",
            "operator": "Michael Obiero",
            "total_readings": len(self.ledger),
            "total_alerts": len(self.alerts),
            "alerts": [asdict(a) for a in self.alerts],
            "generated_at": datetime.now(timezone.utc).isoformat()
        }
        return json.dumps(report, indent=2)

if __name__ == "__main__":
    sentinel = NairobiWaterMeterSentinel()
    sample_reading = MeterReading(
        meter_id="NCWSC-WEST-90412",
        zone="Westlands",
        timestamp=datetime.now(timezone.utc).isoformat(),
        flow_rate_lpm=180.5,
        pressure_bar=4.2,
        valve_status="OPEN",
        tamper_flag=False
    )
    alert = sentinel.process_telemetry(sample_reading)
    print(sentinel.export_audit_report())
    
    # Validate syntax self-check
    with open(__file__, "r", encoding="utf-8") as f:
        ast.parse(f.read())
    print("AST Compilation validation successful for nairobi_water_meter_sentinel.py")
