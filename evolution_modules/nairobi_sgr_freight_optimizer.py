import json
import time
import hashlib
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
from enum import Enum
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("SGR_Freight_Optimizer")

class FreightStatus(Enum):
    SCHEDULED = "SCHEDULED"
    LOADED = "LOADED"
    IN_TRANSIT = "IN_TRANSIT"
    CUSTOMS_HOLD = "CUSTOMS_HOLD"
    DELIVERED = "DELIVERED"
    DELAYED = "DELAYED"

@dataclass
class FreightContainer:
    container_id: str
    origin: str
    destination: str
    weight_kg: float
    cargo_type: str
    status: FreightStatus = FreightStatus.SCHEDULED
    timestamp: float = field(default_factory=time.time)
    hash_signature: str = ""

    def __post_init__(self):
        self._generate_signature()

    def _generate_signature(self):
        """Generate a cryptographic hash for tamper detection."""
        data = f"{self.container_id}|{self.origin}|{self.destination}|{self.weight_kg}|{self.cargo_type}"
        self.hash_signature = hashlib.sha256(data.encode()).hexdigest()

class SGRFreightOptimizer:
    """
    Optimizes freight logistics on the SGR network.
    """
    
    def __init__(self):
        self.containers: Dict[str, FreightContainer] = {}
        self.route_cache: Dict[Tuple[str, str], float] = {}
        
    def register_container(self, container: FreightContainer) -> bool:
        """Register a new freight container."""
        if container.container_id in self.containers:
            logger.warning(f"Container {container.container_id} already registered.")
            return False
        self.containers[container.container_id] = container
        logger.info(f"Registered container {container.container_id}")
        return True

    def estimate_transit_time(self, origin: str, destination: str) -> float:
        """
        Estimate transit time between two SGR stations.
        Uses a simple heuristic based on distance and average speed.
        """
        key = (origin, destination)
        if key in self.route_cache:
            return self.route_cache[key]
        
        # Hardcoded distances for demo (km)
        distances = {
            ("Nairobi", "Naivasha"): 120,
            ("Naivasha", "Nairobi"): 120,
            ("Nairobi", "Mombasa"): 470,
            ("Mombasa", "Nairobi"): 470,
            ("Naivasha", "Mombasa"): 350,
            ("Mombasa", "Naivasha"): 350
        }
        
        distance = distances.get(key, 500)  # Default 500km if unknown
        avg_speed_kmh = 100  # Average SGR freight speed
        transit_time_hours = distance / avg_speed_kmh
        
        self.route_cache[key] = transit_time_hours
        return transit_time_hours

    def optimize_route(self, containers: List[FreightContainer]) -> List[FreightContainer]:
        """
        Optimize the order of containers for loading based on destination priority.
        """
        # Sort by destination to minimize backtracking
        return sorted(containers, key=lambda c: c.destination)

    def generate_manifest(self, containers: List[FreightContainer]) -> str:
        """
        Generate a JSON manifest for customs clearance.
        """
        manifest = {
            "timestamp": time.time(),
            "total_containers": len(containers),
            "containers": [
                {
                    "id": c.container_id,
                    "origin": c.origin,
                    "destination": c.destination,
                    "weight_kg": c.weight_kg,
                    "cargo_type": c.cargo_type,
                    "hash": c.hash_signature
                } for c in containers
            ]
        }
        return json.dumps(manifest, indent=2)

    def verify_integrity(self, container_id: str, expected_hash: str) -> bool:
        """
        Verify the integrity of a container's data.
        """
        if container_id not in self.containers:
            return False
        return self.containers[container_id].hash_signature == expected_hash

if __name__ == "__main__":
    # Test Harness
    optimizer = SGRFreightOptimizer()
    
    # Create sample containers
    c1 = FreightContainer("CONT-001", "Nairobi", "Mombasa", 1000.0, "Electronics")
    c2 = FreightContainer("CONT-002", "Naivasha", "Nairobi", 500.0, "Agriculture")
    c3 = FreightContainer("CONT-003", "Nairobi", "Naivasha", 2000.0, "Machinery")
    
    # Register containers
    optimizer.register_container(c1)
    optimizer.register_container(c2)
    optimizer.register_container(c3)
    
    # Estimate transit time
    transit_time = optimizer.estimate_transit_time("Nairobi", "Mombasa")
    print(f"Estimated transit time Nairobi to Mombasa: {transit_time:.2f} hours")
    
    # Optimize route
    optimized = optimizer.optimize_route([c1, c2, c3])
    print(f"Optimized route order: {[c.container_id for c in optimized]}")
    
    # Generate manifest
    manifest = optimizer.generate_manifest(optimized)
    print("Manifest:")
    print(manifest)
    
    # Verify integrity
    is_valid = optimizer.verify_integrity("CONT-001", c1.hash_signature)
    print(f"Integrity check for CONT-001: {is_valid}")
    
    # Tamper test
    c1.weight_kg = 1500.0  # Tamper with weight
    is_valid_tampered = optimizer.verify_integrity("CONT-001", c1.hash_signature)
    print(f"Integrity check after tampering: {is_valid_tampered}")
    
    assert is_valid == True
    assert is_valid_tampered == False
    print("All tests passed.")