import hashlib
import hmac
import json
import logging
import time

from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("NairobiFreelanceEscrow")

@dataclass
class Milestone:
    milestone_id: str
    description: str
    amount_kes: float
    status: str = "PENDING" # PENDING, LOCKED, SUBMITTED, APPROVED, DISBURSED
    artifact_hash: Optional[str] = None
    disbursement_ref: Optional[str] = None

@dataclass
class ProjectContract:
    contract_id: str
    client_phone: str
    developer_phone: str
    total_amount_kes: float
    milestones: List[Milestone] = field(default_factory=list)
    created_at: float = field(default_factory=time.time)
    is_dispute: bool = False

class NairobiFreelanceEscrowEngine:
    """
    Manages crypto-verified milestones and M-Pesa disbursement triggers for local and diaspora projects.
    """
    def __init__(self, secret_salt: str = "CORTANA_NAIROBI_ESCROW_SALT_2026"):
        self.secret_salt = secret_salt.encode('utf-8')
        self.contracts: Dict[str, ProjectContract] = {}

    def create_contract(self, contract_id: str, client_phone: str, developer_phone: str, milestones_data: List[Dict[str, Any]]) -> ProjectContract:
        milestones = []
        total = 0.0
        for m in milestones_data:
            ms = Milestone(
                milestone_id=m["milestone_id"],
                description=m["description"],
                amount_kes=float(m["amount_kes"])
            )
            milestones.append(ms)
            total += ms.amount_kes

        contract = ProjectContract(
            contract_id=contract_id,
            client_phone=client_phone,
            developer_phone=developer_phone,
            total_amount_kes=total,
            milestones=milestones
        )
        self.contracts[contract_id] = contract
        logger.info(f"[ESCROW] Created contract {contract_id} with {len(milestones)} milestones totalling KES {total}")
        return contract

    def lock_funds(self, contract_id: str, stubs_transaction_id: str) -> bool:
        contract = self.contracts.get(contract_id)
        if not contract:
            raise ValueError(f"Contract {contract_id} not found.")
        
        for m in contract.milestones:
            if m.status == "PENDING":
                m.status = "LOCKED"
                
        logger.info(f"[ESCROW] Funds locked via M-Pesa STK ID {stubs_transaction_id} for contract {contract_id}")
        return True

    def submit_deliverable(self, contract_id: str, milestone_id: str, artifact_data: str) -> str:
        contract = self.contracts.get(contract_id)
        if not contract:
            raise ValueError(f"Contract {contract_id} not found.")

        milestone = next((m for m in contract.milestones if m.milestone_id == milestone_id), None)
        if not milestone:
            raise ValueError(f"Milestone {milestone_id} not found.")

        if milestone.status != "LOCKED":
            raise ValueError(f"Milestone must be LOCKED to submit. Current status: {milestone.status}")

        # Generate cryptographic proof of artifact delivery
        h = hmac.new(self.secret_salt, artifact_data.encode('utf-8'), hashlib.sha256).hexdigest()
        milestone.artifact_hash = h
        milestone.status = "SUBMITTED"
        
        logger.info(f"[ESCROW] Deliverable submitted for {contract_id}:{milestone_id}. Hash: {h[:12]}...")
        return h

    def approve_and_disburse(self, contract_id: str, milestone_id: str) -> Dict[str, Any]:
        contract = self.contracts.get(contract_id)
        if not contract:
            raise ValueError(f"Contract {contract_id} not found.")

        milestone = next((m for m in contract.milestones if m.milestone_id == milestone_id), None)
        if not milestone:
            raise ValueError(f"Milestone {milestone_id} not found.")

        if milestone.status != "SUBMITTED":
            raise ValueError(f"Milestone not in SUBMITTED state. Current: {milestone.status}")

        # Simulate M-Pesa B2C payout
        b2c_ref = f"MPESA_B2C_DISB_{int(time.time())}_{milestone.milestone_id}"
        milestone.disbursement_ref = b2c_ref
        milestone.status = "DISBURSED"

        logger.info(f"[ESCROW] Disbursed KES {milestone.amount_kes} to {contract.developer_phone}. Ref: {b2c_ref}")
        return {
            "status": "SUCCESS",
            "contract_id": contract_id,
            "milestone_id": milestone_id,
            "amount_kes": milestone.amount_kes,
            "developer_phone": contract.developer_phone,
            "disbursement_reference": b2c_ref
        }

if __name__ == "__main__":
    engine = NairobiFreelanceEscrowEngine()
    milestones_spec = [
        {"milestone_id": "M1", "description": "Nairobi IoT Microclimate Node Firmware", "amount_kes": 25000.0},
        {"milestone_id": "M2", "description": "Nairobi Cloud Dashboard Integration", "amount_kes": 40000.0}
    ]
    
    contract = engine.create_contract(
        contract_id="CTR-2026-001",
        client_phone="+254712345678",
        developer_phone="+254798765432",
        milestones_data=milestones_spec
    )
    
    engine.lock_funds("CTR-2026-001", "STK_MPESA_XYZ123")
    engine.submit_deliverable("CTR-2026-001", "M1", "git_commit_sha_9f8e7d6c5b4a")
    res = engine.approve_and_disburse("CTR-2026-001", "M1")
    print(json.dumps(res, indent=2))
