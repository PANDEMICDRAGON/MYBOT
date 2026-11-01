import json
import hashlib
import time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum


class TaxCategory(Enum):
    VAT = "VAT"
    PAYE = "PAYE"
    WITHHOLDING = "WITHHOLDING"
    ELEVATED = "ELEVATED"


@dataclass
class Transaction:
    tx_id: str
    amount: float
    category: TaxCategory
    timestamp: float
    metadata: Dict[str, Any] = field(default_factory=dict)


class KRAComplianceEngine:
    """
    Simulates KRA tax audit trails and validates compliance.
    """

    def __init__(self, vat_rate: float = 0.16, paye_threshold: float = 240000.0):
        self.vat_rate = vat_rate
        self.paye_threshold = paye_threshold
        self.audit_log: List[Dict[str, Any]] = []
        self._hash_chain: Optional[str] = None

    def _compute_hash(self, data: Dict[str, Any]) -> str:
        """Compute SHA-256 hash for tamper-evident logging."""
        return hashlib.sha256(json.dumps(data, sort_keys=True).encode()).hexdigest()

    def log_transaction(self, tx: Transaction) -> None:
        """Log a transaction with tamper-evident hash chaining."""
        entry = {
            "tx_id": tx.tx_id,
            "amount": tx.amount,
            "category": tx.category.value,
            "timestamp": tx.timestamp,
            "metadata": tx.metadata,
            "prev_hash": self._hash_chain,
        }
        entry["hash"] = self._compute_hash(entry)
        self._hash_chain = entry["hash"]
        self.audit_log.append(entry)

    def validate_compliance(self) -> Dict[str, Any]:
        """Validate all logged transactions against KRA rules."""
        violations = []
        for entry in self.audit_log:
            if entry["category"] == TaxCategory.VAT.value and entry["amount"] > 0:
                expected_vat = entry["amount"] * self.vat_rate
                if abs(entry["metadata"].get("vat_amount", 0) - expected_vat) > 0.01:
                    violations.append({
                        "tx_id": entry["tx_id"],
                        "issue": "VAT mismatch",
                        "expected": expected_vat,
                        "actual": entry["metadata"].get("vat_amount", 0)
                    })
            if entry["category"] == TaxCategory.PAYE.value and entry["amount"] > self.paye_threshold:
                if not entry["metadata"].get("paye_declared", False):
                    violations.append({
                        "tx_id": entry["tx_id"],
                        "issue": "PAYE not declared for high-value transaction"
                    })
        return {
            "total_transactions": len(self.audit_log),
            "violations": violations,
            "compliant": len(violations) == 0
        }

    def generate_audit_report(self) -> str:
        """Generate a human-readable audit report."""
        report = ["KRA Tax Audit Report", "=" * 40]
        for entry in self.audit_log:
            report.append(f"TX: {entry['tx_id']} | Amount: {entry['amount']} | Category: {entry['category']}")
        report.append("=" * 40)
        return "\n".join(report)


def main():
    """Test harness for KRA Compliance Engine."""
    engine = KRAComplianceEngine()
    
    # Simulate transactions
    tx1 = Transaction(
        tx_id="TX001",
        amount=10000.0,
        category=TaxCategory.VAT,
        timestamp=time.time(),
        metadata={"vat_amount": 1600.0}
    )
    engine.log_transaction(tx1)

    tx2 = Transaction(
        tx_id="TX002",
        amount=300000.0,
        category=TaxCategory.PAYE,
        timestamp=time.time(),
        metadata={"paye_declared": False}
    )
    engine.log_transaction(tx2)

    # Validate compliance
    result = engine.validate_compliance()
    print(json.dumps(result, indent=2))
    
    # Generate report
    print(engine.generate_audit_report())


if __name__ == "__main__":
    main()