"""
Nairobi High-Voltage Substation Transformer Dissolved Gas Analysis (DGA) Sentinel
-------------------------------------------------------------------------------
Monitors dissolved insulating oil gases (H2, CH4, C2H2, C2H4, C2H6, CO, CO2) across critical
Nairobi grid transformers using IEC 60599 gas ratio interpretation and Duval Triangle 1
polygon mapping to diagnose dielectric arcing, partial discharge, and thermal faults.

Author: Cortana Autonomous Evolutionary Architect
Operator: Michael Obiero (Nairobi, Kenya)
"""

import time
import math
import random
import logging
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, field
from enum import Enum

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("HVTransformerDGASentinel")

class FaultType(Enum):
    NORMAL = "NORMAL"
    PARTIAL_DISCHARGE = "PARTIAL_DISCHARGE"
    DISCHARGE_LOW_ENERGY = "DISCHARGE_LOW_ENERGY_D1"
    DISCHARGE_HIGH_ENERGY = "DISCHARGE_HIGH_ENERGY_D2"
    THERMAL_FAULT_LOW = "THERMAL_FAULT_T1_<300C"
    THERMAL_FAULT_MEDIUM = "THERMAL_FAULT_T2_300_700C"
    THERMAL_FAULT_HIGH = "THERMAL_FAULT_T3_>700C"
    MIXED_FAULT = "MIXED_THERMAL_ELECTRICAL_FAULT"

class AlarmSeverity(Enum):
    GREEN = "GREEN"
    YELLOW = "YELLOW"
    ORANGE = "ORANGE"
    RED = "RED"

@dataclass
class GasConcentration:
    h2: float   # Hydrogen (ppm)
    ch4: float  # Methane (ppm)
    c2h2: float # Acetylene (ppm)
    c2h4: float # Ethylene (ppm)
    c2h6: float # Ethane (ppm)
    co: float   # Carbon Monoxide (ppm)
    co2: float  # Carbon Dioxide (ppm)

@dataclass
class TransformerTelemetry:
    substation_id: str
    transformer_id: str
    timestamp: float
    oil_temp_c: float
    gases: GasConcentration
    oil_moisture_ppm: float

@dataclass
class DGAAnalysisResult:
    transformer_id: str
    substation_id: str
    fault_type: FaultType
    severity: AlarmSeverity
    duval_coordinates: Tuple[float, float, float]  # %CH4, %C2H4, %C2H2
    iec_ratios: Dict[str, float]
    health_index: float  # 0.0 (critical) to 100.0 (pristine)
    recommended_action: str

