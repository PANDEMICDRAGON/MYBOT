import os, json, hashlib, hmac, base64, time
from typing import List, Tuple, Optional

class TamperEvidentLogAuditor:
    """A lightweight, self‑contained log auditor that:
    
    1. Stores log entries in memory.
    2. Builds a Merkle‑tree root hash for tamper evidence.
    3. Encrypts the entire log payload with a symmetric key derived from a passphrase.
    4. Allows export/import of the encrypted blob and verification of integrity.
    
    The implementation relies only on the Python standard library, making it portable
    across all deployment environments.
    """

    def __init__(self, passphrase: str):
        """Create a new auditor.
        
        Args:
            passphrase: Human‑readable secret used to derive the encryption key.
        """
        if not passphrase:
            raise ValueError("Passphrase must be a non‑empty string")
        self._key = hashlib.sha256(passphrase.encode()).digest()  # 32‑byte key
        self._entries: List[Tuple[float, str]] = []  # (timestamp, message)
        self._merkle_root: Optional[bytes] = None

    # ---------------------------------------------------------------------
    # Core log handling
    # ---------------------------------------------------------------------
    def add_entry(self, message: str) -> None:
        """Append a new log entry.
        
        Args:
            message: Arbitrary text describing the event.
        """
        if not isinstance(message, str):
            raise TypeError("Log message must be a string")
        timestamp = time.time()
        self._entries.append((timestamp, message))
        self._merkle_root = None  # Invalidate cached root

    def _leaf_hash(self, entry: Tuple[float, str]) -> bytes:
        """Hash a single log entry.
        
        The leaf hash is SHA‑256(timestamp || message).
        """
        ts_bytes = str(entry[0]).encode()
        msg_bytes = entry[1].encode()
        return hashlib.sha256(ts_bytes + b"|" + msg_bytes).digest()

    def compute_merkle_root(self) -> bytes:
        """Compute (or retrieve cached) Merkle‑tree root for current entries.
        
        Returns:
            32‑byte root hash.
        """
        if self._merkle_root is not None:
            return self._merkle_root
        if not self._entries:
            self._merkle_root = hashlib.sha256(b"").digest()
            return self._merkle_root
        # Build leaf layer
        layer = [self._leaf_hash(e) for e in self._entries]
        # Iteratively hash pairs until a single root remains
        while len(layer) > 1:
            next_layer: List[bytes] = []
            for i in range(0, len(layer), 2):
                left = layer[i]
                right = layer[i + 1] if i + 1 < len(layer) else left
                next_layer.append(hashlib.sha256(left + right).digest())
            layer = next_layer
        self._merkle_root = layer[0]
        return self._merkle_root

    # ---------------------------------------------------------------------
    # Simple XOR‑based encryption (for demonstration only)
    # ---------------------------------------------------------------------
    def _xor_bytes(self, data: bytes) -> bytes:
        """XOR data with the derived key (repeating as necessary)."""
        return bytes(b ^ self._key[i % len(self._key)] for i, b in enumerate(data))

    def export_encrypted_log(self) -> str:
        """Serialize the log entries, compute the Merkle root, and return a base64‑encoded
        encrypted blob that also contains an HMAC for authenticity.
        
        Returns:
            Base64 string ready for storage or transmission.
        """
        payload = {
            "entries": self._entries,
            "merkle_root": base64.b64encode(self.compute_merkle_root()).decode()
        }
        json_bytes = json.dumps(payload, separators=(',', ':')).encode()
        encrypted = self._xor_bytes(json_bytes)
        mac = hmac.new(self._key, encrypted, hashlib.sha256).digest()
        package = mac + encrypted
        return base64.b64encode(package).decode()

    @classmethod
    def import_encrypted_log(cls, passphrase: str, blob: str) -> "TamperEvidentLogAuditor":
        """Decrypt a previously exported blob and verify its integrity.
        
        Args:
            passphrase: The same secret used during export.
            blob: Base64‑encoded string produced by :meth:`export_encrypted_log`.
        
        Returns:
            An instance populated with the recovered log entries.
        """
        if not passphrase:
            raise ValueError("Passphrase must be a non‑empty string")
        key = hashlib.sha256(passphrase.encode()).digest()
        raw = base64.b64decode(blob)
        if len(raw) < 32:
            raise ValueError("Corrupted blob: too short")
        mac, encrypted = raw[:32], raw[32:]
        expected_mac = hmac.new(key, encrypted, hashlib.sha256).digest()
        if not hmac.compare_digest(mac, expected_mac):
            raise ValueError("Integrity check failed: MAC mismatch")
        # Decrypt
        decrypted = bytes(b ^ key[i % len(key)] for i, b in enumerate(encrypted))
        payload = json.loads(decrypted.decode())
        auditor = cls(passphrase)
        auditor._entries = [(float(ts), msg) for ts, msg in payload["entries"]]
        auditor._merkle_root = base64.b64decode(payload["merkle_root"].encode())
        # Verify that recomputed root matches stored root
        if auditor.compute_merkle_root() != auditor._merkle_root:
            raise ValueError("Integrity check failed: Merkle root mismatch")
        return auditor

    # ---------------------------------------------------------------------
    # Utility
    # ---------------------------------------------------------------------
    def verify_integrity(self) -> bool:
        """Re‑compute the Merkle root and compare it to the stored value.
        
        Returns:
            ``True`` if the log has not been tampered with, ``False`` otherwise.
        """
        if self._merkle_root is None:
            return False
        return self.compute_merkle_root() == self._merkle_root

if __name__ == "__main__":
    # Simple self‑test harness
    PASSPHRASE = "C0rt@n@_S3cR3t"
    auditor = TamperEvidentLogAuditor(PASSPHRASE)
    auditor.add_entry("Operator login successful")
    auditor.add_entry("Started autonomous resource quota adjustment")
    auditor.add_entry("Completed heartbeat check with node 7")
    print("Merkle root (hex):", auditor.compute_merkle_root().hex())
    encrypted_blob = auditor.export_encrypted_log()
    print("Encrypted blob (truncated):", encrypted_blob[:60] + "...")
    # Simulate a fresh import
    recovered = TamperEvidentLogAuditor.import_encrypted_log(PASSPHRASE, encrypted_blob)
    assert recovered.verify_integrity(), "Recovered log failed integrity check"
    print("Integrity verified after import. Entries:")
    for ts, msg in recovered._entries:
        print(f"  [{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(ts))}] {msg}")
    print("Self‑test completed successfully.")
