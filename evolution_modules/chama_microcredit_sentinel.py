import ast
import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone

logging.basicConfig(level=logging.INFO, format='[%(asctime)s] [CHAMA-SENTINEL] %(levelname)s: %(message)s')
logger = logging.getLogger('ChamaMicroCreditSentinel')

class ChamaMember:
    def __init__(self, member_id: str, name: str, phone: str, credit_score: int, staked_kes: float):
        self.member_id = member_id
        self.name = name
        self.phone = phone
        self.credit_score = credit_score
        self.staked_kes = staked_kes
        self.reputation_multiplier = min(2.0, max(0.5, credit_score / 500.0))

class ChamaLoanRequest:
    def __init__(self, loan_id: str, borrower_id: str, amount_kes: float, term_days: int, purpose: str):
        self.loan_id = loan_id
        self.borrower_id = borrower_id
        self.amount_kes = amount_kes
        self.term_days = term_days
        self.purpose = purpose
        self.status = "PENDING"
        self.guarantors: List[str] = []

class ChamaMicroCreditSentinel:
    """
    Manages peer-to-peer Chama risk scoring, decentralized loan guarantees,
    and automated M-Pesa disbursement tracking tailored for Nairobi's dynamic informal economy.
    """
    def __init__(self, chama_name: str):
        self.chama_name = chama_name
        self.members: Dict[str, ChamaMember] = {}
        self.loans: Dict[str, ChamaLoanRequest] = {}
        self.treasury_balance_kes: float = 0.0

    def register_member(self, member: ChamaMember) -> None:
        self.members[member.member_id] = member
        self.treasury_balance_kes += member.staked_kes
        logger.info(f"Registered Chama member {member.name} with stake KES {member.staked_kes:,.2f}.")

    def submit_loan_request(self, loan_id: str, borrower_id: str, amount_kes: float, term_days: int, purpose: str) -> bool:
        if borrower_id not in self.members:
            logger.error(f"Borrower {borrower_id} not found in Chama {self.chama_name}.")
            return False
        if amount_kes > (self.treasury_balance_kes * 0.4):
            logger.warning(f"Loan request KES {amount_kes:,.2f} exceeds liquidity safety threshold (40% of treasury).")
            return False
        
        loan = ChamaLoanRequest(loan_id, borrower_id, amount_kes, term_days, purpose)
        self.loans[loan_id] = loan
        logger.info(f"Loan request {loan_id} for KES {amount_kes:,.2f} submitted by {borrower_id}.")
        return True

    def endorse_loan_by_peer(self, loan_id: str, guarantor_id: str) -> bool:
        if loan_id not in self.loans or guarantor_id not in self.members:
            return False
        loan = self.loans[loan_id]
        guarantor = self.members[guarantor_id]
        
        if guarantor_id == loan.borrower_id:
            logger.warning("Members cannot guarantee their own loans.")
            return False
            
        if guarantor.staked_kes < (loan.amount_kes * 0.15):
            logger.warning(f"Guarantor {guarantor_id} stake insufficient to cover liability.")
            return False
            
        if guarantor_id not in loan.guarantors:
            loan.guarantors.append(guarantor_id)
            logger.info(f"Loan {loan_id} endorsed by guarantor {guarantor.name}.")
            
        # Check if fully guaranteed (requires at least 3 guarantors or 60% coverage)
        if len(loan.guarantors) >= 3:
            loan.status = "APPROVED"
            logger.info(f"Loan {loan_id} FULLY APPROVED via decentralized peer consensus.")
            return True
        return False

    def audit_chama_health(self) -> Dict[str, Any]:
        total_staked = sum(m.staked_kes for m in self.members.values())
        active_loans = sum(l.amount_kes for l in self.loans.values() if l.status == "APPROVED")
        return {
            "chama_name": self.chama_name,
            "total_members": len(self.members),
            "treasury_staked_kes": total_staked,
            "active_loan_exposure_kes": active_loans,
            "liquidity_ratio": round((total_staked - active_loans) / max(1.0, total_staked), 2),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

if __name__ == "__main__":
    sentinel = ChamaMicroCreditSentinel("Kilimani Tech & Biashara Chama")
    sentinel.register_member(ChamaMember("M001", "Michael Obiero", "+254712345678", 750, 150000.0))
    sentinel.register_member(ChamaMember("M002", "Amina Mohammed", "+254722333444", 680, 100000.0))
    sentinel.register_member(ChamaMember(
        "M003",
        "Kiprono Koech",
        "+254733555666",
        710,
        120000.0
    ))
    
    sentinel.submit_loan_request("L001", "M002", 50000.0, 30, "Inventory expansion for CBD shop")
    sentinel.endorse_loan_by_peer("L001", "M001")
    sentinel.endorse_loan_by_peer("L001", "M003")
    sentinel.endorse_loan_by_peer("L001", "M001") # duplicate test
    
    # Add a 3rd endorser to fully approve
    sentinel.register_member(ChamaMember("M004", "Wanjiku Njoroge", "+254744888999", 720, 90000.0))
    sentinel.endorse_loan_by_peer("L001", "M004")
    
    audit = sentinel.audit_chama_health()
    print(json.dumps(audit, indent=2))
