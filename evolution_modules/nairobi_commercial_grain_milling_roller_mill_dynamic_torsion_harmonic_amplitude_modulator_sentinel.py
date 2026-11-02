"""
Nairobi Commercial Grain Milling Roller Mill Dynamic Torsion Harmonic Amplitude Modulator Sentinel
Written for Cortana Autonomous Evolutionary Architecture
Operator: Michael Obiero, Nairobi, Kenya
"""

import asyncio
import logging
import random
import time
from typing import Dict, Any, List

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("RollerMillHarmonicAmplitudeModulatorSentinel")


class RollerMillTorsionModulatorSentinel:
    """
    Monitors high-frequency torsional vibration amplitude and phase shifts on commercial
    roller mill drive shafts, applying dynamic counter-phase modulation to prevent mechanical fatigue.
    """

    def __init__(self, mill_id: str, baseline_amplitude_g: float = 0.45):
        self.mill_id = mill_id
        self.baseline_amplitude_g = baseline_amplitude_g
        self.active_modulation_db = 0.0
        self.status = "STANDBY"
        self._lock = asyncio.Lock()

    async def sample_torsional_telemetry(self) -> Dict[str, float]:
        """Simulates high-speed telemetry acquisition from shaft strain gauges and accelerometers."""
        await asyncio.sleep(0.05)
        # Inject occasional harmonic spikes simulating hard grain batches or belt slip
        jitter = random.gauss(0, 0.08)
        spike = random.choice([0.0, 0.0, 0.0, 0.65, 1.2]) if random.random() < 0.1 else 0.0
        current_amplitude = max(0.1, self.baseline_amplitude_g + jitter + spike)
        frequency_hz = 74.5 + random.gauss(0, 1.5)
        phase_deg = (time.time() * 360 * frequency_hz) % 360

        return {
            "timestamp": time.time(),
            "amplitude_g": round(current_amplitude, 4),
            "frequency_hz": round(frequency_hz, 2),
            "phase_deg": round(phase_deg, 2)
        }

    async def calculate_counter_phase_modulation(self, telemetry: Dict[str, float]) -> float:
        """Calculates required actuator feedback amplitude to cancel torsional surge."""
        async with self._lock:
            amp = telemetry["amplitude_g"]
            if amp > self.baseline_amplitude_g * 1.5:
                # Compute attenuation gain
                excess = amp - self.baseline_amplitude_g
                self.active_modulation_db = min(24.0, round(excess * 18.5, 2))
                self.status = "ACTIVE_MODULATION"
            else:
                self.active_modulation_db = max(0.0, self.active_modulation_db - 2.0)
                self.status = "OPTIMIZED" if self.active_modulation_db == 0.0 else "DECAYING"
            return self.active_modulation_db

    async def execute_sentinel_cycle(self) -> Dict[str, Any]:
        telemetry = await sample_torsional_telemetry_wrapper(self)
        mod_db = await self.calculate_counter_phase_modulation(telemetry)
        return {
            "mill_id": self.mill_id,
            "status": self.status,
            "telemetry": telemetry,
            "counter_modulation_db": mod_db
        }


async def sample_torsional_telemetry_wrapper(sentinel: RollerMillTorsionModulatorSentinel) -> Dict[str, float]:
    return await sentinel.sample_torsional_telemetry()


async def main():
    logger.info("Initializing Nairobi Commercial Grain Milling Roller Mill Dynamic Torsion Harmonic Amplitude Modulator Sentinel...")
    sentinel = RollerMillTorsionModulatorSentinel(mill_id="NAI-MILL-ALPHA-04")
    
    for cycle in range(5):
        report = await sentinel.execute_sentinel_cycle()
        logger.info(f"Cycle {cycle+1} Report: {report}")
        await asyncio.sleep(0.1)

    logger.info("Sentinel diagnostic sequence completed successfully.")


if __name__ == "__main__":
    asyncio.run(main())
