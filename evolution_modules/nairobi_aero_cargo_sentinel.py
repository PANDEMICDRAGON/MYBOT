"""
Nairobi Jomo Kenyatta International Airport (JKIA) Perishable Cargo Air-Freight Smart Contract & Customs Expeditor
Designed for Michael Obiero in Nairobi, Kenya.
"""

import json
import hashlib
import time
from typing import Dict, List, Optional, Any

class AeroCargoSentinel:
    """Manages real-time cold-chain telemetry, KRA customs clearance status, and airline escrow for perishable cargo at JKIA."""
    
    def __init__(self, max_temp_celsius: float = 6.5):
        self.max_temp_celsius = max_temp_celsius
        self.shipments: Dict[str, Dict[str, Any]] = {}

    def register_shipment(self, shipment_id: str, exporter: str, destination: str, weight_kg: float, declared_value_kes: float) -> Dict[str, Any]:
        """Registers an outgoing perishable cargo consignment."""
        shipment = {
            "shipment_id": shipment_id,
            "exporter": exporter,
            "destination": destination,
            "weight_kg": weight_kg,
            "declared_value_kes": declared_value_kes,
            "status": "REGISTERED_AT_COLD_ROOM",
            "temperature_logs": [],
            "customs_cleared": False,
            "escrow_locked": True,
            "timestamp": time.time()
        }
        self.shipments[shipment_id] = shipment
        return shipment

    def record_temperature(self, shipment_id: str, temp_celsius: float) -> bool:
        """Appends temperature telemetry to verify cold-chain compliance."""
        if shipment_id not in self.shipments:
            raise ValueError(f"Shipment {shipment_id} not found.")
        
        shipment = self.shipments[shipment_id]
        shipment["temperature_logs"].append({"temp": temp_celsius, "time": time.time()})
        
        if temp_celsius > self.max_temp_celsius:
            shipment["status"] = "COLD_CHAIN_BREACH"
            shipment["escrow_locked"] = False
            return False
        return True

    def verify_kra_customs(self, shipment_id: str, kra_permit_code: str) -> bool:
        """Validates KRA export compliance and customs clearance."""
        if shipment_id not in self.shipments:
            raise ValueError(f"Shipment {shipment_id} not found.")
        
        shipment = self.shipments[shipment_id]
        # Verify dummy KRA digital signature hash format
        if len(kra_permit_code) >= 10 and kra_permit_code.startswith("KRA-EXP-"):
            shipment["customs_cleared"] = True
            if shipment["status"] != "COLD_CHAIN_BREACH":
                shipment["status"] = "CLEARED_FOR_TARMAC_LOADING"
            return True
        
        shipment["status"] = "CUSTOMS_REJECTED"
        return False

    def finalize_dispatch(self, shipment_id: str) -> Dict[str, Any]:
        """Finalizes cargo dispatch if all checks pass."""
        if shipment_id not in self.shipments:
            raise ValueError(f"Shipment {shipment_id} not found.")
        
        shipment = self.shipments[shipment_id]
        if shipment["customs_cleared"] and shipment["status"] == "CLEARED_FOR_TARMAC_LOADING":
            shipment["status"] = "AIRBORNE"
            shipment["escrow_locked"] = False
        else:
            shipment["status"] = "DISPATCH_BLOCKED"
            
        return shipment

if __name__ == "__main__":
    sentinel = AeroCargoSentinel(max_temp_celsius=6.0)
    s_id = "JKIA-EXP-2025-098"
    sentinel.register_shipment(s_id, "Nairobi Flora Ltd", "Amsterdam (AMS)", 1250.0, 850000.0)
    sentinel.record_temperature(s_id, 4.2)
    sentinel.record_temperature(s_id, 5.1)
    assert sentinel.verify_kra_customs(s_id, "KRA-EXP-XYZ12345") is True
    result = sentinel.finalize_dispatch(s_id)
    print(json.dumps(result, indent=2))
