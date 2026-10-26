import os
import time
import hashlib
import secrets
from typing import Dict, Optional, Tuple
from dataclasses import dataclass, field
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class KeyPair:
    """Represents a cryptographic key pair with metadata."""
    public_key: bytes
    private_key: bytes
    algorithm: str
    created_at: float = field(default_factory=time.time)
    rotation_count: int = 0
    entropy_score: float = 1.0

    def to_dict(self) -> Dict:
        return {
            'public_key': self.public_key.hex(),
            'private_key': self.private_key.hex(),
            'algorithm': self.algorithm,
            'created_at': self.created_at,
            'rotation_count': self.rotation_count,
            'entropy_score': self.entropy_score
        }

class QuantumKeyRotationEngine:
    """
    A post-quantum hybrid key rotation engine that dynamically manages
    cryptographic keys using both classical and post-quantum algorithms.
    """
    
    def __init__(self, max_key_age: float = 3600.0, entropy_threshold: float = 0.8):
        """
        Initialize the key rotation engine.
        
        Args:
            max_key_age: Maximum age of a key in seconds before rotation.
            entropy_threshold: Minimum entropy score required for key validity.
        """
        self.max_key_age = max_key_age
        self.entropy_threshold = entropy_threshold
        self.current_key: Optional[KeyPair] = None
        self.key_history: Dict[str, KeyPair] = {}
        self._init_keys()
    
    def _init_keys(self) -> None:
        """Initialize the first key pair."""
        self.current_key = self._generate_key_pair()
        self.key_history[self.current_key.public_key.hex()] = self.current_key
        logger.info("Initial key pair generated.")
    
    def _generate_key_pair(self) -> KeyPair:
        """
        Generate a new hybrid key pair using X25519 (classical) and ML-KEM (post-quantum).
        
        Returns:
            A new KeyPair instance.
        """
        # Simulate X25519 key generation
        x25519_private = secrets.token_bytes(32)
        x25519_public = hashlib.sha256(x25519_private).digest()
        
        # Simulate ML-KEM key generation
        ml_kem_private = secrets.token_bytes(256)
        ml_kem_public = hashlib.sha512(ml_kem_private).digest()
        
        # Combine keys for hybrid approach
        combined_private = x25519_private + ml_kem_private
        combined_public = x25519_public + ml_kem_public
        
        return KeyPair(
            public_key=combined_public,
            private_key=combined_private,
            algorithm="X25519+ML-KEM"
        )
    
    def _calculate_entropy(self, key: KeyPair) -> float:
        """
        Calculate the entropy score of a key based on its randomness.
        
        Args:
            key: The key pair to evaluate.
        
        Returns:
            A float representing the entropy score (0.0 to 1.0).
        """
        # Simple entropy calculation based on byte distribution
        byte_counts = [0] * 256
        for byte in key.private_key:
            byte_counts[byte] += 1
        
        total_bytes = len(key.private_key)
        entropy = 0.0
        for count in byte_counts:
            if count > 0:
                probability = count / total_bytes
                entropy -= probability * (probability ** 0.5)  # Simplified entropy formula
        
        # Normalize to 0.0-1.0 range
        max_entropy = 8.0  # For 256-bit keys
        return min(1.0, abs(entropy) / max_entropy)
    
    def should_rotate(self) -> bool:
        """
        Determine if the current key should be rotated.
        
        Returns:
            True if rotation is needed, False otherwise.
        """
        if not self.current_key:
            return True
        
        age = time.time() - self.current_key.created_at
        entropy = self._calculate_entropy(self.current_key)
        
        return age > self.max_key_age or entropy < self.entropy_threshold
    
    def rotate_key(self) -> KeyPair:
        """
        Rotate the current key pair and archive the old one.
        
        Returns:
            The new KeyPair instance.
        """
        if self.current_key:
            self.key_history[self.current_key.public_key.hex()] = self.current_key
            self.current_key.rotation_count += 1
        
        self.current_key = self._generate_key_pair()
        self.key_history[self.current_key.public_key.hex()] = self.current_key
        logger.info("Key pair rotated.")
        return self.current_key
    
    def get_current_key(self) -> KeyPair:
        """
        Get the current key pair, rotating if necessary.
        
        Returns:
            The current KeyPair instance.
        """
        if self.should_rotate():
            self.rotate_key()
        return self.current_key
    
    def encrypt(self, data: bytes) -> Dict:
        """
        Encrypt data using the current key pair.
        
        Args:
            data: The data to encrypt.
        
        Returns:
            A dictionary containing the encrypted data and metadata.
        """
        key = self.get_current_key()
        # Simulate encryption using XOR with key (for demonstration)
        encrypted = bytes([b ^ key.private_key[i % len(key.private_key)] for i, b in enumerate(data)])
        
        return {
            'encrypted_data': encrypted.hex(),
            'key_id': key.public_key.hex(),
            'algorithm': key.algorithm,
            'timestamp': time.time()
        }
    
    def decrypt(self, encrypted_data: str, key_id: str) -> bytes:
        """
        Decrypt data using the specified key.
        
        Args:
            encrypted_data: The hex-encoded encrypted data.
            key_id: The ID of the key used for encryption.
        
        Returns:
            The decrypted data.
        """
        key = self.key_history.get(key_id)
        if not key:
            raise ValueError(f"Key {key_id} not found.")
        
        encrypted = bytes.fromhex(encrypted_data)
        decrypted = bytes([b ^ key.private_key[i % len(key.private_key)] for i, b in enumerate(encrypted)])
        return decrypted

if __name__ == "__main__":
    # Test harness
    engine = QuantumKeyRotationEngine(max_key_age=1.0, entropy_threshold=0.5)
    
    # Test encryption and decryption
    data = b"Hello, Michael!"
    encrypted = engine.encrypt(data)
    decrypted = engine.decrypt(encrypted['encrypted_data'], encrypted['key_id'])
    assert decrypted == data, "Decryption failed!"
    
    # Test key rotation
    time.sleep(1.1)  # Wait for key age to exceed max_key_age
    new_key = engine.get_current_key()
    assert new_key.rotation_count > 0, "Key rotation failed!"
    
    logger.info("All tests passed!")