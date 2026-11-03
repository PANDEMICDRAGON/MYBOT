"""
Operator Ocular Micro-Saccade & Fixation Trajectory Cognitive Intent Decoding Engine.

Provides real-time high-frequency (250Hz+) gaze tracking analysis, isolating micro-saccades
(amplitude < 1.0 degree) and fixation drift trajectories to predict operator focus shifts,
cognitive workload, visual attention entropy, and pre-motor decision vectors for Michael Obiero in Nairobi.
"""

from dataclasses import dataclass, field
from enum import Enum
import math
import time
from typing import Dict, List, Optional, Tuple, Any


class CognitiveIntentType(Enum):
    FOCUS_TARGET_LOCK = "FOCUS_TARGET_LOCK"
    DEEP_INSPECTION = "DEEP_INSPECTION"
    SYSTEM_OVERRIDE_PREPARATION = "SYSTEM_OVERRIDE_PREPARATION"
    VISUAL_SEARCH_EXPLORATION = "VISUAL_SEARCH_EXPLORATION"
    COGNITIVE_FATIGUE_DRIFT = "COGNITIVE_FATIGUE_DRIFT"


@dataclass
class SaccadeSample:
    timestamp_ms: float
    gaze_x: float
    gaze_y: float
    pupil_diameter_mm: float
    angular_velocity_deg_s: float = 0.0
    amplitude_deg: float = 0.0


@dataclass
class FixationCluster:
    cluster_id: str
    centroid_x: float
    centroid_y: float
    duration_ms: float
    microsaccade_count: int
    focus_target_id: Optional[str] = None


