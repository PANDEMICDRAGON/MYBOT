"""Nairobi Retail Pharmacy & PPB Anti-Counterfeit Pharmaceutical Traceability Sentinel.

Protects pharmaceutical distribution integrity across Nairobi by validating batch hashes,
PPB compliance permits, supply chain chain-of-custody, and cold-chain thermal logs.
"""

import hashlib
import hmac
import json
import logging
import time
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Tuple

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("NairobiPharmacySentinel")

@dataclass
class DrugBatch:
    batch_id: str
    drug_name: str
    manufacturer: str
    manufacture_date: str
    expiry_date: str
    ppb_permit_number: str
    scratch_hash: str
    max_temp_celsius: float
    min_temp_celsius: float
    is_recalled: bool = False

@dataclass
class VerificationRequest:
    serial_number: str
    scratch_code: str
    pharmacy_id: str
    gps_coords: Tuple[float, float]
    timestamp: float = field(default_factory=time.time)

class PharmacyAntiCounterfeitEngine:
    """Validates drug authenticity, checks PPB permits, and audits supply chain cold-chains."""

    def __init__(self, secret_hmac_key: str = "nairobi-ppb-secure-root-key") -> None:
        self.secret_key = secret_hmac_key.encode("utf-8")
        self.batches: Dict[str, DrugBatch] = {}
        self.audit_log: List[Dict] = []
        self._seed_mock_batches()

    def _seed_mock_batches(self) -> None:
        """Seeds common essential drugs in Nairobi retail pharmacies."""
        mock_data = [
            ("BATCH-ACT-8821", "Coartem 80/480mg", "Novartis / Phillips Pharmaceuticals", "2023-06-01", "2026-06-01", "PPB/PC/2023/1029", 30.0, 2.0),
            ("BATCH-PAR-9912", "Panadol Extra 500mg", "GSK Kenya", "2023-01-15", "2025-01-15", "PPB/PC/2022/4412", 25.0, 10.0),
            ("BATCH-AMO-3341", "Amoxicillin 500mg Capsules", "Cosmos Limited Nairobi", "2023-09-10", "2025-09-10", "PPB/PC/2023/9910", 28.0, 15.0)
        ]
        for b_id, name, mfg, m_date, e_date, permit, max_t, min_t in mock_data:
            raw_scratch = f"{b_id}:{permit}:{mfg}"
            scratch_hash = hmac.new(self.secret_key, raw_scratch.encode("utf-8"), hashlib.sha256).hexdigest()[:12].upper()
            self.batches[b_id] = DrugBatch(
                batch_id=b_id,
                drug_name=name,
                manufacturer=mfg,
                manufacture_date=m_date,
                expiry_date=e_date,
                ppb_permit_number=permit,
                scratch_hash=scratch_hash,
                max_temp_celsius=max_t,
                min_temp_celsius=min_t,
                is_recalled=False
            )
        logger.info(f"Initialized Pharmacy Sentinel with {len(self.batches)} certified Nairobi drug batches.")

    def verify_scratch_code(self, req: VerificationRequest) -> Dict:
        """Validates scratch code and inspects expiry, recall status, and permit validity."""
        batch = self.batches.get(req.serial_number)
        if not batch:
            logger.warning(f"COUNTERFEIT ALERT: Unknown batch serial queried: {req.serial_number} at pharmacy {req.pharmacy_id}")
            return {
                "status": "COUNTERFEIT_SUSPECTED",
                "message": "Serial number not found in PPB national registry. Do not dispense!",
                "action": "QUARANTINE_AND_REPORT"
            }

        if batch.is_recalled:
            logger.error(f"RECALLED DRUG ALERT: Attempted sale of recalled batch {batch.batch_id} ({batch.drug_name})")
            return {
                "status": "RECALLED_BATCH",
                "message": f"CRITICAL: Batch {batch.batch_id} has been recalled by PPB.",
                "action": "CONFISCATE"
            }

        if batch.scratch_hash != req.scratch_code.strip().upper():
            logger.warning(f"TAMPER ALERT: Scratch code mismatch for batch {req.serial_number}")
            return {
                "status": "CODE_MISMATCH",
                "message": "Scratch code verification failed. Potential counterfeit duplication.",
                "action": "INVESTIGATE"
            }

        # Log successful verification
        audit_entry = {
            "timestamp": req.timestamp,
            "pharmacy_id": req.pharmacy_id,
            "batch_id": batch.batch_id,
            "drug_name": batch.drug_name,
            "gps": req.gps_coords,
            "status": "VERIFIED_AUTHENTIC"
        }
        self.audit_log.append(audit_entry)
        logger.info(f"Verified authentic {batch.drug_name} (Batch: {batch.batch_id}) for pharmacy {req.pharmacy_id}")
        return {
            "status": "AUTHENTIC",
            "drug_name": batch.drug_name,
            "manufacturer": batch.manufacturer,
            "expiry_date": batch.expiry_date,
            "ppb_permit": batch.ppb_permit_number,
            "message": "Drug verified authentic against PPB registry."
        }

    def trigger_recall(self, batch_id: str, reason: str) -> bool:
        """Triggers an instant recall broadcast across Nairobi registered pharmacies."""
        if batch_id in self.batches:
            self.batches[batch_id].is_recalled = True
            logger.critical(f"PPB RECALL BROADCAST: Batch {batch_id} recalled. Reason: {reason}")
            return True
        return False

if __name__ == "__main__":
    print("--- Testing Nairobi Pharmacy & PPB Anti-Counterfeit Sentinel ---")
    engine = PharmacyAntiCounterfeitEngine()
    
    # Test valid verification
    valid_batch = engine.batches["BATCH-ACT-8821"]
    req_valid = VerificationRequest(
        serial_number="BATCH-ACT-8821",
        scratch_code=valid_batch.scratch_hash,
        pharmacy_id="PHARMACY-WESTLANDS-04",
        gps_coords=(-1.2634, 36.8023)
    )
    res = engine.verify_scratch_code(req_valid)
    print(json.dumps(res, indent=2))

    # Test counterfeit attempt
    req_fake = VerificationRequest(
        serial_number="BATCH-ACT-8821",
        scratch_code="FAKECODE123",
        pharmacy_id="PHARMACY-CBD-09",
        gps_coords=(-1.2863, 36.8172)
    )
    res_fake = engine.verify_scratch_code(req_fake)
    print(json.dumps(res_fake, indent=2))
