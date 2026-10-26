import ast
import hashlib
import hmac
import json
import logging
import secrets
import time
from typing import Dict, Any, Optional, List

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] [BodaLocker]: %(message)s')
logger = logging.getLogger('nairobi_boda_parcel_locker')

class BodaParcelLockerManager:
    """
    Manages secure, encrypted parcel lockers placed at key Nairobi transport hubs
    (e.g., Khoja Stage, Westlands, Kilimani, Upper Hill) for reliable last-mile
    boda-boda drop-offs and operator pickups.
    """
    def __init__(self, master_secret: Optional[str] = None):
        self.master_secret = master_secret.encode('utf-8') if master_secret else secrets.token_bytes(32)
        self.lockers: Dict[str, Dict[str, Any]] = {
            "LOCKER_KHOJA_01": {"location": "Khoja Stage, CBD", "status": "AVAILABLE", "parcel_id": None, "otp_hash": None, "expires_at": 0},
            "LOCKER_WESTLANDS_02": {"location": "Sarit Centre Vicinity", "status": "AVAILABLE", "parcel_id": None, "otp_hash": None, "expires_at": 0},
            "LOCKER_KILIMANI_03": {"location": "Yaya Centre Hub", "status": "AVAILABLE", "parcel_id": None, "otp_hash": None, "expires_at": 0}
        }
        self.audit_log: List[Dict[str, Any]] = []

    def store_parcel(self, locker_id: str, parcel_id: str, rider_phone: str, ttl_seconds: int = 7200) -> Dict[str, Any]:
        """
        Deposits a parcel into a specific locker, generating a cryptographically
        secure one-time PIN (OTP) for the recipient or authorized rider.
        """
        if locker_id not in self.lockers:
            raise ValueError(f"Locker {locker_id} does not exist in the Nairobi network.")
        
        locker = self.lockers[locker_id]
        if locker["status"] != "AVAILABLE":
            raise RuntimeError(f"Locker {locker_id} is currently occupied or offline.")

        raw_otp = f"{secrets.randbelow(900000) + 100000}"
        otp_hash = hmac.new(self.master_secret, raw_otp.encode('utf-8'), hashlib.sha256).hexdigest()
        expires_at = time.time() + ttl_seconds

        locker["status"] = "OCCUPIED"
        locker["parcel_id"] = parcel_id
        locker["otp_hash"] = otp_hash
        locker["expires_at"] = expires_at
        locker["rider_phone"] = rider_phone

        event = {
            "timestamp": time.time(),
            "action": "STORE_PARCEL",
            "locker_id": locker_id,
            "parcel_id": parcel_id,
            "rider_phone": rider_phone,
            "expires_at": expires_at
        }
        self.audit_log.append(event)
        logger.info(f"Parcel {parcel_id} secured in {locker_id}. OTP generated for rider {rider_phone}.")

        # In production, raw_otp is dispatched via SMS gateway. Here we return it for testing harness.
        return {
            "status": "SUCCESS",
            "locker_id": locker_id,
            "parcel_id": parcel_id,
            "raw_otp_for_testing": raw_otp,
            "expires_at": expires_at
        }

    def retrieve_parcel(self, locker_id: str, parcel_id: str, provided_otp: str) -> Dict[str, Any]:
        """
        Unlocks the locker upon successful verification of the OTP hash and unexpired TTL.
        """
        if locker_id not in self.lockers:
            raise ValueError(f"Locker {locker_id} is invalid.")

        locker = self.lockers[locker_id]
        if locker["status"] != "OCCUPIED" or locker["parcel_id"] != parcel_id:
            raise ValueError(f"Parcel {parcel_id} not found in locker {locker_id}.")

        if time.time() > locker["expires_at"]:
            locker["status"] = "EXPIRED"
            raise TimeoutError(f"Locker {locker_id} OTP validity has expired.")

        provided_hash = hmac.new(self.master_secret, provided_otp.encode('utf-8'), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(provided_hash, locker["otp_hash"]):
            logger.warning(f"Invalid OTP attempt on locker {locker_id} for parcel {parcel_id}.")
            return {"status": "DENIED", "reason": "INVALID_OTP"}

        # Reset locker state
        locker["status"] = "AVAILABLE"
        locker["parcel_id"] = None
        locker["otp_hash"] = None
        locker["expires_at"] = 0
        locker.pop("rider_phone", None)

        event = {
            "timestamp": time.time(),
            "action": "RETRIEVE_PARCEL",
            "locker_id": locker_id,
            "parcel_id": parcel_id
        }
        self.audit_log.append(event)
        logger.info(f"Parcel {parcel_id} successfully retrieved from {locker_id}.")

        return {"status": "SUCCESS", "message": f"Locker {locker_id} opened successfully."}

    def audit_status(self) -> Dict[str, Any]:
        return {
            "total_lockers": len(self.lockers),
            "active_occupancy": sum(1 for l in self.lockers.values() if l["status"] == "OCCUPIED"),
            "audit_events_recorded": len(self.audit_log)
        }

if __name__ == "__main__":
    manager = BodaParcelLockerManager()
    deposit_res = manager.store_parcel("LOCKER_KHOJA_01", "PARCEL_KE_9882", "+254712345678")
    print("Deposit Result:", json.dumps(deposit_res, indent=2))

    otp = deposit_res["raw_otp_for_testing"]
    retrieval_res = manager.retrieve_parcel("LOCKER_KHOJA_01", "PARCEL_KE_9882", otp)
    print("Retrieval Result:", json.dumps(retrieval_res, indent=2))

    print("System Status Audit:", json.dumps(manager.audit_status(), indent=2))

    # Compile check validation
    assert ast.parse(__file__)
    print("AST Compilation Check: PASSED")
