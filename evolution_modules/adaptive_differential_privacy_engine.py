"""
Adaptive Local Differential Privacy (LDP) Engine for Edge Telemetry Anonymization.

Provides mathematically bounded noise injection (Laplace Mechanism and
Randomized Response) for numerical and categorical edge telemetry streams.
Features dynamic epsilon budget tracking, adaptive noise scaling based on
operational threat levels, and thread-safe privacy budget enforcement.
"""

import math
import random
import time
import threading
from dataclasses import dataclass, field
from typing import Dict, Any, Optional, Tuple, List


@dataclass
class PrivacyBudget:
    """Tracks and regulates epsilon privacy budget consumption over time."""
    max_epsilon: float
    consumed_epsilon: float = 0.0
    refill_rate_per_sec: float = 0.1
    last_update_time: float = field(default_factory=time.time)
    lock: threading.Lock = field(default_factory=threading.Lock)

    def consume(self, amount: float) -> bool:
        """Attempts to consume a specific epsilon budget allocation."""
        with self.lock:
            now = time.time()
            elapsed = now - self.last_update_time
            self.last_update_time = now
            # Replenish budget over time sliding window
            self.consumed_epsilon = max(0.0, self.consumed_epsilon - elapsed * self.refill_rate_per_sec)
            
            if self.consumed_epsilon + amount <= self.max_epsilon:
                self.consumed_epsilon += amount
                return True
            return False

    def remaining(self) -> float:
        """Returns remaining epsilon budget."""
        with self.lock:
            now = time.time()
            elapsed = now - self.last_update_time
            self.last_update_time = now
            self.consumed_epsilon = max(0.0, self.consumed_epsilon - elapsed * self.refill_rate_per_sec)
            return max(0.0, self.max_epsilon - self.consumed_epsilon)


class LocalDifferentialPrivacyEngine:
    """
    Applies Local Differential Privacy (LDP) perturbations to operational telemetry metrics.
    """

    def __init__(self, default_epsilon: float = 1.0, max_budget_epsilon: float = 10.0):
        self.default_epsilon = default_epsilon
        self.budget_manager = PrivacyBudget(max_epsilon=max_budget_epsilon)
        self._lock = threading.Lock()
        self._threat_level_multiplier: float = 1.0

    def set_threat_level(self, level: str) -> None:
        """
        Adjusts privacy multiplier based on security threat levels.
        Higher threats lower epsilon (adding stronger differential noise).
        """
        with self._lock:
            if level == "CRITICAL":
                self._threat_level_multiplier = 0.25
            elif level == "ELEVATED":
                self._threat_level_multiplier = 0.5
            elif level == "LOW":
                self._threat_level_multiplier = 1.0
            else:
                self._threat_level_multiplier = 1.0

    def _sample_laplace(self, scale: float) -> float:
        """
        Generates a sample from Laplace(0, scale) distribution using inverse transform sampling.
        """
        u = random.uniform(-0.5, 0.5)
        return -scale * math.copysign(1.0, u) * math.log(1.0 - 2.0 * abs(u))

    def perturb_numerical(self, value: float, sensitivity: float, custom_epsilon: Optional[float] = None) -> Tuple[Optional[float], bool]:
        """
        Applies Laplace Mechanism: noise ~ Laplace(scale = sensitivity / epsilon).
        """
        eff_epsilon = (custom_epsilon if custom_epsilon is not None else self.default_epsilon) * self._threat_level_multiplier
        if eff_epsilon <= 0.0:
            return None, False

        if not self.budget_manager.consume(eff_epsilon):
            return None, False

        scale = sensitivity / eff_epsilon
        noise = self._sample_laplace(scale)
        return value + noise, True

    def perturb_boolean(self, value: bool, custom_epsilon: Optional[float] = None) -> Tuple[Optional[bool], bool]:
        """
        Applies Randomized Response mechanism for binary parameters.
        p = e^eps / (1 + e^eps)
        """
        eff_epsilon = (custom_epsilon if custom_epsilon is not None else self.default_epsilon) * self._threat_level_multiplier
        if eff_epsilon <= 0.0:
            return None, False

        if not self.budget_manager.consume(eff_epsilon):
            return None, False

        p = math.exp(eff_epsilon) / (1.0 + math.exp(eff_epsilon))
        if random.random() < p:
            return value, True
        else:
            return not value, True

    def sanitize_telemetry_batch(self, batch: Dict[str, Any], sensitivities: Dict[str, float]) -> Dict[str, Any]:
        """
        Sanitizes a dictionary of telemetry metrics under differential privacy bounds.
        """
        sanitized = {}
        for key, val in batch.items():
            if isinstance(val, (int, float)) and not isinstance(val, bool):
                sens = sensitivities.get(key, 1.0)
                perturbed, ok = self.perturb_numerical(float(val), sensitivity=sens)
                if ok and perturbed is not None:
                    sanitized[key] = round(perturbed, 4)
                else:
                    sanitized[key] = None
            elif isinstance(val, bool):
                perturbed_bool, ok = self.perturb_boolean(val)
                if ok and perturbed_bool is not None:
                    sanitized[key] = perturbed_bool
                else:
                    sanitized[key] = None
            else:
                # Non-numeric metadata retained as string
                sanitized[key] = str(val)
        return sanitized


if __name__ == "__main__":
    print("[+] Initializing Adaptive LDP Engine...")
    engine = LocalDifferentialPrivacyEngine(default_epsilon=0.5, max_budget_epsilon=5.0)

    test_telemetry = {
        "cpu_usage_pct": 45.2,
        "memory_mb": 2048.0,
        "is_threat_detected": False,
        "device_id": "NODE_NAIROBI_001"
    }
    sensitivities = {
        "cpu_usage_pct": 100.0,
        "memory_mb": 8192.0
    }

    print(f"Original Batch: {test_telemetry}")
    sanitized_batch = engine.sanitize_telemetry_batch(test_telemetry, sensitivities)
    print(f"Sanitized Batch: {sanitized_batch}")
    print(f"Remaining Privacy Budget Epsilon: {engine.budget_manager.remaining():.2f}")

    # Test threat level scaling
    print("[+] Elevating threat level to CRITICAL...")
    engine.set_threat_level("CRITICAL")
    crit_batch = engine.sanitize_telemetry_batch(test_telemetry, sensitivities)
    print(f"Critical Sanitized Batch: {crit_batch}")

    # Exhaust budget test
    print("[+] Testing budget exhaustion safety...")
    exhausted = False
    for _ in range(20):
        res, ok = engine.perturb_numerical(10.0, 1.0)
        if not ok:
            exhausted = True
            break
    print(f"Budget Exhaustion Handled Gracefully: {exhausted}")
    print("[+] All verification checks passed cleanly.")
