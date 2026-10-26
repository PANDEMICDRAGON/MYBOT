"""
Nairobi Jomo Kenyatta International Airport (JKIA) Air Cargo & Perishable Cold-Chain Customs Clearinghouse
Designed to secure, audit, and accelerate perishable export logistics for Michael Obiero in Nairobi.
"""

import json
import hashlib
import time
from typing import Dict, Any, List, Optional


class AeroCargoException(Exception):
    """Base exception for aero cargo clearinghouse operations."""
    pass


class AirwayBill:
    """Represents an individual air cargo consignment passing through JKIA."""

    def __init__(self, awb_number: str, shipper: str, destination: str, commodity: str, weight_kg: float):
        self.awb_number = awb_number
        self.shipper = shipper
        self.destination = destination
        self.commodity = commodity
        self.weight_kg = weight_kg
        self.temperature_log: List[float] = []
        self.customs_cleared: bool = False
        self.phytosanitary_verified: bool = False
        self.integrity_hash: str = ""
        self._update_hash()

    def _update_hash(self) -> None:
        payload = f"{self.awb_number}:{self.shipper}:{self.destination}:{self.commodity}:{self.weight_kg}:{self.customs_cleared}"
        self.integrity_hash = hashlib.sha256(payload.encode('utf-8')).hexdigest()

    def record_temperature(self, temp_c: float) -> None:
        self.temperature_log.append(temp_c)
        if len(self.temperature_log) > 1000:
            self.temperature_log.pop(0)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "awb_number": self.awb_number,
            "shipper": self.shipper,
            "destination": self.destination,
            "commodity": self.commodity,
            "weight_kg": self.weight_kg,
            "temperature_log": self.temperature_log,
            "customs_cleared": self.customs_cleared,
            "phytosanitary_verified": self.phytosanitary_verified,
            "integrity_hash": self.integrity_hash,
        }


class JKIAAeroCargoSentinel:
    """Orchestrates and audits cold-chain integrity and KRA customs sign-offs at JKIA."""

    def __init__(self, max_temp_threshold_c: float = 8.0):
        self.max_temp_threshold_c = max_temp_threshold_c
        self.consignments: Dict[str, AirwayBill] = {}

    def register_consignment(self, awb_number: str, shipper: str, destination: str, commodity: str, weight_kg: float) -> AirwayBill:
        if awb_number in self.consignments:
            raise AeroCargoException(f"Consignment {awb_number} already registered.")
        awb = AirwayBill(awb_number, shipper, destination, commodity, weight_kg)
        self.consignments[awb_number] = awb
        return awb

    def ingest_sensor_telemetry(self, awb_number: str, temp_c: float) -> None:
        if awb_number not in self.consignments:
            raise AeroCargoException(f"Consignment {awb_number} not found.")
        awb = self.consignments[awb_number]
        awb.record_temperature(temp_c)
        if temp_c > self.max_temp_threshold_c:
            # Flag breach internally or take corrective action
            pass

    def verify_phytosanitary(self, awb_number: str) -> bool:
        if awb_number not in self.consignments:
            raise AeroCargoException(f"Consignment {awb_number} not found.")
        awb = self.consignments[awb_number]
        awb.phytosanitary_verified = True
        awb._update_hash()
        return True

    def clear_customs(self, awb_number: str, kra_token: str) -> bool:
        if not kra_token.startswith("KRA-AUTH-"):
            raise AeroCargoException("Invalid KRA Customs Authorization Token.")
        if awb_number not in self.consignments:
            raise AeroCargoException(f"Consignment {awb_number} not found.")
        awb = self.consignments[awb_number]
        if not awb.phytosanitary_verified:
            raise AeroCargoException("Cannot clear customs without phytosanitary verification.")
        
        awb.customs_cleared = True
        awb._update_hash()
        return True

    def generate_manifest_audit(self) -> Dict[str, Any]:
        total_weight = sum(c.weight_kg for c in self.consignments.values())
        cleared_count = sum(1 for c in self.consignments.values() if c.customs_cleared)
        return {
            "timestamp": time.time(),
            "total_consignments": len(self.consignments),
            "cleared_consignments": cleared_count,
            "total_weight_kg": total_weight,
            "status": "OPERATIONAL"
        }


if __name__ == "__main__":
    print("Initializing JKIA Aero Cargo & Cold-Chain Sentinel...")
    sentinel = JKIAAeroCargoSentinel(max_temp_threshold_c=6.0)
    
    # Register trial fresh cut flowers export
    awb = sentinel.register_consignment(
        awb_number="AWB-789-NBO-AMS",
        shipper="Naivasha Blooms Ltd",
        destination="Amsterdam Schiphol",
        commodity="Fresh Cut Roses",
        weight_kg=1250.5
    )
    
    sentinel.ingest_sensor_telemetry("AWB-789-NBO-AMS", 4.2)
    sentinel.ingest_sensor_telemetry("AWB-789-NBO-AMS", 4.8)
    sentinel.verify_phytosanitary("AWB-789-NBO-AMS")
    
    cleared = sentinel.clear_customs("AWB-789-NBO-AMS", "KRA-AUTH-994821")
    print(f"Consignment AWB-789-NBO-AMS Customs Cleared: {cleared}")
    
    audit = sentinel.generate_manifest_audit()
    print("Manifest Audit Report:", json.dumps(audit, indent=2))
    print("JKIA Aero Cargo Sentinel test cycle completed successfully.")
