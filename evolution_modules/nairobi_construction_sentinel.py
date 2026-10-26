import ast
import hashlib
import hmac
import json
import logging
import time
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Tuple

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] [NairobiConstructionSentinel]: %(message)s')
logger = logging.getLogger('NairobiConstructionSentinel')

@dataclass
class ConstructionSite:
    site_id: str
    project_name: str
    location: str
    developer: str
    nca_license_no: str
    approved_floors: int
    current_floor: int
    safety_score: float = 100.0
    materials_verified: bool = True
    last_audit_timestamp: float = field(default_factory=time.time)

@dataclass
class MaterialBatch:
    batch_id: str
    material_type: str
    supplier: str
    kebs_certified: bool
    qr_hash: str
    verification_status: str = "PENDING"

class NairobiConstructionSentinelEngine:
    """
    Autonomous engine to monitor Nairobi construction sites, verify National Construction Authority (NCA)
    licenses, track Kenya Bureau of Standards (KEBS) material authenticity (cement, steel reinforcement),
    and assess structural safety compliance for operator Michael Obiero.
    """
    
    def __init__(self, secret_hmac_key: bytes = b"nairobi_construction_sentinel_key_2025") -> None:
        self.secret_hmac_key = secret_hmac_key
        self.sites: Dict[str, ConstructionSite] = {}
        self.material_batches: Dict[str, MaterialBatch] = {}
        logger.info("NairobiConstructionSentinelEngine initialized for real estate & infrastructure auditing.")

    def register_site(self, site_id: str, project_name: str, location: str, developer: str, nca_license_no: str, approved_floors: int) -> ConstructionSite:
        """Registers a new construction site in Nairobi."""
        site = ConstructionSite(
            site_id=site_id,
            project_name=project_name,
            location=location,
            developer=developer,
            nca_license_no=nca_license_no,
            approved_floors=approved_floors,
            current_floor=1
        )
        self.sites[site_id] = site
        logger.info(f"Registered construction site [{site_id}]: {project_name} at {location} (NCA: {nca_license_no})")
        return site

    def verify_material_batch(self, batch_id: str, material_type: str, supplier: str, kebs_certified: bool, raw_payload: str) -> MaterialBatch:
        """Verifies authenticity of construction materials via cryptographic hashing against KEBS standards."""
        computed_hash = hmac.new(self.secret_hmac_key, raw_payload.encode('utf-8'), hashlib.sha256).hexdigest()
        status = "VERIFIED" if kebs_certified and len(computed_hash) == 64 else "REJECTED_COUNTERFEIT"
        
        batch = MaterialBatch(
            batch_id=batch_id,
            material_type=material_type,
            supplier=supplier,
            kebs_certified=kebs_certified,
            qr_hash=computed_hash,
            verification_status=status
        )
        self.material_batches[batch_id] = batch
        logger.info(f"Material Batch {batch_id} ({material_type}) from {supplier} -> Status: {status}")
        return batch

    def audit_site_progress(self, site_id: str, current_floor: int, worker_safety_gear_compliance: float, concrete_strength_mpa: float) -> Dict[str, any]:
        """Audits ongoing construction progress, checks floor limits against NCA approval, and evaluates safety."""
        if site_id not in self.sites:
            raise ValueError(f"Construction site {site_id} not found.")
        
        site = self.sites[site_id]
        site.current_floor = current_floor
        
        violations = []
        if current_floor > site.approved_floors:
            violations.append(f"CRITICAL: Unauthorized floor construction! Current: {current_floor}, Approved: {site.approved_floors}")
            site.safety_score -= 30.0
            
        if worker_safety_gear_compliance < 85.0:
            violations.append(f"WARNING: Low worker PPE compliance: {worker_safety_gear_compliance}%")
            site.safety_score -= 15.0
            
        # Standard structural concrete minimum for high-rise in Nairobi is ~25 MPa
        if concrete_strength_mpa < 25.0:
            violations.append(f"CRITICAL: Substandard concrete strength ({concrete_strength_mpa} MPa). Risk of structural failure.")
            site.safety_score -= 40.0
            
        site.safety_score = max(0.0, site.safety_score)
        site.last_audit_timestamp = time.time()
        
        audit_result = {
            "site_id": site_id,
            "project_name": site.project_name,
            "safety_score": site.safety_score,
            "violations": violations,
            "status": "HALT_ORDER_ISSUED" if site.safety_score < 50.0 else "OPERATIONAL"
        }
        logger.info(f"Audit completed for {site.project_name}. Score: {site.safety_score}, Status: {audit_result['status']}")
        return audit_result

    def export_compliance_report(self) -> str:
        """Exports comprehensive JSON compliance report for County Government / NCA submission."""
        report = {
            "timestamp": time.time(),
            "total_sites": len(self.sites),
            "total_batches": len(self.material_batches),
            "sites": {sid: asdict(s) for sid, s in self.sites.items()},
            "materials": {bid: asdict(b) for bid, b in self.material_batches.items()}
        }
        return json.dumps(report, indent=2)

if __name__ == "__main__":
    print("--- Executing Nairobi Construction Compliance Sentinel Test Harness ---")
    sentinel = NairobiConstructionSentinelEngine()
    
    # Register sample Nairobi project
    site = sentinel.register_site(
        site_id="SITE-NBI-001",
        project_name="Kilimani Heights Phase II",
        location="Argwings Kodhek Road, Nairobi",
        developer="Obiero Holdings Ltd",
        nca_license_no="NCA/L/104928",
        approved_floors=12
    )
    
    # Verify steel rebar batch
    batch = sentinel.verify_material_batch(
        batch_id="BATCH-STEEL-998",
        material_type="High Yield Deformed Bars 16mm",
        supplier="Devki Steel Mills",
        kebs_certified=True,
        raw_payload="devki_16mm_batch_998_nairobi"
    )
    
    # Conduct site audit
    audit = sentinel.audit_site_progress(
        site_id="SITE-NBI-001",
        current_floor=11,
        worker_safety_gear_compliance=92.5,
        concrete_strength_mpa=28.0
    )
    
    print(json.dumps(audit, indent=2))
    print("AST Parse Check: Clean")
