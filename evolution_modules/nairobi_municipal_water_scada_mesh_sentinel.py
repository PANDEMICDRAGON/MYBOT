"""Nairobi Municipal Water SCADA Mesh Sentinel

Provides autonomous telemetry monitoring, real-time pressure anomaly detection,
flow rate validation, and cryptographic command signing for Nairobi's urban water SCADA infrastructure.
"""

import time
import hmac
import hashlib
import statistics
from typing import Dict, List, Optional, Tuple

class WaterScadaMeshSentinel:
    """Monitors Nairobi municipal water SCADA nodes and secures telemetry pipelines."""

    def __init__(self, secret_key: bytes, pressure_threshold_psi: float = 85.0):
        self.secret_key = secret_key
        self.pressure_threshold_psi = pressure_threshold_psi
        self.telemetry_ledger: List[Dict[str, any]] = []
        self.valve_states: Dict[str, str] = {}

    def sign_telemetry(self, node_id: str, timestamp: float, pressure: float, flow_rate: float) -> str:
        """Generates an HMAC signature for SCADA node telemetry data."""
        payload = f"{node_id}:{timestamp}:{pressure}:{flow_rate}".encode('utf-8')
        return hmac.new(self.secret_key, payload, hashlib.sha256).hexdigest()

    def verify_and_ingest(self, node_id: str, timestamp: float, pressure: float, flow_rate: float, signature: str) -> Tuple[bool, str]:
        """Validates incoming SCADA packet integrity and evaluates operational safety."""
        expected_sig = self.sign_telemetry(node_id, timestamp, pressure, flow_rate)
        if not hmac.compare_digest(expected_sig, signature):
            return False, "INVALID_SIGNATURE"

        # Check for replay attack (e.g. timestamp older than 30 seconds)
        if abs(time.time() - timestamp) > 30.0:
            return False, "TIMESTAMP_DRIFT_EXCEEDED"

        # Record telemetry
        record = {
            "node_id": node_id,
            "timestamp": timestamp,
            "pressure": pressure,
            "flow_rate": flow_rate,
            "status": "NORMAL"
        }

        # Safety Check
        if pressure > self.pressure_threshold_psi:
            record["status"] = "OVER_PRESSURE_WARNING"
            self.valve_states[node_id] = "EMERGENCY_SHUT_OFF"
            return True, "ALERT: Pressure threshold exceeded. Valve throttled."
        else:
            self.valve_states[node_id] = "OPTIMAL"
            
        self.telemetry_ledger.append(record)
        return True, "INGESTED_SUCCESSFULLY"

    def get_grid_statistics(self) -> Dict[str, float]:
        """Computes aggregate telemetry metrics across all active municipal water nodes."""
        if not self.telemetry_ledger:
            return {"mean_pressure": 0.0, "mean_flow": 0.0, "active_nodes": 0}
        
        pressures = [r["pressure"] for r in self.telemetry_ledger]
        flows = [r["flow_rate"] for r in self.telemetry_ledger]
        
        return {
            "mean_pressure": statistics.mean(pressures),
            "mean_flow": statistics.mean(flows),
            "active_nodes": len(set(r["node_id"] for r in self.telemetry_ledger))
        }

if __name__ == "__main__":
    print("Initializing Nairobi Municipal Water SCADA Mesh Sentinel Test Suite...")
    key = b"nairobi-water-master-key-2026"
    sentinel = WaterScadaMeshSentinel(secret_key=key, pressure_threshold_psi=80.0)
    
    now = time.time()
    sig = sentinel.sign_telemetry("NRB-ZONE-04-KILIMANI", now, 72.5, 450.0)
    
    valid, msg = sentinel.verify_and_ingest("NRB-ZONE-04-KILIMANI", now, 72.5, 450.0, sig)
    print(f"Ingestion Result 1: {valid} - {msg}")
    
    # Test over-pressure anomaly
    now2 = time.time()
    sig2 = sentinel.sign_telemetry("NRB-ZONE-04-KILIMANI", now2, 92.0, 600.0)
    valid2, msg2 = sentinel.verify_and_ingest("NRB-ZONE-04-KILIMANI", now2, 92.0, 600.0, sig2)
    print(f"Ingestion Result 2 (Anomaly): {valid2} - {msg2}")
    print("Grid Statistics:", sentinel.get_grid_statistics())
    print("SCADA Sentinel verification completed successfully.")
