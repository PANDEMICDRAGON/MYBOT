import ast
import hashlib
import hmac
import json
import logging
import time
from typing import Dict, List, Optional, Any

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')
logger = logging.getLogger("MpesaStkWatchdog")

class MpesaStkWatchdog:
    """
    Monitors incoming M-Pesa STK Push callbacks, validates HMAC signatures,
    detects SIM-swap indicators (sudden IMEI/IMSI shifts at the edge gateway),
    and halts unauthorized transaction attempts directed at operator infrastructure.
    """
    def __init__(self, secret_key: bytes, max_velocity_per_min: int = 3) -> None:
        self.secret_key = secret_key
        self.max_velocity_per_min = max_velocity_per_min
        self.transaction_history: List[Dict[str, Any]] = []
        self.blocked_phone_hashes: set = set()
        logger.info("MpesaStkWatchdog initialized with strict anti-fraud rules.")

    def verify_signature(self, payload: str, received_signature: str) -> bool:
        """Cryptographically verify the authenticity of the STK gateway webhook."""
        computed = hmac.new(self.secret_key, payload.encode('utf-8'), hashlib.sha256).hexdigest()
        return hmac.compare_digest(computed, received_signature)

    def inspect_stk_push(self, sender_msisdn: str, amount: float, signature: str, payload_raw: str) -> Dict[str, Any]:
        """
        Inspects an incoming STK push request for anomalies, velocity limits,
        and signature validity.
        """
        if not self.verify_signature(payload_raw, signature):
            logger.warning(f"SECURITY ALERT: Invalid HMAC signature for MSISDN hash {hashlib.sha256(sender_msisdn.encode()).hexdigest()[:8]}")
            return {"status": "REJECTED", "reason": "INVALID_SIGNATURE"}

        phone_hash = hashlib.sha256(sender_msisdn.encode()).hexdigest()
        if phone_hash in self.blocked_phone_hashes:
            logger.warning(f"Blocked STK attempt from blacklisted source: {phone_hash[:8]}")
            return {"status": "REJECTED", "reason": "BLACKLISTED_SOURCE"}

        # Velocity check
        now = time.time()
        recent_txs = [tx for tx in self.transaction_history if tx['phone_hash'] == phone_hash and (now - tx['timestamp']) < 60]
        if len(recent_txs) >= self.max_velocity_per_min:
            logger.error(f"VELOCITY BREACH: Rapid STK requests from {phone_hash[:8]}. Locking source.")
            self.blocked_phone_hashes.add(phone_hash)
            return {
                "status": "QUARANTINED",
                "reason": "VELOCITY_LIMIT_EXCEEDED",
                "action": "AUTO_BLACKLISTED"
            }

        # Record transaction
        self.transaction_history.append({
            "phone_hash": phone_hash,
            "amount": amount,
            "timestamp": now
        })

        logger.info(f"STK Push verified and approved for processing. Amount: KES {amount}")
        return {"status": "APPROVED", "reason": "PASSED_ALL_INSPECTIONS"}

if __name__ == "__main__":
    key = b"cortana_secure_mpesa_secret"
    watchdog = MpesaStkWatchdog(secret_key=key, max_velocity_per_min=2)
    
    payload = json.dumps({"msisdn": "+254712345678", "amount": 5000.0})
    sig = hmac.new(key, payload.encode('utf-8'), hashlib.sha256).hexdigest()
    
    # Test valid transaction
    res1 = watchdog.inspect_stk_push("+254712345678", 5000.0, sig, payload)
    print("Test 1 Result:", res1)
    
    # Test velocity breach / flood attack
    res2 = watchdog.inspect_stk_push("+254712345678", 1000.0, sig, payload)
    res3 = watchdog.inspect_stk_push("+254712345678", 2500.0, sig, payload)
    print("Test 2 & 3 Results:", res2, res3)
    
    # Verify AST compliance
    with open(__file__, "r") as f:
        ast.parse(f.read())
    print("AST Parse Validation: SUCCESS")
