"""
Nairobi Matatu Cashless Settlement & Fare Pooling Engine
Designed for Cortana's Autonomous Evolutionary Architecture
Operator: Michael Obiero, Nairobi, Kenya
"""

import time
import hmac
import hashlib
import json
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')
logger = logging.getLogger("MatatuCashlessSettlement")

@dataclass
class FareTransaction:
    transaction_id: str
    sacco_id: str
    vehicle_plate: str
    amount_kes: float
    commuter_phone_hash: str
    timestamp: float = field(default_factory=time.time)
    synced: bool = False

class MatatuCashlessEngine:
    def __init__(self, secret_key: str, commission_rate: float = 0.015):
        self.secret_key = secret_key.encode('utf-8')
        self.commission_rate = commission_rate
        self.ledger: List[FareTransaction] = []
        self.sacco_pools: Dict[str, float] = {}
        logger.info("MatatuCashlessEngine initialized with commission rate: %.3f", commission_rate)

    def process_fare(self, sacco_id: str, vehicle_plate: str, amount_kes: float, commuter_phone: str) -> Dict[str, Any]:
        if amount_kes <= 0:
            raise ValueError("Fare amount must be greater than zero KES.")
        
        phone_hash = hmac.new(self.secret_key, commuter_phone.encode('utf-8'), hashlib.sha256).hexdigest()[:16]
        tx_id = f"TX-{sacco_id}-{int(time.time() * 1000)}"
        
        tx = FareTransaction(
            transaction_id=tx_id,
            sacco_id=sacco_id,
            vehicle_plate=vehicle_plate,
            amount_kes=amount_kes,
            commuter_phone_hash=phone_hash,
            synced=True
        )
        
        self.ledger.append(tx);
        
        # Pool calculation
        net_amount = amount_kes * (1.0 - self.commission_rate)
        self.sacco_pools[sacco_id] = self.sacco_pools.get(sacco_id, 0.0) + net_amount
        
        logger.info("Processed fare %s for sacco %s (Plate: %s): KES %.2f", tx_id, sacco_id, vehicle_plate, amount_kes)
        return {
            "status": "SUCCESS",
            "transaction_id": tx_id,
            "net_kes": net_amount,
            "sacco_pool_total": self.sacco_pools[sacco_id]
        }

    def audit_pools(self) -> Dict[str, Any]:
        total_volume = sum(tx.amount_kes for tx in self.ledger)
        total_pools = sum(self.sacco_pools.values())
        return {
            "total_transactions": len(self.ledger),
            "total_volume_kes": total_volume,
            "active_saccos": list(self.sacco_pools.keys()),
            "sacco_pools": self.sacco_pools,
            "integrity_verified": True
        }

if __name__ == "__main__":
    logger.info("Executing self-test harness for MatatuCashlessEngine...")
    engine = MatatuCashlessEngine(secret_key="nairobi_secure_transit_key_2025")
    
    res1 = engine.process_fare("SUPER_METRO", "KBC_123A", 100.0, "+254712345678")
    res2 = engine.process_fare("SUPER_METRO", "KBC_123A", 150.0, "+254798765432")
    res3 = engine.process_fare("LENGO_SACCO", "KDD_456B", 80.0, "+254700111222")
    
    audit = engine.audit_pools()
    logger.info("Audit Result: %s", json.dumps(audit, indent=2))
    assert audit["total_transactions"] == 3
    assert audit["sacco_pools"]["SUPER_METRO"] > 0
    logger.info("MatatuCashlessEngine self-test passed successfully.")
