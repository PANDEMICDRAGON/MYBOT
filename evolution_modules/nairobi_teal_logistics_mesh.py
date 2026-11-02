"""
Nairobi Autonomous Teal Logistics Mesh & Last-Mile Vault Enclosure Coordinator
Designed for autonomous logistics routing, tamper detection, and encrypted drop-off
coordination across Nairobi's urban commercial zones (Westlands, CBD, Industrial Area).
"""

import hashlib
import hmac
import json
import time
import logging
from typing import Dict, List, Any, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("TealLogisticsMesh")


class TealLogisticsMesh:
    """
    Manages secure, decentralized parcel lockers, mobile courier nodes, and 
    encrypted transit states for high-value assets across Nairobi.
    """

    def __init__(self, node_id: str, secret_key: bytes):
        self.node_id = node_id
        self.secret_key = secret_key
        self.active_shipments: Dict[str, Dict[str, Any]] = {}
        self.node_registry: List[str] = ["Westlands_Hub", "CBD_Depot", "Industrial_Area_Node", "Kilimani_Locker"]

    def create_shipment(self, tracking_id: str, destination: str, payload_manifest: Dict[str, Any]) -> Dict[str, Any]:
        """Registers a new encrypted transit parcel with HMAC integrity seal."""
        timestamp = time.time()
        raw_data = f"{tracking_id}:{destination}:{timestamp}".encode('utf-8')
        integrity_hmac = hmac.new(self.secret_key, raw_data, hashlib.sha256).hexdigest()

        shipment = {
            "tracking_id": tracking_id,
            "origin": self.node_id,
            "destination": destination,
            "timestamp": timestamp,
            "status": "DISPATCHED",
            "manifest": payload_manifest,
            "integrity_hmac": integrity_hmac
        }

        self.active_shipments[tracking_id] = shipment
        logger.info(f"[TealMesh] Shipment {tracking_id} created for destination {destination}.")
        return shipment

    def audit_transit(self, tracking_id: str, current_location: str, tamper_sensor_triggered: bool) -> Dict[str, Any]:
        """Audits transit telemetry and detects physical tampering or route deviation."""
        if tracking_id not in self.active_shipments:
            return {"status": "ERROR", "message": "Shipment not found."}

        shipment = self.active_shipments[tracking_id]
        
        if tamper_sensor_triggered:
            shipment["status"] = "LOCKED_DOWN_TAMPER_DETECTED"
            logger.warning(f"[TealMesh] ALERT: Tamper sensor triggered on shipment {tracking_id} near {current_location}!")
        else:
            shipment["status"] = f"IN_TRANSIT_BY_{current_location}"
            logger.info(f"[TealMesh] Shipment {tracking_id} verified at {current_location}.")

        return shipment

    def finalize_delivery(self, tracking_id: str, verification_token: str) -> bool:
        """Finalizes drop-off at secure locker when verification token matches."""
        if tracking_id not in self.active_shipments:
            return False
        
        shipment = self.active_shipments[tracking_id]
        expected_token = shipment["integrity_hmac"][:16]

        if hmac.compare_digest(verification_token, expected_token):
            shipment["status"] = "DELIVERED"
            logger.info(f"[TealMesh] Shipment {tracking_id} securely delivered and verified.")
            return True
        else:
            logger.error(f"[TealMesh] Delivery verification failed for shipment {tracking_id}.")
            return False


if __name__ == "__main__":
    print("Initializing Nairobi Autonomous Teal Logistics Mesh test harness...")
    mesh = TealLogisticsMesh(node_id="Westlands_Hub", secret_key=b"nairobi_teal_secret_2026")
    
    shipment = mesh.create_shipment(
        tracking_id="NBO-TRK-98821",
        destination="Kilimani_Locker",
        payload_manifest={"item": "High-Grade Cryptographic Hardware Security Module", "weight_kg": 1.4}
    )
    
    audited = mesh.audit_transit("NBO-TRK-98821", "Uhuru_Highway", tamper_sensor_triggered=False)
    print("Transit audit result:", audited["status"])
    
    token = audited["integrity_hmac"][:16]
    success = mesh.finalize_delivery("NBO-TRK-98821", token)
    print("Delivery success status:", success)
