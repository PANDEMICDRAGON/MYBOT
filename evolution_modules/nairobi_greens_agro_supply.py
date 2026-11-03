"""
Nairobi Fresh Greens Cold-Chain Micro-Logistics Quantum-Resilient Telemetry Synchronizer
Designed for real-time monitoring and verification of perishable agricultural logistics across Nairobi.
"""

import time
import hmac
import hashlib
import json
from typing import Dict, List, Optional, Any


class GreensLogisticsTelemetry:
    """Manages tamper-evident sensor telemetry for perishable produce transiting Nairobi."""

    def __init__(self, node_id: str, secret_key: bytes):
        self.node_id = node_id
        self.secret_key = secret_key
        self.telemetry_ledger: List[Dict[str, Any]] = []

    def record_checkpoint(self, location: str, temperature_c: float, humidity_pct: float) -> Dict[str, Any]:
        """Records a secure telemetry checkpoint with cryptographic binding."""
        timestamp = time.time()
        payload = {
            "node_id": self.node_id,
            "location": location,
            "temperature_c": temperature_c,
            "humidity_pct": humidity_pct,
            "timestamp": timestamp,
            "spoiled_risk": self._calculate_spoilage_risk(temperature_c, humidity_pct)
        }
        
        payload_bytes = json.dumps(payload, sort_keys=True).encode('utf-8')
        signature = hmac.new(self.secret_key, payload_bytes, hashlib.sha256).hexdigest()
        
        record = {
            "payload": payload,
            "hmac_signature": signature
        }
        self.telemetry_ledger.append(record)
        return record

    def _calculate_spoilage_risk(self, temp: float, humidity: float) -> str:
        """Calculates spoilage risk based on Nairobi climate transport thresholds."""
        if temp > 12.0 and humidity > 80.0:
            return "HIGH_CRITICAL"
        elif temp > 8.0:
            return "MODERATE"
        return "OPTIMAL"

    def verify_ledger(self) -> bool:
        """Verifies the cryptographic integrity of the telemetry audit trail."""
        for entry in self.telemetry_ledger:
            payload_bytes = json.dumps(entry["payload"], sort_keys=True).encode('utf-8')
            expected = hmac.new(self.secret_key, payload_bytes, hashlib.sha256).hexdigest()
            if not hmac.compare_digest(expected, entry["hmac_signature"]):
                return False
        return True


if __name__ == "__main__":
    print("Initializing Nairobi Greens Agro-Supply Cold-Chain Sentinel...")
    key = b"nairobi_agro_secure_key_2025"
    sentinel = GreensLogisticsTelemetry(node_id="KIAMBU_TRANSIT_04", secret_key=key)
    
    # Simulate checkpoints from farm to Wakulima market
    ckpt1 = sentinel.record_checkpoint("Limuru Farm Gate", 6.5, 85.0)
    ckpt2 = sentinel.record_checkpoint("Red Hill Bypass", 9.1, 78.5)
    ckpt3 = sentinel.record_checkpoint("Wakulima Market Depot", 7.2, 82.0)
    
    print(f"Recorded {len(sentinel.telemetry_ledger)} logistics checkpoints.")
    print(f"Ledger Integrity Verified: {sentinel.verify_ledger()}")
    print("Agro-Supply Cold-Chain Sentinel operational.")
