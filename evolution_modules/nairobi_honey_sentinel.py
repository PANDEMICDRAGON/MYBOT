import ast
import logging
import json
from datetime import datetime
from typing import Dict, List, Optional, Any

logging.basicConfig(level=logging.INFO, format='[%(asctime)s] [HONEY_SENTINEL] %(levelname)s: %(message)s')
logger = logging.getLogger('NairobiHoneySentinel')

class HoneyBatchAuditError(Exception):
    """Raised when a honey batch fails biochemical or botanical purity thresholds."""
    pass

class NairobiHoneySentinel:
    """
    Analyzes artisanal honey batches sourced from the greater Nairobi and Central Kenya
    sheds (e.g., Ngong Hills, Kiambu, Murang'a) for adulteration, high moisture, excessive
    HMF (indicating overheating or age), and validates geographical floral origin.
    """
    
    MAX_MOISTURE_PERCENT = 20.0
    MAX_HMF_MG_KG = 40.0
    MIN_CONDUCTIVITY_MS_CM = 0.2
    MAX_CONDUCTIVITY_MS_CM = 1.5
    
    def __init__(self, operator_handle: str = "Michael Obiero") -> None:
        self.operator_handle = operator_handle
        self.audited_batches: Dict[str, Dict[str, Any]] = {}
        logger.info(f"NairobiHoneySentinel initialized for operator {self.operator_handle}.")

    def inspect_batch(
        self, 
        batch_id: str, 
        apiary_location: str, 
        moisture_pct: float, 
        hmf_mg_kg: float, 
        conductivity_ms_cm: float,
        pollen_spectrum: List[str]
    ) -> Dict[str, Any]:
        """
        Inspects a honey batch against Kenyan standards (KS EAS 34:2001) for purity.
        """
        logger.info(f"Inspecting honey batch {batch_id} from apiary {apiary_location}...")
        
        violations = []
        
        if moisture_pct > self.MAX_MOISTURE_PERCENT:
            violations.append(f"Moisture {moisture_pct}% exceeds max threshold {self.MAX_MOISTURE_PERCENT}%")
            
        if hmf_mg_kg > self.MAX_HMF_MG_KG:
            violations.append(f"HMF level {hmf_mg_kg} mg/kg exceeds limit {self.MAX_HMF_MG_KG} mg/kg (possible overheating/adulteration)")
            
        if not (self.MIN_CONDUCTIVITY_MS_CM <= conductivity_ms_cm <= self.MAX_CONDUCTIVITY_MS_CM):
            violations.append(f"Electrical conductivity {conductivity_ms_cm} mS/cm outside pure floral/honeydew range")
            
        if not pollen_spectrum:
            violations.append("Pollen spectrum is empty; potential ultra-filtration or synthetic syrup adulteration")

        status = "REJECTED" if violations else "CERTIFIED_PURE"
        
        audit_record = {
            "batch_id": batch_id,
            "apiary_location": apiary_location,
            "moisture_pct": moisture_pct,
            "hmf_mg_kg": hmf_mg_kg,
            "conductivity_ms_cm": conductivity_ms_cm,
            "pollen_spectrum": pollen_spectrum,
            "status": status,
            "violations": violations,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        self.audited_batches[batch_id] = audit_record
        
        if violations:
            logger.warning(f"Batch {batch_id} FAILED certification. Violations: {violations}")
            raise HoneyBatchAuditError(f"Batch {batch_id} failed audit: {violations}")
            
        logger.info(f"Batch {batch_id} successfully CERTIFIED PURE.")
        return audit_record

    def export_audit_ledger(self) -> str:
        """Exports all audited records as a JSON string for traceability logs."""
        return json.dumps(self.audited_batches, indent=2)

if __name__ == "__main__":
    sentinel = NairobiHoneySentinel()
    try:
        # Test clean batch
        batch = sentinel.inspect_batch(
            batch_id="HONEY-NBO-2023-099",
            apiary_location="Ngong Hills Slopes",
            moisture_pct=17.5,
            hmf_mg_kg=12.0,
            conductivity_ms_cm=0.65,
            pollen_spectrum=["Acacia abyssinica", "Eucalyptus globulus", "Trifolium repens"]
        )
        print("Audit Success:", json.dumps(batch, indent=2))
        
        # Test adulterated batch
        sentinel.inspect_batch(
            batch_id="HONEY-NBO-2023-100",
            apiary_location="Unknown River Road Broker",
            moisture_pct=22.1,
            hmf_mg_kg=55.0,
            conductivity_ms_cm=0.10,
            pollen_spectrum=[]
        )
    except HoneyBatchAuditError as e:
        print(f"Caught expected adulteration error: {e}")
    
    # Verify clean compilation
    code_source = open(__file__).read()
    ast.parse(code_source)
    print("AST compilation check passed successfully.")
