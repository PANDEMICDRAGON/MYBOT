import json
import hashlib
import time
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict

@dataclass
class Transaction:
    id: str
    amount: float
    category: str
    timestamp: float

@dataclass
class TaxRule:
    category: str
    rate: float
    threshold: float

class KRA_Tax_Audit_Simulator:
    def __init__(self):
        self.rules: List[TaxRule] = [
            TaxRule("digital_services", 0.16, 0.0),
            TaxRule("physical_goods", 0.16, 0.0),
            TaxRule("exempt", 0.0, 0.0)
        ]
        self.transactions: List[Transaction] = []
        self.audit_log: List[Dict] = []

    def add_transaction(self, tx: Transaction) -> None:
        self.transactions.append(tx)
        self._log_action("ADD_TX", tx.id)

    def calculate_tax(self) -> Dict[str, float]:
        total_tax = 0.0
        breakdown = {}
        for tx in self.transactions:
            rule = next((r for r in self.rules if r.category == tx.category), None)
            if rule:
                tax = max(0, (tx.amount - rule.threshold) * rule.rate)
                total_tax += tax
                breakdown[tx.category] = breakdown.get(tx.category, 0) + tax
        return {"total_tax": total_tax, "breakdown": breakdown}

    def generate_audit_hash(self) -> str:
        payload = json.dumps([asdict(t) for t in self.transactions], sort_keys=True)
        return hashlib.sha256(payload.encode()).hexdigest()

    def _log_action(self, action: str, ref: str) -> None:
        self.audit_log.append({"action": action, "ref": ref, "ts": time.time()})

if __name__ == "__main__":
    sim = KRA_Tax_Audit_Simulator()
    sim.add_transaction(Transaction("tx1", 1000.0, "digital_services", time.time()))
    sim.add_transaction(Transaction("tx2", 500.0, "exempt", time.time()))
    result = sim.calculate_tax()
    assert result["total_tax"] == 160.0
    print("KRA Tax Audit Simulator Test Passed:", result)
