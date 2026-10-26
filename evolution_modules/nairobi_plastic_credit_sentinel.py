"""
Module: nairobi_plastic_credit_sentinel.py
Description: Cryptographic ledger and verification engine for Nairobi's recycled
             plastic waste credits, supporting EPR compliance and offset trading.
Author: Cortana Autonomous Evolutionary Architect
Operator: Michael Obiero (Nairobi, Kenya)
"""

import hashlib
import json
import time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field


@dataclass
class PlasticBatch:
    batch_id: str
    collection_hub: str
    polymer_type: str  # PET, HDPE, LDPE, PP
    weight_kg: float
    recycler_id: str
    timestamp: float = field(default_factory=time.time)
    inspector_id: str = "NEMA_AUTO_VERIFIER"
    verified: bool = False
    credit_tokens_issued: float = 0.0


class PlasticCreditLedger:
    """Manages immutable recording and credit minting for Nairobi recycled plastics."""
    
    def __init__(self, base_rate_per_kg: float = 1.5):
        self.base_rate_per_kg = base_rate_per_kg
        self.blockchain: List[Dict[str, Any]] = []
        self.pending_batches: Dict[str, PlasticBatch] = {}
        self._create_genesis_block()

    def _create_genesis_block(self) -> None:
        genesis = {
            "index": 0,
            "timestamp": time.time(),
            "previous_hash": "0" * 64,
            "data": {
                "event": "GENESIS",
                "operator": "Michael Obiero",
                "location": "Nairobi, Kenya"
            },
            "nonce": 0
        }
        genesis["hash"] = self._hash_block(genesis)
        self.blockchain.append(genesis)

    def _hash_block(self, block: Dict[str, Any]) -> str:
        block_copy = block.copy()
        block_copy.pop("hash", None)
        block_string = json.dumps(block_copy, sort_keys=True)
        return hashlib.sha256(block_string.encode("utf-8")).hexdigest()

    def register_batch(self, batch_id: str, hub: str, polymer: str, weight: float, recycler: str) -> bool:
        if batch_id in self.pending_batches:
            raise ValueError(f"Batch {batch_id} already registered.")
        if weight <= 0:
            raise ValueError("Weight must be greater than zero.")
        
        batch = PlasticBatch(
            batch_id=batch_id,
            collection_hub=hub,
            polymer_type=polymer.upper(),
            weight_kg=weight,
            recycler_id=recycler
        )
        self.pending_batches[batch_id] = batch
        return True

    def verify_and_mint(self, batch_id: str, quality_multiplier: float = 1.0) -> Dict[str, Any]:
        if batch_id not in self.pending_batches:
            raise KeyError(f"Batch {batch_id} not found in pending queue.")
        
        batch = self.pending_batches.pop(batch_id)
        batch.verified = True
        
        # Calculate credit tokens based on weight and polymer grade multiplier
        multiplier = 1.2 if batch.polymer_type in ["PET", "HDPE"] else 0.9
        batch.credit_tokens_issued = round(batch.weight_kg * self.base_rate_per_kg * multiplier * quality_multiplier, 2)
        
        last_block = self.blockchain[-1]
        new_block = {
            "index": len(self.blockchain),
            "timestamp": time.time(),
            "previous_hash": last_block["hash"],
            "data": {
                "batch_id": batch.batch_id,
                "collection_hub": batch.collection_hub,
                "polymer_type": batch.polymer_type,
                "weight_kg": batch.weight_kg,
                "recycler_id": batch.recycler_id,
                "credit_tokens_issued": batch.credit_tokens_issued
            },
            "nonce": int(time.time())
        }
        new_block["hash"] = self._hash_block(new_block)
        self.blockchain.append(new_block)
        return new_block

    def audit_ledger(self) -> bool:
        for i in range(1, len(self.blockchain)):
            current = self.blockchain[i]
            previous = self.blockchain[i - 1]
            if current["previous_hash"] != previous["hash"]:
                return False
            if current["hash"] != self._hash_block(current):
                return False
        return True


if __name__ == "__main__":
    print("Initializing Nairobi Plastic Credit Ledger...")
    ledger = PlasticCreditLedger()
    
    # Register waste collection batches from Nairobi hubs
    ledger.register_batch("BATCH-DANDORA-001", "Dandora Youth Green Hub", "PET", 450.0, "RecycleAfrika Ltd")
    ledger.register_batch("BATCH-KIBERA-042", "Kibera Upcycle Initiative", "HDPE", 280.5, "TakaTaka Solutions")
    
    # Verify and mint credits
    b1 = ledger.verify_and_mint("BATCH-DANDORA-001", quality_multiplier=1.05)
    b2 = ledger.verify_and_mint("BATCH-KIBERA-042", quality_multiplier=1.0)
    
    print(f"Minted Block 1 Hash: {b1['hash'][:16]}... Tokens: {b1['data']['credit_tokens_issued']}")
    print(f"Minted Block 2 Hash: {b2['hash'][:16]}... Tokens: {b2['data']['credit_tokens_issued']}")
    
    is_valid = ledger.audit_ledger()
    print(f"Ledger Integrity Check: {'PASSED' if is_valid else 'FAILED'}")
    print("Nairobi Plastic Credit Sentinel operational.")
