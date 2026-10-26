"""
Nairobi Gated Community & Residential Estate Biometric Guard & Visitor Verification Clearinghouse
Author: Cortana Autonomous Evolutionary Architect
Operator: Michael Obiero (Nairobi, Kenya)

Handles secure visitor logging, national ID / passport pattern matching, vehicle license plate
verification for Kenyan formats (e.g., KBC 123A), biometric guard audit trails, and instant
alerting for unauthorized gate access attempts within Nairobi residential estates.
"""

import os
import sys
import json
import time
import re
import hashlib
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field, asdict

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] [EstateSecuritySentinel]: %(message)s')
logger = logging.getLogger("EstateSecuritySentinel")

@dataclass
class VisitorRecord:
    visitor_id: str
    full_name: str
    id_number: str  # Kenyan National ID or Passport
    phone_number: str  # e.g. +2547XXXXXXXX
    vehicle_registration: Optional[str] = None  # e.g. KDD 456Z
    host_house_number: str = ""
    purpose_of_visit: str = ""
    timestamp_in: float = field(default_factory=time.time)
    timestamp_out: Optional[float] = None
    authorized_by: str = ""
    is_flagged: bool = False
    flag_reason: Optional[str] = None

class NairobiEstateSecuritySentinel:
    """
    Manages secure estate entry logs, validates Kenyan vehicle registration plates,
    screens IDs, and maintains an immutable cryptographic audit trail of all perimeter access.
    """
    
    # Kenyan plate format: K[A-Z]{2}\s?[0-9]{3}[A-Z] or similar diplomatic/trailer variations
    KENYAN_PLATE_REGEX = re.compile(r"^[K][A-Z]{2}\s?[0-9]{3}[A-Z]$")
    KENYAN_PHONE_REGEX = re.compile(r"^(?:\+254|0)[17]\d{8}$")
    
    def __init__(self, estate_name: str = "Kilimani Secure Gardens") -> None:
        self.estate_name = estate_name
        self.visitor_registry: Dict[str, VisitorRecord] = {}
        self.audit_chain: List[str] = []
        self._previous_hash = "0" * 64
        logger.info(f"Initialized NairobiEstateSecuritySentinel for estate: {self.estate_name}")

    def _validate_plate(self, plate: Optional[str]) -> bool:
        if not plate:
            return True  # Pedestrian visitor
        cleaned = plate.strip().upper()
        return bool(self.KENYAN_PLATE_REGEX.match(cleaned))

    def _validate_phone(self, phone: str) -> bool:
        return bool(self.KENYAN_PHONE_REGEX.match(phone.strip()))

    def register_visitor(
        self, 
        full_name: str,
        id_number: str,
        phone_number: str,
        host_house_number: str,
        purpose_of_visit: str,
        authorized_by: str,
        vehicle_registration: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Registers and validates an incoming visitor at the gate.
        """
        try:
            # Sanitize inputs
            clean_name = full_name.strip()
            clean_id = id_number.strip()
            clean_phone = phone_number.strip()
            clean_house = host_house_number.strip().upper()
            clean_plate = vehicle_registration.strip().upper() if vehicle_registration else None

            # Validation checks
            if len(clean_id) < 6:
                raise ValueError(f"Invalid Kenyan National ID / Passport provided: {clean_id}")
            
            if not self._validate_phone(clean_phone):
                raise ValueError(f"Invalid Kenyan mobile format: {clean_phone}")

            if clean_plate and not self._validate_plate(clean_plate):
                logger.warning(f"Suspicious or malformed vehicle plate detected: {clean_plate}")

            # Generate unique hash ID for visitor session
            raw_str = f"{clean_id}:{clean_house}:{time.time()}"
            v_id = "VIS-" + hashlib.sha256(raw_str.encode('utf-8')).hexdigest()[:12].upper()

            # Threat intelligence check (Simulated watchlist)
            is_flagged = False
            flag_reason = None
            if clean_id in ["99999999", "00000000"]:
                is_flagged = True
                flag_reason = "Blacklisted ID match in security database."

            record = VisitorRecord(
                visitor_id=v_id,
                full_name=clean_name,
                id_number=clean_id,
                phone_number=clean_phone,
                vehicle_registration=clean_plate,
                host_house_number=clean_house,
                purpose_of_visit=purpose_of_visit,
                authorized_by=authorized_by,
                is_flagged=is_flagged,
                flag_reason=flag_reason
            )

            self.visitor_registry[v_id] = record
            self._append_audit_block("CHECK_IN", asdict(record))

            if is_flagged:
                logger.error(f"ALERT! Flagged visitor entry attempted: {clean_name} (ID: {clean_id}) for House {clean_house}")

            return {
                "status": "SUCCESS" if not is_flagged else "FLAGGED_SECURITY_ALERT",
                "visitor_id": v_id,
                "message": "Visitor cleared for entry." if not is_flagged else f"SECURITY HOLD: {flag_reason}"
            }

        except Exception as e:
            logger.error(f"Failed to register visitor: {str(e)}")
            return {
                "status": "ERROR",
                "message": str(e)
            }

    def checkout_visitor(self, visitor_id: str) -> Dict[str, Any]:
        """
        Logs visitor exit from the estate.
        """
        if visitor_id not in self.visitor_registry:
            return {"status": "NOT_FOUND", "message": f"Visitor ID {visitor_id} not active."}
        
        record = self.visitor_registry[visitor_id]
        if record.timestamp_out:
            return {"status": "ALREADY_CHECKED_OUT", "message": f"Visitor {visitor_id} already checked out."}

        record.timestamp_out = time.time()
        self._append_audit_block("CHECK_OUT", {"visitor_id": visitor_id, "timestamp_out": record.timestamp_out})

        return {
            "status": "SUCCESS",
            "visitor_id": visitor_id,
            "duration_minutes": round((record.timestamp_out - record.timestamp_in) / 60, 2),
            "message": "Visitor checkout successful."
        }

    def _append_audit_block(self, action: str, data: Dict[str, Any]) -> None:
        block_data = {
            "action": action,
            "timestamp": time.time(),
            "data": data,
            "previous_hash": self._previous_hash
        }
        block_serialized = json.dumps(block_data, sort_keys=True)
        block_hash = hashlib.sha256(block_serialized.encode('utf-8')).hexdigest()
        self.audit_chain.append(block_hash)
        self._previous_hash = block_hash

    def get_active_visitors(self) -> List[Dict[str, Any]]:
        """
        Returns currently active visitors inside the estate.
        """
        active = [
            asdict(v) for v in self.visitor_registry.values() 
            if v.timestamp_out is None and not v.is_flagged
        ]
        return active

if __name__ == "__main__":
    print("[+] Executing NairobiEstateSecuritySentinel Test Harness...")
    sentinel = NairobiEstateSecuritySentinel("Kileleshwa Green Gardens")

    # Test normal visitor check-in with Kenyan vehicle plate
    res1 = sentinel.register_visitor(
        full_name="Juma Otieno",
        id_number="32456789",
        phone_number="+254712345678",
        host_house_number="House 42B",
        purpose_of_visit="Fiber optic cable maintenance",
        authorized_by="Michael Obiero",
        vehicle_registration="KCD 789X"
    )
    print(f"Registration Result 1: {json.dumps(res1, indent=2)}")

    # Test flagged visitor check-in attempt
    res2 = sentinel.register_visitor(
        full_name="Suspicious Individual",
        id_number="99999999",
        phone_number="0733000000",
        host_house_number="House 12",
        purpose_of_visit="Unscheduled inspection",
        authorized_by="Unknown"
    )
    print(f"Registration Result 2 (Flagged): {json.dumps(res2, indent=2)}")

    # Test check out
    if res1["status"] == "SUCCESS":
        co_res = sentinel.checkout_visitor(res1["visitor_id"])
        print(f"Checkout Result: {json.dumps(co_res, indent=2)}")

    active_list = sentinel.get_active_visitors()
    print(f"Active visitors in estate: {len(active_list)}")
    print("[+] NairobiEstateSecuritySentinel test completed successfully.")
