"""
Module: matatu_fare_gateway.py
Description: Cryptographic offline fare token generator and ledger reconciler for Kitengela-Nairobi commuters.
Author: Cortana Autonomous Evolutionary Architect
Operator: Michael Obiero
"""

import os
import time
import hmac
import hashlib
import json
import logging
from typing import Dict, Any, List, Optional

logging.basicConfig(level=logging.INFO, format='[%(asctime)s] [MATATU-GATEWAY] [%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

class MatatuFareGateway:
    """Manages offline cryptographic transit tokens and fare balances for Nairobi commuters."""
    
    def __init__(self, operator_id: str, secret_seed: Optional[bytes] = None):
        self.operator_id = operator_id
        self.secret_seed = secret_seed or os.urandom(32)
        self.ledger: List[Dict[str, Any]] = []
        self.active_tokens: Dict[str, Dict[str, Any]] = {}
        logger.info(f"Initialized MatatuFareGateway for operator {self.operator_id}")

    def generate_offline_token(self, route_code: str, fare_amount_kes: float) -> Dict[str, Any]:
        """Generates a secure offline cryptographic token representing paid fare."""
        timestamp = int(time.time())
        nonce = os.urandom(8).hex()
        payload = {
            "operator_id": self.operator_id,
            "route": route_code,
            "amount": fare_amount_kes,
            "timestamp": timestamp,
            "nonce": nonce
        }
        
        canonical_data = f"{self.operator_id}:{route_code}:{fare_amount_kes}:{timestamp}:{nonce}"
        signature = hmac.new(
            self.secret_seed,
            canonical_data.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        token = {
            "payload": payload,
            "signature": signature
        }
        
        token_id = f"{timestamp}_{nonce[:6]}"
        self.active_tokens[token_id] = token
        logger.info(f"Generated offline transit token {token_id} for Route {route_code} (KES {fare_amount_kes})")
        return token

    def verify_and_redeem_token(self, token: Dict[str, Any]) -> bool:
        """Verifies and redeems an offline token locally without network access."""
        try:
            payload = token["payload"]
            signature = token["signature"]
            
            op_id = payload["operator_id"]
            route = payload["route"]
            amount = payload["amount"]
            ts = payload["timestamp"]
            nonce = payload["nonce"]
            
            # Check token expiration (e.g., valid for 24 hours offline)
            if int(time.time()) - ts > 86400:
                logger.warning("Token redemption failed: Token expired.")
                return False

            canonical_data = f"{op_id}:{route}:{amount}:{ts}:{nonce}"
            expected_sig = hmac.new(
                self.secret_seed,
                canonical_data.encode('utf-8'),
                hashlib.sha256
            ).hexdigest()
            
            if hmac.compare_digest(expected_sig, signature):
                self.ledger.append({
                    "token_id": f"{ts}_{nonce[:6]}",
                    "route": route,
                    "amount": amount,
                    "redeemed_at": time.time(),
                    "status": "REDEEMED"
                })
                logger.info(f"Token successfully redeemed offline for Route {route}, KES {amount}")
                return True
            else:
                logger.error("Token signature mismatch! Potential fraud detected.")
                return False
        except Exception as e:
            logger.error(f"Error processing token redemption: {e}")
            return False

    def get_ledger_summary(self) -> Dict[str, Any]:
        """Summarizes offline transit transactions for later cloud reconciliation."""
        total_amount = sum(item["amount"] for item in self.ledger)
        return {
            "operator_id": self.operator_id,
            "total_transactions": len(self.ledger),
            "total_revenue_kes": total_amount,
            "transactions": self.ledger
        }

if __name__ == "__main__":
    print("--- Executing Matatu Fare Gateway Test Harness ---")
    gateway = MatatuFareGateway(operator_id="MICHAEL_OBIERO_KTG")
    
    # Test generating token for Kitengela to Nairobi CBD (Route 110)
    token = gateway.generate_offline_token(route_code="110_KITENGELA_NBI", fare_amount_kes=150.0)
    
    # Test offline redemption
    success = gateway.verify_and_redeem_token(token)
    assert success, "Token redemption must succeed"
    
    # Test ledger summary
    summary = gateway.get_ledger_summary()
    print(json.dumps(summary, indent=2))
    assert summary["total_revenue_kes"] == 150.0
    print("--- Matatu Fare Gateway Test Passed Successfully ---")
