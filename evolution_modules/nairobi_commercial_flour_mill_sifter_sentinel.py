"""Nairobi Commercial Flour Mill Plansifter & Particle Grading Biosafety Sentinel.

Protects industrial milling operations in Nairobi, Kenya by monitoring plansifter
oscillatory dynamics, sifting frame bearing temperatures, bolting cloth sieve
integrity, and fine flour dust particulate loading to prevent mechanical failure
and explosive deflagration risks.
"""

import asyncio
import logging
import random
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, List, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("FlourMillSifterSentinel")


@dataclass
class SifterTelemetry:
    """Real-time operational metrics from a commercial plansifter deck."""
    device_id: str
    deck_number: int
    oscillation_frequency_hz: float  # Nominal ~3.5 - 4.5 Hz
    bearing_temp_celsius: float
    sieve_differential_pressure_pa: float
    particle_purity_index: float     # 0.0 to 1.0
    dust_density_mg_m3: float        # Dust explosion hazard metric
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class FlourMillSifterSentinel:
    """Autonomous sentinel managing plansifter diagnostics and safety interlocks."""

    def __init__(self, warning_temp: float = 75.0, max_dust_density: float = 50.0):
        self.warning_temp = warning_temp
        self.max_dust_density = max_dust_density
        self.active_alerts: List[str] = []
        self.pneumatic_feed_diverted: bool = False

    def evaluate_telemetry(self, telemetry: SifterTelemetry) -> Dict[str, any]:
        """Evaluate plansifter telemetry and determine necessary safety actions."""
        status = "OPTIMAL"
        actions_taken = []

        # Check bearing temperature (Risk of seizure / fire)
        if telemetry.bearing_temp_celsius >= self.warning_temp:
            status = "CRITICAL_THERMAL_WARNING"
            actions_taken.append(f"Triggered emergency cooling & slow-down for Deck {telemetry.deck_number}")
            self.active_alerts.append(f"{telemetry.device_id} Deck {telemetry.deck_number} Overheat: {telemetry.bearing_temp_celsius}C")

        # Check dust density explosion risk (Dust deflagration threshold)
        if telemetry.dust_density_mg_m3 >= self.max_dust_density:
            status = "CRITICAL_DUST_EXPLOSION_HAZARD"
            self.pneumatic_feed_diverted = True
            actions_taken.append("Activated explosion suppression inert gas purge & diverted pneumatic grain feed.")
            self.active_alerts.append(f"{telemetry.device_id} High Dust Density: {telemetry.dust_density_mg_m3} mg/m3")

        # Check oscillation stability (Structural balance anomaly)
        if not (3.2 <= telemetry.oscillation_frequency_hz <= 4.8):
            if status == "OPTIMAL":
                status = "DEGRADED_VIBRATION"
            actions_taken.append(f"Warning: Oscillation frequency anomaly at {telemetry.oscillation_frequency_hz} Hz")

        return {
            "device_id": telemetry.device_id,
            "deck_number": telemetry.deck_number,
            "status": status,
            "pneumatic_feed_diverted": self.pneumatic_feed_diverted,
            "actions_taken": actions_taken,
            "timestamp": telemetry.timestamp
        }

    async def run_sentinel_loop(self, duration_cycles: int = 3) -> List[Dict[str, any]]:
        """Asynchronous monitoring loop simulating continuous mill oversight."""
        results = []
        for cycle in range(duration_cycles):
            telemetry = SifterTelemetry(
                device_id="MILL_NBO_IND_04",
                deck_number=cycle + 1,
                oscillation_frequency_hz=round(random.uniform(3.4, 4.6), 2),
                bearing_temp_celsius=round(random.uniform(62.0, 82.0), 1),
                sieve_differential_pressure_pa=round(random.uniform(250.0, 450.0), 1),
                particle_purity_index=round(random.uniform(0.92, 0.99), 3),
                dust_density_mg_m3=round(random.uniform(10.0, 55.0), 1)
            )
            report = self.evaluate_telemetry(telemetry)
            results.append(report)
            logger.info(f"[SifterSentinel] Evaluated Deck {telemetry.deck_number}: Status -> {report['status']}")
            await asyncio.sleep(0.1)
        return results


if __name__ == "__main__":
    sentinel = FlourMillSifterSentinel()
    loop = asyncio.get_event_loop()
    diagnostic_reports = loop.run_until_complete(sentinel.run_sentinel_loop(2))
    print("Flour Mill Sifter Sentinel Diagnostic Run Complete:", diagnostic_reports)
