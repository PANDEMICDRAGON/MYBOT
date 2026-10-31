"""
Nairobi Commercial Solar-Powered Cold Storage & Phase-Change Thermal Battery Sentinel
Author: Cortana Autonomous Evolutionary Architect
Operator: Michael Obiero (Nairobi, Kenya)
"""

import time
import json
import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field, asdict

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')
logger = logging.getLogger("SolarColdStorageSentinel")

@dataclass
class ColdStorageTelemetry:
    device_id: str
    pv_voltage_v: float
    pv_current_a: float
    battery_soc_pct: float
    internal_temp_c: float
    pcm_latent_temp_c: float
    compressor_active: bool
    grid_available: bool
    timestamp: float = field(default_factory=time.time)

@dataclass
class OptimizationDecision:
    device_id: str
    action: str
    compressor_override: bool
    load_shedding_level: int
    target_temp_c: float
    reason: str
    timestamp: float = field(default_factory=time.time)

class SolarColdStorageSentinel:
    """
    Manages power balancing between KPLC grid, PV arrays, and phase-change thermal
    batteries for commercial cold rooms in Nairobi.
    """
    def __init__(self, device_id: str, target_storage_temp_c: float = -18.0):
        self.device_id = device_id
        self.target_storage_temp_c = target_storage_temp_c
        self.telemetry_history: List[ColdStorageTelemetry] = []
        self.decision_history: List[OptimizationDecision] = []

    def ingest_telemetry(self, data: Dict[str, Any]) -> ColdStorageTelemetry:
        telemetry = ColdStorageTelemetry(
            device_id=self.device_id,
            pv_voltage_v=float(data.get("pv_voltage_v", 0.0)),
            pv_current_a=float(data.get("pv_current_a", 0.0)),
            battery_soc_pct=float(data.get("battery_soc_pct", 100.0)),
            internal_temp_c=float(data.get("internal_temp_c", -18.0)),
            pcm_latent_temp_c=float(data.get("pcm_latent_temp_c", -20.0)),
            compressor_active=bool(data.get("compressor_active", False)),
            grid_available=bool(data.get("grid_available", True))
        )
        self.telemetry_history.append(telemetry);
        if len(self.telemetry_history) > 1000:
            self.telemetry_history.pop(0)
        return telemetry

    def evaluate_and_optimize(self, telemetry: ColdStorageTelemetry) -> OptimizationDecision:
        pv_power_w = telemetry.pv_voltage_v * telemetry.pv_current_a
        action = "MAINTAIN"
        compressor_override = telemetry.compressor_active
        load_shedding_level = 0
        target_temp = self.target_storage_temp_c
        reason = "Stable operating parameters."

        # Rule 1: Critical Battery State & No Grid
        if telemetry.battery_soc_pct < 20.0 and not telemetry.grid_available:
            compressor_override = False
            load_shedding_level = 3
            action = "SHUTDOWN_COMPRESSOR_RELY_ON_PCM"
            reason = "Critical battery depletion without KPLC grid. Relying entirely on Phase-Change Material latent cold storage."

        # Rule 2: Excess PV Generation & Low PCM Temp -> Super-Cooling
        elif pv_power_w > 3500.0 and telemetry.battery_soc_pct > 80.0:
            compressor_override = True
            target_temp = self.target_storage_temp_c - 3.0
            action = "SUPER_COOL_THERMAL_BATTERY"
            reason = "High PV generation surplus. Charging Phase-Change Material thermal battery to maximum capacity."

        # Rule 3: Grid Failure but Healthy Battery
        elif not telemetry.grid_available and telemetry.battery_soc_pct >= 50.0:
            compressor_override = True
            load_shedding_level = 1
            action = "BATTERY_BACKED_OPERATION"
            reason = "KPLC grid offline. Running compressors on solar battery bank with moderate load balancing."

        # Rule 4: High Internal Temp Spike
        elif telemetry.internal_temp_c > (self.target_storage_temp_c + 3.0):
            compressor_override = True
            action = "FORCE_COOLING_SPIKE"
            reason = "Internal storage temperature exceeded threshold. Forcing compressor run cycle."

        decision = OptimizationDecision(
            device_id=self.device_id,
            action=action,
            compressor_override=compressor_override,
            load_shedding_level=load_shedding_level,
            target_temp_c=target_temp,
            reason=reason
        )
        self.decision_history.append(decision)
        if len(self.decision_history) > 1000:
            self.decision_history.pop(0)

        logger.info(f"[{self.device_id}] Action: {action} | Reason: {reason}")
        return decision

if __name__ == "__main__":
    print("Initializing Nairobi Commercial Solar-Powered Cold Storage Sentinel...")
    sentinel = SolarColdStorageSentinel(device_id="NBO_COLD_STORE_ALPHA_01")
    sample_data = {
        "pv_voltage_v": 48.5,
        "pv_current_a": 75.0,
        "battery_soc_pct": 45.0,
        "internal_temp_c": -15.5,
        "pcm_latent_temp_c": -21.0,
        "compressor_active": True,
        "grid_available": False
    }
    tel = sentinel.ingest_telemetry(sample_data)
    dec = sentinel.evaluate_and_optimize(tel)
    print(json.dumps(asdict(dec), indent=2))
