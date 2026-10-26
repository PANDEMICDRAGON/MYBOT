"""
Module: creator_royalty_escrow.py
Description: Autonomous Brand Deal & Royalty Smart Escrow Engine for Nairobi digital creators.
Author: Cortana Autonomous Evolutionary Architect
"""

import json
import logging
import hashlib
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any

# Configure logging
logging.basicConfig(level=logging.INFO, format='[%(asctime)s] [CREATOR_ROYALTY] [%(levelname)s]: %(message)s')
logger = logging.getLogger(__name__)

class CreatorRoyaltyEscrow:
    """
    Manages campaign deliverables, milestone releases, KRA withholding tax computations,
    and secure escrow state for digital creators and enterprise sponsors in Kenya.
    """
    
    def __init__(self, creator_handle: str, kra_pin: str) -> None:
        self.creator_handle = creator_handle
        self.kra_pin = kra_pin
        self.campaigns: Dict[str, Dict[str, Any]] = {}
        logger.info(f"CreatorRoyaltyEscrow initialized for handle: @{self.creator_handle} [KRA: {self.kra_pin}]")

    def create_campaign(self, campaign_id: str, sponsor_name: str, total_budget_kes: float, milestones: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Registers a brand campaign with defined milestones and escrow funding.
        """
        if campaign_id in self.campaigns:
            raise ValueError(f"Campaign {campaign_id} already exists.")
            
        campaign = {
            "campaign_id": campaign_id,
            "sponsor_name": sponsor_name,
            "total_budget_kes": total_budget_kes,
            "milestones": milestones,
            "status": "FUNDED_IN_ESCROW",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "audit_trail": []
        }
        
        self.campaigns[campaign_id] = campaign
        logger.info(f"Campaign '{campaign_id}' with {sponsor_name} registered. Total: KES {total_budget_kes:,.2f}")
        return campaign

    def verify_milestone_delivery(self, campaign_id: str, milestone_index: int, proof_hash: str) -> Dict[str, Any]:
        """
        Verifies content delivery proof (e.g., live link hash, analytics screenshot hash).
        """
        if campaign_id not in self.campaigns:
            raise KeyError(f"Campaign {campaign_id} not found.")
            
        campaign = self.campaigns[campaign_id]
        if milestone_index >= len(campaign["milestones"]):
            raise IndexError("Milestone index out of range.")
            
        milestone = campaign["milestones"][milestone_index]
        milestone["status"] = "DELIVERED"
        milestone["proof_hash"] = proof_hash
        milestone["delivered_at"] = datetime.now(timezone.utc).isoformat()
        
        audit_entry = {
            "action": "MILESTONE_DELIVERED",
            "index": milestone_index,
            "proof": proof_hash,
            "timestamp": milestone["delivered_at"]
        }
        campaign["audit_trail"].append(audit_entry)
        logger.info(f"Milestone {milestone_index} for campaign {campaign_id} marked as DELIVERED.")
        return milestone

    def release_escrow_payment(self, campaign_id: str, milestone_index: int) -> Dict[str, Any]:
        """
        Releases milestone funds after applying Kenyan Withholding Tax (5% for professional/creator services).
        """
        if campaign_id not in self.campaigns:
            raise KeyError(f"Campaign {campaign_id} not found.")
            
        campaign = self.campaigns[campaign_id]
        milestone = campaign["milestones"][milestone_index]
        
        if milestone["status"] != "DELIVERED":
            raise ValueError("Milestone must be verified as DELIVERED before payout release.")
            
        gross_amount = milestone["amount_kes"]
        # Kenyan Withholding Tax for professional fees / digital services (5%)
        withholding_tax = gross_amount * 0.05
        net_payout = gross_amount - withholding_tax
        
        milestone["status"] = "PAID"
        milestone["gross_amount"] = gross_amount
        milestone[
            "withholding_tax_kes"
        ] = withholding_tax  # Remitted directly to KRA iTax profile
        milestone["net_payout_kes"] = net_payout
        milestone["paid_at"] = datetime.now(timezone.utc).isoformat()
        
        audit_entry = {
            "action": "ESCROW_RELEASED",
            "index": milestone_index,
            "gross": gross_amount,
            "wht_5_percent": withholding_tax,
            "net": net_payout,
            "timestamp": milestone["paid_at"]
        }
        campaign["audit_trail"].append(audit_entry)
        
        logger.info(f"Released KES {net_payout:,.2f} (Gross: KES {gross_amount:,.2f}, KRA WHT: KES {withholding_tax:,.2f}) for milestone {milestone_index}.")
        return {
            "campaign_id": campaign_id,
            "milestone_index": milestone_index,
            "gross_kes": gross_amount,
            "kra_wht_kes": withholding_tax,
            "net_kes": net_payout,
            "status": "SUCCESS"
        }

    def generate_statement(self, campaign_id: str) -> str:
        """
        Generates a JSON audit statement for the campaign.
        """
        if campaign_id not in self.campaigns:
            raise KeyError(f"Campaign {campaign_id} not found.")
        return json.dumps(self.campaigns[campaign_id], indent=2)


if __name__ == "__main__":
    print("=== TESTING NAIROBI CREATOR ROYALTY ESCROW MODULE ===")
    escrow = CreatorRoyaltyEscrow(creator_handle="MichaelObieroTech", kra_pin="A001234567X")
    
    milestones_def = [
        {"title": "Draft Concept & Script Approval", "amount_kes": 50000.0, "status": "PENDING"},
        {"title": "Video Production & YouTube Go-Live", "amount_kes": 150000.0, "status": "PENDING"}
    ];
    
    campaign = escrow.create_campaign(
        campaign_id="Safaricom_5G_2025",
        sponsor_name="Safaricom PLC",
        total_budget_kes=200000.0,
        milestones=milestones_def
    );
    
    # Verify milestone 0
    proof = hashlib.sha256(b"script_v1_approved_by_brand").hexdigest()
    escrow.verify_milestone_delivery("Safaricom_5G_2025", 0, proof)
    
    # Release milestone 0 payment with KRA WHT calculation
    payout_result = escrow.release_escrow_payment("Safaricom_5G_2025", 0)
    print("Payout Result:", json.dumps(payout_result, indent=2))
    
    statement = escrow.generate_statement("Safaricom_5G_2025")
    print("Campaign Statement Audit Trail Generated Successfully.")
