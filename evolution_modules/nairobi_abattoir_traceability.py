"""Nairobi Municipal Abattoir & Livestock Traceability Sentinel. Provides cryptographic ledger tracking for livestock provenance, veterinary inspection, cold chain telemetry, and wholesale distribution."""

import hashlib
import json
import time
from typing import Dict, List, Optional


class AbattoirTraceabilityLedger:
    """Manages immutable audit trails for livestock intake, vet inspection, and cold-chain dispatch."""

    def __init__(self, abattoir_id: str) -> None:
        self.abattoir_id = abattoir_id
        self.chain: List[Dict] = []
        self.pending_lots: Dict[str, Dict] = {}
        self._initialize_genesis_block()

    def _initialize_genesis_block(self) -> None:
        genesis_block = {
            "block_id": 0,
            "timestamp": time.time(),
            "previous_hash": "0" * 64,
            "data": {
                "type": "GENESIS",
                "abattoir_id": self.abattoir_id,
                "location": "Nairobi County"
            },
            "nonce": 0
        }
        genesis_block["hash"] = self._hash_block(genesis_block)
        self.chain.append(genesis_block)

    def _hash_block(self, block: Dict) -> str:
        block_string = json.dumps({
            "block_id": block["block_id"],
            "timestamp": block["timestamp"],
            "previous_hash": block["previous_hash"],
            "data": block["data"],
            "nonce": block["nonce"]
        }, sort_keys=True).encode("utf-8")
        return hashlib.sha256(block_string).hexdigest()

    def register_livestock_lot(self, lot_id: str, origin_county: str, head_count: int, farmer_tag: str) -> Dict:
        """Registers incoming livestock from counties (e.g., Kajiado, Narok, Kiambu) into the Nairobi abattoir."""
        if lot_id in self.pending_lots:
            raise ValueError(f"Lot {lot_id} already registered.")

        lot_data = {
            "lot_id": lot_id,
            "origin_county": origin_county,
            "head_count": head_count,
            "farmer_tag": farmer_tag,
            "intake_timestamp": time.time(),
            "status": "REGISTERED"
        }
        self.pending_lots[lot_id] = lot_data
        return lot_data

    def record_veterinary_inspection(self, lot_id: str, inspector_id: str, passed: bool, notes: str) -> Dict:
        """Records mandatory ante-mortem / post-mortem vet inspection by Nairobi County health officers."""
        if lot_id not in self.pending_lots:
            raise KeyError(f"Lot {lot_id} not found in pending inventory.")

        lot = self.pending_lots[lot_id]
        lot["inspection"] = {
            "inspector_id": inspector_id,
            "passed": passed,
            "notes": notes,
            "timestamp": time.time()
        }
        lot["status"] = "INSPECTED_PASSED" if passed else "QUARANTINED"
        return lot

    def commit_dispatch_block(self, lot_id: str, vehicle_plate: str, cold_chain_temp_c: float) -> Dict:
        """Commits a validated meat lot dispatch to the cryptographic ledger."""
        if lot_id not in self.pending_lots:
            raise KeyError(f"Lot {lot_id} not found.")

        lot = self.pending_lots[lot_id]
        if lot.get("status") != "INSPECTED_PASSED":
            raise ValueError(f"Lot {lot_id} cannot be dispatched without passing veterinary inspection.")

        if cold_chain_temp_c > 4.0:
            raise ValueError(f"Cold chain violation: Temperature {cold_chain_temp_c}C exceeds max threshold of 4.0C.")

        lot["dispatch"] = {
            "vehicle_plate": vehicle_plate,
            "cold_chain_temp_c": cold_chain_temp_c,
            "dispatch_timestamp": time.time()
        }
        lot["status"] = "DISPATCHED"

        previous_block = self.chain[-1]
        new_block = {
            "block_id": len(self.chain),
            "timestamp": time.time(),
            "previous_hash": previous_block["hash"],
            "data": lot,
            "nonce": 0
        }
        new_block["hash"] = self._hash_block(new_block)
        self.chain.append(new_block)
        
        # Remove from active pending
        del self.pending_lots[lot_id]
        return new_block

    def verify_chain_integrity(self) -> bool:
        """Validates cryptographic integrity across all blocks in the ledger."""
        for i in range(1, len(self.chain)):
            current = self.chain[i]
            prev = self.chain[i - 1]
            if current["previous_hash"] != prev["hash"]:
                return False
            if current["hash"] != self._hash_block(current):
                return False
        return True


if __name__ == "__main__":
    print("Initializing Nairobi Abattoir Traceability Sentinel...")
    ledger = AbattoirTraceabilityLedger(abattoir_id="DAGORETTI_MAIN_01")
    
    # Register livestock
    lot = ledger.register_livestock_lot(
        lot_id="LOT-KAJ-2023-998",
        origin_county="Kajiado",
        head_count=25,
        farmer_tag="MASAI-PASTORAL-COOP-04"
    )
    print(f"Registered Lot: {lot['lot_id']} from {lot['origin_county']}")

    # Vet inspection
    ledger.record_veterinary_inspection(
        lot_id="LOT-KAJ-2023-998",
        inspector_id="DR_OTIENO_NC_HEALTH",
        passed=True,
        notes="All animals certified healthy. Antemortem examination clear."
    )
    print("Veterinary inspection passed.")

    # Dispatch block
    block = ledger.commit_dispatch_block(
        lot_id="LOT-KAJ-2023-998",
        vehicle_plate="KDH 456B",
        cold_chain_temp_c=2.1
    )
    print(f"Committed dispatch block #{block['block_id']} with hash: {block['hash'][:16]}...")

    # Integrity check
    is_valid = ledger.verify_chain_integrity()
    print(f"Ledger cryptographic integrity verified: {is_valid}")
