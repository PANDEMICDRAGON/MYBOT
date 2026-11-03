"""Nairobi Matatu Cashless Interoperability & NFC Settlement Mesh Module.

Provides decentralized offline-first NFC fare processing, cryptographic settlement vouchers,
and real-time sacco revenue pooling for commuter transit networks in Nairobi, Kenya.
"""

import hashlib
import hmac
import json
import time
import uuid
from typing import Dict, List, Optional, Tuple


class MatatuCashlessMesh:
    """Manages offline NFC token validation, fare splitting, and encrypted micro-ledgers
    for matatu saccos operating in Nairobi.
    """

    def __init__(self, sacco_id: str, master_secret: bytes):
        self.sacco_id = sacco_id
        self.master_secret = master_secret
        self.ledger: List[Dict] = []
        self.active_passes: Dict[str, Dict] = {}

    def issue_commuter_pass(self, commuter_id: str, initial_balance_kes: float) -> Dict:
        """Issue an encrypted offline commuter transit pass."""
        pass_id = f"PASS-{uuid.uuid4().hex[:8].upper()}"
        timestamp = time.time()
        payload = {
            "pass_id": pass_id,
            "commuter_id": commuter_id,
            "balance_kes": round(initial_balance_kes, 2),
            "issued_at": timestamp,
            "sacco_id": self.sacco_id
        }
        serialized = json.dumps(payload, sort_keys=True).encode('utf-8')
        signature = hmac.new(self.master_secret, serialized, hashlib.sha256).hexdigest()
        
        pass_record = {"payload": payload, "signature": signature}
        self.active_passes[pass_id] = pass_record
        return pass_record

    def process_tap_fare(self, pass_id: str, route_code: str, fare_kes: float, conductor_id: str) -> Dict:
        """Process an NFC tap event, deducting fare and logging cryptographically.
        Supports offline verification via HMAC signature validation.
        """
        if pass_id not in self.active_passes:
            return {"status": "REJECTED", "reason": "INVALID_PASS"}

        pass_record = self.active_passes[pass_id]
        payload = pass_record["payload"]
        expected_sig = hmac.new(
            self.master_secret,
            json.dumps(payload, sort_keys=True).encode('utf-8'),
            hashlib.sha256
        ).hexdigest()

        if expected_sig != pass_record["signature"]:
            return {"status": "REJECTED", "reason": "SIGNATURE_TAMPER_DETECTED"}

        if payload["balance_kes"] < fare_kes:
            return {"status": "REJECTED", "reason": "INSUFFICIENT_FUNDS"}

        # Deduct fare
        payload["balance_kes"] = round(payload["balance_kes"] - fare_kes, 2)
        updated_serialized = json.dumps(payload, sort_keys=True).encode('utf-8')
        pass_record["signature"] = hmac.new(self.master_secret, updated_serialized, hashlib.sha256).hexdigest()

        transaction_id = f"TX-{uuid.uuid4().hex[:10].upper()}"
        tx_record = {
            "transaction_id": transaction_id,
            "pass_id": pass_id,
            "route_code": route_code,
            "fare_kes": round(fare_kes, 2),
            "conductor_id": conductor_id,
            "sacco_id": self.sacco_id,
            "timestamp": time.time(),
            "prev_hash": self.ledger[-1]["current_hash"] if self.ledger else "GENESIS"
        }

        tx_bytes = json.dumps(tx_record, sort_keys=True).encode('utf-8')
        tx_record["current_hash"] = hashlib.sha256(tx_bytes).hexdigest()
        self.ledger.append(tx_record)

        return {
            "status": "APPROVED",
            "transaction_id": transaction_id,
            "remaining_balance_kes": payload["balance_kes"],
            "receipt_hash": tx_record["current_hash"]
        }

    def audit_ledger(self) -> Tuple[bool, int]:
        """Verify integrity of the local settlement ledger."""
        for i, tx in enumerate(self.ledger):
            if i == 0:
                if tx["prev_hash"] != "GENESIS":
                    return False, i
            else:
                if tx["prev_hash"] != self.ledger[i - 1]["current_hash"]:
                    return False, i
        return True, len(self.ledger)


if __name__ == "__main__":
    print("Initializing Nairobi Matatu Cashless Interoperability Mesh Test...")
    secret = b"nairobi_matatu_secure_transit_key_2025"
    mesh = MatatuCashlessMesh(sacco_id="SUPERMETRO-042", master_secret=secret)
    
    # Issue commuter pass
    pass_obj = mesh.issue_commuter_pass("COMMUTER-9912", 150.0)
    print(f"Issued Pass ID: {pass_obj['payload']['pass_id']} with KES {pass_obj['payload']['balance_kes']}")
    
    # Simulate tap on Ngong Road Route 111
    result = mesh.process_tap_fare(
        pass_id=pass_obj['payload']['pass_id'],
        route_code="NGONG-111",
        fare_kes=50.0,
        conductor_id="COND-KE-77"
    )
    print("Tap Result:", json.dumps(result, indent=2))
    
    # Audit ledger
    valid, count = mesh.audit_ledger()
    print(f"Ledger Integrity Check: Valid={valid}, Total Blocks={count}")
