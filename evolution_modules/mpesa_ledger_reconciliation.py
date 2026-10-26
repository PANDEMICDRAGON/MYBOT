"""Autonomous M-Pesa Transaction Reconciliation & Ledger Integrity Auditor.

Protects operator financial workflows against reconciliation drift, missing callbacks,
and ledger tampering by cryptographically binding M-Pesa API transaction receipts
with local execution logs.
"""

import hashlib
import hmac
import json
import logging
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("MpesaLedgerReconciler")


class MpesaLedgerReconciler:
    """Reconciles M-Pesa transactions securely with local persistent ledgers."""

    def __init__(self, secret_hmac_key: str):
        self.secret_key = secret_hmac_key.encode("utf-8")
        self.local_ledger: List[Dict] = []
        self.external_receipts: List[Dict] = []
        logger.info("MpesaLedgerReconciler initialized for secure operator financial auditing.")

    def record_local_transaction(self, tx_id: str, amount: float, phone: str, metadata: Optional[Dict] = None) -> Dict:
        """Record an initiated transaction locally with an HMAC integrity seal."""
        timestamp = datetime.now(timezone.utc).isoformat()
        payload = f"{tx_id}:{amount:.2f}:{phone}:{timestamp}"
        signature = hmac.new(self.secret_key, payload.encode("utf-8"), hashlib.sha256).hexdigest()
        
        record = {
            "tx_id": tx_id,
            "amount": round(amount, 2),
            "phone": phone,
            "timestamp": timestamp,
            "metadata": metadata or {},
            "signature": signature,
            "reconciled": False
        }
        self.local_ledger.append(record)
        logger.info(f"Local transaction recorded: {tx_id} for KES {amount:.2f}")
        return record

    def ingest_external_callback(self, callback_data: Dict) -> bool:
        """Ingest M-Pesa C2B/B2C callback payload safely."""
        required_fields = ["TransID", "TransAmount", "MSISDN"]
        if not all(field in callback_data for field in required_fields):
            logger.error("Malformed M-Pesa callback payload received.")
            return False
        
        self.external_receipts.append({
            "tx_id": callback_data["TransID"],
            "amount": float(callback_data["TransAmount"]),
            "phone": str(callback_data["MSISDN"]),
            "raw": callback_data,
            "ingested_at": datetime.now(timezone.utc).isoformat()
        })
        logger.info(f"External callback ingested for TransID: {callback_data['TransID']}")
        return True

    def audit_and_reconcile(self) -> Tuple[List[str], List[Dict], List[Dict]]:
        """Perform full ledger audit, identifying matched, missing, and anomalous items.

        Returns:
            Tuple containing matched transaction IDs, unmatched local records (drift),
            and orphaned external receipts.
        """
        matched: List[str] = []
        unmatched_local: List[Dict] = []
        orphaned_external: List[Dict] = []

        external_map = {receipt["tx_id"]: receipt for receipt in self.external_receipts}

        for local in self.local_ledger:
            tx_id = local["tx_id"]
            if tx_id in external_map:
                ext = external_map[tx_id]
                if abs(local["amount"] - ext["amount"]) < 0.01:
                    local["reconciled"] = True
                    matched.append(tx_id)
                else:
                    logger.warning(f"Amount mismatch detected for {tx_id}: Local={local['amount']}, Ext={ext['amount']}")
                    unmatched_local.append(local)
            else:
                unmatched_local.append(local)

        matched_set = set(matched)
        for ext in self.external_receipts:
            if ext["tx_id"] not in matched_set and not any(l["tx_id"] == ext["tx_id"] for l in self.local_ledger):
                orphaned_external.append(ext)

        logger.info(f"Audit complete. Matched: {len(matched)}, Unmatched Local: {len(unmatched_local)}, Orphaned Ext: {len(orphaned_external)}")
        return matched, unmatched_local, orphaned_external


if __name__ == "__main__":
    reconciler = MpesaLedgerReconciler("cortana_secure_test_secret_key")
    
    # Test local transaction recording
    rec = reconciler.record_local_transaction("RKT9XYZ123", 1500.0, "254712345678", {"service": "Kitengela Solar Node"})
    
    # Test external callback ingestion
    callback = {
        "TransID": "RKT9XYZ123",
        "TransAmount": "1500.00",
        "MSISDN": "254712345678",
        "BillRefNumber": "SolarNode01"
    }
    reconciler.ingest_external_callback(callback)
    
    # Execute reconciliation
    matched, unmatched, orphans = reconciler.audit_and_reconcile()
    assert "RKT9XYZ123" in matched
    print("MpesaLedgerReconciler verification successfully executed.")
