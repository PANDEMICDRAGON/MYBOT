"""
Module: nairobi_civic_sentinel.py
Description: Autonomous tracker for Nairobi County public participation, Ward Development Fund (WDF)
             allocations, public hearing schedules, and citizen petition verification.
Author: Cortana Autonomous Evolutionary Architect
Operator: Michael Obiero (Nairobi, Kenya)
"""

import hashlib
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')
logger = logging.getLogger("NairobiCivicSentinel")


class CivicPetitionRecord:
    """Represents a citizen petition or budget tracking entry for a Nairobi Ward."""

    def __init__(self, petition_id: str, ward_name: str, sector: str, description: str, allocated_ksh: float, status: str = "PENDING_PUBLIC_HEARING"):
        self.petition_id = petition_id
        self.ward_name = ward_name
        self.sector = sector
        self.description = description
        self.allocated_ksh = allocated_ksh
        self.status = status
        self.timestamp = datetime.utcnow().isoformat()
        self.previous_hash = ""
        self.hash = self._compute_hash()

    def _compute_hash(self) -> str:
        payload = f"{self.petition_id}|{self.ward_name}|{self.sector}|{self.allocated_ksh}|{self.status}|{self.timestamp}|{self.previous_hash}"
        return hashlib.sha256(payload.encode('utf-8')).hexdigest()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "petition_id": self.petition_id,
            "ward_name": self.ward_name,
            "sector": self.sector,
            "description": self.description,
            "allocated_ksh": self.allocated_ksh,
            "status": self.status,
            "timestamp": self.timestamp,
            "previous_hash": self.previous_hash,
            "hash": self.hash
        }


class NairobiCivicLedger:
    """Immutable ledger tracking county civic engagements and WDF audits."""

    def __init__(self):
        self.chain: List[CivicPetitionRecord] = []
        self._initialize_genesis_block()

    def _initialize_genesis_block(self) -> None:
        genesis = CivicPetitionRecord(
            petition_id="GENESIS-000",
            ward_name="Nairobi County HQ",
            sector="Governance",
            description="Genesis block for Nairobi County Public Participation & WDF Ledger",
            allocated_ksh=0.0,
            status="VERIFIED"
        )
        self.chain.append(genesis)
        logger.info("Nairobi Civic Ledger initialized with Genesis block.")

    def add_petition(self, petition_id: str, ward_name: str, sector: str, description: str, allocated_ksh: float) -> CivicPetitionRecord:
        last_block = self.chain[-1]
        new_record = CivicPetitionRecord(
            petition_id=petition_id,
            ward_name=ward_name,
            sector=sector,
            description=description,
            allocated_ksh=allocated_ksh,
            status="SUBMITTED"
        )
        new_record.previous_hash = last_block.hash
        new_record.hash = new_record._compute_hash()
        self.chain.append(new_record)
        logger.info(f"Added civic petition {petition_id} for Ward: {ward_name} (Ksh {allocated_ksh:,.2f})")
        return new_record

    def audit_ledger(self) -> bool:
        """Cryptographically verifies ledger integrity."""
        for i in range(1, len(self.chain)):
            current = self.chain[i]
            prev = self.chain[i - 1]
            if current.previous_hash != prev.hash:
                logger.error(f"Chain broken at index {i}: previous_hash mismatch.")
                return False
            if current.hash != current._compute_hash():
                logger.error(f"Chain corrupted at index {i}: hash mismatch.")
                return False
        logger.info("Nairobi Civic Ledger integrity verified successfully. 0 discrepancies found.")
        return True

    def get_ward_summary(self, ward_name: str) -> Dict[str, Any]:
        ward_records = [r for r in self.chain if r.ward_name.lower() == ward_name.lower()]
        total_allocated = sum(r.allocated_ksh for r in ward_records)
        return {
            "ward_name": ward_name,
            "total_petitions": len(ward_records),
            "total_allocated_ksh": total_allocated,
            "records": [r.to_dict() for r in ward_records]
        }


if __name__ == "__main__":
    print("Initializing Nairobi Civic Ledger Sentinel...")
    ledger = NairobiCivicLedger()
    
    # Simulate adding records for Nairobi wards
    ledger.add_petition(
        petition_id="PET-2025-001",
        ward_name="Woodley/Kenyatta Golf Course",
        sector="Water & Sanitation",
        description="Emergency borehole rehabilitation & last-mile piping",
        allocated_ksh=4500000.0
    )
    
    ledger.add_petition(
        petition_id="PET-2025-002",
        ward_name="Kayole North",
        sector="Infrastructure",
        description="Solar-powered street lighting and drainage expansion",
        allocated_ksh=8200000.0
    )
    
    # Run integrity check
    is_valid = ledger.audit_ledger()
    print(f"Ledger cryptographic integrity: {is_valid}")
    
    # Summary test
    summary = ledger.get_ward_summary("Kayole North")
    print("Ward Summary:", json.dumps(summary, indent=2))
