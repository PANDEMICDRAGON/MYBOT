import time
import logging
import statistics
from typing import Dict, List, Any, Optional

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')
logger = logging.getLogger("RollerMillControllerBusSentinel")

class RollerMillControllerBusSentinel:
    """
    Monitors industrial communication buses (e.g., Modbus RTU/TCP, CANopen) connecting
    central SCADA to distributed roller mill PLCs in Nairobi grain processing facilities.
    Tracks round-trip latency, frame error rates, and heartbeat packet intervals.
    """
    def __init__(self, mill_id: str, max_allowable_latency_ms: float = 150.0, max_error_rate: float = 0.02):
        self.mill_id = mill_id
        self.max_allowable_latency_ms = max_allowable_latency_ms
        self.max_error_rate = max_error_rate
        self.latency_history: List[float] = []
        self.packet_counts: Dict[str, int] = {"total": 0, "errors": 0, "timeouts": 0}
        self.last_heartbeat_timestamp = time.time()
        self.bus_status = "NOMINAL"
        logger.info(f"Initialized RollerMillControllerBusSentinel for mill {mill_id}")

    def record_poll(self, latency_ms: float, has_error: bool, is_timeout: bool = False) -> Dict[str, Any]:
        """
        Record metrics from a single bus polling cycle.
        """
        self.packet_counts["total"] += 1
        if has_error:
            self.packet_counts["errors"] += 1
        if is_timeout:
            self.packet_counts["timeouts"] += 1
            self.last_heartbeat_timestamp = time.time()
            return self._evaluate_status()

        self.latency_history.append(latency_ms)
        if len(self.latency_history) > 500:
            self.latency_history.pop(0)

        self.last_heartbeat_timestamp = time.time()
        return self._evaluate_status()

    def _evaluate_status(self) -> Dict[str, Any]:
        total = max(1, self.packet_counts["total"])
        error_count = self.packet_counts["errors"] + self.packet_counts["timeouts"]
        current_error_rate = error_count / total

        mean_latency = statistics.mean(self.latency_history) if self.latency_history else 0.0

        if current_error_rate > self.max_error_rate:
            self.bus_status = "CRITICAL_ERROR_RATE"
        elif mean_latency > self.max_allowable_latency_ms:
            self.bus_status = "DEGRADED_LATENCY"
        else:
            self.bus_status = "NOMINAL"

        return {
            "mill_id": self.mill_id,
            "status": self.bus_status,
            "mean_latency_ms": round(mean_latency, 2),
            "error_rate": round(current_error_rate, 4),
            "total_packets": self.packet_counts["total"],
            "timestamp": time.time()
        }

    def check_heartbeat_timeout(self, timeout_threshold_sec: float = 2.0) -> bool:
        """
        Check if the roller mill PLC controller has missed its heartbeat interval.
        """
        elapsed = time.time() - self.last_heartbeat_timestamp
        if elapsed > timeout_threshold_sec:
            self.packet_counts["timeouts"] += 1
            self.bus_status = "HEARTBEAT_TIMEOUT"
            logger.warning(f"[{self.mill_id}] PLC controller heartbeat timeout! Elapsed: {elapsed:.2f}s")
            return True
        return False

if __name__ == "__main__":
    sentinel = RollerMillControllerBusSentinel(mill_id="NAI-MILL-04")
    
    # Simulate polling frames
    for i in range(10):
        lat = 45.0 + (i * 2.5)
        err = (i == 7)
        res = sentinel.record_poll(latency_ms=lat, has_error=err)
        print(f"Poll {i}: Status -> {res['status']}, Latency -> {res['mean_latency_ms']}ms")
    
    # Test heartbeat timeout
    time.sleep(0.1)
    timed_out = sentinel.check_heartbeat_timeout(timeout_threshold_sec=0.05)
    print(f"Heartbeat timed out: {timed_out}, Status: {sentinel.bus_status}")
