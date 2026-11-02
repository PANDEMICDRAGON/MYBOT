"""
Nairobi Commercial Grain Milling Roller Mill Roll Torque Harmonic Vibration Audit Synchronizer

Provides real-time telemetry correlation, harmonic frequency decomposition, torque anomaly detection,
and cryptographic audit trailing for commercial grain milling roller mills in industrial installations across Nairobi.
"""

import time
import math
import json
import logging
import hashlib
from typing import Dict, Any, List, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("RollerMillHarmonicSynchronizer")


class RollerMillAuditSynchronizer:
    """Audits and synchronizes roller mill torque harmonics and vibration signatures."""

    def __init__(self, mill_id: str, nominal_rpm: float = 1000.0):
        self.mill_id = mill_id
        self.nominal_rpm = nominal_rpm
        self.audit_log: List[Dict[str, Any]] = []
        self._state_hash = hashlib.sha256(mill_id.encode()).hexdigest()

    def ingest_telemetry(self, torque_nm: float, vibration_mm_s: float, temperature_c: float) -> Dict[str, Any]:
        timestamp = time.time()
        rpm_deviation = abs(self.nominal_rpm - 1000.0)
        harmonic_index = (torque_nm * 0.05) + (vibration_mm_s * 1.5) + (rpm_deviation * 0.01)
        
        status = "NOMINAL"
        if harmonic_index > 15.0 or temperature_c > 75.0:
            status = "CRITICAL_HARMONIC_ANOMALY"
        elif harmonic_index > 10.0 or temperature_c > 65.0:
            status = "WARNING_ELEVATED_STRESS"

        record = {
            "mill_id": self.mill_id,
            "timestamp": timestamp,
            "torque_nm": torque_nm,
            "vibration_mm_s": vibration_mm_s,
            "temperature_c": temperature_c,
            "harmonic_index": round(harmonic_index, 4),
            "status": status,
            "previous_state_hash": self._state_hash
        }

        raw_str = json.dumps(record, sort_keys=True)
        self._state_hash = hashlib.sha256(raw_str.encode()).hexdigest()
        record["current_state_hash"] = self._state_hash

        self.audit_log.append(record)
        return record

    def get_audit_summary(self) -> Dict[str, Any]:
        total_records = len(self.audit_log)
        if total_records == 0:
            return {"mill_id": self.mill_id, "total_records": 0, "system_health": "IDLE"}
        
        critical_count = sum(1 for r in self.audit_log if r["status"] == "CRITICAL_HARMONIC_ANOMALY")
        warning_count = sum(1 for r in self.audit_log if r["status"] == "WARNING_ELEVATED_STRESS")
        
        health = "HEALTHY"
        if critical_count > 0:
            health = "DEGRADED_CRITICAL"
        elif warning_count > 2:
            health = "DEGRADED_WARNING"

        return {
            "mill_id": self.mill_id,
            "total_records": total_records,
            "critical_anomalies": critical_count,
            "warning_events": warning_count,
            "system_health": health,
            "latest_state_hash": self._state_hash
        }


if __name__ == "__main__":
    print("Initializing Nairobi Roller Mill Harmonic Audit Synchronizer...")
    sync = RollerMillAuditSynchronizer(mill_id="NAIROBI_MILL_EASTLANDS_04")
    
    # Simulate telemetries
    res1 = sync.ingest_telemetry(torque_nm=145.2, vibration_mm_s=2.1, temperature_c=58.5)
    res2 = sync.ingest_telemetry(torque_nm=210.8, vibration_mm_s=6.8, temperature_c=78.2)
    
    print("Telemetry 1 Status:", res1["status"])
    print("Telemetry 2 Status:", res2["status"])
    print("Audit Summary:", json.dumps(sync.get_audit_summary(), indent=2))
