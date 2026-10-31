"""
quantum_anomaly_detection_engine.py
Provides a lightweight anomaly detection using statistical thresholds
augmented with quantum‑grade randomness for jitter.
"""

from __future__ import annotations
import random
import math
from typing import List, Sequence

try:
    import numpy as np
except Exception:  # pragma: no cover
    np = None


class QuantumAnomalyDetector:
    """
    Detects outliers in a numeric series.

    The detector learns the mean and standard deviation of a training
    window and flags values that deviate beyond ``threshold`` standard
    deviations.  To avoid deterministic patterns, a quantum‑style
    jitter (simulated with ``random.SystemRandom``) is added to the
    threshold at detection time.
    """

    def __init__(self, threshold: float = 3.0) -> None:
        if threshold <= 0:
            raise ValueError("threshold must be positive")
        self.threshold = threshold
        self._mean: float | None = None
        self._std: float | None = None
        self._rng = random.SystemRandom()

    def fit(self, data: Sequence[float]) -> None:
        """
        Compute mean and standard deviation from ``data``.
        """
        if not data:
            raise ValueError("training data cannot be empty")
        if np:
            arr = np.asarray(data, dtype=float)
            self._mean = float(np.mean(arr))
            self._std = float(np.std(arr, ddof=1))
        else:
            n = len(data)
            self._mean = sum(data) / n
            variance = sum((x - self._mean) ** 2 for x in data) / (n - 1 if n > 1 else 1)
            self._std = math.sqrt(variance)

    def _jittered_threshold(self) -> float:
        """
        Return the threshold perturbed by a tiny random factor.
        """
        jitter = self._rng.uniform(-0.05, 0.05)  # ±5%
        return self.threshold * (1 + jitter)

    def predict(self, points: Sequence[float]) -> List[bool]:
        """
        Return a list indicating whether each point is an anomaly.
        """
        if self._mean is None or self._std is None:
            raise RuntimeError("fit must be called before predict")
        if self._std == 0:
            # All points equal; treat any deviation as anomaly
            return [abs(p - self._mean) > 0 for p in points]

        thresh = self._jittered_threshold()
        limit = thresh * self._std
        return [abs(p - self._mean) > limit for p in points]

    def fit_predict(self, data: Sequence[float]) -> List[bool]:
        """
        Convenience method that fits on ``data`` and returns anomaly flags.
        The last point is treated as the test point.
        """
        if len(data) < 2:
            raise ValueError("need at least two points for fit/predict")
        self.fit(data[:-1])
        return self.predict([data[-1]])


def _demo() -> None:
    # synthetic normal data
    normal = [random.gauss(0, 1) for _ in range(1000)]
    # inject anomalies
    test_points = normal + [5.0, -6.2, 0.2]
    detector = QuantumAnomalyDetector(threshold=3.0)
    detector.fit(normal)
    results = detector.predict(test_points[-3:])
    for pt, is_anom in zip(test_points[-3:], results):
        print(f"Value {pt:.2f} -> {'ANOMALY' if is_anom else 'normal'}")


if __name__ == "__main__":
    _demo()