class OcularMicrosaccadeIntentDecoder:
    """
    Decodes high-frequency ocular micro-saccades and fixation trajectories to extract
    operator intent prior to manual motor interaction.
    """

    def __init__(
        self,
        velocity_threshold_deg_s: float = 30.0,
        microsaccade_max_amplitude_deg: float = 1.0,
        sampling_rate_hz: int = 250
    ):
        self.velocity_threshold = velocity_threshold_deg_s
        self.microsaccade_max_amplitude = microsaccade_max_amplitude_deg
        self.sampling_rate = sampling_rate_hz
        self.fixation_history: List[FixationCluster] = []

    def compute_kinematics(self, samples: List[SaccadeSample]) -> List[SaccadeSample]:
        """Calculates instantaneous angular velocity and amplitude across gaze stream."""
        if len(samples) < 2:
            return samples

        processed = []
        for i in range(len(samples)):
            sample = samples[i]
            if i == 0:
                processed.append(sample)
                continue
            prev = samples[i - 1]
            dt = (sample.timestamp_ms - prev.timestamp_ms) / 1000.0
            if dt <= 0:
                dt = 1.0 / self.sampling_rate

            dx = sample.gaze_x - prev.gaze_x
            dy = sample.gaze_y - prev.gaze_y
            dist_px = math.sqrt(dx * dx + dy * dy)
            # Assuming standard screen distance and scale: 1 degree approx 35 pixels
            amp_deg = dist_px / 35.0
            vel_deg_s = amp_deg / dt

            updated = SaccadeSample(
                timestamp_ms=sample.timestamp_ms,
                gaze_x=sample.gaze_x,
                gaze_y=sample.gaze_y,
                pupil_diameter_mm=sample.pupil_diameter_mm,
                angular_velocity_deg_s=vel_deg_s,
                amplitude_deg=amp_deg
            )
            processed.append(updated)
        return processed

    def filter_microsaccades(self, samples: List[SaccadeSample]) -> List[SaccadeSample]:
        """Filters high-velocity rapid ballistic movements under amplitude threshold."""
        kinematic_samples = self.compute_kinematics(samples)
        microsaccades = [
            s for s in kinematic_samples
            if s.angular_velocity_deg_s >= self.velocity_threshold and s.amplitude_deg <= self.microsaccade_max_amplitude
        ]
        return microsaccades

    def detect_fixations(
        self,
        samples: List[SaccadeSample],
        ui_bounds: Dict[str, Tuple[float, float, float, float]]
    ) -> List[FixationCluster]:
        """Clusters gaze samples into fixations and maps to UI target bounding boxes (x1, y1, x2, y2)."""
        if not samples:
            return []

        clusters: List[FixationCluster] = []
        current_batch: List[SaccadeSample] = []
        microsaccade_counter = 0

        for s in samples:
            if not current_batch:
                current_batch.append(s)
                continue

            last = current_batch[-1]
            dist = math.sqrt((s.gaze_x - last.gaze_x)**2 + (s.gaze_y - last.gaze_y)**2)
            if dist < 20.0:  # Fixation dispersion threshold in pixels
                current_batch.append(s)
                if s.angular_velocity_deg_s >= self.velocity_threshold and s.amplitude_deg <= self.microsaccade_max_amplitude:
                    microsaccade_counter += 1
            else:
                if len(current_batch) >= 5:  # At least 20ms duration at 250Hz
                    avg_x = sum(p.gaze_x for p in current_batch) / len(current_batch)
                    avg_y = sum(p.gaze_y for p in current_batch) / len(current_batch)
                    duration = current_batch[-1].timestamp_ms - current_batch[0].timestamp_ms

                    target_id = self._map_to_ui(avg_x, avg_y, ui_bounds)
                    c = FixationCluster(
                        cluster_id=f"FIX_{int(current_batch[0].timestamp_ms)}",
                        centroid_x=avg_x,
                        centroid_y=avg_y,
                        duration_ms=duration,
                        microsaccade_count=microsaccade_counter,
                        focus_target_id=target_id
                    )
                    clusters.append(c)

                current_batch = [s]
                microsaccade_counter = 0

        if current_batch and len(current_batch) >= 5:
            avg_x = sum(p.gaze_x for p in current_batch) / len(current_batch)
            avg_y = sum(p.gaze_y for p in current_batch) / len(current_batch)
            duration = current_batch[-1].timestamp_ms - current_batch[0].timestamp_ms
            target_id = self._map_to_ui(avg_x, avg_y, ui_bounds)
            clusters.append(FixationCluster(
                cluster_id=f"FIX_{int(current_batch[0].timestamp_ms)}",
                centroid_x=avg_x,
                centroid_y=avg_y,
                duration_ms=duration,
                microsaccade_count=microsaccade_counter,
                focus_target_id=target_id
            ))

        self.fixation_history.extend(clusters)
        return clusters

    def _map_to_ui(self, x: float, y: float, ui_bounds: Dict[str, Tuple[float, float, float, float]]) -> Optional[str]:
        for elem_id, (x1, y1, x2, y2) in ui_bounds.items():
            if x1 <= x <= x2 and y1 <= y <= y2:
                return elem_id
        return None

    def calculate_gaze_entropy(self, samples: List[SaccadeSample]) -> float:
        """Calculates Shannon entropy of gaze spatial distribution to evaluate cognitive visual dispersion."""
        if not samples:
            return 0.0

        grid_counts: Dict[Tuple[int, int], int] = {}
        grid_size = 50.0  # 50px spatial binning

        for s in samples:
            gx = int(s.gaze_x // grid_size)
            gy = int(s.gaze_y // grid_size)
            grid_counts[(gx, gy)] = grid_counts.get((gx, gy), 0) + 1

        total = len(samples)
        entropy = 0.0
        for count in grid_counts.values():
            p = count / total
            if p > 0:
                entropy -= p * math.log2(p)

        return round(entropy, 4)

    def decode_intent(
        self,
        samples: List[SaccadeSample],
        ui_bounds: Dict[str, Tuple[float, float, float, float]]
    ) -> Dict[str, Any]:
        """Analyzes micro-saccade burst rates, pupil dilation, and fixation stability to classify operator cognitive intent."""
        kinematics = self.compute_kinematics(samples)
        microsaccades = self.filter_microsaccades(samples)
        fixations = self.detect_fixations(kinematics, ui_bounds)
        entropy = self.calculate_gaze_entropy(kinematics)

        ms_frequency = len(microsaccades) / (len(samples) / float(self.sampling_rate)) if samples else 0.0
        avg_pupil = sum(s.pupil_diameter_mm for s in samples) / len(samples) if samples else 0.0

        dominant_target = None
        max_duration = 0.0
        for f in fixations:
            if f.focus_target_id and f.duration_ms > max_duration:
                max_duration = f.duration_ms
                dominant_target = f.focus_target_id

        if ms_frequency > 5.0 and avg_pupil > 4.2:
            intent = CognitiveIntentType.SYSTEM_OVERRIDE_PREPARATION
            confidence = min(0.98, 0.65 + (ms_frequency * 0.05))
        elif max_duration > 350.0:
            intent = CognitiveIntentType.DEEP_INSPECTION
            confidence = min(0.95, 0.70 + (max_duration / 1000.0))
        elif entropy > 3.0:
            intent = CognitiveIntentType.VISUAL_SEARCH_EXPLORATION
            confidence = min(0.90, entropy / 4.0)
        elif dominant_target is not None:
            intent = CognitiveIntentType.FOCUS_TARGET_LOCK
            confidence = 0.88
        else:
            intent = CognitiveIntentType.COGNITIVE_FATIGUE_DRIFT
            confidence = 0.60

        return {
            "intent": intent.value,
            "confidence": round(confidence, 4),
            "dominant_target": dominant_target,
            "microsaccade_rate_hz": round(ms_frequency, 2),
            "gaze_entropy": entropy,
            "avg_pupil_diameter_mm": round(avg_pupil, 2),
            "fixation_count": len(fixations)
        }


if __name__ == "__main__":
    import random

    print("[*] Initializing Ocular Micro-Saccade Intent Decoder...")
    decoder = OcularMicrosaccadeIntentDecoder(sampling_rate_hz=250)

    ui_layout = {
        "CRITICAL_OVERRIDE_BUTTON": (400.0, 300.0, 550.0, 380.0),
        "TELEMETRY_STREAM_PANEL": (50.0, 50.0, 350.0, 500.0),
        "TACTICAL_MAP_VIEW": (600.0, 100.0, 1200.0, 700.0)
    }

    synthetic_samples = []
    base_time = time.time() * 1000.0
    for i in range(100):
        t = base_time + (i * 4.0)
        jitter_x = random.uniform(-4.0, 4.0) + (15.0 if i % 10 == 0 else 0.0)
        jitter_y = random.uniform(-4.0, 4.0) + (15.0 if i % 10 == 0 else 0.0)
        pupil = 4.5 + random.uniform(-0.1, 0.2)

        synthetic_samples.append(
            SaccadeSample(
                timestamp_ms=t,
                gaze_x=475.0 + jitter_x,
                gaze_y=340.0 + jitter_y,
                pupil_diameter_mm=pupil
            )
        )

    print(f"[*] Generated {len(synthetic_samples)} gaze trajectory samples.")

    decoded_result = decoder.decode_intent(synthetic_samples, ui_layout)
    print("[+] Decoded Operator Cognitive Intent:")
    for key, val in decoded_result.items():
        print(f"    - {key}: {val}")

    assert decoded_result["dominant_target"] == "CRITICAL_OVERRIDE_BUTTON"
    assert decoded_result["confidence"] > 0.70
    print("[✓] Ocular Micro-Saccade Intent Decoder verification successful.")
