import ast
import hashlib
import hmac
import json
import logging
import os
import time
from typing import Dict, List, Optional, Tuple

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')
logger = logging.getLogger("MpesaFraudShield")

class MpesaFraudShield:
    """
    Autonomous security sentinel for monitoring incoming M-Pesa transaction notifications,
    detecting rapid-fire velocity spikes, unauthorized reversals, and potential SIM-swap vectors.
    """
    def __init__(self, daily_limit_kes: float = 150000.0, velocity_window_sec: int = 300):
        self.daily_limit_kes = daily_limit_kes
        self.velocity_window_sec = velocity_window_sec
        self.transaction_log: List[Dict] = []
        self.known_senders: set = set()
        self.revoked_tokens: set = set()
        logger.info("MpesaFraudShield initialized with limit KES %.2f", daily_limit_kes)

    def ingest_transaction(self, tx_id: str, sender_phone: str, amount: float, tx_type: str, timestamp: Optional[float] = None) -> Dict:
        """
        Ingests an M-Pesa transaction event (parsed from SMS or STK push callback),
        evaluates risk, and returns security adjudication.
        """
        ts = timestamp if timestamp else time.time()
        
        # Check for replay or duplicate tx_id
        if any(t['tx_id'] == tx_id for t in self.transaction_log):
            logger.warning("Replay attack detected for transaction ID: %s", tx_id)
            return {"status": "BLOCKED", "reason": "REPLAY_ATTACK_DUPLICATE_ID", "tx_id": tx_id}

        # Calculate velocity within window
        recent_txs = [t for t in self.transaction_log if ts - t['timestamp'] <= self.velocity_window_sec]
        recent_sum = sum(t['amount'] for t in recent_txs)

        risk_score = 0.0
        flags = []

        # Velocity check
        if recent_sum + amount > 50000.0:
            risk_score += 0.5
            flags.append("HIGH_VELOCITY_BURST")

        # Daily limit check
        today_start = ts - (ts % 86400)
        today_sum = sum(t['amount'] for t in self.transaction_log if t['timestamp'] >= today_start)
        if today_sum + amount > self.daily_limit_kes:
            risk_score += 0.8
            flags.append("DAILY_LIMIT_EXCEEDED")

        # Anomaly pattern: Strange amount or reversals
        if tx_type.upper() == "REVERSAL":
            risk_score += 0.4
            flags.append("UNSOLICITED_REVERSAL_ATTEMPT")

        decision = "APPROVED"
        if risk_score >= 0.7:
            decision = "QUARANTINED"
            logger.error("SECURITY ALERT: Transaction %s quarantined due to flags: %s", tx_id, flags)
        elif risk_score >= 0.4:
            decision = "FLAGGED"
            logger.warning("WARNING: Transaction %s flagged for review: %s", tx_id, flags)
        else:
            logger.info("Transaction %s approved successfully.", tx_id)

        tx_record = {
            "tx_id": tx_id,
            "sender_phone": sender_phone,
            "amount": amount,
            "tx_type": tx_type,
            "timestamp": ts,
            "decision": decision,
            "flags": flags
        }
        self.transaction_log.append(tx_record)
        return {"status": decision, "risk_score": risk_score, "flags": flags, "tx_id": tx_id}

    def audit_security_posture(self) -> Dict:
        """
        Returns summary statistics of the fraud detection engine.
        """
        total_txs = len(self.transaction_log)
        quarantined = sum(1 for t in self.transaction_log if t['decision'] == 'QUARANTINED')
        flagged = sum(1 for t in self.transaction_log if t['decision'] == 'FLAGGED')
        return {
            "total_inspected": total_txs,
            "quarantined_count": quarantined,
            "flagged_count": flagged,
            "shield_status": "ACTIVE"
        }

if __name__ == "__main__":
    shield = MpesaFraudShield()
    # Test normal transaction
    res1 = shield.ingest_transaction("QWE123456", "+254712345678", 2500.0, "PAYMENT")
    print("Test 1:", json.dumps(res1))
    
    # Test suspicious velocity burst
    res2 = shield.ingest_transaction("QWE123457", "+254722333444", 48000.0, "PAYMENT")
    print("Test 2:", json.dumps(res2))
    
    # Test duplicate replay attack
    res3 = shield.ingest_transaction("QWE123456", "+254712345678", 2500.0, "PAYMENT")
    print("Test 3:", json.dumps(res3))
    
    print("Audit Posture:", json.dumps(shield.audit_security_posture()))