class HVTransformerDGASentinel:
    """
    Sentinel monitoring high-voltage transformer health across Nairobi's major substations
    to prevent catastrophic grid failure and safeguard Cortana operational resilience.
    """
    
    # Thresholds based on IEEE C57.104 & IEC 60599 standard limits (ppm)
    THRESHOLD_LIMITS = {
        'h2': 100.0,
        'ch4': 120.0,
        'c2h2': 1.0,
        'c2h4': 50.0,
        'c2h6': 65.0,
        'co': 350.0,
        'co2': 2500.0
    }

    def __init__(self, baseline_health: float = 100.0):
        self.baseline_health = baseline_health
        self.history: List[DGAAnalysisResult] = []

    def compute_iec_ratios(self, gases: GasConcentration) -> Dict[str, float]:
        """Calculates IEC 60599 gas ratios."""
        eps = 1e-6
        r1 = gases.c2h2 / (gases.c2h4 + eps)  # C2H2 / C2H4
        r2 = gases.ch4 / (gases.h2 + eps)      # CH4 / H2
        r3 = gases.c2h4 / (gases.c2h6 + eps)    # C2H4 / C2H6
        return {"r1_c2h2_c2h4": round(r1, 4), "r2_ch4_h2": round(r2, 4), "r3_c2h4_c2h6": round(r3, 4)}

    def calculate_duval_triangle1(self, gases: GasConcentration) -> Tuple[Tuple[float, float, float], FaultType]:
        """
        Computes Duval Triangle 1 percentages (%CH4, %C2H4, %C2H2) and determines fault classification.
        """
        total = gases.ch4 + gases.c2h4 + gases.c2h2
        if total <= 1e-4:
            return (0.0, 0.0, 0.0), FaultType.NORMAL

        p_ch4 = (gases.ch4 / total) * 100.0
        p_c2h4 = (gases.c2h4 / total) * 100.0
        p_c2h2 = (gases.c2h2 / total) * 100.0

        # Duval Triangle 1 decision logic
        if p_c2h2 >= 98.0:
            fault = FaultType.PARTIAL_DISCHARGE
        elif p_c2h2 >= 13.0 and p_c2h4 >= 50.0:
            fault = FaultType.DISCHARGE_HIGH_ENERGY
        elif p_c2h2 >= 13.0 and p_c2h4 < 50.0:
            fault = FaultType.DISCHARGE_LOW_ENERGY
        elif p_c2h2 < 4.0 and p_c2h4 >= 50.0:
            fault = FaultType.THERMAL_FAULT_HIGH
        elif p_c2h2 < 4.0 and 20.0 <= p_c2h4 < 50.0 and p_ch4 >= 50.0:
            fault = FaultType.THERMAL_FAULT_LOW
        elif p_c2h2 < 4.0 and 20.0 <= p_c2h4 < 50.0 and p_ch4 < 50.0:
            fault = FaultType.THERMAL_FAULT_MEDIUM
        elif p_c2h2 >= 4.0 and p_c2h4 < 50.0 and p_c2h2 < 13.0:
            fault = FaultType.MIXED_FAULT
        else:
            fault = FaultType.NORMAL

        return (round(p_ch4, 2), round(p_c2h4, 2), round(p_c2h2, 2)), fault

    def compute_health_index(self, gases: GasConcentration, temp: float) -> float:
        """Calculates normalized Health Index (0-100)."""
        score = 100.0
        for gas_name, limit in self.THRESHOLD_LIMITS.items():
            val = getattr(gases, gas_name, 0.0)
            if val > limit:
                excess_ratio = (val - limit) / limit
                score -= min(25.0, excess_ratio * 15.0)

        if temp > 90.0:
            score -= (temp - 90.0) * 1.5

        return max(0.0, round(score, 2))

    def analyze(self, telemetry: TransformerTelemetry) -> DGAAnalysisResult:
        """Processes telemetry input and generates diagnostic assessment."""
        ratios = self.compute_iec_ratios(telemetry.gases)
        duval_coords, fault = self.calculate_duval_triangle1(telemetry.gases)
        health_idx = self.compute_health_index(telemetry.gases, telemetry.oil_temp_c)

        if health_idx > 85.0 and fault == FaultType.NORMAL:
            severity = AlarmSeverity.GREEN
            action = "Normal operation. Maintain baseline DGA sampling frequency."
        elif health_idx > 65.0 and fault in (FaultType.NORMAL, FaultType.THERMAL_FAULT_LOW):
            severity = AlarmSeverity.YELLOW
            action = "Minor gas accumulation. Increase DGA sampling to bi-weekly and monitor load."
        elif health_idx > 40.0:
            severity = AlarmSeverity.ORANGE
            action = "Moderate fault detected. Schedule oil degassing, thermal imaging, and load reduction."
        else:
            severity = AlarmSeverity.RED
            action = "CRITICAL INSULATION FAULT! Trigger emergency grid rerouting & dispatch immediate field inspection."

        result = DGAAnalysisResult(
            transformer_id=telemetry.transformer_id,
            substation_id=telemetry.substation_id,
            fault_type=fault,
            severity=severity,
            duval_coordinates=duval_coords,
            iec_ratios=ratios,
            health_index=health_idx,
            recommended_action=action
        )
        self.history.append(result)
        logger.info(f"Analyzed {telemetry.transformer_id} @ {telemetry.substation_id}: {fault.value} (Health: {health_idx}%)")
        return result

def main():
    sentinel = HVTransformerDGASentinel()
    
    sample_telemetry = [
        TransformerTelemetry(
            substation_id="NBI_JUJA_RD_220KV",
            transformer_id="TX_01_JUJA",
            timestamp=time.time(),
            oil_temp_c=55.0,
            gases=GasConcentration(h2=15.0, ch4=20.0, c2h2=0.0, c2h4=10.0, c2h6=12.0, co=150.0, co2=1200.0),
            oil_moisture_ppm=10.0
        ),
        TransformerTelemetry(
            substation_id="NBI_EMBAKASI_220KV",
            transformer_id="TX_03_EMB",
            timestamp=time.time(),
            oil_temp_c=88.0,
            gases=GasConcentration(h2=80.0, ch4=140.0, c2h2=2.0, c2h4=180.0, c2h6=45.0, co=400.0, co2=2800.0),
            oil_moisture_ppm=22.0
        ),
        TransformerTelemetry(
            substation_id="NBI_RUARAKA_66KV",
            transformer_id="TX_02_RUA",
            timestamp=time.time(),
            oil_temp_c=98.5,
            gases=GasConcentration(h2=450.0, ch4=210.0, c2h2=85.0, c2h4=310.0, c2h6=30.0, co=650.0, co2=3500.0),
            oil_moisture_ppm=35.0
        )
    ]

    for t in sample_telemetry:
        res = sentinel.analyze(t)
        print(f"=== Substation: {res.substation_id} | TX: {res.transformer_id} ===")
        print(f"  Health Index: {res.health_index}% | Severity: {res.severity.value}")
        print(f"  Fault Type: {res.fault_type.value}")
        print(f"  Duval Coordinates (%CH4, %C2H4, %C2H2): {res.duval_coordinates}")
        print(f"  Action: {res.recommended_action}\n")

if __name__ == "__main__":
    main()
