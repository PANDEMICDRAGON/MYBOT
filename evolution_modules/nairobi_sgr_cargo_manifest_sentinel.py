import hashlib
import json
import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from enum import Enum


class ManifestStatus(Enum):
    DRAFT = "DRAFT"
    SEALED = "SEALED"
    IN_TRANSIT = "IN_TRANSIT"
    ARRIVED = "ARRIVED"
    CLEARED = "CLEARED"
    DISPUTED = "DISPUTED"


@dataclass
class CargoItem:
    item_id: str
    description: str
    weight_kg: float
    value_kes: float
    hs_code: str  # Harmonized System Code
    origin_country: str
    destination_country: str

    def to_dict(self) -> Dict:
        return {
            "item_id": self.item_id,
            "description": self.description,
            "weight_kg": self.weight_kg,
            "value_kes": self.value_kes,
            "hs_code": self.hs_code,
            "origin_country": self.origin_country,
            "destination_country": self.destination_country
        }


@dataclass
class Manifest:
    manifest_id: str
    items: List[CargoItem]
    status: ManifestStatus
    created_at: float
    sealed_hash: Optional[str] = None
    checksum_history: List[Dict] = field(default_factory=list)

    def calculate_checksum(self) -> str:
        """Calculate a deterministic SHA-256 checksum of the manifest content."""
        # Sort items by item_id to ensure consistent hashing regardless of order
        sorted_items = sorted(self.items, key=lambda x: x.item_id)
        items_json = json.dumps([item.to_dict() for item in sorted_items], sort_keys=True)
        return hashlib.sha256(items_json.encode('utf-8')).hexdigest()

    def seal(self) -> bool:
        """Seal the manifest, making it immutable."""
        if self.status != ManifestStatus.DRAFT:
            return False
        self.sealed_hash = self.calculate_checksum()
        self.status = ManifestStatus.SEALED
        self.checksum_history.append({
            "timestamp": time.time(),
            "hash": self.sealed_hash,
            "action": "SEAL"
        })
        return True

    def verify_integrity(self) -> bool:
        """Verify that the current manifest content matches the sealed hash."""
        if not self.sealed_hash:
            return False
        current_hash = self.calculate_checksum()
        return current_hash == self.sealed_hash

    def update_status(self, new_status: ManifestStatus) -> bool:
        """Update the status of the manifest."""
        if self.status == ManifestStatus.DRAFT:
            return False  # Cannot change status of a draft
        self.status = new_status
        self.checksum_history.append({
            "timestamp": time.time(),
            "hash": self.sealed_hash,
            "action": f"STATUS_CHANGE_TO_{new_status.value}"
        })
        return True


class SGRCargoSentinel:
    """Sentinel for monitoring and securing SGR cargo manifests."""

    def __init__(self):
        self.manifests: Dict[str, Manifest] = {}

    def create_manifest(self, items: List[CargoItem]) -> Manifest:
        """Create a new draft manifest."""
        manifest_id = f"SGR-{uuid.uuid4().hex[:8].upper()}"
        manifest = Manifest(
            manifest_id=manifest_id,
            items=items,
            status=ManifestStatus.DRAFT,
            created_at=time.time()
        )
        self.manifests[manifest_id] = manifest
        return manifest

    def seal_manifest(self, manifest_id: str) -> bool:
        """Seal a draft manifest."""
        manifest = self.manifests.get(manifest_id)
        if not manifest:
            return False
        return manifest.seal()

    def verify_manifest(self, manifest_id: str) -> bool:
        """Verify the integrity of a sealed manifest."""
        manifest = self.manifests.get(manifest_id)
        if not manifest:
            return False
        return manifest.verify_integrity()

    def get_manifest_status(self, manifest_id: str) -> Optional[ManifestStatus]:
        """Get the current status of a manifest."""
        manifest = self.manifests.get(manifest_id)
        if not manifest:
            return None
        return manifest.status

    def get_audit_trail(self, manifest_id: str) -> List[Dict]:
        """Get the audit trail for a manifest."""
        manifest = self.manifests.get(manifest_id)
        if not manifest:
            return []
        return manifest.checksum_history


if __name__ == "__main__":
    # Test Harness
    print("Initializing SGR Cargo Manifest Sentinel...")
    sentinel = SGRCargoSentinel()

    # Create sample cargo items
    items = [
        CargoItem(
            item_id="ITEM-001",
            description="Electronics - Laptops",
            weight_kg=500.0,
            value_kes=15000000.0,
            hs_code="8471.30",
            origin_country="China",
            destination_country="Kenya"
        ),
        CargoItem(
            item_id="ITEM-002",
            description="Textiles - Cotton Fabric",
            weight_kg=2000.0,
            value_kes=8000000.0,
            hs_code="5208.11",
            origin_country="India",
            destination_country="Kenya"
        )
    ]

    # Create and seal manifest
    manifest = sentinel.create_manifest(items)
    print(f"Created Manifest: {manifest.manifest_id}")
    
    sealed = sentinel.seal_manifest(manifest.manifest_id)
    print(f"Sealed Manifest: {sealed}")
    
    # Verify integrity
    is_valid = sentinel.verify_manifest(manifest.manifest_id)
    print(f"Integrity Check: {is_valid}")
    
    # Simulate tampering
    manifest.items[0].value_kes = 16000000.0  # Tamper with value
    is_valid_after_tamper = sentinel.verify_manifest(manifest.manifest_id)
    print(f"Integrity Check After Tamper: {is_valid_after_tamper}")
    
    # Restore and verify again
    manifest.items[0].value_kes = 15000000.0
    is_valid_restored = sentinel.verify_manifest(manifest.manifest_id)
    print(f"Integrity Check After Restore: {is_valid_restored}")
    
    # Get audit trail
    audit_trail = sentinel.get_audit_trail(manifest.manifest_id)
    print(f"Audit Trail Entries: {len(audit_trail)}")
    
    print("SGR Cargo Manifest Sentinel Test Complete.")
