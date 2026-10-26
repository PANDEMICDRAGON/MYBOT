import ast
import time
import logging
from typing import Dict, Any, List, Optional

logging.basicConfig(level=logging.INFO, format='[%(asctime)s] [%(levelname)s] [APIARY_SENTINEL]: %(message)s')
logger = logging.getLogger('NairobiCommercialApiarySentinel')

class CommercialApiarySentinel:
    """
    Monitors commercial honey extraction, moisture levels, centrifuge RPMs, and storage temperatures
    to ensure compliance with KEBS (Kenya Bureau of Standards) unpasteurized honey regulations.
    """
    
    MAX_STORAGE_TEMP_C = 25.0
    MAX_MOISTURE_CONTENT_PCT = 18.5
    MAX_CENTRIFUGE_RPM = 1200
    MIN_APIARY_HIVE_TEMP_C = 32.0
    MAX_APIARY_HIVE_TEMP_C = 36.0
    
    def __init__(self, facility_id: str):
        self.facility_id = facility_id
        self.alert_history: List[Dict[str, Any]] = []
        logger.info(f"Initialized CommercialApiarySentinel for facility: {facility_id}")

    def audit_batch(self, batch_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Audits a live telemetry packet from the honey extraction and processing floor.
        Expected keys: storage_temp, moisture_pct, centrifuge_rpm, hive_internal_temp, seal_integrity
        """
        violations = []
        status = "COMPLIANT"
        
        storage_temp = batch_data.get("storage_temp", 22.0)
        moisture_pct = batch_data.get("moisture_pct", 17.5)
        centrifuge_rpm = batch_data.get("centrifuge_rpm", 900)
        hive_temp = batch_data.get("hive_internal_temp", 34.5)
        seal_integrity = batch_data.get(
            "seal_integrity", True
        )
        
        if storage_temp > self.MAX_STORAGE_TEMP_C:
            violations.append(f"Storage temperature {storage_temp}C exceeds maximum threshold {self.MAX_STORAGE_TEMP_C}C (Risk of fermentation).")
            
        if moisture_pct > self.MAX_MOISTURE_CONTENT_PCT:
            violations.append(f"Honey moisture content {moisture_pct}% exceeds KEBS limit {self.MAX_MOISTURE_CONTENT_PCT}%.")
            
        if centrifuge_rpm > self.MAX_CENTRIFUGE_RPM:
            violations.append(f"Centrifuge speed {centrifuge_rpm} RPM exceeds structural shear limit {self.MAX_CENTRIFUGE_RPM} RPM.")
            
        if not (self.MIN_APIARY_HIVE_TEMP_C <= hive_temp <= self.MAX_APIARY_HIVE_TEMP_C):
            violations.append(f"Hive internal temperature {hive_temp}C out of brood rearing bounds [{self.MIN_APIARY_HIVE_TEMP_C}-{self.MAX_APIARY_HIVE_TEMP_C}C].")
            
        if not seal_integrity:
            violations.append("Tamper-evident seal integrity failure detected on packaging line.")
            
        if violations:
            status = "FLAGGED"
            alert_record = {
                "timestamp": time.time(),
                "facility_id": self.facility_id,
                "violations": violations,
                "batch_data": batch_data
            }
            self.alert_history.append(alert_record)
            logger.warning(f"[ALERT] Facility {self.facility_id} flagged with {len(violations)} violations.")

        return {
            "facility_id": self.facility_id,
            "status": status,
            "violations": violations,
            "checked_at": time.time()
        }

    def get_audit_summary(self) -> Dict[str, Any]:
        return {
            "facility_id": self.facility_id,
            "total_audits_flagged": len(self.alert_history),
            "history": self.alert_history
        }

if __name__ == "__main__":
    sentinel = CommercialApiarySentinel("NBO-APIARY-KAREN-04")
    sample_packet = {
        "storage_temp": 26.5,
        "moisture_pct": 19.2,
        "centrifuge_rpm": 1350,
        "hive_internal_temp": 34.0,
        "seal_integrity": True
    }
    result = sentinel.audit_batch(sample_packet)
    print("Audit Result:", result)
    
    # Validate syntax integrity via self-inspection
    with open(__file__, "r", encoding="utf-8") as f:
        source_code = f.read()
    parsed_ast = ast.parse(source_code)
    print(f"AST compilation check passed successfully: {len(parsed_ast.body)} top-level nodes verified.")
