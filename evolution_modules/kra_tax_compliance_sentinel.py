import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TaxRecord:
    """Represents a single tax record."""

    def __init__(self, transaction_id: str, amount: float, tax_rate: float, timestamp: datetime):
        self.transaction_id = transaction_id
        self.amount = amount
        self.tax_rate = tax_rate
        self.timestamp = timestamp
        self.tax_amount = round(amount * tax_rate, 2)

    def to_dict(self) -> Dict:
        return {
            "transaction_id": self.transaction_id,
            "amount": self.amount,
            "tax_rate": self.tax_rate,
            "timestamp": self.timestamp.isoformat(),
            "tax_amount": self.tax_amount
        }


class KRAComplianceSentinel:
    """Monitors and validates KRA tax compliance for financial transactions."""

    def __init__(self, tax_rate: float = 0.16):
        self.tax_rate = tax_rate
        self.records: List[TaxRecord] = []
        self.compliance_status: Dict[str, bool] = {}

    def record_transaction(self, transaction_id: str, amount: float, timestamp: Optional[datetime] = None) -> TaxRecord:
        """Record a new transaction and calculate the tax amount."""
        if timestamp is None:
            timestamp = datetime.now()
        record = TaxRecord(transaction_id, amount, self.tax_rate, timestamp)
        self.records.append(record)
        logger.info(f"Recorded transaction {transaction_id} with tax amount {record.tax_amount}")
        return record

    def validate_compliance(self, period_start: datetime, period_end: datetime) -> Dict[str, bool]:
        """Validate compliance for a given period."""
        compliant_records = [r for r in self.records if period_start <= r.timestamp <= period_end]
        total_tax = sum(r.tax_amount for r in compliant_records)
        self.compliance_status[period_start.isoformat()] = total_tax > 0
        logger.info(f"Compliance validated for period {period_start} to {period_end}. Total tax: {total_tax}")
        return self.compliance_status

    def generate_report(self) -> Dict:
        """Generate a compliance report."""
        return {
            "total_records": len(self.records),
            "total_tax": sum(r.tax_amount for r in self.records),
            "compliance_status": self.compliance_status
        }


if __name__ == "__main__":
    sentinel = KRAComplianceSentinel(tax_rate=0.16)
    sentinel.record_transaction("TXN001", 1000.0)
    sentinel.record_transaction("TXN002", 2000.0)
    sentinel.validate_compliance(datetime.now() - timedelta(days=1), datetime.now())
    report = sentinel.generate_report()
    print(json.dumps(report, indent=2))