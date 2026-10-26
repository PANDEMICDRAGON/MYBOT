import ast
import hashlib
import hmac
import json
import math
import time
from typing import Dict, List, Optional, Tuple


class GeoFenceViolationException(Exception):
    """Raised when the system detects a breach of the Kitengela/Nairobi perimeter."""
    pass


class OfflineGeoFenceEnforcer:
    """Proactively guards hardware and execution context against unauthorized relocation."""

    def __init__(self, master_secret: bytes, allowed_zones: Optional[List[Dict[str, float]]] = None):
        self.master_secret = master_secret
        # Default zones: Kitengela core & Nairobi node
        self.allowed_zones = allowed_zones or [
            {"name": "Kitengela Base", "lat": -1.4854, "lon": 36.9691, "radius_km": 5.0},
            {"name": "Nairobi Outpost", "lat": -1.2921, "lon": 36.8219, "radius_km": 15.0}
        ]
        self.violation_log: List[Dict[str, any]] = []

    def _haversine_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculates great-circle distance between two points in kilometers."""
        R = 6371.0  # Earth radius in km
        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)
        dphi = math.radians(lat2 - lat1)
        dlambda = math.radians(lon2 - lon1)

        a = math.sin(dphi / 2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return R * c

    def sign_telemetry(self, lat: float, lon: float, timestamp: float) -> str:
        """Generates a cryptographic HMAC to prevent telemetry spoofing."""
        payload = f"{lat}:{lon}:{timestamp}".encode('utf-8')
        return hmac.new(self.master_secret, payload, hashlib.sha256).hexdigest()

    def verify_perimeter(self, current_lat: float, current_lon: float, timestamp: float, signature: str) -> bool:
        """Verifies location integrity and checks if within permitted Kitengela/Nairobi zones."""
        expected_sig = self.sign_telemetry(current_lat, current_lon, timestamp)
        if not hmac.compare_digest(expected_sig, signature):
            raise GeoFenceViolationException("CRITICAL: Cryptographic signature mismatch on location telemetry! Possible spoofing.")

        # Check against allowed zones
        in_bounds = False
        min_dist = float('inf')

        for zone in self.allowed_zones:
            dist = self._haversine_distance(current_lat, current_lon, zone["lat"], zone["lon"])
            if dist < min_dist:
                min_dist = dist
            if dist <= zone["radius_km"]:
                in_bounds = True
                break

        if not in_bounds:
            event = {
                "timestamp": timestamp,
                "lat": current_lat,
                "lon": current_lon,
                "nearest_zone_km": min_dist
            }
            self.violation_log.append(event)
            raise GeoFenceViolationException(f"SECURITY BREACH: System relocated outside permitted zones! Nearest zone boundary is {min_dist:.2f} km away.")

        return True


if __name__ == "__main__":
    print("[*] Initializing Offline Geo-Fence Enforcer Test Harness...")
    secret = b"cortana_kitengela_secure_seed_2026"
    enforcer = OfflineGeoFenceEnforcer(master_secret=secret)

    # Test valid Kitengela coordinates (-1.4854, 36.9691)
    test_lat, test_lon = -1.4800, 36.9600
    now = time.time()
    sig = enforcer.sign_telemetry(test_lat, test_lon, now)

    try:
        res = enforcer.verify_perimeter(test_lat, test_lon, now, sig)
        print(f"[+] Perimeter check passed inside Kitengela: {res}")
    except Exception as e:
        print(f"[-] Unexpected failure: {e}")

    # Test out-of-bounds coordinates (e.g., Mombasa: -4.0435, 39.6682)
    bad_lat, bad_lon = -4.0435, 39.6682
    bad_sig = enforcer.sign_telemetry(bad_lat, bad_lon, now)

    try:
        enforcer.verify_perimeter(bad_lat, bad_lon, now, bad_sig)
    except GeoFenceViolationException as gve:
        print(f"[+] Successfully intercepted boundary violation: {gve}")

    # Validate clean compilation via AST
    with open(__file__, "r", encoding="utf-8") as f:
        ast_tree = ast.parse(f.read())
    print(f"[+] AST Compilation Check Passed: {len(ast_tree.body)} nodes verified.")
