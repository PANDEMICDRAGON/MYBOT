"""
Operator Multimodal Cognitive Attention & Workload Governor Module
Evolves Cortana's interaction surface by real-time tracking of operator telemetry
and system memory pressure to dynamically tune AI verbosity and background execution.
"""

from dataclasses import dataclass, field
import math
import threading
import time
from typing import Dict, List, Optional, Tuple, Any


@dataclass
class TelemetryFrame:
    timestamp: float
    keystroke_interval_ms: float
    backspace_rate: float
    task_switch_rate: float
    system_ram_percent: float
    active_focus_domain: str


@dataclass
class CognitiveWorkloadProfile:
    fatigue_index: float
    granularity_mode: str
    recommended_token_cap: int
    throttle_ratio: float
    timestamp: float


class OperatorAttentionGovernor:
    """
    Monitors operator telemetry and system memory status to dynamically adapt
    AI context depth, response verbosity, and background task scheduling.
    """
    def __init__(self, history_window: int = 50, ram_threshold_percent: float = 85.0):
        self._history_window = history_window
        self._ram_threshold_percent = ram_threshold_percent
        self._lock = threading.Lock()
        self._telemetry_history: List[TelemetryFrame] = []
        self._current_profile: Optional[CognitiveWorkloadProfile] = None

    def record_telemetry(self, frame: TelemetryFrame) -> None:
        with self._lock:
            self._telemetry_history.append(frame)
            if len(self._telemetry_history) > self._history_window:
                self._telemetry_history.pop(0)

    def compute_workload_index(self) -> CognitiveWorkloadProfile:
        with self._lock:
            if not self._telemetry_history:
                profile = CognitiveWorkloadProfile(
                    fatigue_index=0.0,
                    granularity_mode="BALANCED",
                    recommended_token_cap=2048,
                    throttle_ratio=1.0,
                    timestamp=time.time()
                )
                self._current_profile = profile
                return profile

            recent = self._telemetry_history[-20:]
            avg_interval = sum(f.keystroke_interval_ms for f in recent) / len(recent)
            avg_backspace = sum(f.backspace_rate for f in recent) / len(recent)
            avg_task_switches = sum(f.task_switch_rate for f in recent) / len(recent)
            latest_ram = recent[-1].system_ram_percent

            # Calculate raw fatigue index based on erratic keystrokes and high switch rates
            interval_variance = sum((f.keystroke_interval_ms - avg_interval) ** 2 for f in recent) / len(recent)
            std_dev_interval = math.sqrt(interval_variance)

            # Heuristic normalization
            fatigue_score = min(1.0, (avg_backspace * 2.5) + (avg_task_switches * 0.15) + (std_dev_interval / 500.0))
            
            # RAM pressure weighting
            ram_stress = max(0.0, (latest_ram - self._ram_threshold_percent) / (100.0 - self._ram_threshold_percent))
            combined_index = min(1.0, 0.7 * fatigue_score + 0.3 * ram_stress)

            if combined_index > 0.75:
                mode = "ULTRA_COMPACT"
                token_cap = 512
                throttle = 0.25
            elif combined_index > 0.5:
                mode = "BALANCED"
                token_cap = 1024
                throttle = 0.5
            elif combined_index > 0.25:
                mode = "DETAILED"
                token_cap = 2048
                throttle = 0.85
            else:
                mode = "VERBOSE"
                token_cap = 4096
                throttle = 1.0

            profile = CognitiveWorkloadProfile(
                fatigue_index=round(combined_index, 4),
                granularity_mode=mode,
                recommended_token_cap=token_cap,
                throttle_ratio=throttle,
                timestamp=time.time()
            )
            self._current_profile = profile
            return profile

    def adapt_output_verbosity(self, message: str) -> str:
        profile = self.compute_workload_index()
        if profile.granularity_mode == "ULTRA_COMPACT":
            lines = message.strip().split("\n")
            summary = [l for l in lines if l.strip().startswith(("-", "*", "•", "1.", "2.", "3.", "[", "SYSTEM", "ALERT", "ACTION"))]
            if not summary:
                summary = lines[:2]
            return "[COMPACT MODE] " + " ".join(summary)
        elif profile.granularity_mode == "BALANCED":
            lines = message.strip().split("\n")
            return "\n".join(lines[:10]) if len(lines) > 10 else message
        return message

    def get_throttling_directives(self) -> Dict[str, Any]:
        profile = self._current_profile or self.compute_workload_index()
        return {
            "fatigue_index": profile.fatigue_index,
            "granularity_mode": profile.granularity_mode,
            "recommended_token_cap": profile.recommended_token_cap,
            "background_task_throttle_ratio": profile.throttle_ratio,
            "system_ram_pressure_mitigated": profile.fatigue_index > 0.7
        }


if __name__ == "__main__":
    governor = OperatorAttentionGovernor()
    for i in range(15):
        frame = TelemetryFrame(
            timestamp=time.time() + i,
            keystroke_interval_ms=120.0 + (i * 15),
            backspace_rate=0.05 + (i * 0.02),
            task_switch_rate=1.0 + (i * 0.2),
            system_ram_percent=89.4,
            active_focus_domain="OPERATOR_AMPLIFICATION"
        )
        governor.record_telemetry(frame)

    prof = governor.compute_workload_index()
    print("Computed Profile:", prof)
    test_payload = "Header: Security Audit Results\n- Alert: High RAM detected\n- Action: Compacted memory buffers\n- Notice: Swarm heartbeat active\nAdditional technical stack trace information follows here..."
    print("Adapted Output:", governor.adapt_output_verbosity(test_payload))
    print("Directives:", governor.get_throttling_directives())
