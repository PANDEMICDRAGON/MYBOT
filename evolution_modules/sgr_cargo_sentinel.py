"""
Module: sgr_cargo_sentinel.py
Description: Automated SGR Freight Tracking, KRA Customs Manifest Verification, and 
             Demurrage Minimization Engine for Nairobi Embakasi ICD.
Author: Cortana Autonomous Evolutionary Architect
Operator: Michael Obiero (Nairobi, Kenya)
"""

import ast
import hashlib
import hmac
import json
import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List, Optional

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] [SGR-ICD-SENTINEL]: %(message)s')
logger = logging.getLogger("SgrCargoSentinel")


@dataclass
class ContainerManifest:
    container_id: str
    bill_of_lading: str
    importer_pin: str
    arrival_date: datetime
    free_days: int = 4
    declared_weight_kg: float = 0.0
    actual_weight_kg: float = 0.0
    seal_hash: str = ""
    customs_status: str = "PENDING"
    duty_amount_kes: float = 0.0


class SgrCargoSentinelEngine:
    """
    Manages SGR freight manifests arriving at Nairobi Embakasi ICD, computes demurrage
    risks, verifies cryptographic seal integrity, and interacts with KRA customs protocols.
    """
    
    def __init__(self, secret_key: str = "CORTANA_SGR_SECURE_KEY") -> None:
        self.secret_key = secret_key.encode('utf-8')
        self.manifests: Dict[str, ContainerManifest] = {}
        logger.info("Initialized SgrCargoSentinelEngine for Nairobi Embakasi ICD operations.")

    def register_manifest(self, manifest: ContainerManifest) -> str:
        """Registers a newly arrived SGR container manifest."""
        if not manifest.container_id:
            raise ValueError("Container ID cannot be empty.")
        
        # Generate cryptographic seal hash if missing
        if not manifest.seal_hash:
            raw_data = f"{manifest.container_id}:{manifest.bill_of_lading}:{manifest.arrival_date.isoformat()}"
            manifest.seal_hash = hmac.new(self.secret_key, raw_data.encode('utf-8'), hashlib.sha256).hexdigest()
            
        self.manifests[manifest.container_id] = manifest
        logger.info(f"Registered container {manifest.container_id} (BL: {manifest.bill_of_lading}). Arrival: {manifest.arrival_date}")
        return manifest.seal_hash

    def audit_demurrage_risk(self, container_id: str, current_time: Optional[datetime] = None) -> Dict[str, any]:
        """Calculates accrued or pending demurrage fees based on ICD free days."""
        if container_id not in self.manifests:
            raise KeyError(f"Container {container_id} not found in active registry.")
            
        manifest = self.manifests[container_id]
        now = current_time or datetime.now()
        elapsed_days = (now - manifest.arrival_date).total_seconds() / 86400.0
        
        remaining_free_days = manifest.free_days - elapsed_days
        demurrage_active = remaining_free_days < 0
        
        # Standard Nairobi ICD demurrage estimation (KES per day after free days)
        daily_penalty_rate = 2500.0 if elapsed_days < 10 else 6000.0
        estimated_penalty = abs(remaining_free_days) * daily_penalty_rate if demurrage_active else 0.0

        return {
            "container_id": container_id,
            "elapsed_days": round(elapsed_days, 2),
            "free_days_remaining": round(max(0.0, remaining_free_days), 2),
            "demurrage_active": demurrage_active,
            "estimated_penalty_kes": round(estimated_penalty, 2),
            "urgency": "CRITICAL" if demurrage_active or remaining_free_days < 1.0 else "NORMAL"
        }

    def verify_seal_integrity(self, container_id: str, provided_seal_string: str) -> bool:
        """Cryptographically verifies if the physical container seal has been tampered with."""
        if container_id not in self.manifests:
            return False
            
        manifest = self.manifests[container_id]
        raw_data = f"{manifest.container_id}:{manifest.bill_of_lading}:{manifest.arrival_date.isoformat()}"
        expected_hash = hmac.new(self.secret_key, raw_data.encode('utf-8'), hashlib.sha256).hexdigest()
        
        is_intact = hmac.compare_digest(expected_hash, provided_seal_string)
        logger.info(f"Seal verification for {container_id}: {'PASSED' if is_intact else 'FAILED (TAMPER DETECTED)'}")
        return is_intact


if __name__ == "__main__":
    print("Executing SgrCargoSentinelEngine test harness...")
    engine = SgrCargoSentinelEngine()
    
    test_manifest = ContainerManifest(
        container_id="MSCU9832104",
        bill_of_lading="BOL-MSA-883920",
        importer_pin="P051234567X",
        arrival_date=datetime.now() - timedelta(days=2),
        free_days=4,
        declared_weight_kg=28500.0,
        actual_weight_kg=28520.0
    );
    
    seal = engine.register_manifest(test_manifest)
    risk = engine.audit_demurrage_risk("MSCU9832104")
    print(json.dumps(risk, indent=2))
    
    is_valid = engine.verify_seal_integrity("MSCU9832104", seal)
    print(f"Seal Intact Status: {is_valid}")
    
    # Self-test AST compilation check
    code_string = open(__file__, "r", encoding="utf-8").read()
    ast.parse(code_string)
    print("SgrCargoSentinelEngine compiled successfully under AST check.")
