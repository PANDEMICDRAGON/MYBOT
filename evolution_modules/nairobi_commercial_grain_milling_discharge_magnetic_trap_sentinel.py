"""Nairobi Commercial Grain Milling Discharge Magnetic Trap & Ferrous Sentinel.

Monitors magnetic flux, ferrous debris collection thresholds, and automated trap cleaning actuators
in commercial milling post-milling discharge streams to protect consumer products.
"""

import time
import logging
from typing import Dict, Any, List, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("MagneticTrapSentinel")



class MagneticTrapSentinel:
    """Monitors permanent neodymium magnetic traps and electromagnet purges on mill discharge lines."""

    def __init__(self, trap_id: str, nominal_flux_tesla: float = 1.25, max_ferrous_load_grams: float = 50.0):
        self.trap_id = trap_id
        self.nominal_flux_tesla = nominal_flux_tesla
        self.max_ferrous_load_grams = max_ferrous_load_grams
        self.current_flux = nominal_flux_tesla
        self.accumulated_ferrous_grams = 0.0
        self.purge_count = 0
        self.status = "ONLINE"

    def update_telemetry(self, flux_tesla: float, ferrous_delta_grams: float) -> Dict[str, Any]:
        """Ingests live sensor readings from the magnetic trap."""
        self.current_flux = flux_tesla
        self.accumulated_ferrous_grams += max(0.0, ferrous_delta_grams)
        
        alerts = []
        
        # Check flux degradation (demagnetization or high heat)
        flux_ratio = self.current_flux / self.nominal_flux_tesla
        if flux_ratio < 0.85:
            alerts.append(f"CRITICAL: Magnetic flux degraded to {self.current_flux}T ({flux_ratio:.1%} of nominal).")
            self.status = "FLUX_DEGRADED"
            
        # Check ferrous capacity threshold
        if self.accumulated_ferrous_grams >= self.max_ferrous_load_grams:
            alerts.append(f"WARNING: Ferrous load capacity reached ({self.accumulated_ferrous_grams}g). Purge required.")
            self.status = "PURGE_REQUIRED"
            
        return {
            "trap_id": self.trap_id,
            "status": self.status,
            "current_flux_tesla": self.current_flux,
            "accumulated_ferrous_grams": self.accumulated_ferrous_grams,
            "flux_health_ratio": round(flux_ratio, 3),
            "alerts": alerts,
            "timestamp": time.time()
        }

    def execute_purge(self) -> Dict[str, Any]:
        """Triggers pneumatic or solenoid discharge of collected ferrous debris."""
        logger.info(f"Executing automated purge for magnetic trap {self.trap_id}...")
        purged_amount = self.accumulated_ferrous_grams
        self.accumulated_ferrous_grams = 0.0
        self.purge_count += 1
        self.status = "ONLINE"
        return {
            "trap_id": self.trap_id,
            "action": "PURGE_COMPLETE",
            "purged_grams": purged_amount,
            "total_purges": self.purge_count,
            "timestamp": time.time()
        }


if __name__ == "__main__":
    logger.info("Initializing Nairobi Commercial Grain Milling Discharge Magnetic Trap Sentinel...")
    sentinel = MagneticTrapSentinel(trap_id="TRAP-DISCHARGE-04")
    
    # Simulate normal operation with minor accumulation
    telemetry_1 = sentinel.update_telemetry(flux_tesla=1.24, ferrous_delta_grams=12.5)
    logger.info(f"Telemetry 1: {telemetry_1}")
    
    # Simulate reaching threshold
    telemetry_2 = sentinel.update_telemetry(flux_tesla=1.22, ferrous_delta_grams=40.0)
    logger.info(f"Telemetry 2: {telemetry_2}")
    
    # Execute purge
    purge_res = sentinel.execute_purge()
    logger.info(f"Purge Result: {purge_res}")
    
    logger.info("Discharge Magnetic Trap Sentinel self-test completed successfully.")
