"""
Nairobi Electric Vehicle Battery Swap Hub Thermal Runaway & Cell State-of-Health Sentinel
========================================================================================
Monitors high-density Lithium-ion / LFP battery swap racks across Nairobi's Boda-Boda
and Matatu EV stations. Prevents cascading thermal runaway events by performing real-time
d/dT rate-of-change analysis, cell voltage imbalance tracking, and automated microgrid rack isolation.

Author: Cortana Autonomous Evolutionary Architect
Operator: Michael Obiero <Nairobi, Kenya>
"""

import math
import time
import json
import logging
import hashlib
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass, field, asdict
from enum import Enum

# Configure logger
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("ThermalRunawaySentinel")


class BatteryChemistry(str, Enum):
    LFP = "LFP"            # Lithium Iron Phosphate
    NMC = "NMC"            # Nickel Manganese Cobalt
    LTO = "LTO"            # Lithium Titanate Oxide


class IsolationStatus(str, Enum):
    NOMINAL = "NOMINAL"
    WARNING = "WARNING"
    THERMAL_CRITICAL = "THERMAL_CRITICAL"
    ISOLATED = "ISOLATED"
    QUENCH_TRIGGERED = "QUENCH_TRIGGERED"


@dataclass
class CellSensorReading:
    cell_id: str
    voltage_v: float
    current_a: float
    temperature_c: float
    internal_resistance_mOhm: float
    timestamp: float = field(default_factory=time.time)


@dataclass
class RackTelemetry:
    rack_id: str
    station_id: str
    chemistry: BatteryChemistry
    cells: List[CellSensorReading]
    ambient_temp_c: float
    cooling_flow_lmin: float
    timestamp: float = field(default_factory=time.time)


@dataclass
class ThermalAnalysisResult:
    rack_id: str
    station_id: str
    max_dT_dt_c_per_sec: float
    max_cell_temp_c: float
    voltage_imbalance_v: float
    runaway_risk_score: float  # 0.0 (safe) to 1.0 (imminent fire)
    status: IsolationStatus
    recommended_action: str
    telemetry_hash: str
    evaluated_at: float = field(default_factory=time.time)


class ThermalRunawaySentinel:
    """
    Real-time early thermal runaway detection and microgrid isolation engine
    for Nairobi EV battery swap infrastructure.
    """

    CRITICAL_TEMP_THRESHOLDS = {
        BatteryChemistry.LFP: 70.0,
        BatteryChemistry.NMC: 60.0,
        BatteryChemistry.LTO: 85.0,
    }

    CRITICAL_DT_DT = 1.5  # °C / second rate of change threshold

    def __init__(self, station_id: str, cooldown_period_sec: float = 30.0):
        self.station_id = station_id
        self.cooldown_period_sec = cooldown_period_sec
        self._history: Dict[str, List[CellSensorReading]] = {}
        self._isolation_log: List[ThermalAnalysisResult] = []

    def _compute_hash(self, telemetry: RackTelemetry) -> str:
        serialized = f"{telemetry.rack_id}:{telemetry.station_id}:{telemetry.timestamp}:{len(telemetry.cells)}"
        return hashlib.sha256(serialized.encode('utf-8')).hexdigest()[:16]

    def process_rack_telemetry(self, telemetry: RackTelemetry) -> ThermalAnalysisResult:
        """
        Processes multi-cell sensor telemetry to evaluate thermal stability and predict runaway risk.
        """
        if not telemetry.cells:
            return ThermalAnalysisResult(
                rack_id=telemetry.rack_id,
                station_id=self.station_id,
                max_dT_dt_c_per_sec=0.0,
                max_cell_temp_c=0.0,
                voltage_imbalance_v=0.0,
                runaway_risk_score=0.0,
                status=IsolationStatus.NOMINAL,
                recommended_action="No cells present in telemetry.",
                telemetry_hash=self._compute_hash(telemetry)
            )

        max_temp = max(cell.temperature_c for cell in telemetry.cells)
        min_v = min(cell.voltage_v for cell in telemetry.cells)
        max_v = max(cell.voltage_v for cell in telemetry.cells)
        voltage_imbalance = max_v - min_v

        max_dT_dt = 0.0

        for cell in telemetry.cells:
            cell_key = f"{telemetry.rack_id}_{cell.cell_id}"
            hist = self._history.get(cell_key, [])
            
            if hist:
                prev = hist[-1]
                dt = cell.timestamp - prev.timestamp
                if dt > 0.001:
                    dT = cell.temperature_c - prev.temperature_c
                    rate = dT / dt
                    if rate > max_dT_dt:
                        max_dT_dt = rate

            hist.append(cell)
            if len(hist) > 10:
                hist.pop(0)
            self._history[cell_key] = hist

        temp_threshold = self.CRITICAL_TEMP_THRESHOLDS.get(telemetry.chemistry, 65.0)
        temp_factor = min(1.0, max(0.0, (max_temp - 40.0) / (temp_threshold - 40.0)))
        rate_factor = min(1.0, max(0.0, max_dT_dt / self.CRITICAL_DT_DT))
        imbalance_factor = min(1.0, max(0.0, voltage_imbalance / 0.5))

        risk_score = (0.45 * temp_factor) + (0.40 * rate_factor) + (0.15 * imbalance_factor)
        risk_score = min(1.0, max(0.0, risk_score))

        if max_temp >= temp_threshold or max_dT_dt >= self.CRITICAL_DT_DT or risk_score >= 0.85:
            status = IsolationStatus.QUENCH_TRIGGERED
            action = f"CRITICAL: Initiate automatic nitrogen aerosol quench on Rack {telemetry.rack_id}. Disconnect relay."
        elif risk_score >= 0.60:
            status = IsolationStatus.THERMAL_CRITICAL
            action = f"WARNING: Isolate Rack {telemetry.rack_id} electrical contactors. Increase cooling flow to max."
        elif risk_score >= 0.35:
            status = IsolationStatus.WARNING
            action = f"CAUTION: High thermal drift detected on Rack {telemetry.rack_id}. Throttling charge current."
        else:
            status = IsolationStatus.NOMINAL
            action = f"Nominal operations on Rack {telemetry.rack_id}."

        result = ThermalAnalysisResult(
            rack_id=telemetry.rack_id,
            station_id=self.station_id,
            max_dT_dt_c_per_sec=round(max_dT_dt, 4),
            max_cell_temp_c=round(max_temp, 2),
            voltage_imbalance_v=round(voltage_imbalance, 4),
            runaway_risk_score=round(risk_score, 4),
            status=status,
            recommended_action=action,
            telemetry_hash=self._compute_hash(telemetry)
        )

        if status in [IsolationStatus.THERMAL_CRITICAL, IsolationStatus.QUENCH_TRIGGERED]:
            self._isolation_log.append(result)
            logger.error(f"THERMAL SENTINEL ALERT: {result.recommended_action} | Risk: {result.runaway_risk_score}")

        return result


