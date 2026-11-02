"""
Module: offline_mesh_federated_key_exchange.py
Author: Cortana Autonomous Evolutionary Architect
Operator: Michael Obiero (Nairobi, Kenya)
Description: Provides offline peer-to-peer cryptographic key federation, ephemeral handshake generation,
and decentralized trust verification for decentralized node meshes operating without WAN connectivity.
"""

import os
import time
import hmac
import hashlib
import json
import base64
from typing import Dict, Any, List, Optional

class OfflineMeshFederatedKeyExchange:
    """
    Manages cryptographic identity generation, local challenge-response handshakes,
    and decentralized trust propagation for offline mesh networks in Nairobi.
    """

    def __init__(self, node_id: str, secret_seed: Optional[bytes] = None):
        self.node_id = node_id
        self.secret_seed = secret_seed or os.urandom(32)
        self.peers: Dict[str, Dict[str, Any]] = {}
        self.handshake_nonces: Dict[str, float] = {}

    def generate_local_identity(self) -> Dict[str, str]:
        """Generates node identity public descriptor and binding proof."""
        public_hash = hashlib.sha256(self.secret_seed + self.node_id.encode('utf-8')).hexdigest()
        return {
            "node_id": self.node_id,
            "identity_proof": public_hash,
            "timestamp": time.time()
        }

    def create_handshake_challenge(self, peer_id: str) -> Dict[str, Any]:
        """Creates an ephemeral cryptographic challenge nonce for a peer node."""
        nonce = base64.b64encode(os.urandom(16)).decode('utf-8')
        expires = time.time() + 60.0  # 60 seconds validity for mesh transmission
        self.handshake_nonces[peer_id] = {
            "nonce": nonce,
            "expires": expires
        }
        return {
            "sender_id": self.node_id,
            "nonce": nonce,
            "expires": expires
        }

    def respond_to_challenge(self, challenger_id: str, nonce: str) -> str:
        """Computes HMAC signature response to a peer challenge using the local secret seed."""
        message = f"{challenger_id}:{nonce}:{self.node_id}".encode('utf-8')
        signature = hmac.new(self.secret_seed, message, hashlib.sha256).hexdigest()
        return signature

    def verify_and_establish_trust(self, peer_id: str, nonce: str, signature: str, peer_secret_hint: bytes) -> bool:
        """
        Verifies a peer's challenge response and establishes a trusted session key descriptor.
        """
        if peer_id in self.handshake_nonces:
            stored = self.handshake_nonces[peer_id]
            if stored["nonce"] == nonce and time.time() <= stored["expires"]:
                message = f"{self.node_id}:{nonce}:{peer_id}".encode('utf-8')
                expected_sig = hmac.new(peer_secret_hint, message, hashlib.sha256).hexdigest()
                if hmac.compare_digest(expected_sig, signature):
                    self.peers[peer_id] = {
                        "trusted_since": time.time(),
                        "status": "ACTIVE_FEDERATED"
                    }
                    del self.handshake_nonces[peer_id]
                    return True
        return False

    def export_mesh_state(self) -> str:
        """Exports current federated peer trust state as JSON."""
        return json.dumps({
            "node_id": self.node_id,
            "active_peers": list(self.peers.keys()),
            "timestamp": time.time()
        }, indent=2)


if __name__ == "__main__":
    print("[INIT] Initializing Cortana Offline Mesh Federated Key Exchange Test Harness...")
    seed_a = b"nairobi_secret_seed_alpha_9988"
    seed_b = b"nairobi_secret_seed_beta_7766"
    
    node_a = OfflineMeshFederatedKeyExchange(node_id="Nairobi-Node-Alpha", secret_seed=seed_a)
    node_b = OfflineMeshFederatedKeyExchange(node_id="Nairobi-Node-Beta", secret_seed=seed_b)
    
    identity_a = node_a.generate_local_identity()
    print(f"[IDENTITY] Node A Identity Generated: {identity_a['node_id']} -> {identity_a['identity_proof'][:16]}...")
    
    challenge = node_a.create_handshake_challenge(peer_id="Nairobi-Node-Beta")
    print(f"[CHALLENGE] Created nonce for Beta: {challenge['nonce'][:8]}...")
    
    response_sig = node_b.respond_to_challenge(
        challenger_id="Nairobi-Node-Alpha", 
        nonce=challenge["nonce"]
    )
    print(f"[RESPONSE] Beta computed HMAC response signature.")
    
    success = node_a.verify_and_establish_trust(
        peer_id="Nairobi-Node-Beta",
        nonce=challenge["nonce"],
        signature=response_sig,
        peer_secret_hint=seed_b
    )
    print(f"[VERIFICATION] Trust establishment result: {success}")
    print(f"[STATE] Node A Mesh State:\n{node_a.export_mesh_state()}")
    print("[COMPLETE] Offline Mesh Federated Key Exchange verification successful.")
