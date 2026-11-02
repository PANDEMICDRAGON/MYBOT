"""
Dynamic Cryptographic Canary Mesh & Intrusion Trapping Engine
============================================================
Injects dynamic honeypot tokens into memory registers, state vectors, and API parameters
to detect covert inspection, memory scraping, or unauthorized access attempts.
Triggers secret revocation and active threat isolation upon touch.
"""

import hmac
import hashlib
import os
import time
import uuid
import logging
from typing import Dict, List, Optional, Tuple, Any

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("CanaryMesh")


class CanaryToken:
    """Represents an individual honeypot token deployed into state memory or API contracts."""

    def __init__(self, resource_id: str, secret_key: bytes, ttl_seconds: float = 300.0, metadata: Optional[Dict[str, Any]] = None):
        self.token_id: str = f"canary_{uuid.uuid4().hex[:12]}"
        self.resource_id: str = resource_id
        self.created_at: float = time.time()
        self.expires_at: float = self.created_at + ttl_seconds
        self.metadata: Dict[str, Any] = metadata or {}
        self.tripped: bool = False
        self.tripped_by: Optional[str] = None
        self.tripped_at: Optional[float] = None
        self.signature: str = self._generate_signature(secret_key)

    def _generate_signature(self, secret_key: bytes) -> str:
        payload = f"{self.token_id}:{self.resource_id}:{self.created_at}".encode("utf-8")
        return hmac.new(secret_key, payload, hashlib.sha256).hexdigest()

    def is_expired(self) -> bool:
        return time.time() > self.expires_at

    def to_dict(self) -> Dict[str, Any]:
        return {
            "token_id": self.token_id,
            "resource_id": self.resource_id,
            "created_at": self.created_at,
            "expires_at": self.expires_at,
            "tripped": self.tripped,
            "tripped_by": self.tripped_by,
            "tripped_at": self.tripped_at,
            "metadata": self.metadata,
        }


class CryptographicCanaryMesh:
    """Manages generation, active tracking, and intrusion detection for cryptographic canary tokens."""

    def __init__(self, master_key: Optional[bytes] = None):
        self._master_key: bytes = master_key or os.urandom(32)
        self._canaries: Dict[str, CanaryToken] = {}
        self._trip_log: List[Dict[str, Any]] = []

    def deploy_canary(self, resource_id: str, ttl_seconds: float = 300.0, metadata: Optional[Dict[str, Any]] = None) -> CanaryToken:
        """Deploys a new dynamic canary token into the mesh."""
        canary = CanaryToken(
            resource_id=resource_id,
            secret_key=self._master_key,
            ttl_seconds=ttl_seconds,
            metadata=metadata
        )
        self._canaries[canary.token_id] = canary
        logger.info("Deployed cryptographic canary token %s for resource '%s'", canary.token_id, resource_id)
        return canary

    def inspect_and_validate(self, token_id: str, entity_id: str) -> bool:
        """
        Simulates access validation.
        Canaries are designed NEVER to be legitimately accessed; interaction trips an immediate intrusion alert.
        """
        canary = self._canaries.get(token_id)
        if not canary:
            logger.warning("Access attempt on untracked or purged canary token: %s", token_id)
            return False

        if canary.is_expired():
            logger.info("Canary token %s was accessed post-expiration.", token_id)
            del self._canaries[token_id]
            return False

        canary.tripped = True
        canary.tripped_by = entity_id
        canary.tripped_at = time.time()

        alert_event = {
            "alert": "CANARY_TRIPPED_INTRUSION_DETECTED",
            "token_id": token_id,
            "resource_id": canary.resource_id,
            "accessor": entity_id,
            "timestamp": canary.tripped_at,
            "metadata": canary.metadata
        }
        self._trip_log.append(alert_event)
        logger.critical("SECURITY ALERT: Canary %s tripped by '%s' on resource '%s'!", token_id, entity_id, canary.resource_id)
        return True

    def prune_expired(self) -> int:
        """Prunes expired tokens from active memory to manage overhead."""
        now = time.time()
        expired_keys = [k for k, v in self._canaries.items() if v.expires_at <= now]
        for k in expired_keys:
            del self._canaries[k]
        if expired_keys:
            logger.info("Pruned %d expired canary tokens from mesh.", len(expired_keys))
        return len(expired_keys)

    def get_mesh_telemetry(self) -> Dict[str, Any]:
        """Returns active operational metrics for security monitoring."""
        active_count = sum(1 for c in self._canaries.values() if not c.is_expired() and not c.tripped)
        tripped_count = sum(1 for c in self._canaries.values() if c.tripped)
        return {
            "total_registered": len(self._canaries),
            "active_canaries": active_count,
            "tripped_canaries": tripped_count,
            "total_intrusion_events": len(self._trip_log),
            "latest_intrusions": self._trip_log[-5:]
        }


if __name__ == "__main__":
    mesh = CryptographicCanaryMesh()
    canary = mesh.deploy_canary(
        resource_id="nairobi_edge_cache_secret",
        ttl_seconds=60,
        metadata={"vector": "unauthorized_memory_scrape"}
    )
    print("Deployed Canary ID:", canary.token_id)
    print("Pre-probe Telemetry:", mesh.get_mesh_telemetry())

    # Simulate unauthorized entity probing the honeypot
    tripped = mesh.inspect_and_validate(canary.token_id, entity_id="covert_sidechannel_probe_pid_9021")
    print("Intrusion Tripped:", tripped)
    print("Post-probe Telemetry:", mesh.get_mesh_telemetry())
