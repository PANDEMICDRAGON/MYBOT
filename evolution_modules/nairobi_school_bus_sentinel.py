"""
Nairobi School Bus IoT Telemetry & Geofence Route Compliance Sentinel
Designed to monitor school transport in Nairobi, Kenya, checking speed compliance,
geofence boundaries (e.g., designated school zones and authorized drop-offs), and
issuing cryptographic event logs for safety audits.
"""

import json
import hashlib
import time
from typing import Dict, List, Optional, Tuple


class NairobiSchoolBusSentinel:
    """Monitors real-time telemetry for school buses across Nairobi."""

    def __init__(self, speed_limit_kmh: float = 80.0):
        self.speed_limit_kmh = speed_limit_kmh
        self.bus_states: Dict[str, Dict] = {}
        self.audit_log: List[Dict] = []

    def update_telemetry(self, bus_id: str, lat: float, lon: float, speed: float, timestamp: float) -> Dict:
        """Process incoming telemetry ping from a school bus."""
        alerts = []
        is_speeding = speed > self.speed_limit_kmh
        if is_speeding:
            alerts.append(f"SPEEDING_ALERT: Bus {bus_id} traveling at {speed} km/h (Limit: {self.speed_limit_kmh} km/h)")

        # Simple Nairobi bounding box sanity check (Lat: -1.45 to -1.15, Lon: 36.60 to 37.10)
        out_of_bounds = not (-1.45 <= lat <= -1.15 and 36.60 <= lon <= 37.10)
        if out_of_bounds:
            alerts.append(f"GEOFENCE_ALERT: Bus {bus_id} outside Nairobi metropolitan boundary at ({lat}, {lon})")

        state = {
            "bus_id": bus_id,
            "lat": lat,
            "lon": lon,
            "speed": speed,
            "timestamp": timestamp,
            "is_speeding": is_speeding,
            "out_of_bounds": out_of_bounds,
            "alerts": alerts
        }

        self.bus_states[bus_id] = state
        self._record_audit(state)
        return state

    def _record_audit(self, state: Dict) -> None:
        """Cryptographically hash and record telemetry event."""
        raw_data = json.dumps(state, sort_keys=True)
        proof = hashlib.sha256(raw_data.encode('utf-8')).hexdigest()
        audit_entry = {
            "proof": proof,
            "state": state
        }
        self.audit_log.append(audit_entry)

    def get_fleet_status(self) -> Dict[str, Dict]:
        return self.bus_states


if __name__ == "__main__":
    print("Initializing Nairobi School Bus IoT Telemetry Sentinel...")
    sentinel = NairobiSchoolBusSentinel(speed_limit_kmh=60.0)

    # Test normal ping
    res1 = sentinel.update_telemetry("KBB-123A", -1.2921, 36.8219, 45.0, time.time())
    print(f"Bus KBB-123A Status: {res1['alerts'] or 'Normal'}")

    # Test speeding ping on Thika Road corridor
    res2 = sentinel.update_telemetry("KBC-456B", -1.2233, 36.8865, 75.0, time.time())
    print(f"Bus KBC-456B Status: {res2['alerts']}")

    print(f"Total Audit Entries Recorded: {len(sentinel.audit_log)}")
    print("Nairobi School Bus Sentinel online and protecting operator domain.")
