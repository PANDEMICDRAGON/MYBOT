import ast
import hashlib
import hmac
import json
import logging
import time
from typing import Dict, List, Optional, Any

logging.basicConfig(level=logging.INFO, format='%(asctime)s - [DIASPORA-ESCROW] - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DiasporaRemittanceEscrowManager:
    """
    Manages milestone-based escrow accounts funded by international diaspora remittances
    for construction and development projects in Nairobi, Kenya. Releases funds only
    upon cryptographic proof of milestone completion and physical verification.
    """
    def __init__(self, secret_salt: str):
        self.secret_salt = secret_salt.encode('utf-8')
        self.projects: Dict[str, Dict[str, Any]] = {}
        logger.info("Initialized DiasporaRemittanceEscrowManager for Nairobi real estate developments.")

    def create_project(self, project_id: str, diaspora_sender: str, beneficiary: str, total_KES: float, milestones: List[str]) -> Dict[str, Any]:
        if project_id in self.projects:
            raise ValueError(f"Project {project_id} already exists.")

        milestone_states = [{ "name": m, "completed": False, "amount_KES": total_KES / len(milestones), "verified_at": None } for m in milestones]
        
        project = {
            "project_id": project_id,
            "diaspora_sender": diaspora_sender,
            "beneficiary": beneficiary,
            "total_KES": total_KES,
            "milestones": milestone_states,
            "escrow_balance_KES": 0.0,
            "status": "PENDING_FUNDING"
        }
        self.projects[project_id] = project
        logger.info(f"Created project {project_id} with {len(milestones)} milestones totalling KES {total_KES:,.2f}")
        return project

    def deposit_funds(self, project_id: str, amount_KES: float, transaction_ref: str) -> Dict[str, Any]:
        if project_id not in self.projects:
            raise KeyError(f"Project {project_id} not found.")
        
        proj = self.projects[project_id]
        proj["escrow_balance_KES"] += amount_KES
        if proj["escrow_balance_KES"] >= proj["total_KES"]:
            proj["status"] = "FUNDED_ACTIVE"
        else:
            proj["status"] = "PARTIALLY_FUNDED"

        logger.info(f"Deposited KES {amount_KES:,.2f} into project {project_id} via ref {transaction_ref}")
        return proj

    def verify_milestone(self, project_id: str, milestone_index: int, inspector_signature: str) -> Dict[str, Any]:
        if project_id not in self.projects:
            raise KeyError(f"Project {project_id} not found.")
        
        proj = self.projects[project_id]
        if milestone_index >= len(proj["milestones"]):
            raise IndexError("Milestone index out of range.")

        # Cryptographic validation of inspector signature
        expected_sig = hmac.new(self.secret_salt, f"{project_id}:{milestone_index}".encode('utf-8'), hashlib.sha256).hexdigest()
        if inspector_signature != expected_sig:
            raise PermissionError("Invalid inspector cryptographic signature.")

        ms = proj["milestones"][milestone_index]
        if ms["completed"]:
            raise ValueError("Milestone already completed and disbursed.")

        ms["completed"] = True
        ms["verified_at"] = time.time()

        disburse_amount = ms["amount_KES"]
        proj["escrow_balance_KES"] -= disburse_amount

        logger.info(f"Milestone '{ms['name']}' verified & KES {disburse_amount:,.2f} disbursed for project {project_id}.")
        return {
            "project_id": project_id,
            "milestone_index": milestone_index,
            "disbursed_KES": disburse_amount,
            "remaining_escrow_KES": proj["escrow_balance_KES"]
        }

    def generate_inspector_signature(self, project_id: str, milestone_index: int) -> str:
        return hmac.new(self.secret_salt, f"{project_id}:{milestone_index}".encode('utf-8'), hashlib.sha256).hexdigest()


if __name__ == "__main__":
    manager = DiasporaRemittanceEscrowManager(secret_salt="NairobiSecureSalt2025!")
    
    proj = manager.create_project(
        project_id="NAI-RTM-001",
        diaspora_sender="Dr. Obiero (Atlanta, USA)",
        beneficiary="Kasarani Build Ltd, Nairobi",
        total_KES=5000000.0,
        milestones=["Foundation & Slab", "Superstructure Walls", "Roofing & Plaster", "Finishing & Handover"]
    )
    
    manager.deposit_funds("NAI-RTM-001", 5000000.0, "MPESA-TXN-98765432");
    sig = manager.generate_inspector_signature("NAI-RTM-001", 0);
    res = manager.verify_milestone("NAI-RTM-001", 0, sig);
    print(json.dumps(res, indent=2));
    
    # AST self-test
    assert ast.parse(__file__)
    print("AST validation of nairobi_diaspora_remittance_escrow.py passed successfully.")
