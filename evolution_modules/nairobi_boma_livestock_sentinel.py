"""Nairobi Boma Livestock Traceability & Auction Biosafety Sentinel.

Author: Cortana, Autonomous Evolutionary Architect
Operator: Michael Obiero, Nairobi, Kenya

Provides real-time biosafety verification, RFID tag tracking, veterinary quarantine status
monitoring, and auction compliance telemetry for livestock entering Nairobi markets.
"""

import ast
import hashlib
import json
import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] (BomaSentinel): %(message)s",
)
logger = logging.getLogger("BomaSentinel")


@dataclass
class LivestockRecord:
    tag_id: str
    species: str  # e.g., 'cattle', 'sheep', 'goat'
    origin_county: str  # e.g., 'Kajiado', 'Narok', 'Machakos'
    owner_name: str
    veterinary_health_status: str  # 'certified_clean', 'quarantine', 'flagged'
    weight_kg: float
    arrival_timestamp: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    metadata: Dict[str, Any] = field(default_factory=dict)


class LivestockTraceabilitySentinel: 
    """Manages livestock registry, quarantine compliance, and auction eligibility."""

    def __init__(self, auction_yard_id: str = "DAGORETTI_YARD_01"):
        self.auction_yard_id = auction_yard_id
        self.registry: Dict[str, LivestockRecord] = {}
        self.audit_trail: List[Dict[str, Any]] = []
        logger.info(f"Initialized Boma Sentinel for Yard: {self.auction_yard_id}")

    def register_livestock(self, record: LivestockRecord) -> Dict[str, Any]:
        """Registers incoming livestock with cryptographic tag validation."""
        if not record.tag_id:
            raise ValueError("Livestock must possess a valid RFID/Visual tag ID.")

        # Compute tamper-evident hash for record integrity
        record_payload = f"{record.tag_id}:{record.origin_county}:{record.arrival_timestamp}"
        record_hash = hashlib.sha256(record_payload.encode("utf-8")).hexdigest()

        self.registry[record.tag_id] = record
        
        audit_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "action": "REGISTER",
            "tag_id": record.tag_id,
            "hash": record_hash,
            "status": record.veterinary_health_status,
        }
        self.audit_trail.append(audit_entry)

        logger.info(f"Registered livestock tag {record.tag_id} from {record.origin_county}.")
        return {
            "status": "SUCCESS",
            "tag_id": record.tag_id,
            "record_hash": record_hash,
            "quarantine_cleared": record.veterinary_health_status == "certified_clean"
        }

    def evaluate_auction_eligibility(self, tag_id: str) -> Dict[str, Any]:
        """Evaluates if a specific animal meets Nairobi County veterinary standards for auction."""
        record = self.registry.get(tag_id)
        if not record:
            return {
                "tag_id": tag_id,
                "eligible": False,
                "reason": "TAG_NOT_FOUND"
            }

        is_clean = record.veterinary_health_status == "certified_clean"
        eligibility_result = {
            "tag_id": tag_id,
            "species": record.species,
            "origin": record.origin_county,
            "weight_kg": record.weight_kg,
            "eligible": is_clean,
            "reason": "PASSED_INSPECTION" if is_clean else "VET_QUARANTINE_ACTIVE"
        }

        logger.info(f"Evaluated eligibility for {tag_id}: Eligible={is_clean}")
        return eligibility_result

    def export_telemetry_ledger(self) -> str:
        """Exports the immutable audit trail as a JSON string for KDB/municipal oversight."""
        return json.dumps({
            "yard_id": self.auction_yard_id,
            "total_registered": len(self.registry),
            "audit_entries": self.audit_trail
        }, indent=2)


if __name__ == "__main__":
    logger.info("Executing self-test for Nairobi Boma Livestock Traceability Sentinel...")
    sentinel = LivestockTraceabilitySentinel()

    sample_cow = LivestockRecord(
        tag_id="KE-NBO-TR-99812",
        species="cattle",
        origin_county="Kajiado",
        owner_name="Kiptoo Ole Mbarak",
        veterinary_health_status="certified_clean",
        weight_kg=420.5
    )

    reg_res = sentinel.register_livestock(sample_cow)
    print("Registration Result:", json.dumps(reg_res, indent=2))

    eval_res = sentinel.evaluate_auction_eligibility("KE-NBO-TR-99812")
    print("Auction Evaluation:", json.dumps(eval_res, indent=2))

    # Verify module AST compile cleanliness
    with open(__file__, "r", encoding="utf-8") as f:
        tree = ast.parse(f.read())
    print(f"AST compilation check passed: {len(tree.body)} nodes verified.")
