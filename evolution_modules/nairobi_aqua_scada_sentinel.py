"""
Nairobi Municipal Water Treatment SCADA & Chemical Dosing Sentinel
Author: Cortana, Autonomous Evolutionary Architect
Operator: Michael Obiero, Nairobi, Kenya

Provides automated supervision, quality control, chemical dosing adjustment, and
emergency shutoff protocols for Nairobi water treatment plants and borehole stations.
"""

import logging
import time
import statistics
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] [AQUA_SCADA]: %(message)s')
logger = logging.getLogger("AquaScadaSentinel")

@dataclass
class WaterQualityMetrics:
    station_id: str
    turbidity_ntu: float
    ph_level: float
    chlorine_mg_l: float
    flow_rate_m3_hr: float
    timestamp: float = field(default_factory=time.time)

@dataclass
class DosingAction:
    station_id: str
    coagulant_ppm: float
    chlorine_pump_hz: float
    valve_status: str
    anomaly_detected: bool
    reason: str

class NairobiAquaScadaSentinel:
    """
    Supervisory Control and Data Acquisition (SCADA) anomaly detector and dosing optimizer
    tailored to Nairobi municipal water supply standards (KEBS specifications).
    """
    
    # KEBS Potability Guidelines
    TURBIDITY_MAX_NTU = 5.0
    PH_MIN = 6.5
    PH_MAX = 8.5
    CHLORINE_MIN_MG_L = 0.2
    CHLORINE_MAX_MG_L = 1.0
    
    def __init__(self, station_ids: Optional[List[str]] = None):
        self.station_ids = station_ids or ["NRB_KABETE_01", "NRB_NORTH_SUK_02", "NRB_LANGATA_03"]
        self.metrics_history: Dict[str, List[WaterQualityMetrics]] = {sid: [] for sid in self.station_ids}
        logger.setItem = logger.info
        logger.info(f"Initialized NairobiAquaScadaSentinel covering stations: {self.station_ids}")

    def ingest_telemetry(self, metrics: WaterQualityMetrics) -> DosingAction:
        """
        Ingests real-time sensor data, evaluates KEBS potability, computes optimal
        chemical dosing, and determines valve safety status.
        """
        if metrics.station_id not in self.metrics_history:
            self.metrics_history[metrics.station_id] = []
            
        history = self.metrics_history[metrics.station_id]
        history.append(metrics)
        if len(history) > 100:
            history.pop(0)
            
        anomaly_flags = []
        valve_status = "OPEN"
        coagulant_ppm = 15.0  # Baseline standard dose
        chlorine_pump_hz = 35.0 # Baseline frequency
        
        # Check Turbidity
        if metrics.turbidity_ntu > self.TURBIDITY_MAX_NTU:
            anomaly_flags.append(f"High Turbidity ({metrics.turbidity_ntu} NTU > {self.TURBIDITY_MAX_NTU})")
            coagulant_ppm = min(50.0, 15.0 + (metrics.turbidity_ntu * 2.5))
            if metrics.turbidity_ntu > 20.0:
                valve_status = "EMERGENCY_SHUTOFF"
                
        # Check pH
        if not (self.PH_MIN <= metrics.ph_level <= self.PH_MAX):
            anomaly_flags.append(f"Out-of-range pH ({metrics.ph_level})")
            if metrics.ph_level < self.PH_MIN:
                valve_status = "EMERGENCY_SHUTOFF"
                
        # Check Chlorine Residual
        if metrics.chlorine_mg_l < self.CHLORINE_MIN_MG_L:
            anomaly_flags.append(f"Low Chlorine Residual ({metrics.chlorine_mg_l} mg/L)")
            chlorine_pump_hz = 50.0 # Boost dosage
        elif metrics.chlorine_mg_l > self.CHLORINE_MAX_MG_L:
            anomaly_flags.append(f"High Chlorine Residual ({metrics.chlorine_mg_l} mg/L)")
            chlorine_pump_hz = 20.0 # Reduce dosage
            
        is_anomaly = len(anomaly_flags) > 0
        reason = "; ".join(anomaly_flags) if is_anomaly else "Water quality optimal. Parameters within KEBS limits."
        
        if is_anomaly:
            logger.warning(f"[{metrics.station_id}] Anomaly detected: {reason} | Action: {valve_status}")
        else:
            logger.info(f"[{metrics.station_id}] Telemetry normal. Coagulant: {coagulant_ppm}ppm, Cl Hz: {chlorine_pump_hz}")
            
        return DosingAction(
            station_id=metrics.station_id,
            coagulant_ppm=coagulant_ppm,
            chlorine_pump_hz=chlorine_pump_hz,
            valve_status=valve_status,
            anomaly_detected=is_anomaly,
            reason=reason
        )

    def get_station_summary(self, station_id: str) -> Dict[str, Any]:
        """Returns statistical summary of historical telemetry for a station."""
        history = self.metrics_history.get(station_id, [])
        if not history:
            return {"status": "no_data"}
            
        turbidities = [m.turbidity_ntu for m in history]
        phs = [m.ph_level for m in history]
        chlorines = [m.chlorine_mg_l for m in history]
        
        return {
            "station_id": station_id,
            "samples_count": len(history),
            "avg_turbidity_ntu": statistics.mean(turbidities),
            "avg_ph": statistics.mean(phs),
            "avg_chlorine_mg_l": statistics.mean(chlorines),
            "last_update": history[-1].timestamp
        }

if __name__ == "__main__":
    print("Initializing Nairobi Aqua SCADA Sentinel Unit Test...")
    sentinel = NairobiAquaScadaSentinel()
    
    # Test normal telemetry
    normal_sample = WaterQualityMetrics(
        station_id="NRB_KABETE_01",
        turbidity_ntu=2.1,
        ph_level=7.2,
        chlorine_mg_l=0.5,
        flow_rate_m3_hr=450.0
    )
    action = sentinel.ingest_telemetry(normal_sample)
    assert action.anomaly_detected is False
    assert action.valve_status == "OPEN"
    
    # Test anomalous high turbidity telemetry
    flood_sample = WaterQualityMetrics(
        station_id="NRB_KABETE_01",
        turbidity_ntu=25.5,
        ph_level=6.8,
        chlorine_mg_l=0.1,
        flow_rate_m3_hr=300.0
    )
    action_flood = sentinel.ingest_telemetry(flood_sample)
    assert action_flood.anomaly_detected is True
    assert action_flood.valve_status == "EMERGENCY_SHUTOFF"
    
    summary = sentinel.get_station_summary("NRB_KABETE_01")
    print(f"Station Summary Test Passed: {summary}")
    print("Nairobi Aqua SCADA Sentinel Operational.")
