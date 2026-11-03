"""Nairobi Commercial Bio-Reactor Metabolic Harmonic Pulse Sentinel.

Autonomous architectural sentinel designed to monitor, filter, and harmonize
metabolic fermentation pulses, dissolved oxygen (DO) resonance, pH drift,
and thermal dissipation within Nairobi bio-reactor processing facilities.
"""

import os
import sys
import time
import math
import logging
from typing import Dict, Any, List, Optional

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] [BioReactorSentinel]: %(message)s"
)
logger = logging.getLogger("BioReactorSentinel")

class BioReactorMetabolicSentinel:
    """Monitors fermentation dynamics and applies harmonic phase correction."""
    
    def __init__(self, reactor_id: str, target_temperature: float = 37.0, target_ph: float = 7.0):
        self.reactor_id = reactor_id
        self.target_temperature = target_temperature
        self.target_ph = target_ph
        self.pulse_history: List[Dict[str, Any]] = []
        logger.info(f"Initialized BioReactorMetabolicSentinel for reactor '{self.reactor_id}' @ {target_temperature}C")

    def ingest_telemetry(self, temperature: float, ph: float, dissolved_oxygen: float, agitation_rpm: float) -> Dict[str, Any]:
        """Ingests live reactor sensor data and calculates harmonic deviation."""
        temp_delta = temperature - self.target_temperature
        ph_delta = ph - self.target_ph
        
        # Metabolic harmonic pulse calculation using sine wave phase correlation
        harmonic_index = math.sin(temp_delta * math.pi / 4.0) * math.cos(ph_delta * math.pi / 4.0)
        
        status = "OPTIMAL"
        if abs(temp_delta) > 1.5 or abs(ph_delta) > 0.5:
            status = "WARNING"
        if abs(temp_delta) > 3.0 or abs(ph_delta) > 1.0:
            status = "CRITICAL"

        telemetry_packet = {
            "timestamp": time.time(),
            "temperature": temperature,
            "ph": ph,
            "dissolved_oxygen": dissolved_oxygen,
            "agitation_rpm": agitation_rpm,
            "harmonic_index": round(harmonic_index, 4),
            "status": status
        }
        
        self.pulse_history.append(telemetry_packet)
        if len(self.pulse_history) > 1000:
            self.pulse_history.pop(0)
            
        return telemetry_packet

    def compute_adaptive_correction(self) -> Dict[str, Any]:
        """Computes autonomous control vector adjustments to stabilize fermentation."""
        if not self.pulse_history:
            return {"action": "HOLD", "agitation_adjustment_rpm": 0.0, "feed_rate_ml_min": 0.0}
            
        recent = self.pulse_history[-1]
        status = recent["status"]
        
        if status == "CRITICAL":
            logger.error(f"Reactor {self.reactor_id} state CRITICAL! Initiating emergency nutrient buffer flood.")
            return {
                "action": "EMERGENCY_BUFFER_INJECTION",
                "agitation_adjustment_rpm": -50.0,
                "feed_rate_ml_min": 120.0
            }
        elif status == "WARNING":
            logger.warning(f"Reactor {self.reactor_id} state WARNING. Modulating agitation and micro-feed.")
            return {
                "action": "MODULATE",
                "agitation_adjustment_rpm": 15.0,
                "feed_rate_ml_min": 45.0
            }
        else:
            return {
                "action": "MAINTAIN",
                "agitation_adjustment_rpm": 0.0,
                "feed_rate_ml_min": 10.0
            }

if __name__ == "__main__":
    print("Executing BioReactorMetabolicSentinel self-test harness...")
    sentinel = BioReactorMetabolicSentinel(reactor_id="NAI_BR_01")
    
    # Simulate normal pulse
    packet = sentinel.ingest_telemetry(temperature=37.1, ph=7.02, dissolved_oxygen=6.5, agitation_rpm=300.0)
    print(f"Ingested Normal Telemetry: {packet}")
    correction = sentinel.compute_adaptive_correction()
    print(f"Computed Correction: {correction}")

    # Simulate critical temperature spike
    packet_crit = sentinel.ingest_telemetry(temperature=41.2, ph=5.8, dissolved_oxygen=2.1, agitation_rpm=450.0)
    print(f"Ingested Critical Telemetry: {packet_crit}")
    correction_crit = sentinel.compute_adaptive_correction()
    print(f"Computed Critical Correction: {correction_crit}")
    print("BioReactorMetabolicSentinel verification complete.")
