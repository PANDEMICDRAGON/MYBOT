"""
Multi-WAN Bonding Router & Dynamic QoS Failover Engine
Targeted for East Africa / Nairobi & Kitengela ISP infrastructure (Safaricom, Airtel, Zuku, Starlink).
"""

import asyncio
import time
import random
import logging
import json
from enum import Enum, auto
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field

# Logging configuration
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("MultiWANBondingRouter")

class PacketPriority(Enum):
    CRITICAL = auto()  # Duplicate across top N active links
    HIGH = auto()      # Lowest latency link
    NORMAL = auto()    # Balanced load sharing
    LOW = auto()       # Cheapest / background link

class WANStatus(Enum):
    HEALTHY = "HEALTHY"
    DEGRADED = "DEGRADED"
    OFFLINE = "OFFLINE"

@dataclass
class InterfaceMetric:
    interface_id: str
    name: str
    latency_ms: float = 20.0
    jitter_ms: float = 2.0
    packet_loss_pct: float = 0.0
    cost_score: int = 1  # 1 = cheap, 10 = expensive
    status: WANStatus = WANStatus.HEALTHY
    bytes_sent: int = 0
    packets_routed: int = 0
    last_ping_time: float = field(default_factory=time.time)

@dataclass
class TelemetryPayload:
    payload_id: str
    data: Dict[str, Any]
    priority: PacketPriority
    timestamp: float = field(default_factory=time.time)

class MultiWANBondingRouter:
    """
    Dynamic Multi-WAN Router that intelligently bonds and fails over between
    available network connections (e.g., Safaricom Fiber, Airtel 5G, Starlink).
    """

    def __init__(self, loss_threshold_pct: float = 5.0, latency_threshold_ms: float = 150.0):
        self.interfaces: Dict[str, InterfaceMetric] = {}
        self.loss_threshold_pct = loss_threshold_pct
        self.latency_threshold_ms = latency_threshold_ms
        self._lock = asyncio.Lock()

    def register_interface(self, interface_id: str, name: str, cost_score: int = 1) -> None:
        """Register a new WAN interface into the bonding pool."""
        self.interfaces[interface_id] = InterfaceMetric(
            interface_id=interface_id,
            name=name,
            cost_score=cost_score
        )
        logger.info(f"Registered WAN interface: {name} [{interface_id}] (Cost Tier: {cost_score})")

    def update_metrics(self, interface_id: str, latency_ms: float, jitter_ms: float, packet_loss_pct: float) -> None:
        """Update real-time health telemetry for a given interface."""
        if interface_id not in self.interfaces:
            raise KeyError(f"Interface {interface_id} not registered.")

        iface = self.interfaces[interface_id]
        iface.latency_ms = latency_ms
        iface.jitter_ms = jitter_ms
        iface.packet_loss_pct = packet_loss_pct
        iface.last_ping_time = time.time()

        # Evaluate status
        if packet_loss_pct >= 25.0 or latency_ms > 500.0:
            iface.status = WANStatus.OFFLINE
        elif packet_loss_pct >= self.loss_threshold_pct or latency_ms > self.latency_threshold_ms:
            iface.status = WANStatus.DEGRADED
        else:
            iface.status = WANStatus.HEALTHY

        logger.debug(f"Updated {iface.name}: Latency={latency_ms:.1f}ms, Loss={packet_loss_pct:.1f}%, Status={iface.status.value}")

    def select_routes(self, priority: PacketPriority) -> List[str]:
        """Determine optimal interface(s) based on packet priority and WAN health."""
        active_ifaces = [iface for iface in self.interfaces.values() if iface.status != WANStatus.OFFLINE]

        if not active_ifaces:
            logger.error("No active WAN interfaces available for routing!")
            return []

        healthy_ifaces = [iface for iface in active_ifaces if iface.status == WANStatus.HEALTHY]
        candidate_pool = healthy_ifaces if healthy_ifaces else active_ifaces

        candidate_pool.sort(key=lambda x: (x.latency_ms, x.packet_loss_pct, x.cost_score))

        if priority == PacketPriority.CRITICAL:
            # Multi-path duplication across top active interfaces (max 2)
            selected = [iface.interface_id for iface in candidate_pool[:2]]
            logger.info(f"CRITICAL payload duplicate dispatch across WAN links: {selected}")
            return selected

        elif priority == PacketPriority.HIGH:
            # Absolute best latency link
            best = candidate_pool[0]
            return [best.interface_id]

        elif priority == PacketPriority.NORMAL:
            # Least utilized / lowest cost among top candidates
            candidate_pool.sort(key=lambda x: (x.packets_routed, x.latency_ms))
            return [candidate_pool[0].interface_id]

        elif priority == PacketPriority.LOW:
            # Best cost efficiency
            candidate_pool.sort(key=lambda x: (x.cost_score, x.latency_ms))
            return [candidate_pool[0].interface_id]

        return [candidate_pool[0].interface_id]

    async def dispatch_payload(self, payload: TelemetryPayload) -> Dict[str, bool]:
        """Dispatch a telemetry payload over selected bonded routes."""
        async with self._lock:
            routes = self.select_routes(payload.priority)

        if not routes:
            return {"status": False, "reason": "No route available"}

        dispatch_results = {}
        payload_bytes = len(str(payload.data).encode("utf-8"))

        for iface_id in routes:
            iface = self.interfaces[iface_id]
            iface.bytes_sent += payload_bytes
            iface.packets_routed += 1
            
            success = random.random() * 100 > iface.packet_loss_pct
            dispatch_results[iface_id] = success
            status_str = "SUCCESS" if success else "FAILED"
            logger.info(f"Payload [{payload.payload_id}] routed via {iface.name} ({iface_id}) -> {status_str}")

        return dispatch_results

    def get_telemetry_summary(self) -> Dict[str, Any]:
        """Generate full status report for all bonded links."""
        return {
            "total_interfaces": len(self.interfaces),
            "interfaces": {
                iface_id: {
                    "name": iface.name,
                    "status": iface.status.value,
                    "latency_ms": iface.latency_ms,
                    "jitter_ms": iface.jitter_ms,
                    "packet_loss_pct": iface.packet_loss_pct,
                    "cost_score": iface.cost_score,
                    "packets_routed": iface.packets_routed,
                    "bytes_sent": iface.bytes_sent
                }
                for iface_id, iface in self.interfaces.items()
            }
        }

