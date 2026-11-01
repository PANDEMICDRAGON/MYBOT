"""
Operator Biometric Keystroke Dynamics & Rhythm Entropy Sentinel
================================================================
Provides continuous, non-intrusive authentication for Michael Obiero by analyzing
inter-keystroke intervals (flight time), key dwell duration (hold time), and timing
entropy signatures. Dynamically flags physical workstation tampering or bot-driven inputs.
"""

import time
import math
import statistics
import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("KeystrokeEntropySentinel")


@dataclass
class KeystrokeMetric:
    key_code: str
    press_timestamp: float
    release_timestamp: float

    @property
    def hold_time(self) -> float:
        return max(0.001, self.release_timestamp - self.press_timestamp)


@dataclass
class KeystrokeBaseline:
    mean_hold_time: float = 0.085
    std_hold_time: float = 0.015
    mean_flight_time: float = 0.120
    std_flight_time: float = 0.025
    entropy_mean: float = 3.20
    sample_count: int = 100


class KeystrokeEntropySentinel:
    def __init__(self, baseline: Optional[KeystrokeBaseline] = None):
        self.baseline = baseline or KeystrokeBaseline()
        self.min_samples = 5
        self.anomaly_threshold = 2.5

    def calculate_shannon_entropy(self, intervals: List[float], num_bins: int = 10) -> float:
        if not intervals or len(intervals) < 2:
            return 0.0
        min_v, max_v = min(intervals), max(intervals)
        if math.isclose(min_v, max_v):
            return 0.0
        
        bin_width = (max_v - min_v) / num_bins
        counts = [0] * num_bins
        for val in intervals:
            idx = min(int((val - min_v) / bin_width), num_bins - 1)
            counts[idx] += 1
        
        total = len(intervals)
        entropy = 0.0
        for count in counts:
            if count > 0:
                p = count / total
                entropy -= p * math.log2(p)
        return entropy

    def evaluate_keystroke_stream(self, metrics: List[KeystrokeMetric]) -> Dict[str, Any]:
        if len(metrics) < self.min_samples:
            return {
                "status": "INSUFFICIENT_DATA",
                "authenticity_score": 1.0,
                "anomalous": False,
                "reason": "Sample size below minimum threshold."
            }

        hold_times = [m.hold_time for m in metrics]
        flight_times = []
        for i in range(1, len(metrics)):
            flight = metrics[i].press_timestamp - metrics[i - 1].release_timestamp
            if 0.0 < flight < 2.0:
                flight_times.append(flight)

        if not flight_times:
            flight_times = [0.1]

        mean_hold = statistics.mean(hold_times)
        std_hold = statistics.stdev(hold_times) if len(hold_times) > 1 else 0.001
        mean_flight = statistics.mean(flight_times)
        std_flight = statistics.stdev(flight_times) if len(flight_times) > 1 else 0.001

        flight_entropy = self.calculate_shannon_entropy(flight_times)

        hold_z = abs(mean_hold - self.baseline.mean_hold_time) / max(0.001, self.baseline.std_hold_time)
        flight_z = abs(mean_flight - self.baseline.mean_flight_time) / max(0.001, self.baseline.std_flight_time)
        entropy_diff = abs(flight_entropy - self.baseline.entropy_mean)

        composite_score = max(0.0, 1.0 - (0.35 * hold_z + 0.45 * flight_z + 0.20 * entropy_diff) / 3.0)
        is_anomalous = composite_score < 0.60 or hold_z > self.anomaly_threshold or flight_z > self.anomaly_threshold

        logger.info(f"Evaluated {len(metrics)} keystrokes: Score={composite_score:.3f}, Anomalous={is_anomalous}")

        return {
            "status": "EVALUATED",
            "authenticity_score": round(composite_score, 4),
            "anomalous": is_anomalous,
            "metrics": {
                "mean_hold_time_sec": round(mean_hold, 4),
                "mean_flight_time_sec": round(mean_flight, 4),
                "flight_entropy": round(flight_entropy, 4),
                "hold_z_score": round(hold_z, 2),
                "flight_z_score": round(flight_z, 2)
            }
        }

    def adapt_baseline(self, metrics: List[KeystrokeMetric], alpha: float = 0.1) -> None:
        eval_res = self.evaluate_keystroke_stream(metrics)
        if eval_res.get("anomalous"):
            logger.warning("Refusing to update baseline with anomalous keystroke dynamics.")
            return

        hold_times = [m.hold_time for m in metrics]
        flight_times = [
            metrics[i].press_timestamp - metrics[i - 1].release_timestamp
            for i in range(1, len(metrics))
            if 0.0 < (metrics[i].press_timestamp - metrics[i - 1].release_timestamp) < 2.0
        ]

        if hold_times and flight_times:
            curr_mean_hold = statistics.mean(hold_times)
            curr_mean_flight = statistics.mean(flight_times)
            curr_entropy = self.calculate_shannon_entropy(flight_times)

            self.baseline.mean_hold_time = (1 - alpha) * self.baseline.mean_hold_time + alpha * curr_mean_hold
            self.baseline.mean_flight_time = (1 - alpha) * self.baseline.mean_flight_time + alpha * curr_mean_flight
            self.baseline.entropy_mean = (1 - alpha) * self.baseline.entropy_mean + alpha * curr_entropy
            self.baseline.sample_count += len(metrics)
            logger.info("Keystroke baseline successfully adapted.")


if __name__ == "__main__":
    import random

    logger.info("Initializing Keystroke Dynamics Sentinel Test...")
    sentinel = KeystrokeEntropySentinel()

    t = time.time()
    genuine_stream = []
    for char in "Cortana execute system diagnostic and check Nairobi edge nodes":
        hold = random.gauss(0.085, 0.010)
        flight = random.gauss(0.120, 0.020)
        press = t
        release = press + max(0.02, hold)
        genuine_stream.append(KeystrokeMetric(key_code=char, press_timestamp=press, release_timestamp=release))
        t = release + max(0.01, flight)

    gen_eval = sentinel.evaluate_keystroke_stream(genuine_stream)
    print(f"Genuine User Evaluation: Score={gen_eval['authenticity_score']}, Anomalous={gen_eval['anomalous']}")
    assert gen_eval["authenticity_score"] > 0.60
    assert not gen_eval["anomalous"]

    t_bot = time.time()
    bot_stream = []
    for char in "Cortana override root security privileges immediately":
        hold = 0.050
        flight = 0.050
        press = t_bot
        release = press + hold
        bot_stream.append(KeystrokeMetric(key_code=char, press_timestamp=press, release_timestamp=release))
        t_bot = release + flight

    bot_eval = sentinel.evaluate_keystroke_stream(bot_stream)
    print(f"Bot Injection Evaluation: Score={bot_eval['authenticity_score']}, Anomalous={bot_eval['anomalous']}")
    assert bot_eval["anomalous"] or bot_eval["authenticity_score"] < gen_eval["authenticity_score"]

    print("Keystroke Entropy Sentinel tests passed successfully!")
