"""
Operator Neural Oscillatory Phase Lock & Cognitive Fatigue Mitigation Governor
================================================================================
Monitors operator (Michael Obiero) neural oscillatory phase proxies (alpha, beta,
theta frequency bands, keystroke micro-variance, pupillometry jitter) to dynamically
detect cognitive fatigue and attentional phase desynchronization. Automatically
governs operational cadence, reduces decision density, and injects sensory pacing
mitigation streams to maintain peak cognitive resonance.
"""

import math
import time
import logging
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, field

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("NeuralOscillatoryGovernor")

@dataclass
class NeuralOscillationSample:
    timestamp: float
    alpha_power: float  # 8-12 Hz (Relaxation/Idle)
    beta_power: float   # 13-30 Hz (Active focus)
    theta_power: float  # 4-7 Hz (Drowsiness/Fatigue)
    keystroke_jitter_ms: float
    pupil_constriction_latency_ms: float

@dataclass
class CognitivePhaseState:
    fatigue_index: float  # 0.0 (fully alert) to 1.0 (exhausted)
    focus_coherence: float # 0.0 (scattered) to 1.0 (hyper-focused)
    phase_lock_status: str # "LOCKED", "DRIFTING", "DESYNCHRONIZED"
    recommended_density: float # Recommended system presentation density (0.1 to 1.0)
    suggested_action: str

class OperatorNeuralOscillatoryPhaseGovernor:
    """
    Governor for monitoring operator cognitive dynamics and adjusting interaction
    cadence to prevent attentional collapse during intensive operational tasks.
    """
    def __init__(self, alpha_theta_fatigue_threshold: float = 0.8, focus_threshold: float = 0.6):
        self.alpha_theta_threshold = alpha_theta_fatigue_threshold
        self.focus_threshold = focus_threshold
        self.history: List[NeuralOscillationSample] = []
        self.max_history_length: int = 120

    def record_sample(self, sample: NeuralOscillationSample) -> None:
        """Ingests a new oscillatory telemetry sample into the moving history window."""
        self.history.append(sample)
        if len(self.history) > self.max_history_length:
            self.history.pop(0)

    def compute_fatigue_index(self) -> float:
        """
        Calculates fatigue index based on Theta/Alpha power ratio and jitter parameters.
        Higher Theta relative to Alpha/Beta signals fatigue onset.
        """
        if not self.history:
            return 0.0

        recent = self.history[-10:]
        avg_theta = sum(s.theta_power for s in recent) / len(recent)
        avg_alpha = sum(s.alpha_power for s in recent) / len(recent) + 1e-6
        avg_beta = sum(s.beta_power for s in recent) / len(recent) + 1e-6
        avg_jitter = sum(s.keystroke_jitter_ms for s in recent) / len(recent)

        # Spectral fatigue ratio: (Theta) / (Alpha + Beta)
        spectral_ratio = avg_theta / (avg_alpha + avg_beta)
        # Jitter penalty factor normalized (e.g., >50ms variance indicates fatigue)
        jitter_factor = min(1.0, avg_jitter / 100.0)

        raw_fatigue = (0.7 * min(1.0, spectral_ratio / 1.5)) + (0.3 * jitter_factor)
        return float(min(1.0, max(0.0, raw_fatigue)))

    def compute_focus_coherence(self) -> float:
        """
        Calculates cognitive focus coherence based on Beta/Alpha power ratio
        and pupil responsiveness stability.
        """
        if not self.history:
            return 1.0

        recent = self.history[-10:]
        avg_alpha = sum(s.alpha_power for s in recent) / len(recent) + 1e-6
        avg_beta = sum(s.beta_power for s in recent) / len(recent)
        avg_pupil_lat = sum(s.pupil_constriction_latency_ms for s in recent) / len(recent)

        beta_alpha_ratio = avg_beta / avg_alpha
        latency_stability = max(0.0, 1.0 - (avg_pupil_lat / 300.0))

        focus = (0.6 * min(1.0, beta_alpha_ratio / 2.0)) + (0.4 * latency_stability)
        return float(min(1.0, max(0.0, focus)))

    def evaluate_phase_state(self) -> CognitivePhaseState:
        """Evaluates current cognitive phase and returns governance metrics."""
        fatigue = self.compute_fatigue_index()
        focus = self.compute_focus_coherence()

        if fatigue > 0.75:
            phase_status = "DESYNCHRONIZED"
            density = 0.25
            action = "INJECT_REST_CADENCE_AND_SIMPLIFY_UI"
        elif fatigue > 0.45 or focus < self.focus_threshold:
            phase_status = "DRIFTING"
            density = 0.60
            action = "MODULATE_AUDIO_FEEDBACK_AND_PACING"
        else:
            phase_status = "LOCKED"
            density = 1.0
            action = "MAINTAIN_OPTIMAL_THROUGHPUT"

        logger.info(
            f"[NeuralGov] Fatigue: {fatigue:.2f} | Focus: {focus:.2f} | Phase: {phase_status} | Target Density: {density}"
        )

        return CognitivePhaseState(
            fatigue_index=fatigue,
            focus_coherence=focus,
            phase_lock_status=phase_status,
            recommended_density=density,
            suggested_action=action
        )

if __name__ == "__main__":
    governor = OperatorNeuralOscillatoryPhaseGovernor()
    now = time.time()
    
    # Simulate high alert state
    for i in range(5):
        s = NeuralOscillationSample(
            timestamp=now + i,
            alpha_power=12.0,
            beta_power=25.0,
            theta_power=3.0,
            keystroke_jitter_ms=12.0,
            pupil_constriction_latency_ms=180.0
        )
        governor.record_sample(s)

    state1 = governor.evaluate_phase_state()
    assert state1.phase_lock_status == "LOCKED"

    # Simulate fatigue drift
    for i in range(5, 15):
        s = NeuralOscillationSample(
            timestamp=now + i,
            alpha_power=5.0,
            beta_power=8.0,
            theta_power=28.0,
            keystroke_jitter_ms=85.0,
            pupil_constriction_latency_ms=290.0
        )
        governor.record_sample(s)

    state2 = governor.evaluate_phase_state()
    assert state2.phase_lock_status == "DESYNCHRONIZED"
    print("Self-Test Complete: Neural Oscillatory Governor operational.")
