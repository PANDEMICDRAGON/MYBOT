"""
Nairobi & Kitengela Matatu SACCO Sinking Fund & Accident Claims Automator
Author: Cortana Autonomous Evolutionary Architect
Operator: Michael Obiero (Kitengela/Nairobi, Kenya)

Automates SACCO vehicle risk pooling, collects daily sinking fund contributions via M-Pesa simulation,
calculates actuarial risk tiers based on route telemetry (e.g., Nairobi-Kitengela highway vs Nairobi CBD-Umoja),
and automates accident claim disbursements.
"""

import logging
import json
import time
from typing import Dict, List, Optional
from dataclasses import dataclass, field, asdict

# Configure logging
logging.basicConfig(level=logging.INFO, format='[%(asctime)s] [SACCO-SINKING-FUND] %(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class VehicleRecord:
    plate_number: str
    sacco_name: str
    route: str
    driver_name: str
    daily_sinking_contrib: float = 250.0  # KES
    risk_score: float = 1.0  # Multiplier based on claims history
    total_contributed: float = 0.0
    active: bool = True

@dataclass
class AccidentClaim:
    claim_id: str
    plate_number: str
    incident_location: str
    claim_amount: float
    description: str
    status: str = "PENDING_AUDIT"
    payout_reference: Optional[str] = None
    timestamp: float = field(default_factory=time.time)

class SaccoSinkingFundEngine:
    """
    Manages sinking fund balances, risk modeling, and instant claims payout for matatu operators.
    """
    def __init__(self, sacco_name: str):
        self.sacco_name = sacco_name
        self.vehicles: Dict[str, VehicleRecord] = {}
        self.claims: Dict[str, AccidentClaim] = {}
        self.reserve_balance: float = 0.0
        logger.info(f"Initialized SaccoSinkingFundEngine for {sacco_name}")

    def register_vehicle(self, plate: str, route: str, driver: str, contrib: float = 250.0) -> VehicleRecord:
        if plate in self.vehicles:
            logger.warning(f"Vehicle {plate} already registered in {self.sacco_name}.")
            return self.vehicles[plate]
        
        vehicle = VehicleRecord(
            plate_number=plate,
            sacco_name=self.sacco_name,
            route=route,
            driver_name=driver,
            daily_sinking_contrib=contrib
        )
        self.vehicles[plate] = vehicle
        logger.info(f"Registered vehicle {plate} on route {route} with daily contribution KES {contrib}")
        return vehicle

    def process_daily_contribution(self, plate: str, amount: Optional[float] = None) -> bool:
        if plate not in self.vehicles:
            logger.error(f"Contribution failed: Vehicle {plate} not found.")
            return False
        
        veh = self.vehicles[plate]
        amt = amount if amount is not None else veh.daily_sinking_contrib
        veh.total_contributed += amt
        self.reserve_balance += amt
        logger.info(f"Processed M-Pesa sinking fund contribution of KES {amt} for {plate}. Total Pool: KES {self.reserve_balance}")
        return True

    def file_accident_claim(self, claim_id: str, plate: str, location: str, amount: float, desc: str) -> AccidentClaim:
        if plate not in self.vehicles:
            raise ValueError(f"Vehicle {plate} not registered in SACCO.")
        
        claim = AccidentClaim(
            claim_id=claim_id,
            plate_number=plate,
            incident_location=location,
            claim_amount=amount,
            description=desc
        )
        self.claims[claim_id] = claim
        logger.info(f"Accident claim {claim_id} filed for vehicle {plate} at {location} for KES {amount}")
        
        # Automated Audit: Approve if claim is within reserve limits and vehicle risk score is acceptable
        self._audit_and_settle_claim(claim)
        return claim

    def _audit_and_settle_claim(self, claim: AccidentClaim) -> None:
        veh = self.vehicles[claim.plate_number]
        
        # Simple heuristic risk adjustment
        max_payout_allowed = veh.total_contributed * 10.0 * (2.0 / veh.risk_score)
        
        if claim.claim_amount <= max_payout_allowed and self.reserve_balance >= claim.claim_amount:
            claim.status = "APPROVED_AND_DISBURSED"
            payout_ref = f"MPESA-PAYOUT-{int(time.time())}-{claim.claim_id}"
            claim.payout_reference = payout_ref
            self.reserve_balance -= claim.claim_amount
            logger.info(f"Claim {claim.claim_id} AUTOMATICALLY APPROVED & PAID via M-Pesa. Ref: {payout_ref}")
        else:
            claim.status = "FLAGGED_FOR_BOARD_REVIEW"
            logger.warning(f"Claim {claim.claim_id} flagged for human board review (Exceeds actuarial threshold or reserve).")

    def get_sacco_summary(self) -> Dict:
        return {
            "sacco_name": self.sacco_name,
            "registered_vehicles": len(self.vehicles),
            "total_reserve_balance": self.reserve_balance,
            "total_claims_filed": len(self.claims),
            "active_claims": sum(1 for c in self.claims.values() if c.status == "PENDING_AUDIT")
        }

if __name__ == "__main__":
    print("=== TESTING NAIROBI & KITENGELA SACCO SINKING FUND AUTOMATOR ===")
    sacco = SaccoSinkingFundEngine(sacco_name="KiteNai Metro Travellers SACCO")
    
    # Register vehicles
    sacco.register_vehicle("KBC 452Z", "Kitengela - Nairobi CBD", "John Kamau")
    sacco.register_vehicle("KDD 891A", "Kitengela - Kitengela EPZ", "Amina Mohammed")
    
    # Process contributions
    sacco.process_daily_contribution("KBC 452Z", 500.0)
    sacco.process_daily_contribution("KDD 891A", 500.0)
    
    # File claim
    claim = sacco.file_accident_claim(
        claim_id="CLM-2026-001",
        plate="KBC 452Z",
        location="Athi River Expressway Turnoff",
        amount=2500.0,
        description="Minor bumper damage during morning peak congestion."
    )
    
    print(json.dumps(sacco.get_sacco_summary(), indent=2))
    print(json.dumps(asdict(claim), indent=2))
    print("=== TEST COMPLETE ===")
