import json
import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Union

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TaxType(Enum):
    """Types of taxes handled by the optimizer."""
    INCOME = "income"
    VAT = "vat"
    PAYE = "paye"
    WITHHOLDING = "withholding"
    PROPERTY = "property"


@dataclass
class TaxRecord:
    """Represents a single tax record."""
    tax_type: TaxType
    amount: float
    period_start: datetime
    period_end: datetime
    status: str = "pending"
    metadata: Dict = field(default_factory=dict)

    def to_dict(self) -> Dict:
        return {
            "tax_type": self.tax_type.value,
            "amount": self.amount,
            "period_start": self.period_start.isoformat(),
            "period_end": self.period_end.isoformat(),
            "status": self.status,
            "metadata": self.metadata
        }


class KRAComplianceException(Exception):
    """Custom exception for KRA compliance issues."""
    pass


class KRAValidationError(Exception):
    """Custom exception for validation errors."""
    pass


class KRATaxOptimizer:
    """Optimizes tax calculations and ensures KRA compliance."""

    def __init__(self, tax_records: Optional[List[TaxRecord]] = None):
        self.tax_records: List[TaxRecord] = tax_records or []
        self.compliance_rules: Dict[str, Dict] = self._load_compliance_rules()
        self.logger = logger

    def _load_compliance_rules(self) -> Dict[str, Dict]:
        """Load KRA compliance rules."""
        return {
            "income": {
                "threshold": 240000.0,
                "rate": 0.30,
                "max_deduction": 24000.0
            },
            "vat": {
                "threshold": 500000.0,
                "rate": 0.16,
                "max_deduction": 0.0
            },
            "paye": {
                "threshold": 240000.0,
                "rate": 0.30,
                "max_deduction": 24000.0
            },
            "withholding": {
                "threshold": 0.0,
                "rate": 0.05,
                "max_deduction": 0.0
            },
            "property": {
                "threshold": 0.0,
                "rate": 0.02,
                "max_deduction": 0.0
            }
        }

    def add_tax_record(self, record: TaxRecord) -> None:
        """Add a tax record to the optimizer."""
        if not isinstance(record, TaxRecord):
            raise KRAValidationError("Record must be a TaxRecord instance")
        self.tax_records.append(record)
        self.logger.info(f"Added tax record: {record.tax_type.value} - {record.amount}")

    def calculate_optimized_tax(self, tax_type: TaxType, income: float) -> float:
        """Calculate optimized tax for a given income."""
        rules = self.compliance_rules.get(tax_type.value, {})
        threshold = rules.get("threshold", 0.0)
        rate = rules.get("rate", 0.0)
        max_deduction = rules.get("max_deduction", 0.0)

        if income <= threshold:
            return 0.0

        taxable_income = income - threshold
        tax = taxable_income * rate

        if max_deduction > 0:
            tax = max(0.0, tax - max_deduction)

        return round(tax, 2)

    def detect_anomalies(self) -> List[Dict]:
        """Detect anomalies in tax records."""
        anomalies = []
        for record in self.tax_records:
            if record.amount < 0:
                anomalies.append({
                    "record": record.to_dict(),
                    "anomaly": "Negative amount",
                    "severity": "high"
                })
            elif record.period_end < record.period_start:
                anomalies.append({
                    "record": record.to_dict(),
                    "anomaly": "Invalid period",
                    "severity": "high"
                })
        return anomalies

    def generate_compliance_report(self) -> Dict:
        """Generate a compliance report."""
        report = {
            "total_records": len(self.tax_records),
            "total_amount": sum(record.amount for record in self.tax_records),
            "anomalies": self.detect_anomalies(),
            "compliance_status": "compliant" if not self.detect_anomalies() else "non_compliant",
            "generated_at": datetime.now().isoformat()
        }
        return report

    def optimize_filing_schedule(self) -> List[Dict]:
        """Optimize the filing schedule for tax records."""
        schedule = []
        for record in self.tax_records:
            if record.status == "pending":
                schedule.append({
                    "record": record.to_dict(),
                    "recommended_filing_date": (record.period_end + timedelta(days=30)).isoformat(),
                    "priority": "high" if record.amount > 10000 else "medium"
                })
        return schedule

    def validate_record(self, record: TaxRecord) -> bool:
        """Validate a tax record."""
        if record.amount < 0:
            raise KRAValidationError("Amount cannot be negative")
        if record.period_end < record.period_start:
            raise KRAValidationError("Period end cannot be before period start")
        return True


def main():
    """Test harness for KRATaxOptimizer."""
    optimizer = KRATaxOptimizer()

    # Add sample tax records
    record1 = TaxRecord(
        tax_type=TaxType.INCOME,
        amount=50000.0,
        period_start=datetime(2023, 1, 1),
        period_end=datetime(2023, 12, 31)
    )
    record2 = TaxRecord(
        tax_type=TaxType.VAT,
        amount=10000.0,
        period_start=datetime(2023, 1, 1),
        period_end=datetime(2023, 12, 31)
    )

    optimizer.add_tax_record(record1)
    optimizer.add_tax_record(record2)

    # Calculate optimized tax
    optimized_tax = optimizer.calculate_optimized_tax(TaxType.INCOME, 100000.0)
    print(f"Optimized Income Tax: {optimized_tax}")

    # Detect anomalies
    anomalies = optimizer.detect_anomalies()
    print(f"Anomalies detected: {len(anomalies)}")

    # Generate compliance report
    report = optimizer.generate_compliance_report()
    print(f"Compliance Report: {json.dumps(report, indent=2)}")

    # Optimize filing schedule
    schedule = optimizer.optimize_filing_schedule()
    print(f"Filing Schedule: {json.dumps(schedule, indent=2)}")


if __name__ == "__main__":
    main()