import time
import logging
import random
from typing import Dict, List, Optional

logging.basicConfig(level=logging.INFO, format='[%(asctime)s] [FIBER_FAILOVER] %(levelname)s: %(message)s')
logger = logging.getLogger('NairobiFiberFailover')

class ISPPath:
    def __init__(self, name: str, gateway: str, base_latency_ms: float, cost_per_gb: float):
        self.name = name
        self.gateway = gateway
        self.base_latency_ms = base_latency_ms
        self.cost_per_gb = cost_per_gb
        self.is_healthy = True
        self.consecutive_failures = 0
        self.current_latency = base_latency_ms

class NairobiFiberFailoverEngine:
    def __init__(self):
        self.paths: List[ISPPath] = [
            ISPPath("Safaricom_FTTH_Primary", "192.168.100.1", 12.5, 2.0),
            ISPPath("Zuku_Cable_Backup", "192.168.200.1", 28.0, 1.5),
            ISPPath("Safaricom_4K_LTE_Failover", "10.0.0.1", 45.0, 5.0)
        ]
        self.active_path: Optional[ISPPath] = self.paths[0]
        logger.info("Initialized Nairobi-Nairobi ISP Failover Engine with %d paths.", len(self.paths))

    def probe_path(self, path: ISPPath) -> bool:
        # Simulate network probing with jitter and occasional packet drops
        jitter = random.uniform(-3.0, 15.0)
        simulated_latency = max(5.0, path.base_latency_ms + jitter)
        
        # Simulate sudden failure condition (1% chance per probe)
        if random.random() < 0.01:
            path.consecutive_failures += 1
            if path.consecutive_failures >= 3:
                path.is_healthy = False
            return False
        
        path.consecutive_failures = 0
        path.is_healthy = True
        path.current_latency = simulated_latency
        return True

    def evaluate_and_switch(self) -> str:
        logger.info("Evaluating health and latency across all ISP links...")
        for path in self.paths:
            self.probe_path(path)
        
        healthy_paths = [p for p in self.paths if p.is_healthy]
        
        if not healthy_paths:
            logger.critical("CRITICAL: All ISP paths down in Nairobi node! Activating emergency loopback.")
            return "EMERGENCY_LOOPBACK"
        
        # Select best path based on latency
        best_path = min(healthy_paths, key=lambda x: x.current_latency)
        
        if self.active_path != best_path:
            logger.warning(f"Switching active route from {self.active_path.name} to {best_path.name} (Latency: {best_path.current_latency:.2f}ms)")
            self.active_path = best_path
        else:
            logger.info(f"Active path {self.active_path.name} remains optimal ({self.active_path.current_latency:.2f}ms)")
            
        return self.active_path.name

    def get_status(self) -> Dict:
        return {
            "active_path": self.active_path.name if self.active_path else None,
            "paths": [
                {
                    "name": p.name,
                    "healthy": p.is_healthy,
                    "latency_ms": round(p.current_latency, 2)
                }
                for p in self.paths
            ]
        }

if __name__ == "__main__":
    engine = NairobiFiberFailoverEngine()
    for cycle in range(3):
        print(f"--- Cycle {cycle + 1} ---")
        selected = engine.evaluate_and_switch()
        print(f"Current Active Route: {selected}")
        print(engine.get_status())
        time.sleep(0.5)
