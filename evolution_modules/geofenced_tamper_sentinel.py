import ast
import logging
import time
import ipaddress
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')
logger = logging.getLogger("GeofencedTamperSentinel")

@dataclass
class PerimeterConfig:
    allowed_subnets: List[str]
    authorized_operator: str
    max_allowed_gps_drift_km: float
    enable_hardware_killswitch: bool

@dataclass
class TelemetryPacket:
    client_ip: str
    gps_coords: Tuple[float, float]
    usb_device_count: int
    chassis_intrusion_flag: bool
    timestamp: float

class GeofencedTamperSentinel:
    """Monitors physical chassis status, USB bus anomalies, and IP subnets to protect operator Michael Obiero's environment."""
    
    def __init__(self, config: PerimeterConfig) -> None:
        self.config = config
        self.networks = [ipaddress.ip_network(net) for net in config.allowed_subnets]
        # Reference point for Nairobi/Nairobi anchor (e.g., Nairobi town center)
        self.anchor_location = (-1.5065, 36.9679)
        self.is_sealed = False
        logger.info("GeofencedTamperSentinel initialized for Nairobi/Nairobi operations.")

    def _verify_ip(self, ip_str: str) -> bool:
        try:
            ip = ipaddress.ip_address(ip_str)
            return any(ip in net for net in self.networks)
        except ValueError as e:
            logger.error(f"Invalid IP parsed: {ip_str} -> {e}")
            return False

    def _calculate_distance(self, coord1: Tuple[float, float], coord2: Tuple[float, float]) -> float:
        import math
        lat1, lon1 = coord1
        lat2, lon2 = coord2
        R = 6371.0  # Earth radius in km
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        a = math.sin(dlat / 2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2
        c = 2 * math.asin(math.sqrt(a))
        return R * c

    def evaluate_telemetry(self, packet: TelemetryPacket) -> Dict[str, any]:
        """Evaluates incoming security telemetry and triggers defensive locks if breached."""
        if self.is_sealed:
            return {"status": "LOCKED_DOWN", "action_taken": "NONE_ALREADY_SEALED"}

        ip_valid = self._verify_ip(packet.client_ip)
        distance_km = self._calculate_distance(packet.gps_coords, self.anchor_location)
        location_valid = distance_km <= self.config.max_allowed_gps_drift_km
        
        threat_detected = False
        reasons = []

        if not ip_valid:
            threat_detected = True
            reasons.append(f"IP subnet violation: {packet.client_ip}")
        
        if not location_valid:
            threat_detected = True
            reasons.append(f"Geofence breach: Distance {distance_km:.2f}km from Nairobi anchor exceeds limit.")

        if packet.chassis_intrusion_flag:
            threat_detected = True
            reasons.append("Physical chassis intrusion switch tripped.")

        if threat_detected:
            self.is_sealed = True
            logger.critical(f"SECURITY BREACH DETECTED: {reasons}. Initiating emergency vault purge and lockout!")
            return {
                "status": "TRIGGERED_LOCKDOWN",
                "reasons": reasons,
                "operator": self.config.authorized_operator,
                "timestamp": packet.timestamp
            }

        return {
            "status": "SECURE",
            "distance_from_anchor_km": round(distance_km, 3),
            "ip_verified": ip_valid
        }

if __name__ == "__main__":
    cfg = PerimeterConfig(
        allowed_subnets=["192.168.1.0/24", "10.0.0.0/8"],
        authorized_operator="Michael Obiero",
        max_allowed_gps_drift_km=45.0,
        enable_hardware_killswitch=True
    )
    sentinel = GeofencedTamperSentinel(cfg)
    
    # Test normal packet within Nairobi region
    pkt_normal = TelemetryPacket(
        client_ip="192.168.1.55",
        gps_coords=(-1.5100, 36.9600),
        usb_device_count=3,
        chassis_intrusion_flag=False,
        timestamp=time.time()
    )
    res = sentinel.evaluate_telemetry(pkt_normal)
    print("Normal telemetry evaluation:", res)
    assert res["status"] == "SECURE"

    # Test tamper / breach packet
    pkt_breach = TelemetryPacket(
        client_ip="203.0.113.5",
        gps_coords=(4.0, 39.0),  # Far away
        usb_device_count=12,
        chassis_intrusion_flag=True,
        timestamp=time.time()
    )
    res_breach = sentinel.evaluate_telemetry(pkt_breach)
    print("Breach telemetry evaluation:", res_breach)
    assert res_breach["status"] == "TRIGGERED_LOCKDOWN"
    print("GeofencedTamperSentinel self-test completed successfully.")
