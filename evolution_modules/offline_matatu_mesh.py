import ast
import hashlib
import hmac
import json
import logging
import time
from typing import Dict, List, Optional, Tuple

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')
logger = logging.getLogger("MatatuMeshRelay")

class OfflineMatatuMeshRelay:
    """
    Facilitates opportunistic delay-tolerant networking (DTN) for Cortana and operator
    Michael Obiero between Kitengela and Nairobi using mobile public transit (Matatu)
    nodes as physical data mules when cellular infrastructure fails.
    """
    
    def __init__(self, node_id: str = "CORTANA_KITENGELA_NODE_01", secret_key: bytes = b"kitengela-nairobi-transit-key"):
        self.node_id = node_id
        self.secret_key = secret_key
        self.packet_store: Dict[str, Dict] = {}
        self.transit_log: List[Dict] = []

    def create_payload(self, destination: str, payload_data: Dict) -> Dict:
        """Encapsulates and signs an outgoing telemetry or message packet for transit."""
        timestamp = time.time()
        body = {
            "source": self.node_id,
            "destination": destination,
            "timestamp": timestamp,
            "data": payload_data
        }
        serialized = json.dumps(body, sort_keys=True).encode('utf-8')
        signature = hmac.new(self.secret_key, serialized, hashlib.sha256).hexdigest()
        
        packet = {
            "packet_id": hashlib.sha256(serialized + signature.encode()).hexdigest()[:16],
            "body": body,
            "signature": signature,
            "hops": 0,
            "status": "QUEUED"
        }
        self.packet_store[packet["packet_id"]] = packet
        logger.info(f"Created mesh packet {packet['packet_id']} destined for {destination}")
        return packet

    def ingest_transit_node_data(self, vehicle_id: str, incoming_packets: List[Dict]) -> Tuple[int, List[str]]:
        """Ingests packets offloaded from a physical Matatu transit mule node."""
        accepted_count = 0
        synced_ids = []
        
        for pkt in incoming_packets:
            pid = pkt.get("packet_id")
            sig = pkt.get("signature")
            body = pkt.get("body")
            
            if not pid or not sig or not body:
                continue
                
            # Verify HMAC signature
            serialized = json.dumps(body, sort_keys=True).encode('utf-8')
            expected_sig = hmac.new(self.secret_key, serialized, hashlib.sha256).hexdigest()
            
            if hmac.compare_digest(sig, expected_sig):
                if pid not in self.packet_store:
                    pkt["hops"] = pkt.get("hops", 0) + 1
                    self.packet_store[pid] = pkt
                    accepted_count += 1
                    synced_ids.append(pid)
                    logger.info(f"Accepted packet {pid} via transit vehicle {vehicle_id} (Hops: {pkt['hops']})")
                else:
                    logger.debug(f"Packet {pid} already present in local store.")
            else:
                logger.warning(f"Cryptographic verification failed for packet {pid} from vehicle {vehicle_id}")
                
        self.transit_log.append({
            "vehicle_id": vehicle_id,
            "timestamp": time.time(),
            "ingested_count": accepted_count
        })
        return accepted_count, synced_ids

    def get_pending_bundles(self, target_destination: Optional[str] = None) -> List[Dict]:
        """Retrieves queued packets ready to be handed off to outbound transit nodes."""
        bundles = []
        for pid, pkt in self.packet_store.items():
            if pkt["status"] == "QUEUED":
                if target_destination is None or pkt["body"]["destination"] == target_destination:
                    bundles.append(pkt)
        return bundles

    def mark_delivered(self, packet_id: str) -> bool:
        """Marks a packet as successfully delivered to its final destination."""
        if packet_id in self.packet_store:
            self.packet_store[packet_id]["status"] = "DELIVERED"
            logger.info(f"Packet {packet_id} marked as DELIVERED.")
            return True
        return False

    def get_status_summary(self) -> Dict:
        """Returns health and transit statistics of the offline mesh."""
        total = len(self.packet_store)
        queued = sum(1 for p in self.packet_store.values() if p["status"] == "QUEUED")
        delivered = sum(1 for p in self.packet_store.values() if p["status"] == "DELIVERED")
        return {
            "node_id": self.node_id,
            "total_packets": total,
            "queued_packets": queued,
            "delivered_packets": delivered,
            "transit_nodes_encountered": len(self.transit_log)
        }

if __name__ == "__main__":
    print("Initializing Offline Matatu Fleet Mesh Relay Test Harness...")
    mesh = OfflineMatatuMeshRelay(node_id="KITENGELA_BASE_01")
    
    # Create a test emergency telemetry bundle
    pkt = mesh.create_payload(destination="NAIROBI_HQ", payload_data={"alert": "Kitengela perimeter secure, solar surplus nominal."})
    
    # Simulate transit mule vehicle coming into range from Route 125 (Kitengela-Nairobi)
    simulated_mule_payload = [pkt]
    accepted, ids = mesh.ingest_transit_node_data(vehicle_id="MATATU_KBN_452A", incoming_packets=simulated_mule_payload)
    assert accepted == 1
    
    summary = mesh.get_status_summary()
    print(f"Mesh Status Summary: {json.dumps(summary, indent=2)}")
    
    # Verify AST compilation safety
    code_string = open(__file__, "r", encoding="utf-8").read()
    ast.parse(code_string)
    print("AST Compilation Check: PASSED")
