import logging, random, threading, time
from dataclasses import dataclass
from typing import Callable, Dict, Optional

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

@dataclass
class DecoyEndpoint:
    """Metadata for a decoy service."""
    name: str
    address: str
    port: int
    payload_generator: Callable[[], str]
    last_rotated: float = 0.0

class AdaptiveDeceptionMesh:
    """Manages a collection of decoy endpoints that can be dynamically rotated and monitored to lure adversaries."""

    def __init__(self, rotation_interval: int = 300) -> None:
        """Initialize the mesh.

        Args:
            rotation_interval: Seconds between automatic decoy rotations.
        """
        self._decoys: Dict[str, DecoyEndpoint] = {}
        self._rotation_interval = rotation_interval
        self._stop_event = threading.Event()
        self._rotator_thread = threading.Thread(target=self._auto_rotate, daemon=True)
        self._rotator_thread.start()
        logger.info("AdaptiveDeceptionMesh started with rotation interval %s seconds.", rotation_interval)

    def register_decoy(self, decoy: DecoyEndpoint) -> None:
        """Add a new decoy to the mesh."""
        if decoy.name in self._decoys:
            raise ValueError(f"Decoy with name '{decoy.name}' already exists.")
        self._decoys[decoy.name] = decoy
        logger.info("Registered decoy %s at %s:%d.", decoy.name, decoy.address, decoy.port)

    def unregister_decoy(self, name: str) -> None:
        """Remove a decoy from the mesh."""
        if name not in self._decoys:
            raise KeyError(f"No decoy named '{name}'.")
        del self._decoys[name]
        logger.info("Unregistered decoy %s.", name)

    def process_traffic(self, src_ip: str, dst_port: int) -> Optional[str]:
        """Simulate processing inbound traffic. If the destination port matches a decoy, return the generated payload; otherwise return None.

        Args:
            src_ip: Source IP address of the traffic.
            dst_port: Destination port targeted.

        Returns:
            The decoy payload if a match is found, else None.
        """
        for decoy in self._decoys.values():
            if decoy.port == dst_port:
                payload = decoy.payload_generator()
                logger.warning(
                    "Decoy triggered: %s from %s:%d. Payload delivered.",
                    decoy.name,
                    src_ip,
                    dst_port,
                )
                return payload
        logger.debug("No decoy matched for traffic to port %d.", dst_port)
        return None

    def rotate_decoy(self, name: str) -> None:
        """Rotate the payload of a specific decoy."""
        decoy = self._decoys.get(name)
        if not decoy:
            raise KeyError(f"No decoy named '{name}'.")
        decoy.last_rotated = time.time()
        logger.info("Rotated decoy %s at %s:%d.", name, decoy.address, decoy.port)

    def _auto_rotate(self) -> None:
        """Background thread that rotates all decoys periodically."""
        while not self._stop_event.wait(self._rotation_interval):
            logger.info("Auto‑rotating all decoys.")
            for name in list(self._decoys.keys()):
                try:
                    self.rotate_decoy(name)
                except Exception as exc:
                    logger.exception("Failed to rotate decoy %s: %s", name, exc)

    def shutdown(self) -> None:
        """Cleanly stop the background rotator."""
        self._stop_event.set()
        self._rotator_thread.join()
        logger.info("AdaptiveDeceptionMesh shut down.")

def _sample_payload() -> str:
    """Generate a random JSON‑like payload."""
    sample = {"token": f"{random.getrandbits(128):032x}", "timestamp": int(time.time())}
    return str(sample)

if __name__ == "__main__":
    mesh = AdaptiveDeceptionMesh(rotation_interval=10)
    try:
        mesh.register_decoy(
            DecoyEndpoint(name="honeypot_ssh", address="10.0.0.5", port=22, payload_generator=_sample_payload)
        )
        mesh.register_decoy(
            DecoyEndpoint(name="honeypot_http", address="10.0.0.6", port=8080, payload_generator=_sample_payload)
        )
        for _ in range(3):
            payload = mesh.process_traffic(src_ip="192.168.1.100", dst_port=22)
            if payload:
                print(f"Received decoy payload: {payload}")
            time.sleep(5)
    finally:
        mesh.shutdown()
