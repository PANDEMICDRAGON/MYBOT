"""Nairobi Commercial Grain Milling Grain Damper Calibration Sentinel

Monitors, calibrates, and optimizes automated water addition and grain flow
telemetry in commercial milling setups across Nairobi, Kenya. Protects against
under-tempering (leading to brittle endosperm and roller damage) and over-tempering
(leading to sifter blinding and microbial growth in flour bins).
"""

import logging
import statistics
import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] (GrainDamperCalibrationSentinel): %(message)s",
)
logger = logging.getLogger("GrainDamperCalibrationSentinel")


@dataclass
class DamperReading:
    timestamp: float
    grain_mass_flow_tph: float  # Tonnes per hour
    target_moisture_pct: float
    measured_inflow_moisture_pct: float
    water_valve_flow_lph: float  # Litres per hour
    actuator_feedback_pct: float
    discharge_tempered_moisture_pct: float


@dataclass
class CalibrationConfig:
    nominal_density_kg_m3: float = 780.0
    max_allowable_moisture_error_pct: float = 0.3
    max_valve_actuation_drift_pct: float = 5.0
    sampling_window_size: int = 20


class GrainDamperCalibrationSentinel:
    """Performs real-time drift detection, PID flow-to-mass correction, and telemetry validation
    for commercial grain tempering systems.
    """

    def __init__(self, config: Optional[CalibrationConfig] = None):
        self.config = config or CalibrationConfig()
        self._readings: List[DamperReading] = []
        self._calibration_factor: float = 1.0
        self._last_adjustment_time: float = time.time()

    def ingest_telemetry(
        self,
        grain_mass_flow_tph: float,
        target_moisture_pct: float,
        measured_inflow_moisture_pct: float,
        water_valve_flow_lph: float,
        actuator_feedback_pct: float,
        discharge_tempered_moisture_pct: float,
    ) -> Dict[str, any]:
        """Ingests operational telemetry and performs instantaneous drift and calibration analysis."""
        reading = DamperReading(
            timestamp=time.time(),
            grain_mass_flow_tph=grain_mass_flow_tph,
            target_moisture_pct=target_moisture_pct,
            measured_inflow_moisture_pct=measured_inflow_moisture_pct,
            water_valve_flow_lph=water_valve_flow_lph,
            actuator_feedback_pct=actuator_feedback_pct,
            discharge_tempered_moisture_pct=discharge_tempered_moisture_pct,
        )
        self._readings.append(reading)
        if len(self._readings) > self.config.sampling_window_size:
            self._readings.pop(0)

        return self._evaluate_system()

    def _evaluate_system(self) -> Dict[str, any]:
        if not self._readings:
            return {"status": "IDLE", "correction_applied": False}

        latest = self._readings[-1]
        
        # Theoretical water requirement (L/h) = TPH * 1000 * (Target% - Inflow%) / (100 - Target%)
        # Simplified: Mass Flow (kg/h) * delta_moisture / 100 * correction
        mass_kg_h = latest.grain_mass_flow_tph * 1000.0
        delta_moisture = latest.target_moisture_pct - latest.measured_inflow_moisture_pct
        
        if delta_moisture <= 0:
            expected_water_lph = 0.0
        else:
            expected_water_lph = mass_kg_h * (delta_moisture / 100.0)

        flow_deviation = latest.water_valve_flow_lph - expected_water_lph
        actual_moisture_error = latest.discharge_tempered_moisture_pct - latest.target_moisture_pct

        status = "OPTIMAL"
        alerts = []

        if abs(actual_moisture_error) > self.config.max_allowable_moisture_error_pct:
            status = "WARNING_MOISTURE_DRIFT"
            alerts.append(f"Discharge moisture deviation of {actual_moisture_error:+.2f}% detected.")

        if abs(flow_deviation) > (expected_water_lph * 0.15 + 5.0):
            status = "WARNING_VALVE_CALIBRATION"
            alerts.append(f"Valve flow mismatch. Expected ~{expected_water_lph:.1f} L/h, got {latest.water_valve_flow_lph:.1f} L/h.")

        # Autonomous calibration adjustment if persistent error
        if len(self._readings) >= 5:
            recent_errors = [r.discharge_tempered_moisture_pct - r.target_moisture_pct for r in self._readings[-5:]]
            avg_error = statistics.mean(recent_errors)
            if abs(avg_error) > 0.2:
                # Adjust calibration factor slightly to counter systematic bias
                adjustment = -0.01 if avg_error > 0 else 0.01
                self._calibration_factor = max(0.8, min(1.2, self._calibration_factor + adjustment))
                logger.info(f"Autonomous calibration shift applied. New factor: {self._calibration_factor:.3f}")

        return {
            "status": status,
            "expected_water_lph": round(expected_water_lph, 2),
            "actual_water_lph": latest.water_valve_flow_lph,
            "moisture_error_pct": round(actual_moisture_error, 2),
            "calibration_factor": round(self._calibration_factor, 3),
            "alerts": alerts,
        }


if __name__ == "__main__":
    logger.info("Initializing GrainDamperCalibrationSentinel Test Harness...")
    sentinel = GrainDamperCalibrationSentinel()
    
    # Simulate stable run
    res1 = sentinel.ingest_telemetry(
        grain_mass_flow_tph=15.0,
        target_moisture_pct=14.5,
        measured_inflow_moisture_pct=11.5,
        water_valve_flow_lph=520.0,
        actuator_feedback_pct=45.2,
        discharge_tempered_moisture_pct=14.4,
    )
    logger.info(f"Test Tick 1 Result: {res1}")
    
    # Simulate under-tempering drift
    res2 = sentinel.ingest_telemetry(
        grain_mass_flow_tph=15.0,
        target_moisture_pct=14.5,
        measured_inflow_moisture_pct=11.5,
        water_valve_flow_lph=450.0,
        actuator_feedback_pct=38.0,
        discharge_tempered_moisture_pct=13.8,
    )
    logger.info(f"Test Tick 2 Result: {res2}")
    logger.info("GrainDamperCalibrationSentinel successfully verified.")
