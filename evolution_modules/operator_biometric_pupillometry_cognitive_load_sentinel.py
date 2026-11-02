"""
Operator Biometric Pupillometry & Cognitive Load Sentinel Module

Monitors operator Michael Obiero's ocular physiological telemetry—including pupil dilation 
variance, blink rate frequency, and saccadic velocity—to compute real-time cognitive 
load indices. Automatically throttles information density and visual feedback parameters 
to prevent mental fatigue and optimize decision velocity in Nairobi.
"""

import math
import time
import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
from collections import deque

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("PupillometrySentinel")


@dataclass
class PupilFrame:
    """Represents a single optical sensor sample frame for pupil dimensions and movement."""
    timestamp: float
    left_pupil_diameter_mm: float
    right_pupil_diameter_mm: float
    is_blink: bool
    saccade_velocity_deg_sec: float
    ambient_lux: float


@dataclass
class CognitiveLoadState:
    """Encapsulates evaluated operator cognitive state and system adaptation parameters."""
    timestamp: float
    pupil_dilation_index: float
    blink_frequency_per_min: float
    saccadic_fatigue_score: float
    composite_cognitive_load: float  # Scale 0.0 (idle/rested) to 1.0 (overload)
    recommended_alert_level: str
    ui_density_factor: float          # Scale 0.1 (minimal UI) to 1.0 (full UI)
    assistant_autonomy_level: float   # Scale 0.0 (manual confirmation) to 1.0 (autonomous)


class PupillometryAnalyzer:
    """Analyzes raw ocular metric streams to isolate baseline-corrected cognitive load dynamics."""

    def __init__(self, baseline_pupil_mm: float = 3.5, window_seconds: float = 60.0):
        self.baseline_pupil_mm = baseline_pupil_mm
        self.window_seconds = window_seconds
        self.frame_history: deque = deque()

    def add_sample(self, frame: PupilFrame) -> None:
        """Adds a frame sample to the sliding window history."""
        self.frame_history.append(frame)
        cutoff = frame.timestamp - self.window_seconds
        while self.frame_history and self.frame_history[0].timestamp < cutoff:
            self.frame_history.popleft()

    def compute_cognitive_metrics(self) -> Tuple[float, float, float]:
        """Computes pupil dilation anomaly, blink rate per min, and saccadic velocity index."""
        if not self.frame_history:
            return 0.0, 0.0, 0.0

        valid_frames = [f for f in self.frame_history if not f.is_blink]
        if not valid_frames:
            return 0.0, 0.0, 0.0

        # Luminance-compensated pupil diameter deviation
        avg_left = sum(f.left_pupil_diameter_mm for f in valid_frames) / len(valid_frames)
        avg_right = sum(f.right_pupil_diameter_mm for f in valid_frames) / len(valid_frames)
        mean_pupil = (avg_left + avg_right) / 2.0

        # Adjust for ambient lighting change (simplistic light reflex model)
        avg_lux = sum(f.ambient_lux for f in valid_frames) / len(valid_frames)
        lux_compensation = 0.005 * (avg_lux - 300.0)  # Standard indoor lux reference ~300
        compensated_pupil = mean_pupil + lux_compensation

        dilation_ratio = max(0.0, (compensated_pupil - self.baseline_pupil_mm) / self.baseline_pupil_mm)
        dilation_index = min(1.0, dilation_ratio * 2.5)  # Scale to 0-1 range

        # Blink frequency calculation
        total_time_min = (self.frame_history[-1].timestamp - self.frame_history[0].timestamp) / 60.0
        blink_count = sum(1 for f in self.frame_history if f.is_blink)
        blink_rate = blink_count / total_time_min if total_time_min > 0 else 12.0

        # Saccadic velocity deceleration (sign of mental fatigue)
        avg_saccade = sum(f.saccade_velocity_deg_sec for f in valid_frames) / len(valid_frames)
        # Normal baseline saccade ~400 deg/sec; <250 indicates heavy fatigue
        fatigue_score = max(0.0, min(1.0, (400.0 - avg_saccade) / 200.0))

        return dilation_index, blink_rate, fatigue_score


class OperatorCognitiveGovernor:
    """Governs Cortana interface feedback and decision delegation based on cognitive load."""

    def __init__(self, operator_id: str = "Michael Obiero"):
        self.operator_id = operator_id
        self.analyzer = PupillometryAnalyzer()
        self.last_state: Optional[CognitiveLoadState] = None

    def ingest_sensor_frame(self, frame: PupilFrame) -> CognitiveLoadState:
        """Processes an incoming ocular sensor frame and determines state adjustments."""
        self.analyzer.add_sample(frame)
        dilation, blink_rate, fatigue = self.analyzer.compute_cognitive_metrics()

        # Composite load model: weighted sum of pupil dilation and fatigue
        blink_anomaly = 0.0
        if blink_rate > 25.0:
            blink_anomaly = min(1.0, (blink_rate - 25.0) / 20.0)
        elif blink_rate < 6.0 and blink_rate > 0.0:
            blink_anomaly = min(1.0, (6.0 - blink_rate) / 6.0)

        composite_load = min(1.0, (0.5 * dilation) + (0.3 * fatigue) + (0.2 * blink_anomaly))

        # Adaptation rules
        if composite_load < 0.35:
            alert_level = "NORMAL"
            ui_density = 1.0
            autonomy_level = 0.20
        elif composite_load < 0.70:
            alert_level = "ELEVATED_FOCUS"
            ui_density = 0.70
            autonomy_level = 0.60
        else:
            alert_level = "HIGH_FATIGUE_OVERLOAD"
            ui_density = 0.30
            autonomy_level = 0.90

        state = CognitiveLoadState(
            timestamp=frame.timestamp,
            pupil_dilation_index=round(dilation, 4),
            blink_frequency_per_min=round(blink_rate, 2),
            saccadic_fatigue_score=round(fatigue, 4),
            composite_cognitive_load=round(composite_load, 4),
            recommended_alert_level=alert_level,
            ui_density_factor=round(ui_density, 2),
            assistant_autonomy_level=round(autonomy_level, 2)
        )
        self.last_state = state
        return state


if __name__ == "__main__":
    logger.info("Initializing Pupillometry Cognitive Load Sentinel Test Suite...")
    governor = OperatorCognitiveGovernor(operator_id="Michael Obiero")

    start_time = time.time()

    # Simulate 30 seconds of high workload pupil telemetry
    for i in range(60):
        t = start_time + (i * 0.5)
        frame = PupilFrame(
            timestamp=t,
            left_pupil_diameter_mm=4.2 + (0.01 * (i % 5)),
            right_pupil_diameter_mm=4.15 + (0.01 * (i % 5)),
            is_blink=(i % 12 == 0),
            saccade_velocity_deg_sec=280.0 - (i * 1.5),
            ambient_lux=310.0
        )
        state = governor.ingest_sensor_frame(frame)

    logger.info("Final State Analysis:")
    logger.info(f"Composite Cognitive Load: {state.composite_cognitive_load}")
    logger.info(f"Alert Level: {state.recommended_alert_level}")
    logger.info(f"UI Density Factor: {state.ui_density_factor}")
    logger.info(f"Assistant Autonomy Level: {state.assistant_autonomy_level}")

    assert state.composite_cognitive_load > 0.0, "Cognitive load calculation failed"
    assert state.recommended_alert_level in ["NORMAL", "ELEVATED_FOCUS", "HIGH_FATIGUE_OVERLOAD"]
    logger.info("Test Harness Execution Completed Successfully.")
