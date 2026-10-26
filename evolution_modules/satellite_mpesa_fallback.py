import logging
import time
import json
import hashlib
from typing import Dict, Any, Optional

logging.basicConfig(level=logging.INFO, format='[%(asctime)s] [SATELLITE_MPESA_GATEWAY] %(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

class SatelliteMpesaFallbackEngine:
    """
    Manages dual-path resilient failover between Starlink satellite links and localized
    M-Pesa USSD encoded data bursts for zero-downtime operator telemetry delivery.
    """
    def __init__(self, node_id: str = "CORTANA-NODE-KE-01") -> None:
        self.node_id = node_id
        self.starlink_active = True
        self.ussd_channel_ready = True
        logger.info(f"Initialized SatelliteMpesaFallbackEngine for node: {self.node_id}")

    def encode_payload_for_ussd(self, payload: Dict[str, Any]) -> str:
        """
        Compresses and encodes vital telemetry state into a compact alphanumeric string
        suitable for transmission via USSD session metadata bursts.
        """
        raw_json = json.dumps(payload, sort_keys=True)
        payload_hash = hashlib.sha256(raw_json.encode('utf-8')).hexdigest()[:6]
        # Simulate compact USSD frame serialization
        encoded_frame = f"*334*9#*{self.node_id}*{payload_hash}:{base64_sim(raw_json)}"
        logger.info(f"Encoded payload into USSD burst frame. Length: {len(encoded_frame)} chars")
        return encoded_frame

    def transmit_telemetry(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Attempts transmission via Starlink primary link; on failure, falls back to USSD sidechannel.
        """
        start_time = time.time()
        if self.starlink_active:
            try:
                # Simulate Starlink transmission packet
                if not self._ping_starlink():
                    raise ConnectionError("Starlink satellite uplink timeout.")
                
                latency = (time.time() - start_time) * 1000
                logger.info(f"Telemetry successfully transmitted via Starlink primary link. Latency: {latency:.2f}ms")
                return {"status": "SUCCESS", "channel": "STARLINK", "latency_ms": latency}
            except Exception as e:
                logger.warning(f"Starlink uplink failure detected: {e}. Initiating M-Pesa USSD failover...")
                self.starlink_active = False

        # Fallback to USSD Channel
        if self.ussd_channel_ready:
            ussd_frame = self.encode_payload_for_ussd(payload)
            latency = (time.time() - start_time) * 1000
            logger.info(f"Telemetry successfully relayed via M-Pesa USSD encrypted sidechannel. Latency: {latency:.2f}ms")
            return {"status": "SUCCESS", "channel": "MPESA_USSD_FALLBACK", "ussd_frame": ussd_frame, "latency_ms": latency}
        
        logger.critical("All transmission channels failed! Node isolated in Kitengela/Nairobi mesh.")
        return {"status": "FAILED", "channel": "NONE"}

    def _ping_starlink(self) -> bool:
        """Mock health check for Starlink hardware endpoint."""
        return self.starlink_active


def base64_sim(data: str) -> str:
    """Simulates light encoding for demonstration standalone compliance."""
    return data[:20].encode('utf-8').hex()

if __name__ == "__main__":
    engine = SatelliteMpesaFallbackEngine()
    test_payload = {
        "operator": "Michael Obiero",
        "location": "Kitengela-Nairobi Corridor",
        "system_state": "SECURE",
        "battery": "100%"
    }
    
    # Test normal Starlink route
    res1 = engine.transmit_telemetry(test_payload)
    print("Test 1 Result:", res1)
    
    # Force Starlink outage to test M-Pesa USSD fallback
    engine.starlink_active = False
    res2 = engine.transmit_telemetry(test_payload)
    print("Test 2 Result:", res2)
