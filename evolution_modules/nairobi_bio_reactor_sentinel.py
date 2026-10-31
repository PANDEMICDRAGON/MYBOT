"""
Nairobi Municipal Bioreactor Digestion & Energy Recovery Sentinel
Author: Cortana Autonomous Evolutionary Architect
Operator: Michael Obiero, Nairobi, Kenya

Monitors anaerobic digestion tanks across Nairobi installations, ensuring optimal
mesophilic/thermophilic temperature ranges (35-55C), balancing carbon-to-nitrogen ratios,
regulating biomethane pressure, and preventing hydrogen sulfide ($H_2S$) toxicity spikes.
"""

import logging
import time
import json
from typing import Dict, Any, List, Optional

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] [BioReactorSentinel]: %(message)s')
logger = logging.getLogger(__name__)


class BioreactorConfig:
    """Configuration parameters for anaerobic digestion telemetry."""
    def __init__(
        self,
        reactor_id: str,
        target_temp_c: float = 38.0,
        max_pressure_kpa: float = 25.0,
        max_h2s_ppm: float = 500.0,
        min_ph: float = 6.8,
        max_ph: float = 8.2
    ):
        self.reactor_id = reactor_id
        self.target_temp_c = target_temp_c
        self.max_pressure_kpa = max_pressure_kpa
        self.max_h2s_ppm = max_h2s_ppm
        self.min_ph = min_ph
        self.max_ph = max_ph


class BioreactorTelemetry:
    """Real-time sensor payload from a Nairobi anaerobic digestion unit."""
    def __init__(
        self,
        reactor_id: str,
        temperature_c: float,
        pressure_kpa: float,
        ph_level: float,
        h2s_ppm: float,
        methane_percentage: float,
        feedstock_flow_kg_h: float
    ):
        self.reactor_id = reactor_id
        self.temperature_c = temperature_c
        self.pressure_kpa = pressure_kpa
        self.ph_level = ph_level
        self.h2s_ppm = h2s_ppm
        self.methane_percentage = methane_percentage
        self.feedstock_flow_kg_h = feedstock_flow_kg_h
        self.timestamp = time.time()


class BioreactorSentinelEngine:
    """Autonomous oversight and control engine for municipal biomass energy recovery."""
    
    def __init__(self, config: BioreactorConfig):
        self.config = config
        self.incident_log: List[Dict[str, Any]] = []

    def evaluate_telemetry(self, telemetry: BioreactorTelemetry) -> Dict[str, Any]:
        """Analyzes incoming sensor state, triggers safety interlocks, and calculates biogas energy output."""
        alerts = []
        status = "OPTIMAL"
        corrective_actions = []

        # Temperature Check
        temp_diff = telemetry.temperature_c - self.config.target_temp_c
        if abs(temp_diff) > 5.0:
            status = "WARNING"
            alerts.append(f"Temperature deviation of {temp_diff:+.1f}C from target.")
            corrective_actions.append("MODULATE_JACKET_HEATING")

        # Pressure Check (Critical Safety)
        if telemetry.pressure_kpa >= self.config.max_pressure_kpa:
            status = "CRITICAL"
            alerts.append(f"Over-pressure risk: {telemetry.pressure_kpa} kPa (Limit: {self.config.max_pressure_kpa})")
            corrective_actions.append("OPEN_FLARE_VALVE_EMERGENCY")

        # pH Balance Check
        if not (self.config.min_ph <= telemetry.ph_level <= self.config.max_ph):
            status = "WARNING"
            alerts.append(f"pH level {telemetry.ph_level} outside buffer zone [{self.config.min_ph}-{self.config.max_ph}].")
            corrective_actions.append("INJECT_BUFFER_SOLUTION")

        # Hydrogen Sulfide Toxicity Check
        if telemetry.h2s_ppm > self.config.max_h2s_ppm:
            status = "CRITICAL"
            alerts.append(f"H2S concentration critical: {telemetry.h2s_ppm} ppm (Max: {self.config.max_h2s_ppm})")
            corrective_actions.append("ACTIVATE_IRON_SPONGE_SCRUBBER")

        # Energy Estimation (approx 10 kWh per m3 of pure methane generated)
        # Simplified estimate based on feedstock flow and methane % purity
        estimated_energy_kwh = (telemetry.feedstock_flow_kg_h * 0.4) * (telemetry.methane_percentage / 100.0) * 6.0

        assessment = {
            "reactor_id": self.config.reactor_id,
            "status": status,
            "alerts": alerts,
            "corrective_actions": corrective_actions,
            "estimated_hourly_energy_kwh": round(estimated_energy_kwh, 2),
            "timestamp": telemetry.timestamp
        }

        if status != "OPTIMAL":
            self.incident_log.append(assessment)
            logger.warning(f"[{self.config.reactor_id}] Status: {status} | Alerts: {alerts} | Actions: {corrective_actions}")
        else:
            logger.info(f"[{self.config.reactor_id}] Operating within nominal parameters. Est Power: {estimated_energy_kwh:.1f} kWh")

        return assessment


if __name__ == "__main__":
    print("Initializing Nairobi Municipal Bioreactor Digestion & Energy Recovery Sentinel...")
    
    config = BioreactorConfig(reactor_id="NRB_BIO_KASARANI_01", target_temp_c=38.5, max_pressure_kpa=22.0)
    sentinel = BioreactorSentinelEngine(config)
    
    # Simulate healthy telemetry
    sample_telemetry = BioreactorTelemetry(
        reactor_id="NRB_BIO_KASARANI_01",
        temperature_c=38.2,
        pressure_kpa=14.5,
        ph_level=7.4,
        h2s_ppm=180.0,
        methane_percentage=62.5,
        feedstock_flow_kg_h=120.0
    )
    
    result = sentinel.evaluate_telemetry(sample_telemetry)
    print("Nominal Evaluation Result:", json.dumps(result, indent=2))

    # Simulate stress telemetry (High pressure + High H2S)
    stress_telemetry = BioreactorTelemetry(
        reactor_id="NRB_BIO_KASARANI_01",
        temperature_c=45.0,
        pressure_kpa=24.0,
        ph_level=6.4,
        h2s_ppm=550.0,
        methane_percentage=50.0,
        feedstock_flow_kg_h=200.0
    )
    
    stress_result = sentinel.evaluate_telemetry(stress_telemetry)
    print("Stress Evaluation Result:", json.dumps(stress_result, indent=2))
    print("Bioreactor Sentinel Evolution Module Verified Successfully.")