if __name__ == "__main__":
    sentinel = ThermalRunawaySentinel(station_id="NRO_SWAP_HUB_CBD_01")
    
    now = time.time()
    mock_cells = [
        CellSensorReading(cell_id="c01", voltage_v=3.25, current_a=45.0, temperature_c=32.0, internal_resistance_mOhm=1.2, timestamp=now - 2.0),
        CellSensorReading(cell_id="c02", voltage_v=3.24, current_a=45.0, temperature_c=33.5, internal_resistance_mOhm=1.3, timestamp=now - 2.0),
        CellSensorReading(cell_id="c03", voltage_v=3.10, current_a=45.0, temperature_c=58.0, internal_resistance_mOhm=4.8, timestamp=now - 2.0),
    ]
    
    t1 = RackTelemetry(
        rack_id="RACK_ALPHA_04",
        station_id="NRO_SWAP_HUB_CBD_01",
        chemistry=BatteryChemistry.NMC,
        cells=mock_cells,
        ambient_temp_c=24.5,
        cooling_flow_lmin=12.0,
        timestamp=now - 2.0
    )
    
    _ = sentinel.process_rack_telemetry(t1)
    
    mock_cells_spike = [
        CellSensorReading(cell_id="c01", voltage_v=3.24, current_a=45.0, temperature_c=32.5, internal_resistance_mOhm=1.2, timestamp=now),
        CellSensorReading(cell_id="c02", voltage_v=3.23, current_a=45.0, temperature_c=34.0, internal_resistance_mOhm=1.3, timestamp=now),
        CellSensorReading(cell_id="c03", voltage_v=2.85, current_a=45.0, temperature_c=63.5, internal_resistance_mOhm=6.5, timestamp=now),
    ]
    
    t2 = RackTelemetry(
        rack_id="RACK_ALPHA_04",
        station_id="NRO_SWAP_HUB_CBD_01",
        chemistry=BatteryChemistry.NMC,
        cells=mock_cells_spike,
        ambient_temp_c=24.8,
        cooling_flow_lmin=12.0,
        timestamp=now
    )
    
    res = sentinel.process_rack_telemetry(t2)
    print(json.dumps(asdict(res), indent=2))
    assert res.status in [IsolationStatus.THERMAL_CRITICAL, IsolationStatus.QUENCH_TRIGGERED]
    print("Self-test completed successfully.")
