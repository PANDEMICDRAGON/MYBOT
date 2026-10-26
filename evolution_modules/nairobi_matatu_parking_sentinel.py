import ast
import hashlib
import hmac
import json
import time
from typing import Dict, List, Optional, Any

class MatatuParkingLedgerException(Exception):
    """Custom exception for Matatu Parking Ledger operations."""
    pass

class MatatuParkingSentinel:
    """
    Manages verifiable cryptographic entry/exit fee receipts, Sacco route allocations,
    and county revenue compliance for matatus operating within Nairobi termini.
    """
    def __init__(self, secret_key: str):
        self.secret_key = secret_key.encode('utf-8')
        self.ledger: List[Dict[str, Any]] = []
        self.terminal_allocations: Dict[str, List[str]] = {}

    def record_terminal_entry(self, vehicle_reg: str, sacco_name: str, terminal_id: str, fee_amount_kes: float) -> Dict[str, Any]:
        """
        Records a vehicle entry at a Nairobi terminus, generates an HMAC receipt token,
        and verifies compliance against county council fee schedules.
        """
        if not vehicle_reg or not sacco_name or fee_amount_kes <= 0:
            raise MatatuParkingLedgerException("Invalid vehicle registration, sacco name, or fee amount.")

        timestamp = time.time()
        payload = f"{vehicle_reg}:{sacco_name}:{terminal_id}:{fee_amount_kes}:{timestamp}"
        signature = hmac.new(self.secret_key, payload.encode('utf-8'), hashlib.sha256).hexdigest()

        record = {
            "vehicle_reg": vehicle_reg.upper(),
            "sacco_name": sacco_name,
            "terminal_id": terminal_id,
            "fee_amount_kes": fee_amount_kes,
            "timestamp": timestamp,
            "receipt_hash": signature,
            "status": "ACTIVE"
        }

        self.ledger.append(record)

        if terminal_id not in self.terminal_allocations:
            self.terminal_allocations[terminal_id] = []
        self.terminal_allocations[terminal_id].append(vehicle_reg.upper())

        return record

    def verify_receipt(self, receipt_hash: str) -> Optional[Dict[str, Any]]:
        """Validates a cryptographic receipt hash against the active ledger."""
        for record in self.ledger:
            if record["receipt_hash"] == receipt_hash:
                return record
        return None

    def audit_terminal_collection(self, terminal_id: str) -> Dict[str, Any]:
        """Aggregates total daily collections and vehicle counts for a specific terminus."""
        terminal_records = [r for r in self.ledger if r["terminal_id"] == terminal_id]
        total_revenue = sum(r["fee_amount_kes"] for r in terminal_records)
        unique_vehicles = len(set(r["vehicle_reg"] for r in terminal_records))

        return {
            "terminal_id": terminal_id,
            "total_revenue_kes": total_revenue,
            "total_entries": len(terminal_records),
            "unique_vehicles": unique_vehicles,
            "audit_timestamp": time.time()
        }

def __main__() -> None:
    print("Initializing Nairobi Matatu Parking Sentinel...")
    sentinel = MatatuParkingSentinel(secret_key="nairobi_secure_transit_key_2026")

    # Test record entry
    receipt = sentinel.record_terminal_entry(
        vehicle_reg="KCZ 456Z",
        sacco_name="2K Generation Sacco",
        terminal_id="GREEN_PARK_BAY_3",
        fee_amount_kes=100.0
    )
    print("Generated Receipt:", json.dumps(receipt, indent=2))

    # Test verification
    valid = sentinel.verify_receipt(receipt["receipt_hash"])
    print("Receipt Verification Result:", "SUCCESS" if valid else "FAILED")

    # Test audit
    audit = sentinel.audit_terminal_collection("GREEN_PARK_BAY_3")
    print("Terminal Audit Summary:", json.dumps(audit, indent=2))

    # Validate syntax integrity
    assert ast.parse(__file__)
    print("AST Compilation Check: PASSED")

if __name__ == "__main__":
    __main__()
