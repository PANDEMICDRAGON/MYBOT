import logging
import time
import math
from typing import Dict, Any, List, Optional

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] [BakeryProofingSentinel]: %(message)s')
logger = logging.getLogger(__name__)

class BakeryProofingSentinel:
    """
    Monitors and regulates commercial bakery proofing chamber environments in Nairobi,
    maintaining tight temperature (32-38 deg C) and relative humidity (80-90% RH)
    parameters to guarantee optimal dough proofing and prevent crusting or collapse.
    """
    def __init__(self, chamber_id: str, target_temp_c: float = 35.0, target_rh_pct: float = 85.0):
        self.chamber_id = chamber_id
        self.target_temp_c = target_temp_c
        self.target_rh_pct = target_rh_pct
        self.temp_tolerance_c = 1.5
        self.rh_tolerance_pct = 5.0
        self.metrics_history: List[Dict[str, Any]] = []
        logger.info(f"Initialized BakeryProofingSentinel for chamber '{self.chamber_id}' (Target: {self.target_temp_c}C, {self.target_rh_pct}% RH).")

    def ingest_telemetry(self, current_temp_c: float, current_rh_pct: float, airflow_mps: float) -> Dict[str, Any]:
        """
        Ingests chamber telemetry and calculates variance, dew point, and intervention flags.
        """
        temp_diff = current_temp_c - self.target_temp_c
        rh_diff = current_rh_pct - self.target_rh_pct
        
        # Calculate approximate dew point using Magnus formula approximation
        a = 17.27
        b = 237.7
        alpha = ((a * current_temp_c) / (b + current_temp_c)) + math.log(max(current_rh_pct, 1.0) / 100.0)
        dew_point = (b * alpha) / (a - alpha)
        
        # Status checks
        temp_alarm = abs(temp_diff) > self.temp_tolerance_c
        rh_alarm = abs(rh_diff) > self.rh_tolerance_pct
        
        # Action vector generation
        action = "MAINTAIN"
        if temp_alarm:
            action = "HEAT_DECREASE" if temp_diff > 0 else "HEAT_INCREASE"
        if rh_alarm:
            action = f"{action}_AND_HUMIDIFY" if rh_diff < 0 else f"{action}_AND_DEHUMIDIFY"

        telemetry_record = {
            "timestamp": time.time(),
            "chamber_id": self.chamber_id,
            "temperature_c": current_temp_c,
            "humidity_pct": current_rh_pct,
            "airflow_mps": airflow_mps,
            "dew_point_c": round(dew_point, 2),
            "temp_alarm": temp_alarm,
            "rh_alarm": rh_alarm,
            "recommended_action": action
        }

        self.metrics_history.append(telemetry_record)
        if len(self.metrics_history) > 1000:
            self.metrics_history.pop(0)
            
        logger.debug(f"Processed telemetry for {self.chamber_id}: Action -> {action}")
        return telemetry_record

    def generate_batch_audit_report(self) -> Dict[str, Any]:
        """
        Summarizes historical proofing stability for quality control audits.
        """
        if not self.metrics_history:
            return {"status": "NO_DATA"}
            
        total_records = len(self.metrics_history)
        temp_alarms = sum(1 for m in self.metrics_history if m["temp_alarm"])
        rh_alarms = sum(1 for m in self.metrics_history if m["rh_alarm"])
        
        avg_temp = sum(m["temperature_c"] for m in self.metrics_history) / total_records
        avg_rh = sum(m["humidity_pct"] for m in self.metrics_history) / total_records
        
        compliance_score = max(0.0, 100.0 - ((temp_alarms + rh_alarms) / (total_records * 2) * 100.0))
        
        return {
            "chamber_id": self.chamber_id,
            "total_samples": total_records,
            "average_temperature_c": round(avg_temp, 2),
            "average_humidity_pct": round(avg_rh, 2),
            "temperature_violations": temp_alarms,
            "humidity_violations": rh_alarms,
            "proofing_compliance_score_pct": round(compliance_score, 2)
        }

if __name__ == "__main__":
    print("Executing BakeryProofingSentinel self-test...")
    sentinel = BakeryProofingSentinel(chamber_id="NAI_INDUSTRIAL_BakeLine_03")
    
    # Simulate normal and drifting cycles
    test_inputs = [
        (35.2, 84.5, 0.4),
        (34.8, 85.1, 0.4),
        (37.5, 74.0, 0.6), # Trigger heat and low humidity alarms
        (33.0, 91.0, 0.3)  # Trigger low temp and high humidity alarms
    ];
    
    for t, rh, air in test_inputs:
        res = sentinel.ingest_telemetry(t, rh, air)
        print(f"Telemetry Result: {res}")
        
    report = sentinel.generate_batch_audit_report()
    print(f"Batch Audit Report: {report}")
    print("BakeryProofingSentinel self-test complete.")