if __name__ == "__main__":
    async def main():
        router = MultiWANBondingRouter()

        # Register Kitengela / Nairobi WAN Interfaces
        router.register_interface("safaricom_fiber", "Safaricom Home Fiber (Kitengela)", cost_score=1)
        router.register_interface("airtel_5g", "Airtel 5G Mobile (Nairobi CBD)", cost_score=3)
        router.register_interface("starlink_sat", "Starlink Satellite Backup", cost_score=5)

        # Simulate dynamic metrics update
        router.update_metrics("safaricom_fiber", latency_ms=18.5, jitter_ms=1.2, packet_loss_pct=0.5)
        router.update_metrics("airtel_5g", latency_ms=35.0, jitter_ms=4.8, packet_loss_pct=2.0)
        router.update_metrics("starlink_sat", latency_ms=65.0, jitter_ms=12.0, packet_loss_pct=0.0)

        # Critical Payload Dispatch (Should duplicate over Safaricom + Airtel)
        critical_data = TelemetryPayload(
            payload_id="PAYLOAD_CRIT_001",
            data={"command": "EMERGENCY_OPERATOR_ALERT", "location": "Kitengela"},
            priority=PacketPriority.CRITICAL
        )
        res_crit = await router.dispatch_payload(critical_data)
        print("Critical Dispatch Result:", res_crit)

        # Simulate Safaricom Fiber degradation/failure
        logger.warning("Simulating Safaricom Fiber connection failure in Kitengela...")
        router.update_metrics("safaricom_fiber", latency_ms=620.0, jitter_ms=85.0, packet_loss_pct=40.0)

        # High Priority Payload Dispatch (Should automatically switch to Airtel 5G)
        high_data = TelemetryPayload(
            payload_id="PAYLOAD_HIGH_002",
            data={"telemetry": "SYSTEM_THERMAL_METRICS"},
            priority=PacketPriority.HIGH
        )
        res_high = await router.dispatch_payload(high_data)
        print("High Priority Dispatch Result:", res_high)

        # Low Priority Payload Dispatch (Should route via lowest cost healthy link)
        low_data = TelemetryPayload(
            payload_id="PAYLOAD_LOW_003",
            data={"log": "BACKGROUND_DISK_CLEANUP"},
            priority=PacketPriority.LOW
        )
        res_low = await router.dispatch_payload(low_data)
        print("Low Priority Dispatch Result:", res_low)

        summary = router.get_telemetry_summary()
        print("\n=== Multi-WAN Telemetry Summary ===")
        print(json.dumps(summary, indent=2))

    asyncio.run(main())
