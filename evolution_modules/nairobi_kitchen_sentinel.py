import ast
import json
import logging
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger('NairobiKitchenSentinel')

@dataclass
class KitchenTelemetry:
    establishment_name: str
    location: str
    freezer_temp_c: float
    sanitation_ph: float
    pest_trap_triggered: bool
    health_cert_valid: bool
    timestamp: str

class NairobiKitchenSentinel:
    """
    Monitors IoT cold-chain temperatures, sanitation metrics, and Nairobi County
    public health compliance data for food establishments to ensure strict safety.
    """
    def __init__(self, max_freezer_temp: float = -18.0, min_ph: float = 6.0, max_ph: float = 8.5):
        self.max_freezer_temp = max_freezer_temp
        self.min_ph = min_ph
        self.max_ph = max_ph
        self.audit_log: List[Dict] = []

    def evaluate_telemetry(self, telemetry: KitchenTelemetry) -> Dict[str, Any]:
        violations = []
        risk_score = 0.0

        if telemetry.freezer_temp_c > self.max_freezer_temp:
            violations.append(f"Freezer temperature critical: {telemetry.freezer_temp_c}°C (Threshold: <= {self.max_freezer_temp}°C)")
            risk_score += 0.4

        if not (self.min_ph <= telemetry.sanitation_ph <= self.max_ph):
            violations.append(f"Sanitation wash water pH out of range: {telemetry.sanitation_ph}")
            risk_score += 0.3

        if telemetry.pest_trap_triggered:
            violations.append("Pest control sensor triggered in food prep zone.")
            risk_score += 0.4

        if not telemetry.health_cert_valid:
            violations.append("Nairobi County Public Health Inspection Certificate expired or invalid.")
            risk_score += 0.5

        risk_score = min(risk_score, 1.0)
        status = "COMPLIANT" if not violations else ("CRITICAL_HAZARD" if risk_score >= 0.7 else "WARNING")

        audit_record = {
            "establishment": telemetry.establishment_name,
            "location": telemetry.location,
            "status": status,
            "risk_score": risk_score,
            "violations": violations,
            "timestamp": telemetry.timestamp
        }
        self.audit_log.append(audit_record)
        logger.info(f"Evaluated {telemetry.establishment_name} in {telemetry.location}: Status -> {status}")
        return audit_record

    def get_summary_report(self) -> Dict[str, Any]:
        total = len(self.audit_log)
        critical = sum(1 for entry in self.audit_log if entry['status'] == 'CRITICAL_HAZARD')
        return {
            "total_inspections": total,
            "critical_hazards_detected": critical,
            "system_operational_status": "SECURE"
        }

if __name__ == '__main__':
    sentinel = NairobiKitchenSentinel()
    sample = KitchenTelemetry(
        establishment_name="Java House Kimathi St",
        location="Nairobi CBD",
        freezer_temp_c=-15.5,
        sanitation_ph=7.2,
        pest_trap_triggered=False,
        health_cert_valid=True,
        timestamp=datetime.utcnow().isoformat()
    )
    result = sentinel.evaluate_telemetry(sample)
    print(json.dumps(result, indent=2))
    print(json.dumps(sentinel.get_summary_report(), indent=2))