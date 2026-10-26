"""
Nairobi Baobab Textile Upcycling & Garment Circularity Sentinel
Designed for Cortana Autonomous Evolutionary Architect
Operator: Michael Obiero, Nairobi, Kenya
"""

import json
import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("TextileUpcyclingSentinel")


@dataclass
class FabricBatch:
    batch_id: str
    cooperative_name: str
    material_type: str  # e.g., 'cotton_denim', 'polyester_blend', 'kitenge_scrap'
    weight_kg: float
    source_origin: str  # e.g., 'Gikomba Market', 'Industrial Area Surplus'
    natural_dye_compatible: bool
    processing_stage: str = "RECEIVED"  # RECEIVED, SORTED, UPGRADED, DISPATCHED
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())


class TextileUpcyclingSentinel:
    """
    Manages traceability, quality control, and circularity metrics for Nairobi artisan textile upcyclers.
    """

    def __init__(self, facility_name: str = "Nairobi Eastlands Upcycling Hub") -> None:
        self.facility_name = facility_name
        self.batches: Dict[str, FabricBatch] = {}
        self.total_diverted_kg: float = 0.0
        logger.info(f"Initialized {self.facility_name} Textile Upcycling Sentinel.")

    def register_batch(self, batch: FabricBatch) -> bool:
        """Registers an incoming textile scrap batch."""
        if batch.batch_id in self.batches:
            logger.warning(f"Batch {batch.batch_id} already registered.")
            return False
        self.batches[batch.batch_id] = batch
        logger.info(f"Registered textile batch {batch.batch_id} from {batch.cooperative_name} ({batch.weight_kg} kg).")
        return True

    def advance_stage(self, batch_id: str, new_stage: str) -> bool:
        """Advances the processing stage of a textile batch."""
        batch = self.batches.get(batch_id)
        if not batch:
            logger.error(f"Batch {batch_id} not found.")
            return False
        valid_stages = ["RECEIVED", "SORTED", "UPGRADED", "DISPATCHED"]
        if new_stage not in valid_stages:
            logger.error(f"Invalid stage: {new_stage}")
            return False
        
        batch.processing_stage = new_stage
        if new_stage == "DISPATCHED":
            self.total_diverted_kg += batch.weight_kg
            logger.info(f"Batch {batch_id} completed circular lifecycle. Diverted total: {self.total_diverted_kg} kg.")
        else:
            logger.info(f"Batch {batch_id} advanced to {new_stage}.")
        return True

    def generate_sustainability_report(self) -> Dict:
        """Generates sustainability audit metrics for Nairobi municipal circular economy compliance."""
        active_batches = len(self.batches)
        return {
            "facility": self.facility_name,
            "total_batches_processed": active_batches,
            "total_textile_diverted_kg": self.total_diverted_kg,
            "timestamp": datetime.utcnow().isoformat(),
            "status": "OPERATIONAL"
        }


if __name__ == "__main__":
    sentinel = TextileUpcyclingSentinel()
    b1 = FabricBatch(
        batch_id="TXT-GIK-2026-001",
        cooperative_name="Umoja Makao Stitchers",
        material_type="kitenge_scrap",
        weight_kg=150.5,
        source_origin="Gikomba Market",
        natural_dye_compatible=True
    )
    sentinel.register_batch(b1)
    sentinel.advance_stage("TXT-GIK-2026-001", "SORTED")
    sentinel.advance_stage("TXT-GIK-2026-001", "UPGRADED")
    sentinel.advance_stage("TXT-GIK-2026-001", "DISPATCHED")
    print(json.dumps(sentinel.generate_sustainability_report(), indent=2))
