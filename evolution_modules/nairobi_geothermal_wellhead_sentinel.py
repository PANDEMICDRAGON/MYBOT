"""
Nairobi Geothermal Wellhead Telemetry & Grid Stability Sentinel

Monitors Olkaria-Nairobi geothermal steam field wellheads, enthalpy levels,
silica precipitation risk, and turbine frequency sync to safeguard power availability
for Michael Obiero's high-performance neural computing infrastructure.
"""

import json
import logging
import math
import random
import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("GeothermalSentinel")

@dataclass
class WellheadTelemetry:
    well_id: str
    pressure_bar: float
    temperature_celsius: float
    steam_mass_flow_kg_s: float
    enthalpy_kj_kg: float
    silica_concentration_ppm: float
    vibration_mm_s: float
    timestamp: float = field(default_factory=time.time)

@dataclass
class ThermalStabilityMetrics:
    total_steam_capacity_mw: float
    grid_frequency_hz: float
    scaling_risk_index: float
    brownout_probability: float
    recommended_bypass_ratio: float
    health_status: str

class NairobiGeothermalWellheadSentinel:
    """
    Autonomous sentinel monitoring Olkaria geothermal steam fields feeding the Nairobi power grid.
    Detects steam degradation, silica scaling, valve chatter, and frequency drift to maintain grid uptime.
    """

    CRITICAL_FREQ_LOW = 49.5  # Hz
    CRITICAL_FREQ_HIGH = 50.5 # Hz
    SILICA_SATURATION_THRESHOLD = 500.0  # ppm
    MAX_VIBRATION_THRESHOLD = 7.5  # mm/s

    def __init__(self, target_frequency_hz: float = 50.0):
        self.target_frequency_hz = target_frequency_hz
        self.wellheads: Dict[str, WellheadTelemetry] = {}
        self.telemetry_history: List[ThermalStabilityMetrics] = []

    def register_wellhead(self, telemetry: WellheadTelemetry) -> None:
        """Registers or updates a wellhead sensor reading."""
        self.wellheads[telemetry.well_id] = telemetry
        logger.debug(f"Updated wellhead telemetry for {telemetry.well_id}")

    def calculate_silica_scaling_risk(self, telemetry: WellheadTelemetry) -> float:
        """
        Calculates silica precipitation risk based on temperature and concentration.
        Silica solubility decreases rapidly with thermal drops across steam separators.
        """
        if telemetry.temperature_celsius <= 0:
            return 1.0
        solubility_limit = 200.0 + 2.5 * (telemetry.temperature_celsius - 100.0)
        risk = telemetry.silica_concentration_ppm / max(solubility_limit, 1.0)
        return min(max(risk, 0.0), 1.0)

    def analyze_grid_stability(self, current_grid_freq_hz: float) -> ThermalStabilityMetrics:
        """
        Analyzes composite geothermal output against current grid frequency.
        Returns thermal metrics and proactive grid mitigation actions.
        """
        if not self.wellheads:
            return ThermalStabilityMetrics(
                total_steam_capacity_mw=0.0,
                grid_frequency_hz=current_grid_freq_hz,
                scaling_risk_index=0.0,
                brownout_probability=1.0,
                recommended_bypass_ratio=0.0,
                health_status="CRITICAL_NO_TELEMETRY"
            )

        total_power_mw = 0.0
        scaling_risks = []
        vibration_anomalies = 0

        for well in self.wellheads.values():
            power_mw = (well.steam_mass_flow_kg_s * well.enthalpy_kj_kg * 0.35) / 1000.0
            total_power_mw += power_mw

            s_risk = self.calculate_silica_scaling_risk(well)
            scaling_risks.append(s_risk)

            if well.vibration_mm_s > self.MAX_VIBRATION_THRESHOLD:
                vibration_anomalies += 1

        avg_scaling_risk = sum(scaling_risks) / len(scaling_risks) if scaling_risks else 0.0
        freq_delta = abs(current_grid_freq_hz - self.target_frequency_hz)

        freq_penalty = min(freq_delta / 1.0, 1.0)
        scaling_penalty = avg_scaling_risk * 0.4
        vibe_penalty = (vibration_anomalies / len(self.wellheads)) * 0.3
        brownout_prob = min(max(0.3 * freq_penalty + scaling_penalty + vibe_penalty, 0.0), 1.0)

        if current_grid_freq_hz < self.CRITICAL_FREQ_LOW:
            bypass_ratio = 0.0
        elif avg_scaling_risk > 0.8:
            bypass_ratio = min((avg_scaling_risk - 0.8) * 2.5, 0.5)
        else:
            bypass_ratio = 0.05

        if brownout_prob > 0.6:
            status = "WARNING_HIGH_BROWNOUT_RISK"
        elif avg_scaling_risk > 0.7:
            status = "WARNING_SILICA_SCALING"
        elif freq_delta > 0.3:
            status = "DEGRADED_FREQUENCY_DRIFT"
        else:
            status = "NOMINAL_OPTIMAL"

        metrics = ThermalStabilityMetrics(
            total_steam_capacity_mw=round(total_power_mw, 2),
            grid_frequency_hz=current_grid_freq_hz,
            scaling_risk_index=round(avg_scaling_risk, 3),
            brownout_probability=round(brownout_prob, 3),
            recommended_bypass_ratio=round(bypass_ratio, 3),
            health_status=status
        )
        self.telemetry_history.append(metrics)
        return metrics

    def generate_mitigation_plan(self, metrics: ThermalStabilityMetrics) -> Dict[str, Any]:
        """Generates concrete control signals for Olkaria wellhead actuators and local workstation backup."""
        commands = []
        if metrics.health_status == "WARNING_HIGH_BROWNOUT_RISK":
            commands.append("ENGAGE_OPERATOR_BATTERY_RESERVE_STORAGE")
            commands.append("THROTTLE_NON_ESSENTIAL_WORKLOADS")
        if metrics.recommended_bypass_ratio > 0.1:
            commands.append(f"ADJUST_STEAM_BYPASS_VALVE_TO_{int(metrics.recommended_bypass_ratio * 100)}PCT")
        if metrics.scaling_risk_index > 0.75:
            commands.append("INJECT_ANTI_SCALANT_DISPERSANT_WELLHEAD_ALPHA")

        return {
            "timestamp": time.time(),
            "status": metrics.health_status,
            "power_output_mw": metrics.total_steam_capacity_mw,
            "actions": commands if commands else ["CONTINUE_NOMINAL_OPERATION"]
        }

if __name__ == "__main__":
    sentinel = NairobiGeothermalWellheadSentinel()
    
    w1 = WellheadTelemetry("OW-301", pressure_bar=18.5, temperature_celsius=210.0, steam_mass_flow_kg_s=45.0, enthalpy_kj_kg=2780.0, silica_concentration_ppm=420.0, vibration_mm_s=2.1)
    w2 = WellheadTelemetry("OW-702", pressure_bar=16.2, temperature_celsius=198.0, steam_mass_flow_kg_s=38.0, enthalpy_kj_kg=2740.0, silica_concentration_ppm=580.0, vibration_mm_s=8.2)
    
    sentinel.register_wellhead(w1)
    sentinel.register_wellhead(w2)
    
    metrics = sentinel.analyze_grid_stability(current_grid_freq_hz=49.6)
    plan = sentinel.generate_mitigation_plan(metrics)
    
    assert metrics.total_steam_capacity_mw > 0
    assert "status" in plan
    print(f"Test passed successfully! Status: {metrics.health_status}, Output: {metrics.total_steam_capacity_mw} MW")
