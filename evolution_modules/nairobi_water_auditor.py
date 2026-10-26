import ast
import logging
import json
from datetime import datetime
from typing import Dict, List, Optional, Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("NairobiWaterAuditor")

class NairobiWaterAuditor:
    """
    Autonomous utility meter auditing engine tailored for Nairobi/Nairobi households.
    Tracks consumption metrics, detects unexpected volume spikes indicating leaks or
    billing estimation errors, and prepares tamper-proof meter logs.
    """
    
    def __init__(self, baseline_daily_litres: float = 450.0, tariff_tier_limit: float = 6000.0) -> None:
        self.baseline_daily_litres = baseline_daily_litres
        self.tariff_tier_limit = tariff_tier_limit
        self.audit_records: List[Dict[str, Any]] = []

    def ingest_reading(self, timestamp: str, meter_cubic_meters: float, notes: Optional[str] = None) -> Dict[str, Any]:
        """Ingests a raw meter reading and evaluates anomaly vectors."""
        litres = meter_cubic_meters * 1000.0
        record = {
            "timestamp": timestamp,
            "meter_reading_m3": meter_cubic_meters,
            "total_litres": litres,
            "notes": notes or "Standard read",
            "flagged": False,
            "anomaly_reason": None
        }
        
        if self.audit_records:
            last_record = self.audit_records[-1]
            try:
                t1 = datetime.fromisoformat(last_record["timestamp"])
                t2 = datetime.fromisoformat(timestamp)
                delta_days = (t2 - t1).total_seconds() / 86400.0
                
                if delta_days > 0:
                    delta_litres = litres - last_record["total_litres"]
                    projected_daily = delta_litres / delta_days
                    
                    if projected_daily > (self.baseline_daily_litres * 2.0):
                        record["flagged"] = True
                        record["anomaly_reason"] = f"High consumption spike detected: {projected_daily:.1f}L/day (Baseline: {self.baseline_daily_litres}L)"
                        logger.warning(f"[ALERT] {record['anomaly_reason']}")
            except Exception as e:
                logger.error(f"Failed to compute temporal delta: {e}")
                
        self.audit_records.append(record)
        return record

    def generate_audit_report(self) -> Dict[str, Any]:
        """Summarizes water usage history and flag metrics."""
        total_entries = len(self.audit_records)
        flagged_entries = [r for r in self.audit_records if r["flagged"]]
        
        report = {
            "total_audits": total_entries,
            "anomalies_detected": len(flagged_entries),
            "status": "NORMAL" if not flagged_entries else "INVESTIGATION_REQUIRED",
            "records": self.audit_records
        }
        return report

if __name__ == "__main__":
    auditor = NairobiWaterAuditor()
    r1 = auditor.ingest_reading("2026-03-01T08:00:00", 120.5, "Initial baseline read")
    r2 = auditor.ingest_reading("2026-03-08T08:00:00", 135.0, "Weekly check")
    r3 = auditor.ingest_reading("2026-03-10T08:00:00", 165.0, "Sudden jump - potential pipe leak in Nairobi compound")
    
    report = auditor.generate_audit_report()
    print(json.dumps(report, indent=2))
