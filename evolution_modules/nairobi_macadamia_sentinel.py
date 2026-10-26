import ast
import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')
logger = logging.getLogger('MacadamiaSentinel')

@dataclass
class MacadamiaBatch:
    batch_id: str
    processing_facility: str
    weight_kg: float
    moisture_pct: float
    crack_recovery_rate: float
    aflatoxin_ppb: float
    status: str = "PENDING_GRADING"

@dataclass
class GradeReport:
    batch_id: str
    assigned_grade: str
    export_certified: bool
    recommendations: List[str] = field(default_factory=list)

class NairobiMacadamiaProcessor:
    """
    Evaluates raw macadamia nut batches entering Nairobi processing hubs for moisture content,
    crack recovery efficiency, and aflatoxin thresholds, ensuring top-tier export compliance.
    """
    def __init__(self, max_allowable_moisture: float = 1.5, max_aflatoxin_ppb: float = 2.0):
        self.max_allowable_moisture = max_allowable_moisture
        self.max_aflatoxin_ppb = max_aflatoxin_ppb
        self.batches: Dict[str, MacadamiaBatch] = {}

    def register_batch(self, batch: MacadamiaBatch) -> None:
        self.batches[batch.batch_id] = batch
        logger.info(f"Registered macadamia batch {batch.batch_id} at {batch.processing_facility} ({batch.weight_kg} kg).")

    def evaluate_batch(self, batch_id: str) -> GradeReport:
        if batch_id not in self.batches:
            raise ValueError(f"Batch {batch_id} not found in processor registry.")
        
        batch = self.batches[batch_id]
        recs = []
        export_ready = True
        
        # Moisture check (Target: 1.2% - 1.5% for optimum kernel crispness)
        if batch.moisture_pct > self.max_allowable_moisture:
            export_ready = False
            recs.append(f"Moisture level {batch.moisture_pct}% exceeds maximum limit ({self.max_allowable_moisture}%). Requires extended kiln drying.")
        elif batch.moisture_pct < 1.0:
            recs.append(f"Moisture level {batch.moisture_pct}% is too low; risk of brittle kernel fracturing.")

        # Aflatoxin safety threshold
        if batch.aflatoxin_ppb > self.max_aflatoxin_ppb:
            export_ready = False
            recs.append(f"Aflatoxin concentration {batch.aflatoxin_ppb} ppb exceeds international safety limit ({self.max_aflatoxin_ppb} ppb). Quarantine batch.")

        # Crack recovery rate grading
        if batch.crack_recovery_rate >= 38.0 and export_ready:
            grade = "GRADE_I_PREMIUM_EXTRA"
            recs.append("Meets European and North American gourmet snack standards.")
        elif batch.crack_recovery_rate >= 32.0 and export_ready:
            grade = "GRADE_II_STANDARD_KERNEL"
            recs.append("Suitable for commercial ingredient blending and confectionery use.")
        else:
            grade = "SUB_STANDARD_OIL_EXTRACTION"
            export_ready = False
            recs.append("Diverted to mechanical cold-pressed cosmetic macadamia oil production.")

        batch.status = grade
        logger.info(f"Evaluated batch {batch_id}: {grade} (Export Certified: {export_ready})")
        return GradeReport(batch_id=batch_id, assigned_grade=grade, export_certified=export_ready, recommendations=recs)

if __name__ == '__main__':
    logger.info("Executing self-test for NairobiMacadamiaProcessor...")
    processor = NairobiMacadamiaProcessor()
    
    test_batch = MacadamiaBatch(
        batch_id="MAC-NBI-2026-009",
        processing_facility="Thika Road Agro-Industrial Park",
        weight_kg=4500.0,
        moisture_pct=1.4,
        crack_recovery_rate=39.5,
        aflatoxin_ppb=0.5
    )
    
    processor.register_batch(test_batch)
    report = processor.evaluate_batch("MAC-NBI-2026-009")
    print(f"Test Report Result: {report}")
    
    # Validate syntax integrity
    source_code = open(__file__).read()
    ast.parse(source_code)
    logger.info("Module AST compilation verified successfully.")
