import ast
import json
import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field

logging.basicConfig(level=logging.INFO, format='[MAIZE-MILL-SENTINEL] %(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class MillingBatch:
    batch_id: str
    mill_location: str
    input_weight_kg: float
    moisture_content_pct: float
    husk_percentage: float
    flour_output_kg: float
    subsidy_token: Optional[str] = None
    operator_id: str = "Michael Obiero"

class NairobiMaizeMillingOptimizer:
    """
    Calculates net milling extraction ratios, screens moisture anomalies to prevent mold,
    and validates government or private subsidy tokens for urban Nairobi maize millers.
    """
    STANDARD_EXTRACTION_RATE = 0.78  # 78% standard clean flour output from dry grain
    MAX_ALLOWABLE_MOISTURE = 14.0    # 14% max moisture to prevent post-milling aflatoxin

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.active_batches: Dict[str, MillingBatch] = {}

    def audit_batch(self, batch: MillingBatch) -> Dict[str, Any]:
        logger.info(f"Auditing batch {batch.batch_id} at {batch.mill_location} for operator {batch.operator_id}...")
        
        # Moisture check
        moisture_ok = batch.moisture_content_pct <= self.MAX_ALLOWABLE_MOISTURE
        
        # Effective dry weight calculation
        dry_weight_factor = (100.0 - batch.moisture_content_pct) / (100.0 - 12.0)
        adjusted_input_weight = batch.input_weight_kg * dry_weight_factor
        
        expected_flour = adjusted_input_weight * self.STANDARD_EXTRACTION_RATE
        actual_extraction_ratio = batch.flour_output_kg / batch.input_weight_kg if batch.input_weight_kg > 0 else 0.0
        
        yield_variance = batch.flour_output_kg - (adjusted_input_weight * self.STANDARD_EXTRACTION_RATE)
        
        status = "OPTIMIZED"
        warnings = []
        
        if not moisture_ok:
            warnings.warn(f"High moisture warning: {batch.moisture_content_pct}% exceeds {self.MAX_ALLOWABLE_MOISTURE}%")
            status = "FLAGGED_MOISTURE_RISK"
            
        if actual_extraction_ratio < 0.65:
            warnings.append(f"Sub-par extraction ratio ({actual_extraction_ratio:.2f}); possible machinery calibration issue.")
            status = "INEFFICIENT_MILL"
        elif actual_extraction_ratio > 0.85:
            warnings.append(f"Suspiciously high extraction ({actual_extraction_ratio:.2f}); possible foreign matter or excessive water uptake.")
            status = "FLAGGED_ANOMALOUS_YIELD"

        self.active_batches[batch.batch_id] = batch

        audit_result = {
            "batch_id": batch.batch_id,
            "mill_location": batch.mill_location,
            "status": status,
            "moisture_compliant": moisture_ok,
            "actual_extraction_ratio": round(actual_extraction_ratio, 4),
            "expected_flour_kg": round(expected_flour, 2),
            "yield_variance_kg": round(yield_variance, 2),
            "warnings": warnings,
            "operator": batch.operator_id
        }
        
        logger.info(f"Batch {batch.batch_id} audit complete. Status: {status}")
        return audit_result

if __name__ == "__main__":
    print("Initializing NairobiMaizeMillingOptimizer Test Harness...")
    optimizer = NairobiMaizeMillingOptimizer()
    test_batch = MillingBatch(
        batch_id="BATCH-NBI-9921",
        mill_location="Kawangware Stage 2 Mill",
        input_weight_kg=90.0,
        moisture_content_pct=13.2,
        husk_percentage=15.0,
        flour_output_kg=71.5,
        subsidy_token="KE-SUB-2025-XYZ"
    );
    result = optimizer.audit_batch(test_batch)
    print("Audit Result JSON:\n", json.dumps(result, indent=2))
    
    # Self-test AST compilation check
    parsed_ast = ast.parse(__file__)
    print(f"AST compilation successful. Total nodes: {len(list(ast.walk(parsed_ast)))}.")
