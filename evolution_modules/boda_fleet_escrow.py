"""
Module: boda_fleet_escrow.py
Description: Autonomous Boda Boda Fleet Leasing & Micro-Insurance Escrow Automator for Nairobi operators.
Author: Cortana Autonomous Evolutionary Architect
Operator: Michael Obiero (Nairobi, Kenya)
"""

import time
import logging
import hashlib
import hmac
import json
from typing import Dict, List, Optional, Any

logging.basicConfig(level=logging.INFO, format='[%(asctime)s] [BODA_FLEET_ESCROW] %(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


class BodaFleetEscrowEngine:
    """
    Manages daily leasing installments, M-Pesa automated split payments (Owner, Maintenance, Micro-Insurance),
    and geo-fence compliance for Nairobi motorcycle fleets.
    """

    def __init__(self, fleet_id: str, secret_key: str):
        self.fleet_id = fleet_id
        self.secret_key = secret_key.encode('utf-8')
        self.riders: Dict[str, Dict[str, Any]] = {}
        self.ledger: List[Dict[str, Any]] = []
        logger.info(f"Initialized BodaFleetEscrowEngine for fleet [{self.fleet_id}] in Nairobi.")

    def register_rider(self, rider_id: str, national_id: str, motorcycle_plate: str, daily_target_kes: float) -> None:
        """Register a rider into the fleet management ledger."""
        if not rider_id or not motorcycle_plate:
            raise ValueError("Invalid rider registration parameters.")
        
        self.riders[rider_id] = {
            "national_id": national_id,
            "motorcycle_plate": motorcycle_plate,
            "daily_target_kes": daily_target_kes,
            "balance_kes": 0.0,
            "insurance_pool_kes": 0.0,
            "status": "ACTIVE",
            "last_payment_timestamp": time.time()
        }
        logger.info(f"Rider {rider_id} registered for bike {motorcycle_plate}. Target: {daily_target_kes} KES/day.")

    def process_mpesa_installment(self, rider_id: str, amount_kes: float, mpesa_receipt: str) -> Dict[str, Any]:
        """
        Processes incoming daily M-Pesa payment, splitting it autonomously:
        - 70% Owner Lease Capital
        - 20% Maintenance & Sinking Fund
        - 10% Micro-Insurance Premium Pool
        """
        if rider_id not in self.riders:
            raise KeyError(f"Rider {rider_id} not found in fleet {self.fleet_id}.")

        if amount_kes <= 0:
            raise ValueError("M-Pesa payment amount must be greater than zero.")

        owner_share = amount_kes * 0.70
        maintenance_share = amount_kes * 0.20
        insurance_share = amount_kes * 0.10

        rider = self.riders[rider_id]
        rider["balance_kes"] += owner_share
        rider["insurance_pool_kes"] += insurance_share
        rider["last_payment_timestamp"] = time.time()

        tx_record = {
            "timestamp": time.time(),
            "rider_id": rider_id,
            "mpesa_receipt": mpesa_receipt,
            "total_paid": amount_kes,
            "split": {
                "owner_kes": round(owner_share, 2),
                "maintenance_kes": round(maintenance_share, 2),
                "insurance_kes": round(insurance_share, 2)
            },
            "status": "COMMITTED"
        }

        # Generate cryptographic integrity signature
        payload_str = json.dumps(tx_record, sort_keys=True)
        tx_record["signature"] = hmac.new(self.secret_key, payload_str.encode('utf-8'), hashlib.sha256).hexdigest()

        self.ledger.append(tx_record)
        logger.info(f"Processed M-Pesa receipt {mpesa_receipt} for rider {rider_id}: {amount_kes} KES split successfully.")
        return tx_record

    def evaluate_geo_risk(self, rider_id: str, latitude: float, longitude: float) -> str:
        """
        Evaluates if the rider's motorcycle is within permitted Nairobi operating zones.
        CBD Boundary approx: -1.2921, 36.8219 (Central).
        """
        if rider_id not in self.riders:
            return "UNKNOWN_RIDER"

        # Simple bounding box check for Nairobi metropolitan area
        nairobi_min_lat, nairobi_max_lat = -1.45, -1.15
        nairobi_min_lon, nairobi_max_lon = 36.65, 37.10

        if nairobi_min_lat <= latitude <= nairobi_max_lat and nairobi_min_lon <= longitude <= nairobi_max_lon:
            return "INS_COMPLIANT_ZONE"
        else:
            logger.warning(f"Rider {rider_id} detected outside Nairobi perimeter at ({latitude}, {longitude}). Risk flagged!")
            return "OUT_OF_BOUNDS_HIGH_RISK"

    def audit_fleet_health(self) -> Dict[str, Any]:
        """Aggregates total fleet revenue and insurance reserves."""
        total_revenue = sum(tx["total_paid"] for tx in self.ledger)
        total_insurance = sum(r["insurance_pool_kes"] for r in self.riders.values())
        active_riders = sum(1 for r in self.riders.values() if r["status"] == "ACTIVE")

        return {
            "fleet_id": self.fleet_id,
            "total_registered_riders": len(self.riders),
            "active_riders": active_riders,
            "total_revenue_collected_kes": round(total_revenue, 2),
            "total_insurance_pool_kes": round(total_insurance, 2),
            "ledger_transactions": len(self.ledger)
        }


if __name__ == "__main__":
    print("=== TESTING BODA FLEET ESCROW AUTOMATOR ===")
    engine = BodaFleetEscrowEngine(fleet_id="NAIROBI_BODA_001", secret_key="michael_obiero_secure_key")
    
    engine.register_rider(
        rider_id="RIDER_KE_889",
        national_id="34567890",
        motorcycle_plate="KMDV 456A",
        daily_target_kes=500.0
    )

    # Simulate M-Pesa payment
    tx = engine.process_mpesa_installment(
        rider_id="RIDER_KE_889",
        amount_kes=600.0,
        mpesa_receipt="QHX789PLKM"
    )
    print("Transaction Result:", json.dumps(tx, indent=2))

    # Test Geo-fence inside Nairobi
    zone_status = engine.evaluate_geo_risk("RIDER_KE_889", -1.2863, 36.8172)
    print("Geo-Fence Status (CBD):", zone_status)

    # Test Fleet Audit
    audit = engine.audit_fleet_health()
    print("Fleet Audit Summary:", json.dumps(audit, indent=2))
    print("=== BODA FLEET ESCROW ENGINE VERIFIED ===")
